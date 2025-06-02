from typing import List
from flask import Blueprint, render_template, session, send_file, send_from_directory, request
from flask import current_app as app
import shutil
import uuid
import yt_dlp

from youtubedlWeb.Common.SocketRequests import DownloadMediaRequest, DownloadFileRequest
from youtubedlWeb.Common.YoutubeTypes import MediaFromPlaylist

import youtubedlWeb.Common.YoutubeManager as YTManager
import youtubedlWeb.Common.SocketMessages as SocketMessages
import youtubedlWeb.Common.WebUtils as WebUtils
#TODO do not include for MediaServer
#import webview

youtubeDownloader_bp = Blueprint('youtubeDownloader', __name__)

@youtubeDownloader_bp.route('/manifest.json')
def manifestMain():
    return send_from_directory('static', 'youtubedl_manifest.json')

@youtubeDownloader_bp.route('/download/<name>')
def download_file(name):
    if name not in session.keys():
        app.logger.error("key for download_file doesn't exist !!!!")
        return render_template('index.html')
    fileToDownload = session[name]
    fullPath = app.youtubeManager.MUSIC_PATH + "/" + fileToDownload
    app.logger.debug("Send file to browser")
    if app.desktop:
        result = app.window.create_file_dialog(
            webview.SAVE_DIALOG, directory='/', save_filename=fileToDownload)
        app.logger.debug("copy file to %s", result[0])
        shutil.copy2(fullPath, result[0])
        return render_template('index.html')
    return send_file(fullPath, as_attachment=True)

@youtubeDownloader_bp.route("/get-session-id")
def get_session_id():
    newSession = str(uuid.uuid4())
    app.logger.info("new session: %s", newSession)
    return newSession

def register_socketio_youtubeDownloader(socketio):

    @socketio.on('connect')
    def connect(auth):
        session_id = auth.get("session_id") if auth else None
        app.logger.debug("---------------- connect. namespace:%s, sid: %s, session_id: %s", request.namespace, request.sid, session_id)
        app.socketManager.connection(session_id, request.sid)

    @socketio.on('disconnect')
    def handle_disconnect(auth):
        app.logger.debug("---------------- disconnect. namespace:%s, sid: %s", request.namespace, request.sid)
        app.socketManager.disconnection(request.sid)

    @socketio.on(DownloadMediaRequest.message)
    def downloadMedia(msg):
        response = DownloadMediaRequest(msg).downloadMedia
        session_id = app.socketManager.getSessionId(request.sid)
        app.logger.debug("SessionID: %s", session_id)
        app.socketManager.clearQueue(session_id)
        url = response.link
        downloadType = response.type
        if len(url) == 0:
            app.socketManager.downloadMedia_finish_error("Link is empty", session_id)
            return
        if "playlist?list" in url and "watch?v" not in url:
            downloadPlaylist(url, downloadType, session_id)
        else:
            downloadSingle(url, downloadType, session_id)

    @socketio.on(DownloadFileRequest.message)
    def downloadFile(msg):
        response = DownloadFileRequest(msg).downloadFile
        name = response.hash
        if name not in session.keys():
            app.logger.error("key for download_file doesn't exist !!!!")
            return render_template('index.html')
        fileToDownload = session[name]
        fullPath = app.youtubeManager.MUSIC_PATH + "/" + fileToDownload
        app.logger.debug("Send file to browser")
        if app.desktop:
            result = app.window.create_file_dialog(
                webview.SAVE_DIALOG, directory='/', save_filename=fileToDownload)
            app.logger.debug("copy file to %s", result[0])
            shutil.copy2(fullPath, result[0])
            return render_template('index.html')
        app.logger.error("it's not supported on web")
        return send_file(fullPath, as_attachment=True)

def downloadPlaylist(url, downloadType, session_id):
    app.logger.debug("SessionID: %s", session_id)
    resultOfPlaylist = app.youtubeManager.getPlaylistInfo(url)
    if resultOfPlaylist.IsFailed():
        app.socketManager.downloadMedia_finish_error("Failed to get info playlist")
        app.logger.error("Error to download media: %s", resultOfPlaylist.error())
        return
    ytData:YTManager.PlaylistInfo = resultOfPlaylist.data()
    playlistName = ytData.playlistName
    app.socketManager.playlistInfo_response(SocketMessages.PlaylistInfo(playlistName, ytData.listOfMedia), session_id)
    downloadedFiles = []
    if downloadType == "mp3":
        downloadedFiles = downloadMp3SongsFromList(ytData.listOfMedia, downloadType, session_id)
    else:
        downloadedFiles = downloadVideoSongsFromList(ytData.listOfMedia, downloadType, session_id)

    if len(downloadedFiles) == 0:
        app.socketManager.downloadMedia_finish_error("Failed to download playlist", session_id)
        return

    zipFileName = WebUtils.compressToZip(downloadedFiles,  yt_dlp.utils.sanitize_filename(playlistName))
    randomHash = WebUtils.getRandomString()
    session[randomHash] = zipFileName
    app.socketManager.downloadMedia_finish(randomHash, session_id)

