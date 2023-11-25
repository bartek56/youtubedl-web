import logging
from abc import abstractmethod
from typing import List
from flask_socketio import emit

logger = logging.getLogger(__name__)

class PlaylistMediaInfo:
    def __init__(self, playlistIndex:str, filename:str, hash:str):
        self.playlistIndex = playlistIndex
        self.filename = filename
        self.hash = hash

class MediaFromPlaylist:
    def __init__(self, index:str, url:str, title:str):
        self.playlistIndex = index
        self.url = url
        self.title = title

class PlaylistInfo:
    def __init__(self, name:str, listOfMedia:List[MediaFromPlaylist]):
        self.playlistName = name
        self.listOfMedia = listOfMedia

class MediaInfo:
    def __init__(self, title:str=None, artist:str=None):
        self.title = title
        self.artist = artist

class Message:
    message = ""
    _messageContent={}
    _errorKey = "error"
    _dataKey =  "data"
    data=None

    def __init__(self, message:str):
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

# data: hash
class DownloadMedia_finish(Message):
    message="downloadMedia_finish"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, hash:str):
        self.data = hash

# data: [{"url" "playlist_index" "title"}, ..]
class PlaylistInfo_response(Message):
    message="getPlaylistInfo_response"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, playlistInfo:PlaylistInfo):
        self.data = []
        listOfMedia = playlistInfo.listOfMedia
        for media in listOfMedia:
            mediaInfo = {}
            mediaInfo["url"] = media.url
            mediaInfo["playlist_index"] = media.playlistIndex
            mediaInfo["title"] = media.title
            self.data.append(mediaInfo)

#data: {playlist_index, filename, hash}
class PlaylistMediaInfo_response(Message):
    message = "getPlaylistMediaInfo_response"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, playlistInfo:PlaylistMediaInfo):
        self.data = {}
        self.data["playlist_index"] = playlistInfo.playlistIndex
        self.data["filename"]       = playlistInfo.filename
        self.data["hash"]           = playlistInfo.hash

#data: {"artist", "title"}
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

#data: index of downloaded playlist
class DownloadPlaylist_response(Message):
    message = "downloadPlaylist_response"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, indexOfDownloadedPlaylist:int):
        self.data = indexOfDownloadedPlaylist

#data: number of downloaded songs
class DownloadPlaylist_finish(Message):
    message = "downloadPlaylist_finish"

    def __init__(self):
        super().__init__(self.message)

    def _setMessage(self, numberOfDownloadedPlaylists:int):
        self.data = numberOfDownloadedPlaylists
