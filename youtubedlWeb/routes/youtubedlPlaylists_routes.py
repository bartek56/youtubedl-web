from flask import Blueprint, render_template, request, jsonify, flash, redirect, session
from flask import current_app as app
from youtubedlWeb.Common.SocketRequests import ArchiveSongRequest, DownloadPlaylistsRequest
from youtubedlWeb.Common.SocketMessages import DownloadPlaylists_finish, DownloadMediaFromPlaylist_finish, PlaylistInfo, PlaylistMediaInfo, PlaylistInfo_response, MediaFromPlaylist, DownloadMediaFromPlaylist_start, DownloadMediaFromPlaylistError
import youtubedlWeb.Common.WebUtils as WebUtils
import os

youtubePlaylists_bp = Blueprint('youtubePlaylists', __name__)

@youtubePlaylists_bp.route('/playlists.html')
def playlists():
        remoteAddress = request.remote_addr

        playlistsName = app.youtubeConfig.getPlaylistsName()
        data = []

        for playlistName in playlistsName:
            data.append({'name':playlistName})
        path = app.youtubeConfig.getPath()

        return render_template('playlists.html', playlists_data=data, path=path)

@youtubePlaylists_bp.route('/playlists',methods = ['POST', 'GET'])
def playlists_request():
    if request.method == 'POST':
        if 'add' in request.form:
            playlist_name = request.form['playlist_name']
            link = request.form['link']
            app.logger.debug("add playlist %s %s", playlist_name, link)
            allPlaylists = app.youtubeConfig.getPlaylistsName()
            if playlist_name in allPlaylists:
                info = "Playlist " + playlist_name + " was updated"
            else:
                info = "Playlist " + playlist_name + " has been added"
            if app.youtubeConfig.addPlaylist({"name":playlist_name, "link":link}) is True:
                 flash(info, 'success')
            else:
                warning = "Playlist " + playlist_name + " was not added"
                flash(warning, 'warning')

        if 'remove' in request.form:
            playlistToRemove = str(request.form['playlists'])
            result = app.youtubeConfig.removePlaylist(playlistToRemove)
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
                app.youtubeConfig.setPath(str(newPath))
                flash("Successfull updated download path", "success")
            else:
                flash("wrong path", 'warning')

        return redirect('playlists.html')

    else:
        app.logger.debug("error")
        return redirect('playlists.html')

@youtubePlaylists_bp.route('/getLinkOfPlaylist', methods=['GET'])
def getLinkOfPlaylist():
    playlistName = request.args.get('playlistName')
    url = app.youtubeConfig.getUrlOfPlaylist(playlistName)
    return jsonify(url)

def register_socketio_youtubePlaylist(socketio):
    @socketio.on(DownloadPlaylistsRequest.message)
    def handle_message(msg):
        playlistsDir = app.youtubeConfig.getPath()
        if playlistsDir == None:
            DownloadPlaylists_finish().sendError("Playlist dir doesn't exist")
            return

        if len(msg) == 0:
            app.logger.debug("download all playlists")
            playlists = app.youtubeConfig.getPlaylists()
            numberOfDownloadedSongs = 0
            if len(playlists) == 0:
                DownloadPlaylists_finish().sendError("Your music collection is empty")
                return
            for playlist in playlists:
                resultOfPlaylist = app.youtubeManager.getPlaylistInfo(playlist.link)
                if resultOfPlaylist.IsFailed():
                    DownloadPlaylists_finish().sendError("Failed to get info playlist")
                    app.logger.error("Error to download media: %s", resultOfPlaylist.error())
                    return
                ytData = resultOfPlaylist.data()
                #TODO validate difference between names of playlist the same as MediaServerDownloader
                #playlistName = ytData.playlistName
                playlistName = playlist.name
                PlaylistInfo_response().sendMessage(PlaylistInfo(playlistName, ytData.listOfMedia))
                numberOfDownloadedSongs += downloadSongsFromPlaylist(playlistsDir, playlistName, ytData.listOfMedia)
        else:
            downloadPlaylistRequest = DownloadPlaylistsRequest(msg).downloadPlaylists
            playlistName = downloadPlaylistRequest.playlistName
            app.logger.debug("download playlist " + playlistName)

            resultOfPlaylist = app.youtubeManager.getPlaylistInfo(downloadPlaylistRequest.link)
            if resultOfPlaylist.IsFailed():
                DownloadPlaylists_finish().sendError("Failed to get info playlist")
                app.logger.error("Error to download media: %s", resultOfPlaylist.error())
                return
            ytData:PlaylistInfo = resultOfPlaylist.data()
            PlaylistInfo_response().sendMessage(PlaylistInfo(playlistName, ytData.listOfMedia))
            numberOfDownloadedSongs = downloadSongsFromPlaylist(playlistsDir, playlistName, ytData.listOfMedia)
        DownloadPlaylists_finish().sendMessage(numberOfDownloadedSongs)

    @socketio.on(ArchiveSongRequest.message)
    def archiveSong(msg):
        archiveSong = ArchiveSongRequest(msg).archiveSong
        hash = app.youtubeManager.getMediaHashFromLink(archiveSong.ytHash)
        if hash is None:
            app.logger.error("failed to get hash")
            return
        playlistsDir = app.youtubeConfig.getPath()
        archiveFilename = app.youtubeManager.mp3DownloadedListFileName
        playlistName = archiveSong.platlistName
        archiveFilenameWithPath = "%s/%s/%s"%(playlistsDir,playlistName,archiveFilename)
        newSongForArchive = "youtube %s\n"%(hash)
        app.logger.debug("archive song: " + playlistName + "  "+ hash + " in file " + archiveFilenameWithPath)
        with open(archiveFilenameWithPath, 'a') as file:
            file.write(newSongForArchive)

def downloadSongsFromPlaylist(playlistsDir, playlistName, listOfMedia):
    path=os.path.join(playlistsDir, playlistName)
    app.youtubeManager._createDirIfNotExist(path)
    songCounter = 0
    for songData in listOfMedia:
        app.logger.debug(str(songData))
        if app.youtubeManager.isMusicClipArchived(path, songData.url):
            app.logger.info("clip \"%s\" from link %s is archived", songData.title, songData.url)
            continue
        app.logger.debug("start download clip from")
        DownloadMediaFromPlaylist_start().sendMessage(PlaylistMediaInfo(songData.playlistIndex, songData.title, ""))

        #TODO rename template request if song was duplicated
        result = app.youtubeManager._download_mp3(songData.url, path)
        if result.IsFailed():
            app.logger.error("Failed to download song from url")
            DownloadMediaFromPlaylist_finish().sendError(DownloadMediaFromPlaylistError(songData.playlistIndex, songData.url, songData.title))
            continue
        songCounter+=1
        songMetadata = result.data()
        filenameFullPath = app.youtubeManager.addMetadataToPlaylist(playlistsDir, songData.playlistIndex, playlistName,
                                                                 songMetadata.artist, songMetadata.album, songMetadata.title, songMetadata.hash)
        filename = filenameFullPath.split("/")[-1]
        randomHash = WebUtils.getRandomString()
        session[randomHash] = filename
        DownloadMediaFromPlaylist_finish().sendMessage(PlaylistMediaInfo(songData.playlistIndex, filename.replace(".mp3", ""), ""))
    return songCounter
