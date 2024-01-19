from youtubedl import app, logger, youtubeConfig, youtubeManager, socketio
from flask import render_template, request, flash, redirect, session, send_file


from Common.SocketMessages import PlaylistInfo_response, PlaylistMediaInfo_response
from Common.SocketMessages import MediaInfo_response, DownloadMedia_finish

import Common.YouTubeManager as YTManager
import Common.SocketMessages as SocketMessages
import WebAPI.webUtils as webUtils


def downloadMediaOfType(url, type):
    if type == "mp3":
        return youtubeManager.download_mp3(url)
    elif type == "360p":
        return youtubeManager.download_360p(url)
    elif type == "720p":
        return youtubeManager.download_720p(url)
    elif type =="4k":
        return youtubeManager.download_4k(url)

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
            logger.error(error)
            continue
        numberOfDownloadedSongs+=1
        data:YTManager.YoutubeClipData = resultOfMedia.data()
        downloadedFiles.append(data.path)
        filename = data.path.split("/")[-1]
        randomHash = webUtils.getRandomString()
        session[randomHash] = filename
        PlaylistMediaInfo_response().sendMessage(SocketMessages.PlaylistMediaInfo(x.playlistIndex, filename, randomHash))
    if numberOfDownloadedSongs == 0:
        DownloadMedia_finish().sendError("Failed to download playlist")
        return
    return downloadedFiles

def downloadPlaylist(url, downloadType):
        resultOfPlaylist = youtubeManager.getPlaylistInfo(url)
        if resultOfPlaylist.IsFailed():
            DownloadMedia_finish().sendError("Failed to get info playlist")
            logger.error("Error to download media: %s", resultOfPlaylist.error())
            return
        ytData:YTManager.PlaylistInfo = resultOfPlaylist.data()
        playlistName = ytData.playlistName
        PlaylistInfo_response().sendMessage(SocketMessages.PlaylistInfo(playlistName, ytData.listOfMedia))
        downloadedFiles = downloadSongsFromList(ytData.listOfMedia, downloadType)
        webUtils.compressToZip(downloadedFiles, playlistName)
        randomHash = webUtils.getRandomString()
        session[randomHash] = "%s.zip"%playlistName
        DownloadMedia_finish().sendMessage(randomHash)

def downloadSingle(url, downloadType):
        result = youtubeManager.getMediaInfo(url)
        if result.IsFailed():
            DownloadMedia_finish().sendError(result.error())
            logger.error("Failed download from url %s - error: %s", url, result.error())
            return
        mediaInfo:YTManager.MediaInfo = result.data()

        MediaInfo_response().sendMessage(SocketMessages.MediaInfo(mediaInfo.title, mediaInfo.artist))
        result2 = downloadMediaOfType(url, downloadType)

        if result2.IsFailed():
            logger.error("Failed with download media %s - %s", url, result2.error())
            DownloadMedia_finish().sendError("problem with download media: " + result2.error())
            return

        data:YTManager.YoutubeClipData = result2.data()
        filename = data.path.split("/")[-1]
        randomHash = webUtils.getRandomString()
        session[randomHash] = filename
        DownloadMedia_finish().sendMessage(randomHash)

@socketio.on('downloadMedia')
def downloadMedia(msg):
    url = msg['url']
    downloadType = str(msg['type'])
    if "playlist?list" in url and "watch?v" not in url:
        downloadPlaylist(url, downloadType)
    else:
        downloadSingle(url, downloadType)

@app.route('/download/<name>')
def download_file(name):
    if name not in session.keys():
        app.logger.error("key for download_file doesn't exist !!!!")
        return render_template('index.html')
    fileToDownload = session[name]
    fullPath = "/tmp/quick_download/" + fileToDownload
    return send_file(fullPath, as_attachment=True)

