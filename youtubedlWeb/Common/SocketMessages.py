import logging
from typing import List
from flask_socketio import emit

logger = logging.getLogger(__name__)

class Message:
    _errorKey = "error"
    _dataKey =  "data"

    def __init__(self, message:str):
        self._messageContent={}
        self.data=None
        self.error=None
        self.message = message

    def _emitMessage(self, to_=None):
        logger.debug("emit message to sid: %s", to_)
        emit(self.message, self._messageContent, namespace='/', to=to_)

    def _setMessage(self, data):
        self.data = data

    def _addMessageToContent(self):
        self._messageContent[self._dataKey] = self.data

    def sendMessage(self, data, to=None):
        self._setMessage(data)
        self._addMessageToContent()
        self._emitMessage(to)

    def _setError(self, error):
        self.error = error

    def _addErrorToContent(self):
        self._messageContent[self._errorKey] = self.error

    def sendError(self, error):
        self._setError(error)
        self._addErrorToContent()
        self._emitMessage()


# ------------------ MediaInfo_response -----------------------------------
class MediaInfo:
    def __init__(self, title:str, artist:str, hash:str):
        self.title = title
        self.artist = artist
        self.hash = hash

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
        self.data["hash"] = mediaInfo.hash


# ------------------- Resume -------------------------------
# data: empty
class Resume(Message):
    message="resume"

    def __init__(self):
        super().__init__(self.message)

# ------------------- downloadMedia_finish -------------------------------
# data: hash
class DownloadMedia_finish(Message):
    message="downloadMedia_finish"

    def __init__(self):
        super().__init__(self.message)


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
class DownloadMediaFromPlaylistError:
    def __init__(self, index:str, ytHash:str, title:str):
        self.index = index
        self.ytHash = ytHash
        self.title = title


# data: {playlist_index, filename}
class DownloadMediaFromPlaylist_finish(Message):
    message = "downloadMediaFromPlaylist_finish"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, playlistInfo:PlaylistMediaInfo):
        self.data = {}
        self.data["playlist_index"] = playlistInfo.playlistIndex
        self.data["filename"]       = playlistInfo.filename

    def _setError(self, data:DownloadMediaFromPlaylistError):
        self.error = {"index":data.index, "ytHash": data.ytHash, "title":data.title}


# ------------------- downloadPlaylist_finish -----------------------------
# data: numberOfDownloadedPlaylists
class DownloadPlaylists_finish(Message):
    message = "downloadPlaylist_finish"

    def __init__(self):
        super().__init__(self.message)
