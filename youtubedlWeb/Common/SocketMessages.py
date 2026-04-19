import logging
from typing import List
from flask_socketio import emit

logger = logging.getLogger(__name__)

class Message:
    _errorKey = "error"
    _dataKey =  "data"

    def __init__(self, message:str):
        """
        Initialize the Message object.

        Args:
            message (str): The message to be sent.

        Sets the message content to an empty dictionary, the data to None, the error to None, and the message to the given message.
        """
        self._messageContent={}
        self.data=None
        self.error=None
        self.message = message

    def _emitMessage(self, to_=None):
        """
        Emits a message with the given data to the given sid.

        Args:
            to_ (str): The sid to emit the message to. If not given, emits to all connected clients.

        Emits a message with the given data to the given sid.
        """
        logger.debug("emit message %s:%s to sid: %s", self.message, self._messageContent, to_)
        emit(self.message, self._messageContent, namespace='/', to=to_)

    def _setMessage(self, data):
        """
        Sets the data of the message to the given data.

        Args:
            data: The data to be set.
        """
        self.data = data

    def _addMessageToContent(self):
        """
        Adds the data to the message content.

        Adds the data to the message content and sets the data key to the given data.
        """
        self._messageContent[self._dataKey] = self.data

    def sendMessage(self, data, to=None):
        """
        Sends a message with the given data to the given sid.

        Args:
            data: The data to be sent.
            to_ (str): The sid to emit the message to. If not given, emits to all connected clients.

        Sets the data of the message to the given data, adds it to the message content, and emits the message to the given sid.
        """
        self._setMessage(data)
        self._addMessageToContent()
        self._emitMessage(to)

    def _setError(self, error):
        """
        Sets the error of the message to the given error.

        Args:
            error: The error to be set.
        """
        self.error = error

    def _addErrorToContent(self):
        """
        Adds the error to the message content.

        Sets the error key to the error content and adds it to the message content.
        """
        self._messageContent[self._errorKey] = self.error

    def sendError(self, error, to=None):
        """
        Sends an error message with the given error to the given sid.

        Args:
            error: The error to be sent.
            to_ (str): The sid to emit the message to. If not given, emits to all connected clients.

        Sets the error of the message to the given error, adds it to the message content, and emits the message to the given sid.

        """
        self._setError(error)
        self._addErrorToContent()
        self._emitMessage(to)

# ------------------ MediaInfo_response -----------------------------------
class MediaInfo:
    def __init__(self, title:str, artist:str, hash:str):
        """
        Initializes a MediaInfo object.

        Args:
            title (str): The title of the media.
            artist (str): The artist of the media.
            hash (str): The YouTube hash of the media.

        Sets the title, artist, and YouTube hash of the media.
        """
        self.title = title
        self.artist = artist
        self.hash = hash

# data: {"artist", "title"}
class MediaInfo_response(Message):
    message = "getMediaInfo_response"

    def __init__(self):
        """
        Initializes a MediaInfo_response object.

        Calls the parent class's __init__ method with the "getMediaInfo_response" message.
        """
        super().__init__(self.message)

    def _setMessage(self, mediaInfo:MediaInfo):
        """
        Sets the data of the message to the given media information.

        Parameters:
            mediaInfo (MediaInfo): The media information to be set.

        Sets the data of the message to a dictionary containing the artist, title, and YouTube hash of the media.
        """
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
        """
        Initializes the Resume object.

        Args:
            None

        Calls the __init__ method of the parent class with the message.
        """
        super().__init__(self.message)

# ------------------- downloadMedia_finish -------------------------------
# data: hash
class DownloadMedia_finish(Message):
    message="downloadMedia_finish"

    def __init__(self):
        """
        Initializes the DownloadMedia_finish object.

        Calls the __init__ method of the parent class with the message.
        """
        super().__init__(self.message)


# -------------------- getPlaylistInfo_response ----------------------------
class MediaFromPlaylist:
    def __init__(self, index:str, url:str, title:str):
        """
        Initializes a MediaFromPlaylist object.

        Parameters:
            index (str): The playlist index of the media.
            url (str): The URL of the media.
            title (str): The title of the media.
        """
        self.playlistIndex = index
        self.url = url
        self.title = title

class PlaylistInfo:
    def __init__(self, name:str, listOfMedia:List[MediaFromPlaylist]):
        """
        Initializes a PlaylistInfo object.

        Parameters:
            name (str): The name of the playlist.
            listOfMedia (List[MediaFromPlaylist]): A list of MediaFromPlaylist objects.
        """
        self.playlistName = name
        self.listOfMedia = listOfMedia

