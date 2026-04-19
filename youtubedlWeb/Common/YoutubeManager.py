from datetime import datetime, timedelta
import os
import logging
import argparse

import yt_dlp
import metadata_mp3
from metadata_mp3 import Mp3Info

from .YoutubeConfig import YoutubeConfig
from .YoutubeTypes import ResultOfDownload, YoutubeManagerLogs
from .YoutubeTypes import AudioData, MediaFromPlaylist, PlaylistInfo, MediaInfo
from .YoutubeTypes import VideoSettings, VideoData
from .PlaylistsManager import PlaylistsManager

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

    def getMediaInfo(self, url) -> ResultOfDownload:

        """
        Get media information from a given url.

        Parameters:
            url (str): A youtube url.

        Returns:
            ResultOfDownload: A result object containing the media information, or an error message if the download failed.
        """
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

    def getPlaylistInfo(self, url) -> ResultOfDownload:
        """
        Get playlist information from a given url.

        Parameters:
            url (str): A youtube url.

        Returns:
            ResultOfDownload: A result object containing the playlist information, or an error message if the download failed.
        """
        logger.debug("Get playlist infor from url: %s", url)

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
            #logger.debug(str(mediaFromPlaylist))
            data.append(mediaFromPlaylist)
            playlistIndex+=1

        return ResultOfDownload(PlaylistInfo(playlistTitle, data))

    def download_4k(self, url) -> ResultOfDownload:
        """
        Download video from a given url in high quality (4K).

        Parameters:
            url (str): A youtube url.

        Returns:
            ResultOfDownload: A result object containing the downloaded video, or an error message if the download failed.
        """
        logger.info("start download video [high quality] from link %s", url)
        return self._downloadVideo(url, self.high4kSettings)

    def download_720p(self, url) -> ResultOfDownload:
        """
        Download video from a given url in medium quality (720p).

        Parameters:
            url (str): A youtube url.

        Returns:
            ResultOfDownload: A result object containing the downloaded video, or an error message if the download failed.
        """
        logger.info("start download video [medium quality] from link %s", url)
        return self._downloadVideo(url, self.medium720pSettings)

    def download_360p(self, url) -> ResultOfDownload:
        """
        Download video from a given url in low quality (360p).

        Parameters:
            url (str): A youtube url.

        Returns:
            ResultOfDownload: A result object containing the downloaded video, or an error message if the download failed.
        """
        logger.info("start download video [low quality] from link %s", url)
        return self._downloadVideo(url, self.low360pSettings)

    def _downloadVideo(self, url, config:VideoSettings) -> ResultOfDownload:
        """
        Download a video from a given url with a given configuration.

        Parameters:
            url (str): A youtube url.
            config (VideoSettings): A configuration object containing the format and subtitle for the downloaded video.

        Returns:
            ResultOfDownload: A result object containing the downloaded video, or an error message if the download failed.
        """
        path=self.VIDEO_PATH
        self._createDirIfNotExist(path)
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

    def download_mp3(self, url) -> ResultOfDownload:
        """
        Download an MP3 from a given url.

        If the file for the given url already exists, this method will only get information about the media and will not download anything.
        If the file does not exist, this method will download the MP3 and add metadata to it.

        Parameters:
            url (str): A youtube url.

        Returns:
            ResultOfDownload: A result object containing the downloaded MP3, or an error message if the download failed.
        """
        info = "[INFO] start download MP3 from link %s "%(url)
        logger.info(info)
        if self.isMusicClipArchived(self.MUSIC_PATH, url):
            # only get information about media, file exists
            logger.debug("clip exists, only get information about MP3")
            result = self._getMetadataFromYTForMp3(url, self.MUSIC_PATH)
        else:
            logger.debug("Download MP3")
            result = self._downloadMp3AndAddMetadata(url)

        return result

    def getListOfDownloadedSongs(self):
        """
        Get a list of all the downloaded songs in the MUSIC_PATH directory.

        Each element of the list is a tuple containing the full path of the downloaded song and the metadata associated with it.

        Returns:
            list: A list of tuples containing the full path of the downloaded song and the metadata associated with it.
        """
        listOfDownlodedFiles = []
        for dirpath, _, filenames in os.walk(self.MUSIC_PATH):
                for filename in filenames:
                    if filename.lower().endswith(".mp3"):
                        filepath = os.path.join(dirpath, filename)
                        mp3Metadata = self.metadataManager.getMp3Info(filepath)
                        if mp3Metadata is None or mp3Metadata.website is None:
                            continue
                        listOfDownlodedFiles.append((filepath, mp3Metadata))
        return listOfDownlodedFiles

    def isMusicClipArchived(self, path, url): # pragma: no cover
        """
        Check if a music clip from a given url already exists in the given path.

        The method will return True if the clip exists and False otherwise.

        Parameters:
            path (str): The path to check for the music clip.
            url (str): The url of the music clip to check.

        Returns:
            bool: True if the clip exists, False otherwise.
        """
        hash = self.getMediaHashFromLink(url)
        contentOfFile = self._openFile(path, self.mp3DownloadedListFileName)
        if contentOfFile is not None and hash in contentOfFile:
            return True
        return False

    def _getMetadataFromYTForMp3(self, url, path) -> ResultOfDownload:
        """
        Get metadata from a given youtube url without downloading the file.

        Parameters:
            url (str): A youtube url.
            path (str): The path to check for the music clip.

        Returns:
            ResultOfDownload: A result object containing the metadata of the downloaded MP3, or an error message if the download failed.
        """
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
        mp3Data.title = self.metadataManager._removeSheetFromSongName(mp3Data.title)
        mp3Data.artist  = self.metadataManager._cutLengthAndRemoveDuplicates(mp3Data.artist, self.metadataManager.maxLenghtOfArtist)
        if len(mp3Data.title) > self.metadataManager.maxLenghtOfTitle:
            mp3Data.title = self.metadataManager._cutLenght(mp3Data.title, self.metadataManager.maxLenghtOfTitle)

        full_path = self._lookingForFile(path, mp3Data.title, mp3Data.artist)

        if full_path is None:
            log = YoutubeManagerLogs.NOT_FOUND
            logger.error(log)
            return ResultOfDownload(log)

        mp3Data.setPath(full_path)

        return ResultOfDownload(mp3Data)

    def _downloadMp3AndAddMetadata(self, url) -> ResultOfDownload:
        """
        Download MP3 and add metadata to it.

        Args:
            url (str): url of the song to download

        Returns:
            ResultOfDownload: result of the operation, containing data about downloaded song
        """
        result = self._download_mp3(url)
        if result.IsFailed():
            return result
        mp3Data:AudioData = result.data()
        fileNameWithPath = mp3Data.path
        fileName = fileNameWithPath.split("/")[-1]
        if not os.path.isfile(fileNameWithPath):
            logger.warning("File %s doesn't exist. Sanitize is require", fileNameWithPath)
            mp3Data.title = yt_dlp.utils.sanitize_filename(mp3Data.title)
        mp3Data.artist = yt_dlp.utils.sanitize_filename(mp3Data.artist)
        website = self.ytDomain + mp3Data.hash
        full_path = self.metadataManager.renameAndAddMetadata(os.path.join(self.MUSIC_PATH, fileName), None,
                                                                    mp3Data.title, mp3Data.artist, mp3Data.album, None, website, self._getDateTimeNowStr())

        if full_path is None:
            log = YoutubeManagerLogs.NOT_FOUND
            logger.error(log)
            return ResultOfDownload(log)

        self.metadataManager.addCoverOfYtMp3(full_path, mp3Data.hash)

        mp3Data.setPath(full_path)
        return ResultOfDownload(mp3Data)

    def _download_mp3(self, url, path=MUSIC_PATH, titleFormat='%(title)s.%(ext)s') -> ResultOfDownload:
        """
        Download a song from YouTube in MP3 format and add metadata to it.

        Args:
            url (str): url of the song to download
            path (str, optional): path to save the song. Defaults to MUSIC_PATH.
            titleFormat (str, optional): format of the title of the song. Defaults to '%(title)s.%(ext)s'.

        Returns:
            ResultOfDownload: result of the operation, containing data about downloaded song
        """
        self._createDirIfNotExist(path)

        ydl_opts = {
              #'format': 'bestaudio/best',
              'addmetadata': True,
              'logger': self.logger,
              'outtmpl': path+'/'+titleFormat,
              'download_archive': path+'/'+self.mp3DownloadedListFileName,
              'ignoreerrors': False,
              'continue': True,
              'no-overwrites': True,
              'noplaylist': True,
              'quiet': self.quietSetting,
              'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                 }]
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

    def _get_metadataForMP3(self, data) -> AudioData:
        """
        Extract metadata from a YouTube video download result and return it as AudioData.

        Args:
            data (dict): result of YouTube video download, containing metadata about downloaded song

        Returns:
            AudioData: extracted metadata as AudioData
        """
        songTitle = ""
        artist = ""
        album = ""
        hash = ""
        year = ""
        filePath = None

        if "title" in data:
            songTitle = data['title']
        if "artist" in data:
            artist = data['artist']
        if "album" in data:
            album = data['album']
        if "id" in data:
            hash = data['id']
        if "requested_downloads" in data:
            filePath = data["requested_downloads"][0]['filepath']
        if "release_year" in data:
            year = data["release_year"]

        return AudioData(path=filePath,title=songTitle, hash=hash, artist=artist, album=album, year=year)

    def downloadPlaylistMp3Fast(self, playlistDir, playlistName, url) -> ResultOfDownload:
        """
        Download a YouTube playlist and save all songs as MP3, fast version.

        Args:
            playlistDir (str): path to the directory where the playlist will be saved
            playlistName (str): name of the playlist
            url (str): URL of the YouTube playlist

        Returns:
            ResultOfDownload: result of the operation, containing the number of downloaded songs or an error message
        """
        path=os.path.join(playlistDir, playlistName)
        self._createDirIfNotExist(path)

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
        albumList = []
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

            if "album" in i:
                albumList.append(i['album'])
            else:
                albumList.append("")

        songCounter=0
        for x in range(len(songsTitleList)):
            songTitle = songsTitleList[x]
            artist = artistList[x]
            album = albumList[x]
            fileName="%s%s"%(songTitle, ".mp3")
            if not os.path.isfile(os.path.join(path,fileName)):
                logger.warning("File doesn't exist. Sanitize is require")
                songTitle = yt_dlp.utils.sanitize_filename(songTitle)
                fileName="%s%s"%(songTitle, ".mp3")
                if not os.path.isfile(os.path.join(path,fileName)):
                    logger.error("File doesn't exists! %s", os.path.join(path,fileName))

            artist = yt_dlp.utils.sanitize_filename(artist)
            website = self.ytDomain + hashList[x]
            self.metadataManager.renameAndAddMetadata(os.path.join(playlistDir,playlistName,fileName), playlistIndexList[x],
                                                                songTitle, artist, album, "YT "+playlistName, website, self._getDateTimeNowStr())

            songCounter+=1
        logger.info("Downloaded %i songs", songCounter)

        return ResultOfDownload(songCounter)

    def _validateYTResult(self, results):
        """
        Validate the result of YouTube video download.

        Args:
            results (dict): result of YouTube video download, containing metadata about downloaded song

        Returns:
            bool: True if the result is valid, False otherwise
        """
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

    def addMetadataToPlaylist(self, playlistDir, playlistName, fileName, playlistIndex, title, artist, album, hash, year=None):
        """
        Add metadata to a song in a playlist.

        Args:
            playlistDir (str): path to the directory where the playlist is saved
            playlistName (str): name of the playlist
            fileName (str): name of the song file
            playlistIndex (str): index of the song in the playlist
            title (str): title of the song
            artist (str): artist of the song
            album (str): album of the song
            hash (str): YouTube hash of the song
            year (str): year of the album (optional)

        Returns:
            str: path to the song file after adding metadata
        """
        title = yt_dlp.utils.sanitize_filename(title)
        artist = yt_dlp.utils.sanitize_filename(artist)
        website = ""
        albumArtist = album
        album = ""
        if len(playlistName) > 0:
            album = "YT "+playlistName
        if hash is not None and len(hash) > 0:
            website = self.ytDomain + hash
        album_date = ""
        if year is not None and len(year) > 0:
            album_date = year
        else:
            album_date = self._getDateTimeNowStr()

        return self.metadataManager.renameAndAddMetadata(os.path.join(playlistDir, playlistName, fileName), playlistIndex,
                                                                   title, artist, album, albumArtist, website, album_date)

    def _getSongsOfDir(self, playlistDir): # pragma: no cover
        """
        Get all songs from a given directory.

        Args:
            playlistDir (str): path to the directory where the songs are saved

        Returns:
            list: list of Mp3Info objects, each containing metadata about a song
        """
        if not os.path.isdir(playlistDir):
            logger.error("Wrong dir path: %s", playlistDir)
            return

        files = os.listdir(playlistDir)
        listMp3 = []
        isTrackNumber = True
        for file in files:
            if ".mp3" in file:
                fullPath = os.path.join(playlistDir, file)
                audio = self.metadataManager.getMp3Info(fullPath)
                if audio.trackNumber is None:
                    isTrackNumber = False
                audio.fileName = file
                listMp3.append(audio)
        if isTrackNumber:
            listMp3 = sorted(listMp3, key=lambda x: float(x.trackNumber))

        return listMp3

    def _getIndexOfMediaFromPlaylistList(self, list, url):
        """
        Get the index of a MediaFromPlaylist object in a list by its url.

        Args:
            list (list): list of MediaFromPlaylist objects
            url (str): url of the song to find

        Returns:
            int: index of the song in the list, or None if not found
        """
        index = 0
        for x in list:
            x:MediaFromPlaylist
            if x.url == url:
                return index
            index+=1
        logger.error("Song with url:%s was not found!", url)
        return None

    def _getIndexOfMp3InfoList(self, list, website):
        """
        Get the index of a Mp3Info object in a list by its website.

        Args:
            list (list): list of Mp3Info objects
            website (str): website of the song to find

        Returns:
            int: index of the song in the list, or None if not found
        """
        index = 0
        for x in list:
            x:Mp3Info
            if x.website == website:
                return index
            index+=1
        logger.error("Song with website:%s was not found!", website)
        return None

    def _getDateTimeNowStr(self):
        """
        Get current date in the format YYYY-MM-DD.

        Returns:
            str: current date in the format YYYY-MM-DD
        """
        return datetime.now().strftime("%Y-%m-%d")

    def _createDirIfNotExist(self, path):
        """
        Create a directory if it doesn't exist.

        Args:
            path (str): path to the directory to create

        Returns:
            None
        """
        if not os.path.exists(path): # pragma: no cover
            logger.warning("Directory %s was created", path)
            os.makedirs(path)

    def _lookingForFile(self, path, songTitle, artist): # pragma: no cover
        """
        Look for a file with the given song title and artist in the given path.

        It first looks for a file with the given song title, then looks for a file with
        the song title without the sheet name, then looks for a file with the song
        title and artist without the sheet name, and finally looks for a file with
        the song title and artist sanitized.

        Args:
            path (str): path to look for the file
            songTitle (str): title of the song to look for
            artist (str): artist of the song to look for

        Returns:
            str: path to the file if found, otherwise None
        """
        def lookingForFileAccordWithYTFilename(path, songName, artist):
            songName = self.metadataManager._removeSheetFromSongName(songName)
            fileName="%s%s"%(songName,".mp3")
            if os.path.isfile(os.path.join(path, fileName)):
                return songName
            songName = "%s - %s"%(artist, songName)
            fileName="%s%s"%(songName,".mp3")
            if os.path.isfile(os.path.join(path, fileName)):
             return songName
            else:
                return None

        fileName = "%s.mp3"%(songTitle)
        full_path = os.path.join(path,fileName)
        if os.path.isfile(full_path):
            return full_path
        songName = lookingForFileAccordWithYTFilename(path, songTitle, artist)
        fileName = "%s.mp3"%(songName)
        full_path = os.path.join(path,fileName)
        if os.path.isfile(full_path):
            return full_path
        songTitleTemp = yt_dlp.utils.sanitize_filename(songTitle)
        songName = lookingForFileAccordWithYTFilename(path, songTitleTemp, artist)
        fileName = "%s.mp3"%(songName)
        full_path = os.path.join(path, fileName)
        if os.path.isfile(full_path):
            return full_path
        artistTemp = yt_dlp.utils.sanitize_filename(artist)
        songName = lookingForFileAccordWithYTFilename(path, songTitleTemp, artistTemp)
        fileName = "%s.mp3"%(songName)
        full_path = os.path.join(path, fileName)
        if os.path.isfile(full_path):
            return full_path
        logger.error("clip is archived, but doesn't exists in server")
        return None

    def getMediaHashFromLink(self, url):
        """
        Get the media hash from the given youtube link.

        Args:
            url (str): the youtube link to get the media hash from

        Returns:
            str: the media hash if found, otherwise None
        """
        mediaData = url.split('.com/')[1]
        parametersFromLink = mediaData.split("&")
        for param in parametersFromLink:
            if "watch" in param:
                return param.split("=")[1]
        logger.error("error with getting hash from link")

    def _openFile(self, path, fileName): # pragma: no cover
        """
        Open a file and return its content.

        Args:
            path (str): the path to the directory where the file is located
            fileName (str): the name of the file to open

        Returns:
            str: the content of the file if found, otherwise None
        """
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

    def download_playlists(self):
        if not self._isDirForPlaylists():
            logger.error("wrong path for playlists")
            return 0
        downloadedSongs = []
        songsCounter = 0
        playlists = self.ytConfig.getPlaylists()
        for playlist in playlists:
            logger.info("--------------- %s ------------------", playlist.name)
            logger.info("%s", playlist.link)
            result = self.downloadPlaylistMp3(self.ytConfig.getPath(), playlist.name, playlist.link)
            self.checkPlaylistStatus(self.ytConfig.getPath(), playlist.name, playlist.link)
            if result.IsFailed():
                logger.error("Failed to download playlist %s", playlist.name)
                continue
            downloadedFiles:list = result.data()
            numberOfDownloadedSongs = len(downloadedFiles)
            logger.info("--------------- downloaded %s songs from \"%s\" playlist ------------------", numberOfDownloadedSongs, playlist.name)
            if numberOfDownloadedSongs > 0:
                downloadedSongs.append(downloadedFiles)
                songsCounter += numberOfDownloadedSongs
        logger.info("[SUMMARY] downloaded %s songs"%(songsCounter))
        return downloadedSongs

    def downloadPlaylistMp3(self, playlistDir, playlistName, url) -> ResultOfDownload:
        path=os.path.join(playlistDir, playlistName)
        self._createDirIfNotExist(path)

        result = self.getPlaylistInfo(url)
        if result.IsFailed():
            return result
        playlistInfo:PlaylistInfo
        playlistInfo = result.data()
        downloadedSongs = []

        numberOfDownloadedSongsLocally = self._getNumberOfDownloadedSongs(path)
        if len(playlistInfo.listOfMedia) > 2:
            isFirstClipArchive = self.isMusicClipArchived(path, playlistInfo.listOfMedia[0].url)
            isLastClipArchive = self.isMusicClipArchived(path, playlistInfo.listOfMedia[len(playlistInfo.listOfMedia)-1].url)
            if not isFirstClipArchive and isLastClipArchive:
                playlistInfo.listOfMedia.reverse()

        for songData in playlistInfo.listOfMedia:
            logger.debug(str(songData))
            if self.isMusicClipArchived(path, songData.url):
                logger.debug("clip \"%s\" from link %s is archived", songData.title, songData.url)
                continue
            logger.debug("start download clip from")
            fileToCheck = os.path.join(path, "%s.mp3"%(songData.title))
            titleFormat='%(title)s.%(ext)s'
            if os.path.isfile(fileToCheck):
                logger.warning("File %s was downloaded before", fileToCheck)
                titleFormat = self._changeTitleTemplate(path, songData)
                if titleFormat is None:
                    logger.error("File %s exists and new song can not be downloaded!", fileToCheck)
                    continue

            result = self._download_mp3(songData.url, path, titleFormat)
            if result.IsFailed():
                logger.error("Failed to download song from url: %s", songData.url)
                continue
            songMetadata:AudioData
            songMetadata = result.data()
            numberOfDownloadedSongsLocally+=1
            filenameWithPath = self.addMetadataToPlaylist(playlistDir, playlistName, songMetadata.path.split("/")[-1], str(numberOfDownloadedSongsLocally), songMetadata.title, songMetadata.artist, songMetadata.album, songMetadata.hash)
            self.metadataManager.addCoverOfYtMp3(filenameWithPath, songMetadata.hash)
            downloadedSongs.append(filenameWithPath)
        return ResultOfDownload(downloadedSongs)

    def checkPlaylistStatus(self, playlistDir, playlistName, url):
        directory=os.path.join(playlistDir, playlistName)
        localFiles = self._getSongsOfDir(directory)
        localFilesTemp = localFiles.copy()
        if localFiles is None:
            logger.error("Failed to get songs")
            return
        playlistInfoResponse = self.getPlaylistInfo(url)
        if playlistInfoResponse.IsFailed():
            logger.error("Failed to get info about playlists")
            return
        playlistInfo:PlaylistInfo = playlistInfoResponse.data()
        ytSongsTemp = playlistInfo.listOfMedia.copy()

        for ytSong in playlistInfo.listOfMedia:

            ytHash = ytSong.url.split("?v=")[1]
            for localFile in localFiles:
                localFile:Mp3Info
                if localFile.website is None or len(localFile.website) < 2:
                    logger.error("Local song: %s doesn't have website link !!!", localFile.fileName)
                    continue
                localHash = localFile.website.split(".be/")[1]
                if ytHash == localHash:
                    logger.debug("------")
                    logger.debug("file from yt: %s, %s, %s", ytSong.playlistIndex, ytSong.title, ytSong.url)
                    logger.debug("file locally: %s, %s, %s, %s", localFile.trackNumber, localFile.title, localFile.website, localFile.fileName)

                    indexToRemove = self._getIndexOfMp3InfoList(localFilesTemp, localFile.website)
                    if indexToRemove is None:
                        logger.error("Local file %s, %s, %s, %s was not found! This song was added twice on the Youtube playlist", localFile.fileName, localFile.trackNumber, localFile.title, localFile.website)
                    else:
                        localFilesTemp.pop(indexToRemove)

                    indexToRemove = self._getIndexOfMediaFromPlaylistList(ytSongsTemp, ytSong.url)
                    if indexToRemove is None:
                        logger.error("YT song %s, %s, %s was not found! It is duplication locally", ytSong.playlistIndex, ytSong.title, ytSong.url)
                    else:
                        ytSongsTemp.pop(indexToRemove)

        countOfLocalFiles = len(localFiles)
        countOfPlaylistSongs = len(playlistInfo.listOfMedia)
        if countOfLocalFiles != countOfPlaylistSongs:
            logger.warning("Locally is %s songs, but in playlist is %s", countOfLocalFiles, countOfPlaylistSongs)

        if len(localFilesTemp) > 0:
            logger.info("Files exists in local, but was not found in youtube")
            for x in localFilesTemp:
                logger.info("%s", x)

        if len(ytSongsTemp) > 0:
            logger.info("Files exists in Youtube, but was not found locally")
            for x in ytSongsTemp:
                logger.info("%s", x)

        if len(ytSongsTemp) == 0 and len(localFilesTemp) == 0:
            logger.info("Playlist %s is perfect synchonized!", playlistInfo.playlistName)

        return (localFilesTemp, ytSongsTemp)

    def checkPlaylistsSync(self):
        if not self._isDirForPlaylists(self.ytConfig.getPath()):
            logger.error("wrong path for playlists")
            return
        playlists = self.ytConfig.getPlaylists()
        for playlist in playlists:
            logger.info("--------------- %s %s------------------", playlist.name, playlist.link)
            self.checkPlaylistStatus(self.ytConfig.getPath(), playlist.name, playlist.link)

    def updateTrackNumberAllPlaylists(self, indexOfPlaylist=None, isSave=False):
        if not self._isDirForPlaylists(self.ytConfig.getPath()):
            logger.error("wrong path for playlists")
            return
        playlists = self.ytConfig.getPlaylists()
        if indexOfPlaylist is not None:
            playlist = playlists[indexOfPlaylist]
            logger.info("--------------- %s ------------------", playlist.name)
            logger.info(" %s ", playlist.link)
            playlistDir = os.path.join(self.ytConfig.getPath(), playlist.name)
            self.updateTrackNumber(playlistDir,playlist.link, isSave)
        else:
            for playlist in playlists:
                logger.info("--------------- %s ------------------", playlist.name)
                logger.info(" %s ", playlist.link)
                playlistDir = os.path.join(self.ytConfig.getPath(), playlist.name)
                self.updateTrackNumber(playlistDir,playlist.link, isSave)

    def updateMetadataForPlaylists(self):
        playlists = self.ytConfig.getPlaylists()
        for playlist in playlists:
            logger.info("--------------- %s ------------------", playlist.name)
            logger.info(" %s ", playlist.link)
            playlistDir = os.path.join(self.ytConfig.getPath(), playlist.name)
            self.metadataManager.updateMetadata(playlistDir, "YT "+playlist.name)

    def updateTrackNumber(self, playlistDir, url, isSave=False):
        songs = self._getSongsOfDir(playlistDir)

#        songsSorted = sorted(songs, key=lambda x: (int(x.trackNumber), x.date))
        songs = sorted(songs, key=lambda x: (x.date, int(x.trackNumber)))

        logger.debug("all songs: %i", len(songs))

        counter=0
        for x in songs:
            logger.info(x)
            x:Mp3Info
            x.trackNumber = str(counter+1)
            counter+=1
            if isSave:
                self.metadataManager.setMetadataMp3Info(os.path.join(playlistDir, x.fileName), x)
            logger.info(x)
            logger.info("------------------------------")

    def addCoversToPlaylistSongs(self, playlistDir):
        playlistsPath = self.ytConfig.getPath()
        playlistFullPath = os.path.join(playlistsPath,playlistDir)
        songs = self._getSongsOfDir(playlistFullPath)
        if not songs:
            return
        for song in songs:
            song:Mp3Info
            if song.website is None:
                logger.warning("Song %s doesn't contain website", song.fileName)
                continue
            hash = song.website.split("/")[-1]
            self.metadataManager.addCoverOfYtMp3(os.path.join(playlistFullPath, song.fileName), hash)

    def removeCoversToPlaylistSongs(self, playlistDir):
        playlistsPath = self.ytConfig.getPath()
        playlistFullPath = os.path.join(playlistsPath,playlistDir)
        songs = self._getSongsOfDir(playlistFullPath)
        if not songs:
            return
        for song in songs:
            song:Mp3Info
            self.metadataManager.removeCoverOfMp3(os.path.join(playlistFullPath, song.fileName))

    def _changeTitleTemplate(self, path, songData):
        fileToCheck = os.path.join(path, "%s.mp3"%(songData.title))
        i=1
        titleFormat = '%(title)s.%(ext)s'
        while not (i>5 or not os.path.isfile(fileToCheck)):
            newFilenameWithNumber = "%s (%s).mp3"%(songData.title, str(i))
            titleFormat = '%(title)s ('+ str(i)+').%(ext)s'
            fileToCheck=os.path.join(path,newFilenameWithNumber)
            i+=1
        #self.metadataManager.showMp3Info(fileToCheck)
        if os.path.isfile(fileToCheck):
            logger.error("File %s exists!", fileToCheck)
            return
        logger.info("New version of file: %s", str(i))
        return titleFormat

    def _getDateTimeNowStr(self):
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")

    def _getNumberOfDownloadedSongs(self, path): # pragma: no cover
        filesInPlaylistDir = os.listdir(path)
        numberOfDownloadedSongs = 0
        for x in filesInPlaylistDir:
            if ".mp3" in x:
                numberOfDownloadedSongs +=1

        return numberOfDownloadedSongs

    def _isDirForPlaylists(self): # pragma: no cover
        if not os.path.isdir(self.ytConfig.getPath()):
            logger.error("wrong path for playlists")
            return False
        return True


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
        downloadedFiles:list = yt.download_playlists()
        if len(downloadedFiles) > 0:
            logger.info("Downloaded songs:")
            for x in downloadedFiles:
                for y in x:
                    logger.info(y)
            logger.info("Updating playlists")
            playlistsCreator = PlaylistsManager(yt.ytConfig.getPath())
            updatedPlaylists = []
            for x in downloadedFiles:
                downloadedFile = x[0]
                playlistDir = downloadedFile.split("/")[-2]
                playlistsCreator.createPlaylist(playlistDir)
                updatedPlaylists.append(playlistDir)
            playlistsCreator.createTopOfMusic(30)
            playlistsCreator.createTopOfMusic(100)
            playlistsCreator.createTopOfMusic(200)


            folders=["imprezka","techno","Rock-Electronic","relaks","stare hity"]
            common = (set(folders) & set(updatedPlaylists))
            if len(common) > 0:
                playlistsCreator.createGroupOfPlaylists("trening", folders)

            folders=["relaks","chillout","spokojne-sad","cafe","positive chill","polskie hity","muzyka filmowa"]
            common = (set(folders) & set(updatedPlaylists))
            if len(common) > 0:
                playlistsCreator.createGroupOfPlaylists("praca", folders)

            folders=["Bachata","Bachata Dominikana","Kizomba","latino","Semba"]
            common = (set(folders) & set(updatedPlaylists))
            if len(common) > 0:
                playlistsCreator.createGroupOfPlaylists("taniec", folders)

    else:
        if args.mode is not None and args.playlistUpdate is not None:
            my_parser.error("choose only one purpose")
        if args.mode is not None:
            yt = YoutubeManager()
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
        if args.playlistUpdate is not None:
            yt = MediaServerDownloader(args.playlistUpdate)
            yt.updateMetadataForPlaylists()

if __name__ == "__main__": # pragma: no cover
    #logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG, filename="/tmp/youtubeLogs", filemode='w')
    #logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    logger = logging.getLogger(__name__)
    main()
    #yt = YoutubeManager(musicPath="/mnt/kingston/media/muzyka/Youtube list")
    #yt.setDateAccordingToTrackNumber("/tmp/music/techno", "https://www.youtube.com/playlist?list=PL6uhlddQJkfiC8LyEB92IEsBFlbBjxCj0")
    #yt.downloadPlaylistMp3("/tmp/music", "test2", "https://www.youtube.com/playlist?list=PL6uhlddQJkfig0OO1fsQA9ZbBvH35QViF")
    #yt.checkPlaylistStatus("https://www.youtube.com/playlist?list=PL6uhlddQJkfgHTfI_P_BaACTGN2Km_4Yk", "/mnt/kingston/media/muzyka/Youtube list/Bachata")

    #downloader = MediaServerDownloader("/etc/mediaserver/youtubedl.ini")
    #downloader.addCoversToPlaylistSongs("easyTest")
    #downloader.removeCoversToPlaylistSongs("easyTest")
    #downloader.setDateAccordingToTrackNumberAllPlaylists(6, False)
