from youtubedl import app, logger, youtubeConfig, youtubeManager, socketio
from flask import render_template, request, flash, redirect, session, jsonify

import os
from typing import List

from Common.SocketMessages import PlaylistInfo_response, PlaylistMediaInfo
from Common.SocketMessages import DownloadMediaFromPlaylist_start, DownloadMediaFromPlaylist_finish, DownloadMediaFromPlaylistError, DownloadPlaylists_finish
from Common.SocketRequests import DownloadPlaylistsRequest, ArchiveSongRequest

from Common.YoutubeManager import AudioData, PlaylistInfo, MediaFromPlaylist
import Common.SocketMessages as SocketMessages
import WebAPI.WebUtils as WebUtils

@app.route('/playlists.html')
def playlists():
    remoteAddress = request.remote_addr

    if ("192.168" in remoteAddress) or ("127.0.0.1" in remoteAddress):
        playlistsName = youtubeConfig.getPlaylistsName()
        data = []

        for playlistName in playlistsName:
            data.append({'name':playlistName})
        path = youtubeConfig.getPath()

        return render_template('playlists.html', playlists_data=data, path=path)
    else:
        return WebUtils.alert_info("You do not have access to Youtube playlists")

@app.route('/playlists',methods = ['POST', 'GET'])
def playlists_request():
    if request.method == 'POST':
        if 'add' in request.form:
            playlist_name = request.form['playlist_name']
            link = request.form['link']
            app.logger.debug("add playlist %s %s", playlist_name, link)
            allPlaylists = youtubeConfig.getPlaylistsName()
            print(allPlaylists)
            print(playlist_name)
            if playlist_name in allPlaylists:
                info = "Playlist " + playlist_name + " was updated"
            else:
                info = "Playlist " + playlist_name + " has been added"
            if youtubeConfig.addPlaylist({"name":playlist_name, "link":link}) is True:
                 flash(info, 'success')
            else:
                warning = "Playlist " + playlist_name + " was not added"
                flash(warning, 'warning')

        if 'remove' in request.form:
            playlistToRemove = str(request.form['playlists'])
            result = youtubeConfig.removePlaylist(playlistToRemove)
            if result:
                 app.logger.debug("removed playlist %s", playlistToRemove)
                 info = "Sucesssful removed playlist %s"%(playlistToRemove)
                 flash(info, 'success')
            else:
                info = "Failed to remove Youtube playlist: %s"%(playlistToRemove)
                return WebUtils.alert_info(info)

        if 'editPath' in request.form:
            newPath = request.form['path']
            if os.path.isdir(newPath):
                youtubeConfig.setPath(str(newPath))
                flash("Successfull updated download path", "success")
            else:
                flash("wrong path", 'warning')

        return redirect('playlists.html')

    else:
        app.logger.debug("error")
        return redirect('playlists.html')

@socketio.on(DownloadPlaylistsRequest.message)
def handle_message(msg):
    playlistsDir = youtubeConfig.getPath()
    if playlistsDir == None:
        DownloadPlaylists_finish().sendError("Playlist dir doesn't exist")
        return

    if len(msg) == 0:
        logger.debug("download all playlists")
        playlists = youtubeConfig.getPlaylists()
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
            ytData:PlaylistInfo = resultOfPlaylist.data()
            #TODO validate difference between names of playlist the same as MediaServerDownloader
            #playlistName = ytData.playlistName
            playlistName = playlist.name
            PlaylistInfo_response().sendMessage(SocketMessages.PlaylistInfo(playlistName, ytData.listOfMedia))
            numberOfDownloadedSongs += downloadSongsFromPlaylist(playlistsDir, playlistName, ytData.listOfMedia)
    else:
        downloadPlaylistRequest = DownloadPlaylistsRequest(msg).downloadPlaylists
        playlistName = downloadPlaylistRequest.playlistName

        logger.debug("download playlist " + playlistName)

        resultOfPlaylist = youtubeManager.getPlaylistInfo(downloadPlaylistRequest.link)
        if resultOfPlaylist.IsFailed():
            DownloadPlaylists_finish().sendError("Failed to get info playlist")
            logger.error("Error to download media: %s", resultOfPlaylist.error())
            return
        ytData:PlaylistInfo = resultOfPlaylist.data()
        PlaylistInfo_response().sendMessage(SocketMessages.PlaylistInfo(playlistName, ytData.listOfMedia))
        numberOfDownloadedSongs = downloadSongsFromPlaylist(playlistsDir, playlistName, ytData.listOfMedia)
    DownloadPlaylists_finish().sendMessage(numberOfDownloadedSongs)

def downloadSongsFromPlaylist(playlistsDir, playlistName, listOfMedia:List[MediaFromPlaylist]):
    path=os.path.join(playlistsDir, playlistName)
    youtubeManager.createDirIfNotExist(path)
    songCounter = 0
    for songData in listOfMedia:
        logger.debug(str(songData))
        if youtubeManager._isMusicClipArchived(path, songData.url):
            logger.info("clip \"%s\" from link %s is archived", songData.title, songData.url)
            continue
        logger.debug("start download clip from")
        DownloadMediaFromPlaylist_start().sendMessage(PlaylistMediaInfo(songData.playlistIndex, songData.title, ""))

        result:AudioData = youtubeManager._download_mp3(songData.url, path)
        if result.IsFailed():
            logger.error("Failed to download song from url")
            DownloadMediaFromPlaylist_finish().sendError(DownloadMediaFromPlaylistError(songData.playlistIndex, songData.url, songData.title))
            continue
        songCounter+=1
        songMetadata:AudioData
        songMetadata = result.data()
        filenameFullPath = youtubeManager._addMetadataToPlaylist(playlistsDir, songData.playlistIndex, playlistName,
                                                                 songMetadata.artist, songMetadata.album, songMetadata.title, songMetadata.hash)
        filename = filenameFullPath.split("/")[-1]
        randomHash = WebUtils.getRandomString()
        session[randomHash] = filename
        DownloadMediaFromPlaylist_finish().sendMessage(PlaylistMediaInfo(songData.playlistIndex, filename.replace(".mp3", ""), ""))
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

@app.route('/getLinkOfPlaylist', methods=['GET'])
def getLinkOfPlaylist():
    playlistName = request.args.get('playlistName')
    url = youtubeConfig.getUrlOfPlaylist(playlistName)
    return jsonify(url)
