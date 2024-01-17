from youtubedl import app, logger, youtubeConfig, youtubeManager, socketio
from flask import render_template, request, flash, redirect, session, send_file

import os
import zipfile
from typing import List

from Common.SocketMessages import PlaylistInfo_response, PlaylistMediaInfo_response
from Common.SocketMessages import MediaInfo_response, DownloadMedia_finish
from Common .SocketMessages import DownloadMediaFromPlaylist_start, DownloadMediaFromPlaylist_finish, DownloadPlaylists_finish

import Common.YouTubeManager as YTManager
import Common.SocketMessages as SocketMessages
import WebAPI.webUtils as utils


def downloadMediaOfType(url, type):
    if type == "mp3":
        return youtubeManager.download_mp3(url)
    elif type == "360p":
        return youtubeManager.download_360p(url)
    elif type == "720p":
        return youtubeManager.download_720p(url)
    elif type =="4k":
        return youtubeManager.download_4k(url)

def compressToZip(files, playlistName):
    # TODO zip fileName
    zipFileName = "%s.zip"%playlistName
    zipFileWithPath = os.path.join("/tmp/quick_download", zipFileName)
    with zipfile.ZipFile(zipFileWithPath, 'w') as zipf:
        for file_path in files:
            arcname = file_path.split("/")[-1]
            zipf.write(file_path, arcname)

@app.route('/playlists.html')
def playlists():
    remoteAddress = request.remote_addr

    if ("192.168" in remoteAddress) or ("127.0.0.1" in remoteAddress):
        playlistsName = youtubeConfig.getPlaylistsName()
        data = []

        for playlistName in playlistsName:
            data.append({'name':playlistName})

        return render_template('playlists.html', playlists_data=data)
    else:
        return utils.alert_info("You do not have access to Youtube playlists")

@app.route('/download_file',methods = ['POST', 'GET'])
def downloadFile():
   path=''
   if request.method == 'POST':
      path = request.form['path']
      return send_file(path, as_attachment=True)
   else:
      app.logger.debug("error")
      return redirect('/')

@app.route('/playlists',methods = ['POST', 'GET'])
def playlist():
   if request.method == 'POST':
       if 'add' in request.form:
           playlist_name = request.form['playlist_name']
           link = request.form['link']
           app.logger.debug("add playlist %s %s", playlist_name, link)
           youtubeConfig.addPlaylist({"name":playlist_name, "link":link})

       if 'remove' in request.form:
           playlistToRemove = str(request.form['playlists'])
           result = youtubeConfig.removePlaylist(playlistToRemove)
           if result:
                app.logger.debug("removed playlist %s", playlistToRemove)
                info = "Sucesssful removed playlist %s"%(playlistToRemove)
                flash(info, 'success')
           else:
               info = "Failed to remove Youtube playlist: %s"%(playlistToRemove)
               return utils.alert_info(info)

       return redirect('playlists.html')

   else:
       app.logger.debug("error")
       return redirect('playlists.html')

@socketio.on('downloadPlaylists')
def handle_message(msg):
    playlists = youtubeConfig.getPlaylists()
    playlistsDir = youtubeConfig.getPath()
    numberOfDownloadedSongs = 0
    if len(playlists) == 0:
        DownloadPlaylists_finish().sendError("Your music collection is empty")
        return

    for playlist in playlists:
        resultOfPlaylist = youtubeManager.getPlaylistInfo(playlist.link)
        if resultOfPlaylist.IsFailed():
            DownloadPlaylists_finish().sendError("Failed to get info playlist")
            logger.error("Error to download media: %s", resultOfPlaylist.error())
            return
        ytData:YTManager.PlaylistInfo = resultOfPlaylist.data()
        playlistName = ytData.playlistName
        PlaylistInfo_response().sendMessage(SocketMessages.PlaylistInfo(playlistName, ytData.listOfMedia))
        numberOfDownloadedSongs += downloadSongsFromPlaylist(playlistsDir, playlistName, ytData.listOfMedia)
    DownloadPlaylists_finish().sendMessage(numberOfDownloadedSongs)

def downloadSongsFromPlaylist(playlistsDir, playlistName, listOfMedia:List[YTManager.MediaFromPlaylist]):
    path=os.path.join(playlistsDir, playlistName)
    youtubeManager.createDirIfNotExist(path)
    songCounter = 0
    for songData in listOfMedia:
        logger.debug(str(songData))
        if youtubeManager._isMusicClipArchived(path, songData.url):
            logger.info("clip \"%s\" from link %s is archived", songData.title, songData.url)
            continue
        logger.debug("start download clip from")
        DownloadMediaFromPlaylist_start().sendMessage(SocketMessages.PlaylistMediaInfo(songData.playlistIndex, songData.title, ""))

        result = youtubeManager._download_mp3(songData.url, path)
        if result.IsFailed():
            logger.error("Failed to download song from url")
            DownloadMediaFromPlaylist_finish().sendError(str(songData.playlistIndex))
            continue
        songCounter+=1
        songMetadata:YTManager.AudioData
        songMetadata = result.data()
        filenameFullPath = youtubeManager._addMetadataToPlaylist(playlistsDir, songData.playlistIndex, playlistName, songMetadata.artist,  songMetadata.album, songMetadata.title)
        filename = filenameFullPath.split("/")[-1]
        randomHash = utils.getRandomString()
        session[randomHash] = filename
        DownloadMediaFromPlaylist_finish().sendMessage(SocketMessages.PlaylistMediaInfo(songData.playlistIndex, songData.title, ""))
    return songCounter

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
        randomHash = utils.getRandomString()
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
        compressToZip(downloadedFiles, playlistName)
        randomHash = utils.getRandomString()
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
        randomHash = utils.getRandomString()
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

