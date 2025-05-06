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
        self._data = data

    def IsSuccess(self):
        return type(self._data) is not str

    def IsFailed(self):
        return type(self._data) is str

    def data(self):
        if type(self._data) is not str:
            return self._data

    def error(self):
        if type(self._data) is str:
            return self._data

class MediaFromPlaylist:
    def __init__(self, index:int, url:str, title:str):
        self.playlistIndex = index
        self.url = url
        self.title = title

    def __str__(self):
        return str(self.playlistIndex) + " " + self.url + " " + self.title

class PlaylistInfo:
    def __init__(self, name:str, listOfMedia:List[MediaFromPlaylist]):
        self.playlistName = name
        self.listOfMedia = listOfMedia

class PlaylistConfig:
    def __init__(self, name:str, link:str):
        self.name = name
        self.link = link

class MediaInfo:
    def __init__(self, title=None, artist=None, album=None, url=None):
        self.title = title
        self.artist = artist
        self.album = album
        self.url = url

    def __str__(self): # pragma: no cover
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
        self.path = path
        self.title=title

    def setPath(self, path):
        self.path = path

    def __str__(self): # pragma: no cover
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
        super().__init__(path, title)
        self.hash = hash
        self.artist = artist
        self.album = album
        self.year = year

    def __str__(self): # pragma: no cover
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
        super().__init__(path,title)
        self.ext = ext

    def __str__(self): # pragma: no cover
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
        pass

    @abstractmethod
    def getSubname(self):
        pass

