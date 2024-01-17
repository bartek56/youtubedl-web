import logging
from abc import abstractmethod
from typing import List
from flask_socketio import emit

logger = logging.getLogger(__name__)

class Message:
    _errorKey = "error"
    _dataKey =  "data"

    def __init__(self, message:str):
        self._messageContent={}
        self.data=None
        self.message = message

    @abstractmethod
    def _setMessage(self, data):
        pass

    def sendMessage(self, data):
        self._setMessage(data)
        self._addMessageToContent()
        self._emitMessage()

    def sendError(self, error:str):
        self._messageContent[self._errorKey] = error
        self._emitMessage()

    def _addMessageToContent(self):
        self._messageContent[self._dataKey] = self.data

    def _emitMessage(self):
        emit(self.message, self._messageContent)


# ------------------ MediaInfo_response -----------------------------------
class MediaInfo:
    def __init__(self, title:str=None, artist:str=None):
        self.title = title
        self.artist = artist

# data: {"artist", "title"}
class MediaInfo_response(Message):
    message = "getMediaInfo_response"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, mediaInfo:MediaInfo):
        self.data = {}
        if mediaInfo.artist is not None:
            self.data["artist"] = mediaInfo.artist
        else:
            self.data["artist"] = " "
        self.data["title"] = mediaInfo.title


# ------------------- downloadMedia_finish -------------------------------
# data: hash
class DownloadMedia_finish(Message):
    message="downloadMedia_finish"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, hash:str):
        self.data = hash


# -------------------- getPlaylistInfo_response ----------------------------
class MediaFromPlaylist:
    def __init__(self, index:str, url:str, title:str):
        self.playlistIndex = index
        self.url = url
        self.title = title

class PlaylistInfo:
    def __init__(self, name:str, listOfMedia:List[MediaFromPlaylist]):
        self.playlistName = name
        self.listOfMedia = listOfMedia

# data: playlistName, [{"playlist_index" "url" "title"}, ..]
class PlaylistInfo_response(Message):
    message="getPlaylistInfo_response"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, playlistInfo:PlaylistInfo):
        self.data = []
        listOfMedia = playlistInfo.listOfMedia
        playlist = []
        for media in listOfMedia:
            mediaInfo = {}
            mediaInfo["playlist_index"] = media.playlistIndex
            mediaInfo["url"] = media.url
            mediaInfo["title"] = media.title
            playlist.append(mediaInfo)
        self.data.append(playlistInfo.playlistName)
        self.data.append(playlist)


# ------------------ getPlaylistMediaInfo_response -------------------------
class PlaylistMediaInfo:
    def __init__(self, playlistIndex:str, filename:str, hash:str):
        self.playlistIndex = playlistIndex
        self.filename = filename
        self.hash = hash

# data: {playlist_index, filename, hash}
class PlaylistMediaInfo_response(Message):
    message = "getPlaylistMediaInfo_response"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, playlistInfo:PlaylistMediaInfo):
        self.data = {}
        self.data["playlist_index"] = playlistInfo.playlistIndex
        self.data["filename"]       = playlistInfo.filename
        self.data["hash"]           = playlistInfo.hash


# ------------------- downloadMediaFromPlaylist_start ---------------------------
# data: {playlist_index, filename}
class DownloadMediaFromPlaylist_start(Message):
    message = "downloadMediaFromPlaylist_start"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, playlistInfo:PlaylistMediaInfo):
        self.data = {}
        self.data["playlist_index"] = playlistInfo.playlistIndex
        self.data["filename"]       = playlistInfo.filename


# ------------------- downloadMediaFromPlaylist_finish ---------------------------
# data: {playlist_index, filename}
class DownloadMediaFromPlaylist_finish(Message):
    message = "downloadMediaFromPlaylist_finish"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, playlistInfo:PlaylistMediaInfo):
        self.data = {}
        self.data["playlist_index"] = playlistInfo.playlistIndex
        self.data["filename"]       = playlistInfo.filename


# ------------------- downloadPlaylist_finish -----------------------------
# data: numberOfDownloadedPlaylists
class DownloadPlaylists_finish(Message):
    message = "downloadPlaylist_finish"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, numberOfDownloadedPlaylists:int):
        self.data = numberOfDownloadedPlaylists
