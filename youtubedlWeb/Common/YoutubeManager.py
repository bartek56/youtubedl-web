from typing import List
import os
import logging
import argparse

import yt_dlp
import metadata_mp3

from .YoutubeConfig import YoutubeConfig
from .YoutubeTypes import ResultOfDownload, YoutubeManagerLogs
from .YoutubeTypes import AudioData, MediaFromPlaylist, PlaylistInfo, MediaInfo
from .YoutubeTypes import VideoSettings, VideoData

logger = logging.getLogger(__name__)

class Hight4kFormatSettings(VideoSettings):
    format="bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
    subname="_4k"

    def getFormat(self):
        return self.format

    def getSubname(self):
        return self.subname

class Medium720pFormatSettings(VideoSettings):
    format="bestvideo[height=720]/mp4"
    subname="_720p"

    def getFormat(self):
        return self.format

    def getSubname(self):
        return self.subname

class Low360pFormatSettings(VideoSettings):
    format="worse[height<=360]/mp4"
    subname="_360p"

    def getFormat(self):
        return self.format

    def getSubname(self):
        return self.subname

class YoutubeManager:
    MUSIC_PATH="/tmp/quick_download/"
    VIDEO_PATH="/tmp/quick_download/"

    def __init__(self, musicPath="/tmp/quick_download/", videoPath="/tmp/quick_download/", mp3ArchiveFilename="downloaded_songs.txt", logger=None):
        self.metadataManager = metadata_mp3.MetadataManager()
        self.logger = logger
        self.quietSetting = False
        if self.logger is None:
            self.quietSetting = True
        self.ytDomain = "https://youtu.be/"

        self.MUSIC_PATH=musicPath
        self.VIDEO_PATH=videoPath
        self.mp3DownloadedListFileName=mp3ArchiveFilename
        self.videoConfig = {
              'addmetadata': True,
              'logger': self.logger,
              'no-overwrites': True,
              'noplaylist': True,
              'ignoreerrors': False
              }

        self.high4kSettings =     Hight4kFormatSettings()
        self.medium720pSettings = Medium720pFormatSettings()
        self.low360pSettings =    Low360pFormatSettings()



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
        logger.info("Get playlist infor from url: %s", url)

        ydl_opts = {
              'format': 'best/best',
              'logger': self.logger,
              'extract_flat': 'in_playlist',
              'addmetadata': True,
              'ignoreerrors': False,
              'quiet':self.quietSetting
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
            mediaFromPlaylist = MediaFromPlaylist(playlistIndex, i['url'], i['title'])
            logger.debug(str(mediaFromPlaylist))
            data.append(mediaFromPlaylist)
            playlistIndex+=1

        return ResultOfDownload(PlaylistInfo(playlistTitle, data))

    def getMediaInfo(self, url) -> ResultOfDownload:

        ydl_opts = {
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

    def _isMusicClipArchived(self, path, url): # pragma: no cover
        hash = self.getMediaHashFromLink(url)
        contentOfFile = self.openFile(path, self.mp3DownloadedListFileName)
        if contentOfFile is not None and hash in contentOfFile:
            return True
        return False

    def download_mp3(self, url) -> ResultOfDownload:
        info = "[INFO] start download MP3 from link %s "%(url)
        logger.info(info)
        hash = self.getMediaHashFromLink(url)
        contentOfFile = self.openFile(self.MUSIC_PATH, self.mp3DownloadedListFileName)
        if contentOfFile is not None and hash in contentOfFile:
            # only get information about media, file exists
            logger.debug("clip exists, only get information about MP3")
            result = self._getMetadataFromYTForMp3(url)
        else:
            logger.debug("Download MP3")
            result = self._downloadMp3AndAddMetadata(url)

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

    def _download_mp3(self, url, path=MUSIC_PATH) -> ResultOfDownload:
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
              'noplaylist': True,
              'quiet': self.quietSetting
              }

        try:
            result = yt_dlp.YoutubeDL(ydl_opts).extract_info(url)
        except Exception as e:
            strE = str(e).replace('\r', '')
            log = YoutubeManagerLogs.DOWNLOAD_FAILED+": "+strE
            logger.error(log)
            return ResultOfDownload(log)

        if result is None:
            log = YoutubeManagerLogs.EMPTY_RESULT+": "+url
            logger.error(log)
            return ResultOfDownload(log)
        logger.debug("succesfull download")

        mp3Data:AudioData = self._get_metadataForMP3(result)
        logger.debug(mp3Data)
        return ResultOfDownload(mp3Data)

    def _downloadMp3AndAddMetadata(self, url) -> ResultOfDownload:
        result = self._download_mp3(url)
        if result.IsFailed():
            return result
        mp3Data:AudioData = result.data()
        fileName = "%s.mp3"%(mp3Data.title)
        if not os.path.isfile(os.path.join(self.MUSIC_PATH, fileName)):
            logger.warning("File %s doesn't exist. Sanitize is require", fileName)
            mp3Data.title = yt_dlp.utils.sanitize_filename(mp3Data.title)
        mp3Data.artist = yt_dlp.utils.sanitize_filename(mp3Data.artist)
        website = self.ytDomain + mp3Data.hash
        full_path = self.metadataManager.renameAndAddMetadataToSong(self.MUSIC_PATH, mp3Data.album, mp3Data.artist, mp3Data.title, website)

        if full_path is None:
            log = YoutubeManagerLogs.NOT_FOUND
            logger.error(log)
            return ResultOfDownload(log)

        mp3Data.setPath(full_path)
        return ResultOfDownload(mp3Data)

    def _get_metadataForMP3(self, data) -> AudioData:
        songTitle = ""
        artist = ""
        album = ""
        hash = ""

        if "title" in data:
            songTitle = data['title']
        if "artist" in data:
            artist = data['artist']
        if "album" in data:
            album = data['album']
        if "id" in data:
            hash = data['id']

        return AudioData(title=songTitle, hash=hash, artist=artist, album=album)

    def download_4k(self, url) -> ResultOfDownload:
        logger.info("start download video [high quality] from link %s", url)
        return self._downloadVideo(url, self.high4kSettings)

    def download_720p(self, url) -> ResultOfDownload:
        logger.info("start download video [medium quality] from link %s", url)
        return self._downloadVideo(url, self.medium720pSettings)

    def download_360p(self, url) -> ResultOfDownload:
        logger.info("start download video [low quality] from link %s", url)
        return self._downloadVideo(url, self.low360pSettings)

    def _downloadVideo(self, url, config:VideoSettings) -> ResultOfDownload:
        path=self.VIDEO_PATH
        self.createDirIfNotExist(path)
        yt_args = dict(self.videoConfig)
        yt_args["format"] = config.getFormat()
        yt_args["outtmpl"] = path+'/'+'%(title)s'+config.getSubname()+".%(ext)s"

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

        title = yt_dlp.utils.sanitize_filename(result['title'])
        ext = result['ext']
        full_path = "%s/%s%s.%s"%(path, title, config.getSubname(), ext)
        return ResultOfDownload(VideoData(full_path,title,ext))

    def downloadPlaylistMp3Fast(self, playlistDir, playlistName, url) -> ResultOfDownload:
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
              'quiet': self.quietSetting
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
        hashList = []

        for i in results['entries']:
            playlistIndexList.append(i['playlist_index'])
            songsTitleList.append(i['title'])
            hashList.append(i["id"])

            if "artist" in i:
                artistList.append(i['artist'])
            else:
                artistList.append("")

        songCounter=0
        for x in range(len(songsTitleList)):
            songTitle = songsTitleList[x]
            artist = artistList[x]
            fileName="%s%s"%(songTitle, ".mp3")
            if not os.path.isfile(os.path.join(path,fileName)):
                logger.warning("File doesn't exist. Sanitize is require")
                songTitle = yt_dlp.utils.sanitize_filename(songTitle)
            artist = yt_dlp.utils.sanitize_filename(artist)
            website = self.ytDomain + hashList[x]
            self.metadataManager.renameAndAddMetadataToPlaylist(playlistDir, playlistIndexList[x], playlistName, artist, songTitle, website)
            songCounter+=1
        logger.info("Downloaded %i songs", songCounter)

        return ResultOfDownload(songCounter)

    def downloadPlaylistMp3(self, playlistDir, playlistName, url) -> ResultOfDownload:
        path=os.path.join(playlistDir, playlistName)
        self.createDirIfNotExist(path)

        result = self.getPlaylistInfo(url)
        if result.IsFailed():
            return result
        playlistInfo:PlaylistInfo
        playlistInfo = result.data()
        songCounter = 0

        for songData in playlistInfo.listOfMedia:
            logger.debug(str(songData))
            if self._isMusicClipArchived(path, songData.url):
                logger.info("clip \"%s\" from link %s is archived", songData.title, songData.url)
                continue
            logger.debug("start download clip from")
            result = self._download_mp3(songData.url, path)
            if result.IsFailed():
                logger.error("Failed to download song from url")
                continue
            songMetadata:AudioData
            songMetadata = result.data()
            self._addMetadataToPlaylist(playlistDir, songData.playlistIndex, playlistName, songMetadata.artist, songMetadata.album, songMetadata.title, songMetadata.hash)
            songCounter+=1
        return ResultOfDownload(songCounter)

    def _addMetadataToPlaylist(self, playlistDir, playlistIndex, playlistName, artist, album, title, hash):
        fileName="%s%s"%(title, ".mp3")
        path=os.path.join(playlistDir, playlistName)
        if not os.path.isfile(os.path.join(path, fileName)):
            logger.warning("File doesn't exist. Sanitize is require")
            title = yt_dlp.utils.sanitize_filename(title)
        artist = yt_dlp.utils.sanitize_filename(artist)
        website = ""
        if hash is not None and len(hash) > 0:
            website = self.ytDomain + hash

        return self.metadataManager.renameAndAddMetadataToPlaylist(playlistDir, playlistIndex, playlistName, artist, album, title, website)

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

class MediaServerDownloader(YoutubeManager):
    def __init__(self, configFile):
        super().__init__()
        self.ytConfig = YoutubeConfig()
        self.ytConfig.initialize(configFile)

    def setMusicPath(self, path:str):
        if not os.path.isdir(path):
            logger.error("wrong path for set music")
            return
        self.MUSIC_PATH = path
        return path

    def download_playlists(self):
        if self.setMusicPath(self.ytConfig.getPath()) is None:
            logger.error("wrong path for playlists")
            return
        songsCounter = 0
        playlists = self.ytConfig.getPlaylists()
        for playlist in playlists:
            logger.info("--------------- %s ------------------", playlist.name)
            result = self.downloadPlaylistMp3(self.ytConfig.getPath(), playlist.name, playlist.link)
            if result.IsFailed():
                logger.error("Failed to download playlist %s", playlist.name)
                continue
            logger.info("--------------- downloaded %s songs from \"%s\" playlist ------------------", result.data(), playlist.name)
            songsCounter += result.data()
        logger.info("[SUMMARY] downloaded %s songs"%(songsCounter))
        return songsCounter

def main(): # pragma: no cover
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('-t','--type',
                       action='store',
                       choices=['360', '720', '4k', 'mp3'],
                       dest='mode',
                       help='what do you want download')
    my_parser.add_argument('-l','--link',
                       action='store',
                       dest='link',
                       help='link to youtube')

    my_parser.add_argument('-u','--update',
                       action='store',
                       dest='playlistUpdate',
                       help='name playlist which you want update')

    my_parser.add_argument('-c','--config',
                       action='store',
                       dest='configFile',
                       help='download all playlists from config file')

    args = my_parser.parse_args()
    if args.mode is None and args.playlistUpdate is None and args.configFile is None:
        print("non arguments")
    elif args.configFile is not None:
        if not os.path.isfile(args.configFile):
            logger.error("configuration file %s doesn't exists", args.configFile)
            exit()
        yt = MediaServerDownloader(args.configFile)
        yt.download_playlists()
    else:
        yt = YoutubeManager()
        if args.mode is not None and args.playlistUpdate is not None:
            my_parser.error("choose only one purpose")
        if args.mode is not None:
            if args.link is None:
                my_parser.error("-l (--link) is require")
            if args.mode == '360':
                yt.download_360p(args.link)
            elif args.mode == "720":
                yt.download_720p(args.link)
            elif args.mode == "4k":
                yt.download_4k(args.link)
            elif args.mode == "mp3":
                yt.download_mp3(args.link)
        #if args.playlistUpdate is not None:
        #    yt.updat (args.playlistUpdate)

if __name__ == "__main__": # pragma: no cover
    #logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    logger = logging.getLogger(__name__)
    main()
    #yt = YoutubeManager()
    #yt.downloadPlaylistMp3("/tmp/music", "test", "https://www.youtube.com/playlist?list=PL6uhlddQJkfh4YsbxgPE70a6KeFOCDgG_")
