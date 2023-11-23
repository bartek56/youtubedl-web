import os
import yt_dlp
import metadata_mp3
import configparser
import logging

logger = logging.getLogger(__name__)

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

class YoutubeConfig:
    def __init__(self):
        pass

    def initialize(self, configFile, parser = configparser.ConfigParser()):
        self.CONFIG_FILE = configFile
        self.config = parser

    def getPath(self):
        path = None
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        if "GLOBAL" in self.config.sections():
            path = self.config["GLOBAL"]['path']
        return path

    def getPlaylists(self):
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        data = []

        for section_name in self.config.sections():
            if section_name != "GLOBAL":
                data.append({'name':self.config[section_name]['name'], 'link':self.config[section_name]['link']})
        return data

    def getPlaylistsName(self):
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        data = []

        for section_name in self.config.sections():
            if section_name != "GLOBAL":
                data.append(self.config[section_name]['name'])
        return data

    def addPlaylist(self, playlist:dict):
        keys = playlist.keys()
        if not "name" in keys or not "link" in keys:
            return False
        self.config.read(self.CONFIG_FILE)
        playlistName = playlist["name"]
        playlistLink = playlist["link"]

        self.config[playlistName]={}
        self.config[playlistName]["name"]=playlistName
        self.config[playlistName]["link"]=playlistLink
        self.save()
        return True

    def removePlaylist(self, playlistName:str):
        result = False
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        for i in self.config.sections():
               if i == playlistName:
                   self.config.remove_section(i)
                   self.save()
                   result = True
                   break
        return result

    def getUrlOfPlaylist(self, playlistName):
        playlistUrl = None
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        for section_name in self.config.sections():
            if section_name != "GLOBAL":
                if self.config[section_name]['name'] == playlistName:
                    playlistUrl = self.config[section_name]["link"]

        return playlistUrl

    def save(self): # pragma: no cover
        with open(self.CONFIG_FILE,'w') as fp:
            self.config.write(fp)

class MediaFromPlaylist:
    def __init__(self, index:str, url:str, title:str):
        self.playlistIndex = index
        self.url = url
        self.title = title

class PlaylistInfo:
    def __init__(self, name:str, listOfMedia:list):
        self.playlistName = name
        self.listOfMedia = listOfMedia

class MediaInfo:
    def __init__(self, title:str=None, artist:str=None, album:str=None, url:str=None):
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

class Mp3Data(MediaInfo):
    def __init__(self, path:str=None, url:str=None, title:str=None, artist:str=None, album:str=None):
        super().__init__(title, artist, album, url)
        self.path = path

    def setPath(self, path):
        self.path = path

    def __str__(self): # pragma: no cover
        str = super().__str__()
        if self.path is not None and len(self.path)>0:
            if len(str) > 0:
                str += " "
            str += "path: %s"%(self.album)

        return str

