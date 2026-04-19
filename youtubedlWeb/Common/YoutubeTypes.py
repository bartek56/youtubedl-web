from abc import ABC, abstractmethod
from typing import List

class YoutubeManagerLogs:
    DOWNLOAD_FAILED="download failed"
    EMPTY_RESULT="None information from yt"
    NOT_FOUND="couldn't find a downloaded file"
    NOT_ENTRIES="not entries in results"
    NOT_EXTRACT_INFO="not extract_info in results"

class ResultOfDownload:
    def __init__(self, data):
        """
        Initializes a ResultOfDownload object.

        Args:
            data (str or any): Result of the operation, containing data about downloaded song or an error message if the download failed.
        """
        self._data = data

    def IsSuccess(self):
        """
        Returns True if the result of the operation is successful, False otherwise.

        Successful operation means that the data is not a string and is not empty.
        """
        return type(self._data) is not str

    def IsFailed(self):
        """
        Returns True if the result of the operation is failed, False otherwise.

        Failed operation means that the data is a string and is not empty.
        """
        return type(self._data) is str

    def data(self):
        """
        Returns the data of the operation.

        If the result of the operation is successful (i.e. the data is not a string and is not empty), returns the data.
        Otherwise, returns None.
        """
        if type(self._data) is not str:
            return self._data

    def error(self):
        """
        Returns the error message of the operation.

        If the result of the operation is failed (i.e. the data is a string and is not empty), returns the error message.
        Otherwise, returns None.
        """
        if type(self._data) is str:
            return self._data

class MediaFromPlaylist:
    def __init__(self, index:int, url:str, title:str):
        """
        Initializes a MediaFromPlaylist object.

        Parameters:
            index (int): The playlist index of the media.
            url (str): The URL of the media.
            title (str): The title of the media.
        """
        self.playlistIndex = index
        self.url = url
        self.title = title

    def __str__(self):
        return str(self.playlistIndex) + " " + self.url + " " + self.title

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

class PlaylistConfig:
    def __init__(self, name:str, link:str):
        """
        Initializes a PlaylistConfig object.

        Parameters:
            name (str): The name of the playlist config.
            link (str): The URL of the playlist config.
        """
        self.name = name
        self.link = link

class MediaInfo:
    def __init__(self, title=None, artist=None, album=None, url=None):
        """
        Initializes a MediaInfo object.

        Parameters:
            title (str): The title of the media.
            artist (str): The artist of the media.
            album (str): The album of the media.
            url (str): The URL of the media.
        """
        self.title = title
        self.artist = artist
        self.album = album
        self.url = url

    def __str__(self): # pragma: no cover
        """
        Returns a string representation of the MediaInfo object.

        The string representation includes the title, artist, album, and URL of the media, if available.

        :return: A string representation of the MediaInfo object.
        :rtype: str
        """
        str = ""
        if self.title is not None and len(self.title)>0:
            str += "title: %s"%(self.title)
        if self.artist is not None and len(self.artist)>0:
            if len(str) > 0:
                str += " "
            str += "artist: %s"%(self.artist)
        if self.album is not None and len(self.album)>0:
            if len(str) > 0:
                str += " "
            str += "album: %s"%(self.album)
        if self.url is not None and len(self.url)>0:
            if len(str) > 0:
                str += " "
            str += "url: %s"%(self.url)
        return str

class YoutubeClipData:
    def __init__(self, path:str=None, title:str=None):
        """
        Initializes a YoutubeClipData object.

        Parameters:
            path (str): The path to the YouTube clip.
            title (str): The title of the YouTube clip.
        """
        self.path = path
        self.title=title

    def setPath(self, path):
        """
        Sets the path to the YouTube clip.

        Parameters:
            path (str): The path to the YouTube clip.
        """
        self.path = path

    def __str__(self): # pragma: no cover
        """
        Returns a string representation of the YoutubeClipData object.

        The string representation includes the title and path of the YouTube clip, if available.

        :return: A string representation of the YoutubeClipData object.
        :rtype: str
        """
        str = ""
        if self.title is not None and len(self.title)>0:
            str += "title: %s"%(self.title)
        if self.path is not None and len(self.path)>0:
            if len(str) > 0:
                str += " "
            str += "path: %s"%(self.path)
        return str

class AudioData(YoutubeClipData):
    def __init__(self, path:str=None, title:str=None, hash:str=None, artist:str=None, album:str=None, year:str=None):
        """
        Initializes an AudioData object.

        Parameters:
            path (str): The path to the audio clip.
            title (str): The title of the audio clip.
            hash (str): The YouTube hash of the audio clip.
            artist (str): The artist of the audio clip.
            album (str): The album of the audio clip.
            year (str): The year of the album of the audio clip.

        Sets the path, title, YouTube hash, artist, album, and year of the audio clip.
        """
        super().__init__(path, title)
        self.hash = hash
        self.artist = artist
        self.album = album
        self.year = year

    def __str__(self): # pragma: no cover
        """
        Returns a string representation of the AudioData object.

        The string representation includes the title, artist, album, path, YouTube hash, and year of the audio clip, if available.

        :return: A string representation of the AudioData object.
        :rtype: str
        """
        str = ""
        if self.title is not None:
            str += "title: %s"%(self.title)
        if self.artist is not None:
            if len(str) > 0:
                str += " "
            str += "artist: %s"%(self.artist)
        if self.album is not None:
            if len(str) > 0:
                str += " "
            str += "album: %s"%(self.album)
        if self.path is not None:
            if len(str) > 0:
                str += " "
            str += "path: %s"%(self.path)
        if self.hash is not None:
            if len(str) > 0:
                str += " "
            str += "hash: %s"%(self.hash)
        if self.year is not None:
            if len(str) > 0:
                str += " "
            str += "year: %s"%(self.year)

        return str

class VideoData(YoutubeClipData):
    def __init__(self, path:str=None, title:str=None, ext:str=None):
        """
        Initializes a VideoData object.

        Parameters:
            path (str): The path to the video clip.
            title (str): The title of the video clip.
            ext (str): The extension of the video clip.
        """
        super().__init__(path,title)
        self.ext = ext

    def __str__(self): # pragma: no cover
        """
        Returns a string representation of the VideoData object.

        The string representation includes the title, extension, and path of the video clip, if available.

        :return: A string representation of the VideoData object.
        :rtype: str
        """
        str = ""
        if self.title is not None and len(self.title)>0:
            str += "title: %s"%(self.title)
        if self.ext is not None and len(self.ext)>0:
            if len(str) > 0:
                str += " "
            str += "ext: %s"%(self.ext)
        if self.path is not None and len(self.path)>0:
            if len(str) > 0:
                str += " "
            str += "path: %s"%(self.path)
        return str

class VideoSettings(ABC): # pragma: no cover
    @abstractmethod
    def getFormat(self):
        """
        Gets the format of the video to download.

        Returns:
            str: The format of the video to download.
        """
        pass

    @abstractmethod
    def getSubname(self):
        """
        Gets the subname of the video to download.

        The subname is a suffix to add to the title of the video when saving it.

        Returns:
            str: The subname of the video to download.
        """
        pass

