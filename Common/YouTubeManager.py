import os
import yt_dlp
import metadata_mp3
import configparser
import logging

logger = logging.getLogger(__name__)


class YoutubeConfig():
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

class Mp3Data():
    def __init__(self, title, artist, album):
        self.title = title
        self.artist = artist
        self.album = album
    def __str__(self):
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

        return "title: %s, artist: %s, album: %s "%(self.title, self.artist, self.album)

class YoutubeManager:
    def __init__(self, logger=None):
        self.metadataManager = metadata_mp3.MetadataManager()
        self.logger = logger
        self.MUSIC_PATH='/tmp/quick_download/'
        self.VIDEO_PATH='/tmp/quick_download/'

    def validateYTResult(self, results):
        if results is None:
            warningInfo = "Failed to download"
            logger.warning(warningInfo)
            return warningInfo

        if 'entries' not in results:
            warningInfo="not entries in results"
            logger.warning(warningInfo)
            return warningInfo

        for i in results['entries']:
            if i is None:
                warningInfo="not extract_info in results"
                logger.warning(warningInfo)
                return warningInfo
        return None

    def getPlaylistInfo(self, url):

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
            logger.warning("Exception: %s", exceptionMsg)
            return exceptionMsg

        resultOfValidate = self.validateYTResult(results)
        if resultOfValidate is not None:
            return resultOfValidate

        data = []
        playlistTitle = results['title']
        playlistIndex = 1
        for i in results['entries']:
            dictData = {}
            dictData['playlist_name'] = playlistTitle
            dictData['playlist_index'] = playlistIndex
            dictData['url'] = i['url']
            dictData['title'] = i['title']
            data.append(dictData)
            playlistIndex+=1

        return data

    def getMediaInfo(self, url):

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
            exceptionMsg = str(e)
            logger.warning("Exception: %s", exceptionMsg)
            return exceptionMsg

        if result is None:
            logger.error("Failed to download url: %s", url)
            return "Failed to download url: "+ url

        mediaInfo = {}
        mediaInfo['url'] = result['original_url']

        if "title" in result:
            mediaInfo['title'] = result['title']
        if "artist" in result:
            mediaInfo['artist'] = result['artist']
        if "album" in result:
            mediaInfo['album'] = result['album']

        return mediaInfo

    def download_mp3(self, url):
        path=self.MUSIC_PATH
        info = "[INFO] start download MP3 from link %s "%(url)
        logger.info(info)
        metadata = None
        hash = self.getMediaHashFromLink(url)
        if os.path.isdir(path):
            if os.path.isfile(path+'/downloaded_songs.txt'):
                with open(path+'/downloaded_songs.txt', 'r') as plik:
                    zawartosc = plik.read()
                    if hash in zawartosc:
                        # only get information about media, file exists
                        logger.debug("clip exists, only get information about MP3")
                        metadata = self._getMetadataFromYTForMp3(url)
        if metadata is None:
            logger.debug("Download MP3")
            metadata = self._download_mp3(url)

        return metadata

    def _getMetadataFromYTForMp3(self, url):
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
            return str(e)

        if result is None:
            return "Failed to download url: "+ url
        logger.debug("Succesfull got information")
        mp3Data = self._get_metadataForMP3(result)
        logger.debug(mp3Data)
        full_path = self.lookingForFile(path, mp3Data.title, mp3Data.artist)

        if full_path is None:
            logger.error("couldn't find a file")
            return "couldn't find a file"

        metadata = {}
        metadata["path"] = full_path
        if(mp3Data.artist is not None):
            metadata["artist"] = mp3Data.artist
        metadata["title"] = mp3Data.title
        if(mp3Data.album is not None):
            metadata["album"] = mp3Data.album

        return metadata


    def _download_mp3(self, url):
        path=self.MUSIC_PATH
        self.createDirIfNotExist(path)

        ydl_opts = {
              'format': 'bestaudio/best',
              'addmetadata': True,
              'logger': self.logger,
              'outtmpl': path+'/'+'%(title)s.%(ext)s',
              'download_archive': path+'/downloaded_songs.txt',
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
            return str(e)

        if result is None:
            return "Failed to download url: "+ url
        logger.debug("succesfull download")

        mp3Data = self._get_metadataForMP3(result)
        logger.debug(mp3Data)

        fileName = "%s.mp3"%(mp3Data.title)
        if not os.path.isfile(os.path.join(path, fileName)):
            logger.warning("File %s doesn't exist. Sanitize is require", fileName)
            mp3Data.title = yt_dlp.utils.sanitize_filename(mp3Data.title)
        full_path = self.metadataManager.rename_and_add_metadata_to_song(self.MUSIC_PATH, mp3Data.album, mp3Data.artist, mp3Data.title)

        if full_path is None:
            logger.error("couldn't find a file")
            return "couldn't find a file"

        metadata = {}
        metadata["path"] = full_path
        if(mp3Data.artist is not None):
            metadata["artist"] = mp3Data.artist
        metadata["title"] = mp3Data.title
        if(mp3Data.album is not None):
            metadata["album"] = mp3Data.album

        return metadata


    def _get_metadataForMP3(self, data):
        songTitle = ""
        artist = ""
        album = ""

        if "title" in data:
            songTitle = data['title']
        if "artist" in data:
            artist = data['artist']
        if "album" in data:
            album = data['album']

        return Mp3Data(songTitle, artist, album)

    def download_4k(self, url):
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
        if type(result) == str:
            return result

        full_path= "%s/%s_4k.%s"%(path,yt_dlp.utils.sanitize_filename(result['title']),result['ext'])
        result["path"] = full_path
        return result

    def download_720p(self, url):
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
        if type(result) == str:
            return result

        full_path = "%s/%s_720p.%s"%(path,yt_dlp.utils.sanitize_filename(result['title']),result['ext'])
        result["path"] = full_path
        return result

    def download_360p(self, url):
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

        if type(result) == str:
            return result

        full_path = "%s/%s_360p.%s"%(path, yt_dlp.utils.sanitize_filename(result['title']), result['ext'])
        result["path"] = full_path
        return result

    def downloadVideo(self, yt_args, url):
        try:
            result = yt_dlp.YoutubeDL(yt_args).extract_info(url)
        except Exception as e:
            exceptionMsg = str(e)
            logger.warning("Exception: %s", exceptionMsg)
            return exceptionMsg

        if result is None:
            return "Failed to download url: "+ url

        metadata = {}
        metadata["title"] = result['title']
        metadata["ext"] = result['ext']
        return metadata

    def download_playlist_mp3(self, playlistDir, playlistName, url):
        path=os.path.join(playlistDir, playlistName)
        self.createDirIfNotExist(path)

        ydl_opts = {
              'format': 'bestaudio/best',
              'download_archive': path+'/downloaded_songs.txt',
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
            warningMsg = str(e)
            logger.warning("Exception: %s", warningMsg)
            return warningMsg

        resultOfValidate = self.validateYTResult(results)
        if resultOfValidate is not None:
            return resultOfValidate

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

        return songCounter

    def createDirIfNotExist(self, path):
        if not os.path.exists(path): # pragma: no cover
            os.makedirs(path)

    def lookingForFile(self, path, songTitle, artist):
        fileName = "%s.mp3"%(songTitle)
        full_path = os.path.join(path,fileName)
        if os.path.isfile(full_path):
            return full_path
        songName = self.metadataManager.lookingForFileAccordWithYTFilename(path,songTitle,artist)
        fileName = "%s.mp3"%(songName)
        full_path = os.path.join(path,fileName)
        if os.path.isfile(full_path):
            return full_path
        songTitleTemp = yt_dlp.utils.sanitize_filename(songTitle)
        songName = self.metadataManager.lookingForFileAccordWithYTFilename(path,songTitleTemp,artist)
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


if __name__ == "__main__":
    yt = YoutubeManager()
    yt.download_mp3("https://www.youtube.com/watch?v=J9LgHNf2Qy0")
