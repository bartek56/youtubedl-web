from flask import Blueprint, render_template, session, send_file, send_from_directory
from flask import current_app as app

from youtubedlWeb.Common.SocketMessages import PlaylistInfo_response, PlaylistMediaInfo_response
from youtubedlWeb.Common.SocketMessages import MediaInfo_response, DownloadMedia_finish
from youtubedlWeb.Common.SocketRequests import DownloadMediaRequest

import youtubedlWeb.Common.YoutubeManager as YTManager
import youtubedlWeb.Common.SocketMessages as SocketMessages
import youtubedlWeb.Common.WebUtils as WebUtils

youtubeDwonlaoder_bp = Blueprint('youtubeDownloader', __name__)

@youtubeDwonlaoder_bp.route('/manifest.json')
def manifestMain():
    return send_from_directory('static', 'youtubedl_manifest.json')

def downloadMediaOfType(url, type):
    if type == "mp3":
        return app.youtubeManager.download_mp3(url)
    elif type == "360p":
        return app.youtubeManager.download_360p(url)
    elif type == "720p":
        return app.youtubeManager.download_720p(url)
    elif type =="4k":
        return app.youtubeManager.download_4k(url)

def downloadSongsFromList(listOfMedia, downloadType):
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
        data:YTManager.YoutubeClipData = resultOfMedia.data()
        downloadedFiles.append(data.path)
        filename = data.path.split("/")[-1]
        randomHash = WebUtils.getRandomString()
        session[randomHash] = filename
        PlaylistMediaInfo_response().sendMessage(SocketMessages.PlaylistMediaInfo(x.playlistIndex, filename, randomHash))
    if numberOfDownloadedSongs == 0:
        DownloadMedia_finish().sendError("Failed to download playlist")
        return
    return downloadedFiles

def downloadPlaylist(url, downloadType):
        resultOfPlaylist = app.youtubeManager.getPlaylistInfo(url)
        if resultOfPlaylist.IsFailed():
            DownloadMedia_finish().sendError("Failed to get info playlist")
            app.logger.error("Error to download media: %s", resultOfPlaylist.error())
            return
        ytData:YTManager.PlaylistInfo = resultOfPlaylist.data()
        playlistName = ytData.playlistName
        PlaylistInfo_response().sendMessage(SocketMessages.PlaylistInfo(playlistName, ytData.listOfMedia))
        downloadedFiles = downloadSongsFromList(ytData.listOfMedia, downloadType)
        zipFileName = WebUtils.compressToZip(downloadedFiles, playlistName)
        randomHash = WebUtils.getRandomString()
        session[randomHash] = zipFileName
        DownloadMedia_finish().sendMessage(randomHash)

def downloadSingle(url, downloadType):
        result = app.youtubeManager.getMediaInfo(url)
        if result.IsFailed():
            DownloadMedia_finish().sendError(result.error())
            app.logger.error("Failed download from url %s - error: %s", url, result.error())
            return
        mediaInfo:YTManager.MediaInfo = result.data()

        MediaInfo_response().sendMessage(SocketMessages.MediaInfo(mediaInfo.title, mediaInfo.artist))
        result2 = downloadMediaOfType(url, downloadType)

        if result2.IsFailed():
            app.logger.error("Failed with download media %s - %s", url, result2.error())
            DownloadMedia_finish().sendError("problem with download media: " + result2.error())
            return

        data:YTManager.YoutubeClipData = result2.data()
        filename = data.path.split("/")[-1]
        randomHash = WebUtils.getRandomString()
        session[randomHash] = filename
        DownloadMedia_finish().sendMessage(randomHash)

def register_socketio_youtubeDownlaoder(socketio):
    @socketio.on(DownloadMediaRequest.message)
    def downloadMedia(msg):
        response = DownloadMediaRequest(msg).downloadMedia
        url = response.link
        downloadType = response.type
        if "playlist?list" in url and "watch?v" not in url:
            downloadPlaylist(url, downloadType)
        else:
            downloadSingle(url, downloadType)

@youtubeDwonlaoder_bp.route('/download/<name>')
def download_file(name):
    if name not in session.keys():
        app.logger.error("key for download_file doesn't exist !!!!")
        return render_template('index.html')
    fileToDownload = session[name]
    fullPath = app.youtubeManager.MUSIC_PATH + "/" + fileToDownload
    return send_file(fullPath, as_attachment=True)
