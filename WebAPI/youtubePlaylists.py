from youtubedl import app, logger, youtubeConfig, youtubeManager, socketio
from flask import render_template, request, flash, redirect, session

import os
from typing import List

from Common.SocketMessages import PlaylistInfo_response
from Common.SocketMessages import DownloadMediaFromPlaylist_start, DownloadMediaFromPlaylist_finish, DownloadMediaFromPlaylistError, DownloadPlaylists_finish
from Common.SocketRequests import DownloadPlaylistsRequest, ArchiveSongRequest

import Common.YouTubeManager as YTManager
import Common.SocketMessages as SocketMessages
import WebAPI.webUtils as webUtils

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
        return webUtils.alert_info("You do not have access to Youtube playlists")

@app.route('/playlists',methods = ['POST', 'GET'])
def playlists_request():
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
               return webUtils.alert_info(info)

       return redirect('playlists.html')

   else:
       app.logger.debug("error")
       return redirect('playlists.html')

@socketio.on(DownloadPlaylistsRequest.message)
def handle_message(msg):
    playlists = youtubeConfig.getPlaylists()
    playlistsDir = youtubeConfig.getPath()
    numberOfDownloadedSongs = 0
    if len(playlists) == 0:
        DownloadPlaylists_finish().sendError("Your music collection is empty")
        return
    if playlistsDir == None:
        DownloadPlaylists_finish().sendError("Playlist dir doesn't exist")
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
            DownloadMediaFromPlaylist_finish().sendError(DownloadMediaFromPlaylistError(str(songData.playlistIndex), songData.url, songData.title))
            continue
        songCounter+=1
        songMetadata:YTManager.AudioData
        songMetadata = result.data()
        filenameFullPath = youtubeManager._addMetadataToPlaylist(playlistsDir, songData.playlistIndex, playlistName, songMetadata.artist,  songMetadata.album, songMetadata.title)
        filename = filenameFullPath.split("/")[-1]
        randomHash = webUtils.getRandomString()
        session[randomHash] = filename
        DownloadMediaFromPlaylist_finish().sendMessage(SocketMessages.PlaylistMediaInfo(songData.playlistIndex, songData.title, ""))
    return songCounter

@socketio.on(ArchiveSongRequest.message)
def archiveSong(msg):
    archiveSong = ArchiveSongRequest(msg).archiveSong
    hash = youtubeManager.getMediaHashFromLink(archiveSong.ytHash)
    if hash is None:
        logger.error("failed to get hash")
        return
    playlistsDir = youtubeConfig.getPath()
    archiveFilename = youtubeManager.mp3DownloadedListFileName
    playlistName = archiveSong.platlistName
    archiveFilenameWithPath = "%s/%s/%s"%(playlistsDir,playlistName,archiveFilename)
    newSongForArchive = "youtube %s\n"%(hash)
    logger.debug("archive song: " + playlistName + "  "+ hash + " in file " + archiveFilenameWithPath)
    with open(archiveFilenameWithPath, 'a') as file:
        file.write(newSongForArchive)