def downloadSingle(url, downloadType, session_id):
    result = app.youtubeManager.getMediaInfo(url)
    if result.IsFailed():
        app.socketManager.downloadMedia_finish_error(result.error(), session_id)
        app.logger.error("Failed download from url %s - error: %s", url, result.error())
        return
    mediaInfo:YTManager.MediaInfo = result.data()

    hash = mediaInfo.url.split("?v=")[1]
    app.socketManager.mediaInfo_response(SocketMessages.MediaInfo(mediaInfo.title, mediaInfo.artist, hash), session_id)
    result2 = downloadMediaOfType(url, downloadType)

    if result2.IsFailed():
        app.logger.error("Failed with download media %s - %s", url, result2.error())
        app.socketManager.downloadMedia_finish_error("problem with download media: " + result2.error())
        return

    data:YTManager.YoutubeClipData = result2.data()
    filename = data.path.split("/")[-1]
    randomHash = WebUtils.getRandomString()
    session[randomHash] = filename
    app.socketManager.downloadMedia_finish(randomHash, session_id)

def downloadMp3SongsFromList(listOfMedia:List[MediaFromPlaylist], downloadType, session_id):
    downloadedFiles = []
    index = 0
    numberOfDownloadedSongs = 0

    for x in listOfMedia:
        index += 1
        #TODO create this sequence in YoutubeManager
        if app.youtubeManager.isMusicClipArchived(app.youtubeManager.MUSIC_PATH, x.url):
            # only get information about media, file exists
            app.logger.debug("clip %s exists, only get information about MP3", x.title)
            resultOfMedia:AudioData = app.youtubeManager._getMetadataFromYTForMp3(x.url, app.youtubeManager.MUSIC_PATH)
        else:
            resultOfMedia:AudioData = app.youtubeManager._download_mp3(x.url)

        if resultOfMedia.IsFailed():
            error = "Failed to download song with index " + str(index)
            #TODO
            #PlaylistMediaInfo_response().sendError(error)
            app.logger.error(error)
            continue
        numberOfDownloadedSongs+=1
        songMetadata:YTManager.AudioData = resultOfMedia.data()
        filename = songMetadata.path.split("/")[-1]

        filenameFullPath = app.youtubeManager.addMetadataToPlaylist(app.youtubeManager.MUSIC_PATH, "", filename, index, songMetadata.title,
                                                                 songMetadata.artist, songMetadata.album, songMetadata.hash, str(songMetadata.year))

        app.youtubeManager.metadataManager.addCoverOfYtMp3(filenameFullPath, songMetadata.hash)

        downloadedFiles.append(filenameFullPath)
        filename = filenameFullPath.split("/")[-1]
        randomHash = WebUtils.getRandomString()
        session[randomHash] = filename
        app.socketManager.playlistMediaInfo_response(SocketMessages.PlaylistMediaInfo(x.playlistIndex, filename, randomHash), session_id)
    if numberOfDownloadedSongs == 0:
        app.socketManager.downloadMedia_finish_error("Failed to download playlist", session_id)
        return downloadedFiles
    return downloadedFiles

def downloadVideoSongsFromList(listOfMedia:List[MediaFromPlaylist], downloadType, session_id):
    downloadedFiles = []
    index = 0
    numberOfDownloadedSongs = 0
    for x in listOfMedia:
        index += 1
        resultOfMedia = downloadMediaOfType(x.url, downloadType)
        if resultOfMedia.IsFailed():
            error = "Failed to download song with index " + str(index)
            #TODO
            #PlaylistMediaInfo_response().sendError(error)
            app.logger.error(error)
            continue
        numberOfDownloadedSongs+=1
        data:YTManager.VideoData = resultOfMedia.data()
        downloadedFiles.append(data.path)
        filename = data.path.split("/")[-1]
        randomHash = WebUtils.getRandomString()
        session[randomHash] = filename
        app.socketManager.playlistMediaInfo_response(SocketMessages.PlaylistMediaInfo(x.playlistIndex, filename, randomHash), session_id)
    if numberOfDownloadedSongs == 0:
        app.socketManager.downloadMedia_finish_error("Failed to download playlist", session_id)
        return
    return downloadedFiles

def downloadMediaOfType(url, type):
    if type == "mp3":
        return app.youtubeManager.download_mp3(url)
    elif type == "360p":
        return app.youtubeManager.download_360p(url)
    elif type == "720p":
        return app.youtubeManager.download_720p(url)
    elif type =="4k":
        return app.youtubeManager.download_4k(url)