# data: playlistName, [{"playlist_index" "url" "title"}, ..]
class PlaylistInfo_response(Message):
    message="getPlaylistInfo_response"

    def __init__(self):
        """
        Initializes a PlaylistInfo_response object.

        Calls the __init__ method of the parent class with the message.
        """
        super().__init__(self.message)

    def _setMessage(self, playlistInfo:PlaylistInfo):
        """
        Sets the data of the message to the given playlist info.

        Parameters:
            playlistInfo (PlaylistInfo): The playlist info to be set.

        Sets the data of the message to a list containing the playlist name and a list of media info.
        Each media info is a dictionary containing the playlist index, url, and title.
        """
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
        """
        Initializes a PlaylistMediaInfo object.

        Parameters:
            playlistIndex (str): The index of the media in the playlist.
            filename (str): The filename of the media.
            hash (str): The hash of the media.
        """
        self.playlistIndex = playlistIndex
        self.filename = filename
        self.hash = hash

# data: {playlist_index, filename, hash}
class PlaylistMediaInfo_response(Message):
    message = "getPlaylistMediaInfo_response"

    def __init__(self):
        """
        Initializes a PlaylistMediaInfo_response object.

        Calls the parent class's __init__ method with the "getPlaylistMediaInfo_response" message.
        """
        super().__init__(self.message)

    def _setMessage(self, playlistInfo:PlaylistMediaInfo):
        """
        Sets the data of the message to the given playlist media info.

        Parameters:
            playlistInfo (PlaylistMediaInfo): The playlist media info to be set.

        Sets the data of the message to a dictionary containing the playlist index, filename, and hash.
        """
        self.data = {}
        self.data["playlist_index"] = playlistInfo.playlistIndex
        self.data["filename"]       = playlistInfo.filename
        self.data["hash"]           = playlistInfo.hash


# ------------------- downloadMediaFromPlaylist_start ---------------------------
# data: {playlist_index, filename}
class DownloadMediaFromPlaylist_start(Message):
    message = "downloadMediaFromPlaylist_start"

    def __init__(self):
        """
        Initializes a DownloadMediaFromPlaylist_start object.

        Calls the parent class's __init__ method with the "downloadMediaFromPlaylist_start" message.
        """
        super().__init__(self.message)

    def _setMessage(self, playlistInfo:PlaylistMediaInfo):
        """
        Sets the data of the message to the given playlist media info.

        Parameters:
            playlistInfo (PlaylistMediaInfo): The playlist media info to be set.

        Sets the data of the message to a dictionary containing the playlist index and filename.
        """
        self.data = {}
        self.data["playlist_index"] = playlistInfo.playlistIndex
        self.data["filename"]       = playlistInfo.filename


# ------------------- downloadMediaFromPlaylist_finish ---------------------------
class DownloadMediaFromPlaylistError:
    def __init__(self, index:str, ytHash:str, title:str):
        """
        Initializes a DownloadMediaFromPlaylistError object.

        Parameters:
            index (str): The index of the media in the playlist.
            ytHash (str): The YouTube hash of the media.
            title (str): The title of the media.

        Sets the index, YouTube hash, and title of the media.
        """
        self.index = index
        self.ytHash = ytHash
        self.title = title


# data: {playlist_index, filename}
class DownloadMediaFromPlaylist_finish(Message):
    message = "downloadMediaFromPlaylist_finish"

    def __init__(self):
        """
        Initializes a DownloadMediaFromPlaylist_finish object.

        Calls the parent class's __init__ method with the "downloadMediaFromPlaylist_finish" message.
        """
        super().__init__(self.message)

    def _setMessage(self, playlistInfo:PlaylistMediaInfo):
        """
        Sets the data of the message to the given playlist media info.

        Parameters:
            playlistInfo (PlaylistMediaInfo): The playlist media info to be set.

        Sets the data of the message to a dictionary containing the playlist index and filename.
        """
        self.data = {}
        self.data["playlist_index"] = playlistInfo.playlistIndex
        self.data["filename"]       = playlistInfo.filename

    def _setError(self, data:DownloadMediaFromPlaylistError):
        """
        Sets the error of the message to the given download media from playlist error.

        Parameters:
            data (DownloadMediaFromPlaylistError): The download media from playlist error to be set.

        Sets the error of the message to a dictionary containing the index, YouTube hash, and title of the media.
        """
        self.error = {"index":data.index, "ytHash": data.ytHash, "title":data.title}


# ------------------- downloadPlaylist_finish -----------------------------
# data: numberOfDownloadedPlaylists
class DownloadPlaylists_finish(Message):
    message = "downloadPlaylist_finish"

    def __init__(self):
        """
        Initializes a DownloadPlaylists_finish object.

        Calls the parent class's __init__ method with the "downloadPlaylist_finish" message.
        """
        super().__init__(self.message)