class YoutubeManager:
    def __init__(self, musicPath="/tmp/quick_download/", videoPath="/tmp/quick_download/", mp3ArchiveFilename="downloaded_songs.txt", logger=None):
        self.metadataManager = metadata_mp3.MetadataManager()
        self.logger = logger
        self.MUSIC_PATH=musicPath
        self.VIDEO_PATH=videoPath
        self.mp3DownloadedListFileName=mp3ArchiveFilename

    def _validateYTResult(self, results):
        if results is None:
            logger.error(YoutubeManagerLogs.EMPTY_RESULT)
            return False

        if 'entries' not in results:
            logger.error(YoutubeManagerLogs.NOT_ENTRIES)
            return False

        for i in results['entries']:
            if i is None:
                logger.error(YoutubeManagerLogs.NOT_EXTRACT_INFO)
                return False
        return True

    def getPlaylistInfo(self, url) -> ResultOfDownload:

        ydl_opts = {
              'format': 'best/best',
              'logger': self.logger,
              'extract_flat': 'in_playlist',
              'addmetadata': True,
              'ignoreerrors': False,
              'quiet':False
              }
        results = None
        try:
            results = yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
        except Exception as e:
            exceptionMsg = str(e)
            logger.error(YoutubeManagerLogs.DOWNLOAD_FAILED+ ": " + exceptionMsg)
            return ResultOfDownload(YoutubeManagerLogs.DOWNLOAD_FAILED + ": " + exceptionMsg)

        resultOfValidate = self._validateYTResult(results)
        if resultOfValidate is False:
            logger.error(YoutubeManagerLogs.NOT_ENTRIES)
            return ResultOfDownload(YoutubeManagerLogs.NOT_ENTRIES)

        data = []
        playlistTitle = results['title']
        playlistIndex = 1
        for i in results['entries']:
            data.append(MediaFromPlaylist(playlistIndex, i['url'], i['title']))
            playlistIndex+=1

        return ResultOfDownload(PlaylistInfo(playlistTitle, data))

    def getMediaInfo(self, url) -> ResultOfDownload:

        ydl_opts = {
              'format': 'best/best',
              'logger': self.logger,
              'addmetadata': True,
              'ignoreerrors': False,
              'quiet':True,
              'noplaylist':True
              }
        result = None
        try:
            result = yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
        except Exception as e:
            log = str(e)
            logger.error(log)
            return ResultOfDownload(log)

        if result is None:
            logger.error(YoutubeManagerLogs.EMPTY_RESULT + ": " + url)
            return ResultOfDownload(YoutubeManagerLogs.EMPTY_RESULT + ": " + url)

        title=None
        artist=None
        album=None
        if "title" in result:
            title = result['title']
        if "artist" in result:
            artist = result['artist']
        if "album" in result:
            album = result['album']

        return ResultOfDownload(MediaInfo(title,artist,album,result['original_url']))

    def download_mp3(self, url) -> ResultOfDownload:
        path=self.MUSIC_PATH
        info = "[INFO] start download MP3 from link %s "%(url)
        logger.info(info)
        hash = self.getMediaHashFromLink(url)
        contentOfFile = self.openFile(path, self.mp3DownloadedListFileName)
        if contentOfFile is not None and hash in contentOfFile:
            # only get information about media, file exists
            logger.debug("clip exists, only get information about MP3")
            result = self._getMetadataFromYTForMp3(url)
        else:
            logger.debug("Download MP3")
            result = self._download_mp3(url)

        return result

    def _getMetadataFromYTForMp3(self, url) -> ResultOfDownload:
        path=self.MUSIC_PATH

        ydl_opts = {
              'format': 'bestaudio/best',
              'addmetadata': True,
              'logger': self.logger,
              'outtmpl': path+'/'+'%(title)s.%(ext)s',
              'ignoreerrors': False,
              'continue': True,
              'no-overwrites': True,
              'noplaylist': True
              }

        try:
            result = yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
        except Exception as e:
            log = YoutubeManagerLogs.DOWNLOAD_FAILED+": "+str(e)
            logger.error(log)
            return ResultOfDownload(log)

        if result is None:
            log = YoutubeManagerLogs.EMPTY_RESULT+": "+url
            logger.error(log)
            return ResultOfDownload(log)

        logger.debug("Succesfull got information")
        mp3Data = self._get_metadataForMP3(result)
        logger.debug(mp3Data)
        full_path = self.lookingForFile(path, mp3Data.title, mp3Data.artist)

        if full_path is None:
            log = YoutubeManagerLogs.NOT_FOUND
            logger.error(log)
            return ResultOfDownload(log)

        mp3Data.setPath(full_path)

        return ResultOfDownload(mp3Data)

    def _download_mp3(self, url) -> ResultOfDownload:
        path=self.MUSIC_PATH
        self.createDirIfNotExist(path)

        ydl_opts = {
              'format': 'bestaudio/best',
              'addmetadata': True,
              'logger': self.logger,
              'outtmpl': path+'/'+'%(title)s.%(ext)s',
              'download_archive': path+'/'+self.mp3DownloadedListFileName,
              'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                 }],
              'ignoreerrors': False,
              'continue': True,
              'no-overwrites': True,
              'noplaylist': True
              }

        try:
            result = yt_dlp.YoutubeDL(ydl_opts).extract_info(url)
        except Exception as e:
            log = YoutubeManagerLogs.DOWNLOAD_FAILED+": "+str(e)
            logger.error(log)
            return ResultOfDownload(log)

        if result is None:
            log = YoutubeManagerLogs.EMPTY_RESULT+": "+url
            logger.error(log)
            return ResultOfDownload(log)
        logger.debug("succesfull download")

        mp3Data = self._get_metadataForMP3(result)
        logger.debug(mp3Data)

        fileName = "%s.mp3"%(mp3Data.title)
        if not os.path.isfile(os.path.join(path, fileName)):
            logger.warning("File %s doesn't exist. Sanitize is require", fileName)
            mp3Data.title = yt_dlp.utils.sanitize_filename(mp3Data.title)
        full_path = self.metadataManager.rename_and_add_metadata_to_song(self.MUSIC_PATH, mp3Data.album, mp3Data.artist, mp3Data.title)

        if full_path is None:
            log = YoutubeManagerLogs.NOT_FOUND
            logger.error(log)
            return ResultOfDownload(log)

        mp3Data.setPath(full_path)
        return ResultOfDownload(mp3Data)

    def _get_metadataForMP3(self, data) -> Mp3Data:
        songTitle = ""
        artist = ""
        album = ""

        if "title" in data:
            songTitle = data['title']
        if "artist" in data:
            artist = data['artist']
        if "album" in data:
            album = data['album']

        return Mp3Data(title=songTitle, artist=artist, album=album)

    def download_4k(self, url) -> ResultOfDownload:
        path=self.VIDEO_PATH
        self.createDirIfNotExist(path)
        logger.info("start download video [high quality] from link %s", url)

        ydl_opts = {
              'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
              'addmetadata': True,
              'logger': self.logger,
              'outtmpl': path+'/'+'%(title)s_4k.%(ext)s',
              'no-overwrites': True,
              'noplaylist': True,
              'ignoreerrors': False
              }
        result = self.downloadVideo(ydl_opts, url)
        if result.IsFailed():
            return result
        data = result.data()
        full_path= "%s/%s_4k.%s"%(path,yt_dlp.utils.sanitize_filename(data['title']),data['ext'])
        data["path"] = full_path
        return ResultOfDownload(data)

    def download_720p(self, url) -> ResultOfDownload:
        path=self.VIDEO_PATH
        self.createDirIfNotExist(path)
        logger.info("start download video [medium quality] from link %s", url)

        ydl_opts = {
              'format': 'bestvideo[height=720]/mp4',
              'addmetadata': True,
              'logger': self.logger,
              'no-overwrites': True,
              'outtmpl': path+'/'+'%(title)s_720p.%(ext)s',
              'noplaylist': True,
              'ignoreerrors': False
              }
        result = self.downloadVideo(ydl_opts, url)
        if result.IsFailed():
            return result
        data = result.data()
        full_path = "%s/%s_720p.%s"%(path,yt_dlp.utils.sanitize_filename(data['title']), data['ext'])
        data["path"] = full_path
        return ResultOfDownload(data)

    def download_360p(self, url) -> ResultOfDownload:
        path=self.VIDEO_PATH
        self.createDirIfNotExist(path)

        logger.info("start download video [low quality] from link %s", url)

        ydl_opts = {
              'format': 'worse[height<=360]/mp4',
              'addmetadata': True,
              'logger': self.logger,
              'no-overwrites': True,
              'outtmpl': path+'/'+'%(title)s_360p.%(ext)s',
              'noplaylist': True,
              'ignoreerrors': False
              }

        result = self.downloadVideo(ydl_opts, url)

        if result.IsFailed():
            return result
        data = result.data()
        full_path = "%s/%s_360p.%s"%(path, yt_dlp.utils.sanitize_filename(data['title']), data['ext'])

        data["path"] = full_path
        return ResultOfDownload(data)

    def downloadVideo(self, yt_args, url) -> ResultOfDownload:
        try:
            result = yt_dlp.YoutubeDL(yt_args).extract_info(url)
        except Exception as e:
            log = YoutubeManagerLogs.DOWNLOAD_FAILED + ": " + str(e)
            logger.error(log)
            return ResultOfDownload(log)

        if result is None:
            log = YoutubeManagerLogs.EMPTY_RESULT + ": " + url
            logger.error(log)
            return ResultOfDownload(log)

        metadata = {}
        metadata["title"] = result['title']
        metadata["ext"] = result['ext']
        return ResultOfDownload(metadata)

    def download_playlist_mp3(self, playlistDir, playlistName, url) -> ResultOfDownload:
        path=os.path.join(playlistDir, playlistName)
        self.createDirIfNotExist(path)

        ydl_opts = {
              'format': 'bestaudio/best',
              'download_archive': path+'/'+self.mp3DownloadedListFileName,
              'addmetadata': True,
              'logger': self.logger,
              'outtmpl': path+'/'+'%(title)s.%(ext)s',
              'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                    }],
              'ignoreerrors': True,
              'quiet': True
              }
        results = None

        logger.info("started download playlist %s, url: %s", playlistName, url)
        try:
            results = yt_dlp.YoutubeDL(ydl_opts).extract_info(url)
        except Exception as e:
            log = YoutubeManagerLogs.DOWNLOAD_FAILED+": "+str(e)
            logger.error(log)
            return ResultOfDownload(log)

        resultOfValidate = self._validateYTResult(results)
        if resultOfValidate is False:
            log = YoutubeManagerLogs.NOT_ENTRIES
            logger.error(log)
            return ResultOfDownload(log)

        artistList = []
        playlistIndexList = []
        songsTitleList = []

        for i in results['entries']:
            playlistIndexList.append(i['playlist_index'])
            songsTitleList.append(i['title'])

            if "artist" in i:
                artistList.append(i['artist'])
            else:
                artistList.append("")

        songCounter=0
        for x in range(len(songsTitleList)):
            songTitle = songsTitleList[x]
            fileName="%s%s"%(songTitle, ".mp3")
            if not os.path.isfile(os.path.join(path,fileName)):
                logger.warning("File doesn't exist. Sanitize is require")
                songTitle = yt_dlp.utils.sanitize_filename(songTitle)
            self.metadataManager.rename_and_add_metadata_to_playlist(playlistDir, playlistIndexList[x], playlistName, artistList[x], songTitle)
            songCounter+=1

        return ResultOfDownload(songCounter)

    def createDirIfNotExist(self, path):
        if not os.path.exists(path): # pragma: no cover
            os.makedirs(path)

    def lookingForFile(self, path, songTitle, artist): # pragma: no cover
        fileName = "%s.mp3"%(songTitle)
        full_path = os.path.join(path,fileName)
        if os.path.isfile(full_path):
            return full_path
        songName = self.metadataManager.lookingForFileAccordWithYTFilename(path, songTitle, artist)
        fileName = "%s.mp3"%(songName)
        full_path = os.path.join(path,fileName)
        if os.path.isfile(full_path):
            return full_path
        songTitleTemp = yt_dlp.utils.sanitize_filename(songTitle)
        songName = self.metadataManager.lookingForFileAccordWithYTFilename(path, songTitleTemp, artist)
        fileName = "%s.mp3"%(songName)
        full_path = os.path.join(path, fileName)
        if os.path.isfile(full_path):
            return full_path
        artistTemp = yt_dlp.utils.sanitize_filename(artist)
        songName = self.metadataManager.lookingForFileAccordWithYTFilename(path, songTitleTemp, artistTemp)
        fileName = "%s.mp3"%(songName)
        full_path = os.path.join(path, fileName)
        if os.path.isfile(full_path):
            return full_path
        logger.error("clip is archived, but doesn't exists in server")
        return None

    def getMediaHashFromLink(self, url):
        mediaData = url.split('.com/')[1]
        parametersFromLink = mediaData.split("&")
        for param in parametersFromLink:
            if "watch" in param:
                return param.split("=")[1]
        logger.error("error with getting hash from link")

    def openFile(self, path, fileName): # pragma: no cover
        content = None
        if os.path.isdir(path):
            if os.path.isfile(path+'/'+fileName):
                with open(path+'/'+fileName, 'r') as file:
                    content = file.read()
        return content

if __name__ == "__main__":
    yt = YoutubeManager()
    yt.download_mp3("https://www.youtube.com/watch?v=J9LgHNf2Qy0")
