import unittest
import unittest.mock as mock
from unittest.mock import MagicMock
from youtubedlWeb.Common.YoutubeManager import YoutubeManager, MediaServerDownloader
from youtubedlWeb.Common.YoutubeConfig import YoutubeConfig
from youtubedlWeb.Common.YoutubeTypes import PlaylistInfo, MediaFromPlaylist, MediaInfo, AudioData, VideoData, ResultOfDownload
from configparser import ConfigParser
from datetime import datetime, timedelta
import yt_dlp
import os
from yt_dlp import utils
import metadata_mp3
from metadata_mp3 import Mp3Info
import logging

class CustomConfigParser(ConfigParser):
    path = "/tmp/muzyka/Youtube list"
    playlist1Name = "relaks"
    playlist1Link = "http://youtube.com/relaks"

    playlist2Name = "chillout"
    playlist2Link = "http://youtube.com/chillout"

    numberOfPlaylists = 2

    def read(self, filename):
        self.read_string("[GLOBAL]\n"
                         "path = "+ self.path + "\n"+
                         "["+self.playlist1Name+"]\n"+
                         "name = "+self.playlist1Name+"\n"+
                         "link = "+self.playlist1Link+"\n"
                         "["+self.playlist2Name+"]\n"+
                         "name = "+self.playlist2Name+"\n"+
                         "link = "+self.playlist2Link+"\n")

    def setMockForRemoveSection(self, mock):
        self.remove_section = mock


class CustomConfigParserEmptyPath(ConfigParser):
    def read(self, filename):
        self.read_string("[relaks]\nname = relaks\nlink = http://youtube.com/relaks\n[chillout]\nname = chillout\nlink = http://youtube.com/chillout\n")


class YouTubeManagerConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.ytConfig = YoutubeConfig()

    def tearDown(self):
        pass

    def test_getPath(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        path = self.ytConfig.getPath()
        self.assertEqual(path, CustomConfigParser.path)

    @mock.patch.object(YoutubeConfig, "save")
    @mock.patch('configparser.ConfigParser.__setitem__')
    @mock.patch('configparser.ConfigParser.__getitem__')
    def test_setPath(self, mock_getItem, mock_setItem, mock_save):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        newPath = "/tmp/"

        self.ytConfig.setPath(newPath)

        mock_getItem.assert_has_calls([mock.call("GLOBAL"),
                                       mock.call().__setitem__('path', newPath)])
        self.assertEqual(mock_save.call_count, 1)

    @mock.patch.object(YoutubeConfig, "save")
    @mock.patch('configparser.ConfigParser.__setitem__')
    @mock.patch('configparser.ConfigParser.__getitem__')
    def test_setNewPath(self, mock_getItem, mock_setItem, mock_save):
        self.ytConfig.initialize("neverMind", CustomConfigParserEmptyPath())
        newPath = "/tmp/"

        self.ytConfig.setPath(newPath)

        mock_getItem.assert_has_calls([mock.call("GLOBAL"),
                                       mock.call().__setitem__('path', newPath)])
        self.assertEqual(mock_save.call_count, 1)

    def test_getPathFailed(self):
        self.ytConfig.initialize("neverMind", CustomConfigParserEmptyPath())
        path = self.ytConfig.getPath()
        self.assertEqual(path, None)

    def test_getPlaylists(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        playlists = self.ytConfig.getPlaylists()
        self.assertEqual(len(playlists), 2)
        self.assertEqual(playlists[0].name, CustomConfigParser.playlist1Name)
        self.assertEqual(playlists[0].link, CustomConfigParser.playlist1Link)

        self.assertEqual(playlists[1].name, CustomConfigParser.playlist2Name)
        self.assertEqual(playlists[1].link, CustomConfigParser.playlist2Link)

    def test_getPlaylistsName(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        playlists = self.ytConfig.getPlaylistsName()
        self.assertEqual(len(playlists), 2)
        self.assertEqual(playlists[0], CustomConfigParser.playlist1Name)
        self.assertEqual(playlists[1], CustomConfigParser.playlist2Name)

    def test_getUrlOfPaylist(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        url = self.ytConfig.getUrlOfPlaylist(CustomConfigParser.playlist1Name)
        self.assertEqual(url, CustomConfigParser.playlist1Link)

    def test_getUrlOfPlaylistWrongName(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        url = self.ytConfig.getUrlOfPlaylist("WrongPlaylistName")
        self.assertEqual(url, None)

    @mock.patch.object(YoutubeConfig, "save")
    @mock.patch('configparser.ConfigParser.__setitem__')
    @mock.patch('configparser.ConfigParser.__getitem__')
    @mock.patch('configparser.ConfigParser.read')
    def test_addPlaylist(self, mock_read, mock_getItem, mock_setItem, mock_save):
        newPlaylist = {"name":"disco", "link":"https://yt.com/disco"}
        self.ytConfig.initialize("neverMind")
        self.assertTrue(self.ytConfig.addPlaylist(newPlaylist))
        keys = list(newPlaylist.keys())
        values = list(newPlaylist.values())

        mock_getItem.assert_has_calls([
            mock.call(values[0]), mock.call().__setitem__(keys[0], values[0]),
            mock.call(values[0]), mock.call().__setitem__(keys[1], values[1])])
        self.assertEqual(mock_getItem.call_count, 2)

        mock_setItem.assert_has_calls([mock.call("disco",{})])
        self.assertEqual(mock_setItem.call_count, 1)

        self.assertEqual(mock_save.call_count, 1)
        self.assertEqual(mock_read.call_count, 1)

    @mock.patch.object(YoutubeConfig, "save")
    @mock.patch('configparser.ConfigParser.__setitem__')
    @mock.patch('configparser.ConfigParser.__getitem__')
    @mock.patch('configparser.ConfigParser.read')
    def test_addPlaylistWrongKeys(self, mock_read, mock_getItem, mock_setItem, mock_save):
        self.ytConfig.initialize("neverMind")
        newPlaylist = {"name1":"disco", "link":"https://yt.com/disco"}
        self.assertFalse(self.ytConfig.addPlaylist(newPlaylist))

        newPlaylist = {"name":"disco", "link2":"https://yt.com/disco"}
        self.assertFalse(self.ytConfig.addPlaylist(newPlaylist))

        newPlaylist = {"name3":"disco", "link3":"https://yt.com/disco"}
        self.assertFalse(self.ytConfig.addPlaylist(newPlaylist))

        self.assertEqual(mock_getItem.call_count, 0)
        self.assertEqual(mock_setItem.call_count, 0)
        self.assertEqual(mock_save.call_count, 0)
        self.assertEqual(mock_read.call_count, 0)

    @mock.patch('configparser.ConfigParser.remove_section')
    @mock.patch.object(YoutubeConfig, "save")
    def test_removePlaylist(self, mock_save, mock_removeSection):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        self.assertTrue(self.ytConfig.removePlaylist(CustomConfigParser.playlist1Name))
        self.assertEqual(mock_save.call_count, 1)
        self.assertEqual(mock_removeSection.call_count, 1)
        mock_removeSection.assert_called_once_with(CustomConfigParser.playlist1Name)

    @mock.patch.object(YoutubeConfig, "save")
    def test_removePlaylist2(self, mock_save):
        configParser = CustomConfigParser()
        removeSectionMock = mock.MagicMock()
        configParser.setMockForRemoveSection(removeSectionMock)

        self.ytConfig.initialize("neverMind", configParser)
        self.assertTrue(self.ytConfig.removePlaylist(CustomConfigParser.playlist1Name))
        self.assertEqual(mock_save.call_count, 1)
        removeSectionMock.assert_called_once_with(CustomConfigParser.playlist1Name)

    @mock.patch.object(YoutubeConfig, "save")
    def test_removePlaylistWrongName(self, mock_save):
        configParser = CustomConfigParser()
        removeSectionMock = mock.MagicMock()
        configParser.setMockForRemoveSection(removeSectionMock)

        self.ytConfig.initialize("neverMind", configParser)
        self.assertFalse(self.ytConfig.removePlaylist("wrongName"))
        self.assertEqual(mock_save.call_count, 0)
        self.assertEqual(removeSectionMock.call_count, 0)

class YoutubeDownloaderUtilsTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.ytManager = YoutubeManager()

    def test_verifyActualDateTime(self):
        now = datetime.now().strftime("%Y-%m-%d")

        self.assertEqual(self.ytManager._getDateTimeNowStr(), now)

class MediaServerDownloaderUtilsTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.ytManager = MediaServerDownloader("test.ini")

    def test_verifyActualDateTime(self):
        now = datetime.now()

        yesterday = now - timedelta(days=1)
        yesterdayStr = yesterday.strftime("%Y-%m-%d")
        self.assertEqual(self.ytManager._getDateTimeNowStr(), yesterdayStr)

class ResultOfDownloadTestCase(unittest.TestCase):
    def test_resultSuccess(self):
        data = ["data"]

        result = ResultOfDownload(data)

        self.assertTrue(result.IsSuccess())
        self.assertFalse(result.IsFailed())
        self.assertIsNone(result.error())
        self.assertListEqual(data, result.data())

    def test_resultFailed(self):
        error = "error"

        result = ResultOfDownload(error)

        self.assertFalse(result.IsSuccess())
        self.assertTrue(result.IsFailed())
        self.assertIsNone(result.data())
        self.assertEqual(result.error(), error)


class YoutubeTestParams():
    actualDate = "2020-05-05"

    ytDomain = "https://youtu.be/"

    musicPath = "/media/music"

    playlistName = "test_playlist"
    playlistNameAlbum = "YT test_playlist"

    playlistPath = musicPath+"/"+playlistName

    hash = "abcdefgh"
    website = ytDomain + hash

    empty  = ""

    artist = "artist_test"
    title  = "title_test"
    fileName = title + ".mp3"
    album  = "album_test"

    ytLink      = "https://www.youtube.com/watch?v=yqq3p-brlyc"

    playlistIndex1 = 1
    firstTitle     = "first_title"
    firstFilename  =  firstTitle+".mp3"
    firstArtist    = "first_artist"
    firstAlbum     = "first_album"
    firstAlbumArtist = "first_album_artist"
    firstUrl = "https://www.youtube.com/watch?v=1111"
    firstHash = "1111"
    firstWebsite = ytDomain+firstHash
    firstFilenameWithPath  = playlistPath + "/" + firstFilename

    playlistIndex2 = 2
    secondTitle    = "second_title"
    secondFilename = secondTitle+ ".mp3"
    secondArtist   = "second_artist"
    secondAlbum    = "second_album"
    secondAlbumArtist = "second_album_artist"
    secondUrl = "https://www.youtube.com/watch?v=2222"
    secondHash = "2222"
    secondWebsite = ytDomain+secondHash
    secondFilenameWithPath  = playlistPath + "/" + secondFilename

    playlistIndex3 = 3
    thirdTitle    = "third_title"
    thirdFilename = thirdTitle+".mp3"
    thirdArtist   = "third_artist"
    thirdAlbum    = "third_album"
    thirdAlbumArtist = "third_album_artist"
    thirdUrl = "https://www.youtube.com/watch?v=3333"
    thirdHash = "3333"
    thirdWebsite = ytDomain+thirdHash
    thirdFilenameWithPath  = playlistPath + "/" + thirdFilename

    playlistIndex4 = 4
    fourthTitle    = "fourth_title"
    fourthFilename = fourthTitle+".mp3"
    fourthArtist   = "fourth_artist"
    fourthAlbum    = "fourth_album"
    fourthAlbumArtist = "fourth_album_artist"
    fourthUrl = "https://www.youtube.com/watch?v=4444"
    fourthHash = "4444"
    fourthWebsite = ytDomain+fourthHash
    fourthFilenameWithPath  = playlistPath + "/" + fourthFilename

    playlistIndex5 = 5
    fifthTitle    = "fifth_title"
    fifthFilename = fifthTitle+".mp3"
    fifthArtist  = "fifth_artist"
    fifthAlbum    = "fifth_album"
    fifthAlbumArtist = "fifth_album_artist"
    fifthUrl = "https://www.youtube.com/watch?v=5555"
    fifthHash = "5555"
    fifthWebsite = ytDomain+fifthHash
    fifthFilenameWithPath  = playlistPath + "/" + fifthFilename

    playlistIndex6 = 6
    sixthTitle    = "sixth_title"
    sixthFilename = sixthTitle+".mp3"
    sixthArtist  = "sixth_artist"
    sixthAlbum    = "sixth_album"
    sixthAlbumArtist = "sixth_album_artist"
    sixthUrl = "https://www.youtube.com/watch?v=6666"
    sixthHash = "6666"
    sixthWebsite = ytDomain+sixthHash
    sixthFilenameWithPath  = playlistPath + "/" + sixthFilename


class YouTubeManagerDlTestCase(unittest.TestCase, YoutubeTestParams):
    videoPath = "/media/video"


    exceptionMessage = "failed download"
    exceptionErrorExpected = "download failed: "+exceptionMessage

    foundMp3File = YoutubeTestParams.musicPath+"/"+YoutubeTestParams.fileName

    ytMp3ArchiveFilename = "songsArchive.txt"

    ytPlaylistInfoResponse2 = {"title": "testPlaylist","entries":[{"playlist_name":"testPlaylist", "playlist_index":"1", "url":"https://www.youtube.com/watch?v=1111", "title":"firstTitle"},
                                                                     {"playlist_name":"testPlaylist", "playlist_index":"2", "url":"https://www.youtube.com/watch?v=2222", "title":"secondTitle"}]}
    ytMediaInfoResponse = {"original_url":YoutubeTestParams.ytLink, "title":"firstTitle", "title":"testTitle", "artist":"testArtist", "album":"testAlbum"}
    ytMp3DownloadResponse ={"title":YoutubeTestParams.title, "artist":YoutubeTestParams.artist, "album":YoutubeTestParams.album, "id":YoutubeTestParams.hash, "requested_downloads":[{'filepath':foundMp3File}]}
    ytMp3DownloadWithoutArtistResponse = {"title":YoutubeTestParams.title, "artist":YoutubeTestParams.empty, "album":YoutubeTestParams.album, "id":YoutubeTestParams.hash, "requested_downloads":[{'filepath':foundMp3File}]}
    ytEmptyPlaylist = {"title": YoutubeTestParams.playlistName, "entries":[{}, None]}

    numberOfSongs = 4
    extMp4 = "mp4"
    resolution360p = "360p"
    resolution720p = "720p"
    resolution4k   = "4k"
    ytDownloadVideoResponse={"title":YoutubeTestParams.title, "artist":YoutubeTestParams.artist, "ext":extMp4}

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.ytManager = YoutubeManager(videoPath=self.videoPath, musicPath=self.musicPath, mp3ArchiveFilename=self.ytMp3ArchiveFilename)
        self.ytManager._createDirIfNotExist = mock.MagicMock()
        self.ytManager.openFile = mock.MagicMock()
        self.ytManager._lookingForFile = mock.MagicMock()
        self.ytManager.isMusicClipArchived = mock.MagicMock()
        self.ytManager.isMusicClipArchived.configure_mock(return_value=False)
        self.ytManager._getDateTimeNowStr = mock.MagicMock()
        self.ytManager._getDateTimeNowStr.configure_mock(return_value=self.actualDate)
        self.ytManager._getSongsOfDir = mock.MagicMock()

    def checkPlaylist(self, playlist:PlaylistInfo, ytResponse):
        playlistName = ytResponse['title']
        expectedList = ytResponse['entries']

        self.assertEqual(playlist.playlistName, playlistName)
        self.assertEqual(len(playlist.listOfMedia), len(expectedList))

        list = playlist.listOfMedia

        for indexOfList in range(len(expectedList)):
            media:MediaFromPlaylist
            media = list[indexOfList]
            self.assertEqual(playlistName, expectedList[indexOfList]["playlist_name"])
            self.assertEqual(media.playlistIndex, int(expectedList[indexOfList]["playlist_index"]))
            self.assertEqual(media.title, expectedList[indexOfList]["title"])
            self.assertEqual(media.url, expectedList[indexOfList]["url"])

    def checkMediaInfo(self, mediaInfo:MediaInfo, ytResponse):
        self.assertEqual(mediaInfo.url, ytResponse["original_url"])
        self.assertEqual(mediaInfo.title, ytResponse["title"])
        self.assertEqual(mediaInfo.artist, ytResponse["artist"])
        self.assertEqual(mediaInfo.album, ytResponse["album"])

    def checkAudioData(self, audioData:AudioData, ytResponse):
        self.assertEqual(audioData.title, ytResponse["title"])
        if(len(ytResponse["artist"])>0):
            self.assertEqual(audioData.artist, ytResponse["artist"])
            fileName = self.musicPath+audioData.artist + " - " + audioData.title + ".mp3"
        else:
            self.assertEqual(audioData.artist, self.empty)
            self.assertEqual(ytResponse["artist"], "")
            fileName = self.musicPath+audioData.title + ".mp3"

        if(len(ytResponse["album"])>0):
            self.assertEqual(audioData.album, ytResponse["album"])
        else:
            self.assertEqual(audioData.album, None)
            self.assertEqual(ytResponse["album"], self.empty)

    def assertMp3Info(self, actual:Mp3Info, expected:Mp3Info):
        self.assertEqual(actual.fileName, expected.fileName)
        self.assertEqual(actual.title, expected.title)
        self.assertEqual(actual.artist, expected.artist)
        self.assertEqual(actual.albumArtist, expected.albumArtist)
        self.assertEqual(actual.album, expected.album)
        self.assertEqual(actual.trackNumber, expected.trackNumber)
        self.assertEqual(actual.website, expected.website)
        self.assertEqual(actual.date, expected.date)

    def assertMediaFromPlaylist(self, actual:MediaFromPlaylist, expected:MediaFromPlaylist):
        self.assertEqual(actual.playlistIndex, expected.playlistIndex)
        self.assertEqual(actual.title, expected.title)
        self.assertEqual(actual.url , expected.url)

    def assertMediaFromPlaylistAndMp3Info(self, mediaFromPlaylist:MediaFromPlaylist, mp3Info:Mp3Info):
        self.assertEqual(mediaFromPlaylist.title, mp3Info.title)
        hashMp3Info = mp3Info.website.split("/")[-1]
        hashMediaFromPlaylist = mediaFromPlaylist.url.split("v=")[-1]
        self.assertEqual(hashMp3Info, hashMediaFromPlaylist)

    def checkVideoData(self, data:VideoData, ytResponse, videoResolution):
        self.assertEqual(data.title, ytResponse["title"])
        self.assertEqual(data.path, self.videoPath+"/"+ytResponse["title"]+"_"+videoResolution+"."+ytResponse["ext"])

    def test_getMediaHash1(self):
        hash = self.ytManager.getMediaHashFromLink("https://www.youtube.com/watch?v=Lr4x3sCH7l0&list=PL6uhlddQJkfh4YsbxgPE70a6KeFOCDgG")
        self.assertEqual(hash, "Lr4x3sCH7l0")

    def test_getMediaHash2(self):
        hash = self.ytManager.getMediaHashFromLink("https://www.youtube.com/watch?v=Lr4x3sCH7l0")
        self.assertEqual(hash, "Lr4x3sCH7l0")

    def test_getMediaHash3(self):
        hash = self.ytManager.getMediaHashFromLink("https://www.youtube.com/Lr4x3sCH7l0")
        self.assertIsNone(hash)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getPlaylistInfo(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=self.ytPlaylistInfoResponse2)

        result = self.ytManager.getPlaylistInfo(self.ytLink)

        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertTrue(result.IsSuccess())
        self.checkPlaylist(result.data(), self.ytPlaylistInfoResponse2)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getPlaylistInfoEmptyResult(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=None)

        result = self.ytManager.getPlaylistInfo(self.ytLink)

        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getPlaylistInfoEmptyEntries(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=self.ytEmptyPlaylist)

        result = self.ytManager.getPlaylistInfo(self.ytLink)

        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_getPlaylistInfoException(self, mock_extractInfo):
        result = self.ytManager.getPlaylistInfo(self.ytLink)

        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), self.exceptionErrorExpected)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getMediaInfo(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=self.ytMediaInfoResponse)

        result = self.ytManager.getMediaInfo(self.ytLink)
        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertTrue(result.IsSuccess())
        self.checkMediaInfo(result.data(), self.ytMediaInfoResponse)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getMediaInfoEmptyResult(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=None)

        result = self.ytManager.getMediaInfo(self.ytLink)

        mock_extractInfo.assert_has_calls([mock.call(self.ytLink, download=False)])
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_getMediaInfoException(self, mock_extractInfo):
        result = self.ytManager.getMediaInfo(self.ytLink)

        mock_extractInfo.assert_has_calls([mock.call(self.ytLink, download=False)])
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), "failed download")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadata")
    @mock.patch.object(metadata_mp3.MetadataManager, "addCoverOfYtMp3")
    def test_downloadMP3(self, mock_cover, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadResponse)
        fileNameResult = "test.mp3"
        mock_metadata.configure_mock(return_value=fileNameResult)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        mock_cover.assert_called_once_with(fileNameResult, self.hash)
        mock_metadata.assert_called_with(os.path.join(self.musicPath, self.fileName), None, self.title, self.artist, self.album, None, self.website, self.actualDate)
        self.assertTrue(result.IsSuccess())
        self.checkAudioData(result.data(), self.ytMp3DownloadResponse)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadata", return_value=None)
    @mock.patch.object(metadata_mp3.MetadataManager, "addCoverOfYtMp3")
    def test_downloadMP3_failedWithModyfiMetadata(self, mock_cover, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadResponse)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        mock_cover.assert_not_called()
        mock_metadata.assert_called_with(os.path.join(self.musicPath, self.fileName), None, self.title, self.artist, self.album, None, self.website, self.actualDate)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadata")
    @mock.patch.object(metadata_mp3.MetadataManager, "addCoverOfYtMp3")
    def test_downloadMP3_without_artist(self, mock_cover, mock_metadata, mock_extract_info):
        fileNameResult = "test.mp3"
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadWithoutArtistResponse)
        mock_metadata.configure_mock(return_value=fileNameResult)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        mock_cover.assert_called_once_with(fileNameResult, self.hash)
        mock_metadata.assert_called_with(os.path.join(self.musicPath, self.fileName), None, self.title, self.empty, self.album, None, self.website, self.actualDate)
        self.assertTrue(result.IsSuccess())
        self.checkAudioData(result.data(), self.ytMp3DownloadWithoutArtistResponse)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_emptyReturn(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=None)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_downloadMP3Exception(self, mock_extract_info):
        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), self.exceptionErrorExpected)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_onlyMetadata(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadResponse)
        self.ytManager.isMusicClipArchived.configure_mock(return_value=True)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.ytManager._lookingForFile.assert_called_with(self.musicPath, self.title, self.artist)
        self.assertTrue(result.IsSuccess())
        data = result.data()
        self.checkAudioData(data, self.ytMp3DownloadResponse)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_downloadMP3_onlyMetadata_exception(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadResponse)
        self.ytManager.isMusicClipArchived.configure_mock(return_value=True)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), self.exceptionErrorExpected)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_downloadMP3_onlyMetadata_NoneResult(self, mock_extract_info):
        self.ytManager.isMusicClipArchived.configure_mock(return_value=True)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_onlyMetadata_FileNotFound(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadResponse)
        self.ytManager._lookingForFile.configure_mock(return_value=None)
        self.ytManager.isMusicClipArchived.configure_mock(return_value=True)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.ytManager._lookingForFile.assert_called_with(self.musicPath,self.title, self.artist)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_onlyMetadata_VeryLongTitle(self, mock_extract_info):
        titleLong = "title_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test test_test_test_test_test_test_test_test_test_test_test_test_test"
        titleLongExpected = "title_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test"
        ytMp3LongTitleDownloadResponse ={"title":titleLong, "artist":self.artist, "album":self.album, "id":self.hash}
        ytMp3LongTitleDownloadResponseExpected ={"title":titleLongExpected, "artist":self.artist, "album":self.album, "id":self.hash}

        mock_extract_info.configure_mock(return_value=ytMp3LongTitleDownloadResponse)
        self.ytManager.isMusicClipArchived.configure_mock(return_value=True)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.ytManager._lookingForFile.assert_called_with(self.musicPath, titleLongExpected, self.artist)
        self.assertTrue(result.IsSuccess())
        data = result.data()
        self.checkAudioData(data, ytMp3LongTitleDownloadResponseExpected)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadata")
    def test_downloadMP3PlaylistFast(self, mock_metadata:mock.MagicMock, mock_extract_info:mock.MagicMock):
        ytDownloadMp3PlaylistResponse = {"entries":[
            {'playlist_index': self.playlistIndex1,"title":self.firstTitle,  "artist":self.firstArtist, "album":self.firstAlbum, "id":self.firstHash},
            {'playlist_index': self.playlistIndex2,"title":self.secondTitle, "album": self.secondAlbum, "id":self.secondHash},
            {'playlist_index': self.playlistIndex3,"title":self.thirdTitle,  "artist":self.thirdArtist, "album":self.thirdAlbum, "id":self.thirdHash},
            {'playlist_index': self.playlistIndex4,"title":self.fourthTitle, "artist":self.fourthArtist, "album":self.fourthAlbum, "id":self.fourthHash}]}


        mock_extract_info.configure_mock(return_value=ytDownloadMp3PlaylistResponse)

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        self.ytManager._createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        mock_extract_info.assert_called_once_with(self.ytLink)
        self.assertEqual(mock_metadata.call_count, self.numberOfSongs)

        mock_metadata.assert_has_calls([mock.call(os.path.join(self.musicPath, self.playlistName, self.firstFilename),  self.playlistIndex1, self.firstTitle,  self.firstArtist,  self.firstAlbum,  self.playlistNameAlbum, self.firstWebsite,  self.actualDate),
                                        mock.call(os.path.join(self.musicPath, self.playlistName, self.secondFilename), self.playlistIndex2, self.secondTitle, self.empty,        self.secondAlbum, self.playlistNameAlbum, self.secondWebsite, self.actualDate),
                                        mock.call(os.path.join(self.musicPath, self.playlistName, self.thirdFilename),  self.playlistIndex3, self.thirdTitle,  self.thirdArtist,  self.thirdAlbum,  self.playlistNameAlbum, self.thirdWebsite,  self.actualDate),
                                        mock.call(os.path.join(self.musicPath, self.playlistName, self.fourthFilename), self.playlistIndex4, self.fourthTitle, self.fourthArtist, self.fourthAlbum, self.playlistNameAlbum, self.fourthWebsite, self.actualDate)])

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), self.numberOfSongs)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadata")
    def test_downloadMP3PlaylistFast_OneSongWithoutAlbum(self, mock_metadata:mock.MagicMock, mock_extract_info:mock.MagicMock):
        ytDownloadMp3PlaylistResponse = {"entries":[
            {'playlist_index': self.playlistIndex1,"title":self.firstTitle,  "artist":self.firstArtist, "album":self.firstAlbum, "id":self.firstHash},
            {'playlist_index': self.playlistIndex2,"title":self.secondTitle, "artist":self.secondArtist, "id":self.secondHash},
            {'playlist_index': self.playlistIndex3,"title":self.thirdTitle,  "artist":self.thirdArtist, "album":self.thirdAlbum, "id":self.thirdHash},
            {'playlist_index': self.playlistIndex4,"title":self.fourthTitle, "artist":self.fourthArtist, "album":self.fourthAlbum, "id":self.fourthHash}]}


        mock_extract_info.configure_mock(return_value=ytDownloadMp3PlaylistResponse)

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        self.ytManager._createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        mock_extract_info.assert_called_once_with(self.ytLink)
        self.assertEqual(mock_metadata.call_count, self.numberOfSongs)

        mock_metadata.assert_has_calls([mock.call(os.path.join(self.musicPath, self.playlistName, self.firstFilename),  self.playlistIndex1, self.firstTitle,  self.firstArtist,  self.firstAlbum,  self.playlistNameAlbum, self.firstWebsite,  self.actualDate),
                                        mock.call(os.path.join(self.musicPath, self.playlistName, self.secondFilename), self.playlistIndex2, self.secondTitle, self.secondArtist, self.empty,       self.playlistNameAlbum, self.secondWebsite, self.actualDate),
                                        mock.call(os.path.join(self.musicPath, self.playlistName, self.thirdFilename),  self.playlistIndex3, self.thirdTitle,  self.thirdArtist,  self.thirdAlbum,  self.playlistNameAlbum, self.thirdWebsite,  self.actualDate),
                                        mock.call(os.path.join(self.musicPath, self.playlistName, self.fourthFilename), self.playlistIndex4, self.fourthTitle, self.fourthArtist, self.fourthAlbum, self.playlistNameAlbum, self.fourthWebsite, self.actualDate)])

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), self.numberOfSongs)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistFastEmptyResult(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=None)

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager._createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistFastWrongResult(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"fakeData":[]})

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager._createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistFastEmptyEntries(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"entries":[{},None]})

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager._createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_downloadMP3PlaylistFastException(self, mock_extract_info):

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager._createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), self.exceptionErrorExpected)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_download360p(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytDownloadVideoResponse)

        result = self.ytManager.download_360p(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertTrue(result.IsSuccess())
        self.checkVideoData(result.data(), self.ytDownloadVideoResponse, self.resolution360p)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_download360pFailed(self, mock_extract_info):

        result = self.ytManager.download_360p(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_download720p(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytDownloadVideoResponse)

        result = self.ytManager.download_720p(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertTrue(result.IsSuccess())
        self.checkVideoData(result.data(), self.ytDownloadVideoResponse, self.resolution720p)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_download720pFailed(self, mock_extract_info):

        result = self.ytManager.download_720p(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_download4k(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytDownloadVideoResponse)

        result = self.ytManager.download_4k(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertTrue(result.IsSuccess())
        self.checkVideoData(result.data(), self.ytDownloadVideoResponse, self.resolution4k)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_download4kFailed(self, mock_extract_info):

        result = self.ytManager.download_4k(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_download4kFailedRaise(self, mock_extract_info):

        result = self.ytManager.download_4k(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), self.exceptionErrorExpected)


class MediaServerDownloaderTestCase(unittest.TestCase, YoutubeTestParams):

    numberOfSongs = 4
    ytDownloadMp3Response1 = {"title":YoutubeTestParams.firstTitle, "artist":YoutubeTestParams.firstArtist, "album":YoutubeTestParams.firstAlbum, "id":YoutubeTestParams.firstHash, "requested_downloads":[{'filepath': YoutubeTestParams.firstFilenameWithPath}]}
    ytDownloadMp3Response2 = {"title":YoutubeTestParams.secondTitle, "artist":YoutubeTestParams.secondArtist, "album":YoutubeTestParams.secondAlbum, "id":YoutubeTestParams.secondHash, "requested_downloads":[{'filepath':YoutubeTestParams.secondFilenameWithPath}]}
    ytDownloadMp3Response3 = {"title":YoutubeTestParams.thirdTitle, "artist":YoutubeTestParams.thirdArtist, "album":YoutubeTestParams.thirdAlbum, "id":YoutubeTestParams.thirdHash, "requested_downloads":[{'filepath':YoutubeTestParams.thirdFilenameWithPath}]}
    ytDownloadMp3Response4 = {"title":YoutubeTestParams.fourthTitle, "artist":YoutubeTestParams.fourthArtist, "album":YoutubeTestParams.fourthAlbum, "id":YoutubeTestParams.fourthHash, "requested_downloads":[{'filepath':YoutubeTestParams.fourthFilenameWithPath}]}

    ytPlaylistInfoResponse4 = {"title": YoutubeTestParams.playlistName,"entries":[{"playlist_name":YoutubeTestParams.playlistName, "playlist_index":YoutubeTestParams.playlistIndex1, "url":YoutubeTestParams.firstUrl, "title":YoutubeTestParams.firstTitle},
                                                                {"playlist_name":YoutubeTestParams.playlistName, "playlist_index":YoutubeTestParams.playlistIndex2, "url":YoutubeTestParams.secondUrl, "title":YoutubeTestParams.secondTitle},
                                                                {"playlist_name":YoutubeTestParams.playlistName, "playlist_index":YoutubeTestParams.playlistIndex3, "url":YoutubeTestParams.thirdUrl, "title":YoutubeTestParams.thirdTitle},
                                                                {"playlist_name":YoutubeTestParams.playlistName, "playlist_index":YoutubeTestParams.playlistIndex4, "url":YoutubeTestParams.fourthUrl, "title":YoutubeTestParams.fourthTitle}
                                                                ]}

    numberOfArchiveSongs = 5

    mp3InfoTrack1 = Mp3Info(str(YoutubeTestParams.firstArtist + " - " + YoutubeTestParams.firstTitle+".mp3"), YoutubeTestParams.firstTitle, YoutubeTestParams.firstArtist, YoutubeTestParams.firstAlbum, YoutubeTestParams.firstAlbumArtist, str(YoutubeTestParams.playlistIndex1), YoutubeTestParams.firstWebsite, YoutubeTestParams.actualDate)
    mp3InfoTrack2 = Mp3Info(str(YoutubeTestParams.secondArtist + " - " + YoutubeTestParams.secondTitle+".mp3"), YoutubeTestParams.secondTitle, YoutubeTestParams.secondArtist, YoutubeTestParams.secondAlbum, YoutubeTestParams.secondAlbumArtist, str(YoutubeTestParams.playlistIndex2), YoutubeTestParams.secondWebsite, YoutubeTestParams.actualDate)
    mp3InfoTrack3 = Mp3Info(str(YoutubeTestParams.thirdArtist + " - " + YoutubeTestParams.thirdTitle+".mp3"), YoutubeTestParams.thirdTitle, YoutubeTestParams.thirdArtist, YoutubeTestParams.thirdAlbum, YoutubeTestParams.thirdAlbumArtist, str(YoutubeTestParams.playlistIndex3), YoutubeTestParams.thirdWebsite, YoutubeTestParams.actualDate)
    mp3InfoTrack4 = Mp3Info(str(YoutubeTestParams.fourthArtist + " - " + YoutubeTestParams.fourthTitle+".mp3"), YoutubeTestParams.fourthTitle, YoutubeTestParams.fourthArtist, YoutubeTestParams.fourthAlbum, YoutubeTestParams.fourthAlbumArtist, str(YoutubeTestParams.playlistIndex4), YoutubeTestParams.fourthWebsite, YoutubeTestParams.actualDate)
    listOfMp3Info4 = [mp3InfoTrack1, mp3InfoTrack2, mp3InfoTrack3, mp3InfoTrack4]

    extractRequest = {'format': 'bestaudio/best', 'addmetadata': True, 'logger': None, 'outtmpl': '/media/music/test_playlist/%(title)s.%(ext)s', 'download_archive': '/media/music/test_playlist/downloaded_songs.txt', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}], 'ignoreerrors': False, 'continue': True, 'no-overwrites': True, 'noplaylist': True, 'quiet': True}
    getPlaylistInfoRequest={'format': 'best/best', 'logger': None, 'extract_flat': 'in_playlist', 'addmetadata': True, 'ignoreerrors': False, 'quiet': True}
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.ytManager = MediaServerDownloader("test.ini")
        self.ytManager.ytConfig.initialize("test.ini", CustomConfigParser())
        self.ytManager._createDirIfNotExist = mock.MagicMock()
        self.ytManager.openFile = mock.MagicMock()
        self.ytManager._lookingForFile = mock.MagicMock()
        self.ytManager.isMusicClipArchived = mock.MagicMock()
        self.ytManager.isMusicClipArchived.configure_mock(return_value=False)
        self.ytManager._getNumberOfDownloadedSongs = mock.MagicMock()
        self.ytManager._getDateTimeNowStr = mock.MagicMock()
        self.ytManager._getDateTimeNowStr.configure_mock(return_value=self.actualDate)
        self.ytManager._getNumberOfDownloadedSongs.configure_mock(return_value=self.numberOfArchiveSongs)
        self.ytManager._getSongsOfDir = mock.MagicMock()

    def checkPlaylist(self, playlist:PlaylistInfo, ytResponse):
        playlistName = ytResponse['title']
        expectedList = ytResponse['entries']

        self.assertEqual(playlist.playlistName, playlistName)
        self.assertEqual(len(playlist.listOfMedia), len(expectedList))

        list = playlist.listOfMedia

        for indexOfList in range(len(expectedList)):
            media:MediaFromPlaylist
            media = list[indexOfList]
            self.assertEqual(playlistName, expectedList[indexOfList]["playlist_name"])
            self.assertEqual(media.playlistIndex, int(expectedList[indexOfList]["playlist_index"]))
            self.assertEqual(media.title, expectedList[indexOfList]["title"])
            self.assertEqual(media.url, expectedList[indexOfList]["url"])

    def checkMediaInfo(self, mediaInfo:MediaInfo, ytResponse):
        self.assertEqual(mediaInfo.url, ytResponse["original_url"])
        self.assertEqual(mediaInfo.title, ytResponse["title"])
        self.assertEqual(mediaInfo.artist, ytResponse["artist"])
        self.assertEqual(mediaInfo.album, ytResponse["album"])

    def checkAudioData(self, audioData:AudioData, ytResponse):
        self.assertEqual(audioData.title, ytResponse["title"])
        if(len(ytResponse["artist"])>0):
            self.assertEqual(audioData.artist, ytResponse["artist"])
            fileName = self.musicPath+audioData.artist + " - " + audioData.title + ".mp3"
        else:
            self.assertEqual(audioData.artist, self.empty)
            self.assertEqual(ytResponse["artist"], "")
            fileName = self.musicPath+audioData.title + ".mp3"

        if(len(ytResponse["album"])>0):
            self.assertEqual(audioData.album, ytResponse["album"])
        else:
            self.assertEqual(audioData.album, None)
            self.assertEqual(ytResponse["album"], self.empty)

    def assertMp3Info(self, actual:Mp3Info, expected:Mp3Info):
        self.assertEqual(actual.fileName, expected.fileName)
        self.assertEqual(actual.title, expected.title)
        self.assertEqual(actual.artist, expected.artist)
        self.assertEqual(actual.albumArtist, expected.albumArtist)
        self.assertEqual(actual.album, expected.album)
        self.assertEqual(actual.trackNumber, expected.trackNumber)
        self.assertEqual(actual.website, expected.website)
        self.assertEqual(actual.date, expected.date)

    def assertMediaFromPlaylist(self, actual:MediaFromPlaylist, expected:MediaFromPlaylist):
        self.assertEqual(actual.playlistIndex, expected.playlistIndex)
        self.assertEqual(actual.title, expected.title)
        self.assertEqual(actual.url , expected.url)

    def assertMediaFromPlaylistAndMp3Info(self, mediaFromPlaylist:MediaFromPlaylist, mp3Info:Mp3Info):
        self.assertEqual(mediaFromPlaylist.title, mp3Info.title)
        hashMp3Info = mp3Info.website.split("/")[-1]
        hashMediaFromPlaylist = mediaFromPlaylist.url.split("v=")[-1]
        self.assertEqual(hashMp3Info, hashMediaFromPlaylist)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_checkPlaylistStatus(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytPlaylistInfoResponse4)
        self.ytManager._getSongsOfDir.configure_mock(return_value=self.listOfMp3Info4)

        localFilesMissed, ytSongsMissed = self.ytManager.checkPlaylistStatus(self.musicPath+"/"+self.playlistName, self.playlistName, self.ytLink)
        self.assertEqual(len(localFilesMissed), 0)
        self.assertEqual(len(ytSongsMissed), 0)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_checkPlaylistStatus_missedLocally(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytPlaylistInfoResponse4)
        self.ytManager._getSongsOfDir.configure_mock(return_value=[self.mp3InfoTrack2, self.mp3InfoTrack3, self.mp3InfoTrack4])

        localFilesMissed, ytSongsMissed = self.ytManager.checkPlaylistStatus(self.musicPath+"/"+self.playlistName, self.playlistName, self.ytLink)
        self.assertEqual(len(localFilesMissed), 0)
        self.assertEqual(len(ytSongsMissed), 1)

        self.assertMediaFromPlaylistAndMp3Info(ytSongsMissed[0], self.mp3InfoTrack1)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_checkPlaylistStatus_missedYt(self, mock_extract_info):
        ytPlaylistInfoResponse3 = {"title": self.playlistName,"entries":[{"playlist_name":self.playlistName, "playlist_index":self.playlistIndex2, "url":self.secondUrl, "title":self.secondTitle},
                                                                         {"playlist_name":self.playlistName, "playlist_index":self.playlistIndex3, "url":self.thirdUrl, "title":self.thirdTitle},
                                                                         {"playlist_name":self.playlistName, "playlist_index":self.playlistIndex4, "url":self.fourthUrl, "title":self.fourthTitle}
                                                                         ]}

        mock_extract_info.configure_mock(return_value=ytPlaylistInfoResponse3)
        self.ytManager._getSongsOfDir.configure_mock(return_value=[self.mp3InfoTrack1, self.mp3InfoTrack2, self.mp3InfoTrack3, self.mp3InfoTrack4])

        localFilesMissed, ytSongsMissed = self.ytManager.checkPlaylistStatus(self.musicPath+"/"+self.playlistName, self.playlistName, self.ytLink)
        self.assertEqual(len(localFilesMissed), 1)
        self.assertEqual(len(ytSongsMissed), 0)


        ytMediaFromPLaylist1 = MediaFromPlaylist(self.playlistIndex1, self.firstUrl, self.firstTitle)
        self.assertMediaFromPlaylistAndMp3Info(ytMediaFromPLaylist1, localFilesMissed[0])

    @mock.patch.object(metadata_mp3.MetadataManager, "setMetadataMp3Info")
    def test_updateTrackNumber(self, mock_setMetadataMp3Info):
        self.ytManager._getSongsOfDir.configure_mock(return_value=[self.mp3InfoTrack1, self.mp3InfoTrack2])

        self.ytManager.updateTrackNumber(str(self.musicPath+"/"+self.playlistName),self.ytLink,True)

        mock_setMetadataMp3Info.assert_has_calls([mock.call(str(self.musicPath+"/"+self.playlistName+"/"+self.mp3InfoTrack1.fileName),self.mp3InfoTrack1),
                                                  mock.call(str(self.musicPath+"/"+self.playlistName+"/"+self.mp3InfoTrack2.fileName),self.mp3InfoTrack2)])

    @mock.patch.object(metadata_mp3.MetadataManager, "setMetadataMp3Info")
    def test_updateTrackNumber_reverse(self, mock_setMetadataMp3Info):
        self.ytManager._getSongsOfDir.configure_mock(return_value=[self.mp3InfoTrack2, self.mp3InfoTrack1])

        self.ytManager.updateTrackNumber(str(self.musicPath+"/"+self.playlistName),self.ytLink,True)

        mock_setMetadataMp3Info.assert_has_calls([mock.call(str(self.musicPath+"/"+self.playlistName+"/"+self.mp3InfoTrack1.fileName),self.mp3InfoTrack1),
                                                  mock.call(str(self.musicPath+"/"+self.playlistName+"/"+self.mp3InfoTrack2.fileName),self.mp3InfoTrack2)])

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToPlaylist")
    def test_downloadMP3Playlist(self, mock_metadata:mock.MagicMock, mock_extract_info:mock.MagicMock):
        mock_extract_info.configure_mock(side_effect=[self.ytPlaylistInfoResponse4, self.ytDownloadMp3Response1,
                                                      self.ytDownloadMp3Response2, self.ytDownloadMp3Response3, self.ytDownloadMp3Response4])


        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)


        self.assertEqual(self.ytManager._createDirIfNotExist.call_count, 5)
        self.ytManager._createDirIfNotExist.assert_called_with(self.musicPath+"/"+self.playlistName)
        self.assertEqual(mock_extract_info.call_count, 5)
        mock_extract_info.assert_has_calls([mock.call(self.ytLink, download=False),
                                            mock.call(self.firstUrl),
                                            mock.call(self.secondUrl),
                                            mock.call(self.thirdUrl),
                                            mock.call(self.fourthUrl),
                                            ])

        self.assertEqual(mock_metadata.call_count, self.numberOfSongs)
        mock_metadata.assert_has_calls([mock.call(self.musicPath, self.playlistName, self.firstFilename,  str(self.numberOfArchiveSongs+1), self.firstTitle,  self.firstArtist,  self.firstAlbum,  self.firstWebsite,  self.actualDate),
                                        mock.call(self.musicPath, self.playlistName, self.secondFilename, str(self.numberOfArchiveSongs+2), self.secondTitle, self.secondArtist, self.secondAlbum, self.secondWebsite, self.actualDate),
                                        mock.call(self.musicPath, self.playlistName, self.thirdFilename,  str(self.numberOfArchiveSongs+3), self.thirdTitle,  self.thirdArtist,  self.thirdAlbum,  self.thirdWebsite,  self.actualDate),
                                        mock.call(self.musicPath, self.playlistName, self.fourthFilename, str(self.numberOfArchiveSongs+4), self.fourthTitle, self.fourthArtist, self.fourthAlbum, self.fourthWebsite, self.actualDate)])

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), self.numberOfSongs)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "addCoverOfYtMp3")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadata")
    @mock.patch.object(yt_dlp.utils, "sanitize_filename")
    def test_downloadMP3Playlist(self, mock_sanitize, mock_metadata:mock.MagicMock, mock_cover:mock.MagicMock, mock_extract_info:mock.MagicMock):
        mock_extract_info.configure_mock(side_effect=[self.ytPlaylistInfoResponse4, self.ytDownloadMp3Response1,
                                                      self.ytDownloadMp3Response2, self.ytDownloadMp3Response3, self.ytDownloadMp3Response4])

        mock_sanitize.configure_mock(side_effect=[self.firstTitle,  self.firstArtist,
                                                  self.secondTitle, self.secondArtist,
                                                  self.thirdTitle,  self.thirdArtist,
                                                  self.fourthTitle, self.fourthArtist])

        mock_metadata.configure_mock(side_effect=[self.firstFilenameWithPath,
                                                  self.secondFilenameWithPath,
                                                  self.thirdFilenameWithPath,
                                                  self.fourthFilenameWithPath])

        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)


        self.assertEqual(self.ytManager._createDirIfNotExist.call_count, 5)
        self.ytManager._createDirIfNotExist.assert_called_with(self.musicPath+"/"+self.playlistName)
        self.assertEqual(mock_extract_info.call_count, 5)
        mock_extract_info.assert_has_calls([mock.call(self.ytLink, download=False),
                                            mock.call(self.firstUrl),
                                            mock.call(self.secondUrl),
                                            mock.call(self.thirdUrl),
                                            mock.call(self.fourthUrl),
                                            ])
        self.assertEqual(mock_sanitize.call_count, 8)

        self.assertEqual(mock_metadata.call_count, self.numberOfSongs)
        mock_metadata.assert_has_calls([mock.call(os.path.join(self.playlistPath, self.firstFilename),  str(self.numberOfArchiveSongs+1), self.firstTitle,  self.firstArtist,  self.firstAlbum, '', self.firstWebsite,  self.actualDate),
                                        mock.call(os.path.join(self.playlistPath, self.secondFilename), str(self.numberOfArchiveSongs+2), self.secondTitle, self.secondArtist, self.secondAlbum, '', self.secondWebsite, self.actualDate),
                                        mock.call(os.path.join(self.playlistPath, self.thirdFilename),  str(self.numberOfArchiveSongs+3), self.thirdTitle,  self.thirdArtist,  self.thirdAlbum, '', self.thirdWebsite,  self.actualDate),
                                        mock.call(os.path.join(self.playlistPath, self.fourthFilename), str(self.numberOfArchiveSongs+4), self.fourthTitle, self.fourthArtist, self.fourthAlbum, '', self.fourthWebsite, self.actualDate)])
        self.assertEqual(mock_cover.call_count, 4)
        mock_cover.assert_has_calls([mock.call(self.firstFilenameWithPath, self.firstHash),
                                    mock.call(self.secondFilenameWithPath, self.secondHash),
                                    mock.call(self.thirdFilenameWithPath, self.thirdHash),
                                    mock.call(self.fourthFilenameWithPath, self.fourthHash)])

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), self.numberOfSongs)

    @mock.patch("yt_dlp.YoutubeDL")
    @mock.patch.object(metadata_mp3.MetadataManager, "addCoverOfYtMp3")
    @mock.patch("os.path.isfile")
    def test_downloadMP3Playlist_theSameTitle(self, mock_isFile:mock.MagicMock, mock_cover:mock.MagicMock, mock_yt:mock.MagicMock):
        mock_ydl_instance = MagicMock()
        mock_yt.return_value = mock_ydl_instance

        ytDownloadMp3Response3SecondTitle = {"title":self.secondTitle, "artist":self.secondArtist, "album":self.secondAlbum, "id":self.thirdHash, "requested_downloads":[{'filepath':self.secondFilenameWithPath.replace(".mp3", " (1).mp3")}]}
        mock_ydl_instance.extract_info.side_effect=[self.ytPlaylistInfoResponse4, self.ytDownloadMp3Response1,
                                                    self.ytDownloadMp3Response2, ytDownloadMp3Response3SecondTitle, self.ytDownloadMp3Response4]  # Zwracana wartość

        mock_isFile.configure_mock(side_effect=[False,
                                                False,
                                                True, True, False, # third song with the same title
                                                False,
                                                False])

        self.ytManager.addMetadataToPlaylist = mock.MagicMock()
        self.ytManager.addMetadataToPlaylist.configure_mock(side_effect=[self.firstFilenameWithPath,
                                                  self.secondFilenameWithPath,
                                                  self.secondFilenameWithPath.replace(".mp3", " (1).mp3"),
                                                  self.fourthFilenameWithPath])


        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)


        self.ytManager._createDirIfNotExist.assert_called_with(self.musicPath+"/"+self.playlistName)
        extractRequestNewTitle = self.extractRequest.copy()
        extractRequestNewTitle['outtmpl'] = self.musicPath+"/"+self.playlistName+"/"+"%(title)s (1).%(ext)s"

        self.assertEqual(self.ytManager._createDirIfNotExist.call_count, 5)

        mock_yt.assert_has_calls([mock.call(self.getPlaylistInfoRequest),
            mock.call(self.extractRequest),
            mock.call(self.extractRequest),
            mock.call(extractRequestNewTitle),
            mock.call(self.extractRequest),
            ], any_order=True)

        self.assertEqual(mock_yt.call_count, 5)

        self.assertEqual(mock_cover.call_count, 4)
        mock_cover.assert_has_calls([mock.call(self.firstFilenameWithPath, self.firstHash),
                                    mock.call(self.secondFilenameWithPath, self.secondHash),
                                    mock.call(self.secondFilenameWithPath.replace(".mp3", " (1).mp3"), self.thirdHash),
                                    mock.call(self.fourthFilenameWithPath, self.fourthHash)])

        self.assertEqual(mock_ydl_instance.extract_info.call_count, 5)
        mock_ydl_instance.extract_info.assert_has_calls([
            mock.call(self.ytLink, download=False),
            mock.call(self.firstUrl),
            mock.call(self.secondUrl),
            mock.call(self.thirdUrl),
            mock.call(self.fourthUrl)
        ])

        self.assertEqual(self.ytManager.addMetadataToPlaylist.call_count, self.numberOfSongs)
        self.ytManager.addMetadataToPlaylist.assert_has_calls([
            mock.call(self.musicPath, self.playlistName, self.firstFilename,                               str(self.numberOfArchiveSongs+1), self.firstTitle,  self.firstArtist,  self.firstAlbum,  self.firstHash),
            mock.call(self.musicPath, self.playlistName, self.secondFilename,                              str(self.numberOfArchiveSongs+2), self.secondTitle, self.secondArtist, self.secondAlbum, self.secondHash),
            mock.call(self.musicPath, self.playlistName, self.secondFilename.replace(".mp3", " (1).mp3"),  str(self.numberOfArchiveSongs+3), self.secondTitle, self.secondArtist, self.secondAlbum,  self.thirdHash),
            mock.call(self.musicPath, self.playlistName, self.fourthFilename,                              str(self.numberOfArchiveSongs+4), self.fourthTitle, self.fourthArtist, self.fourthAlbum, self.fourthHash)])

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), self.numberOfSongs)

    @mock.patch("yt_dlp.YoutubeDL")
    @mock.patch.object(metadata_mp3.MetadataManager, "addCoverOfYtMp3")
    @mock.patch("os.path.isfile")
    def test_downloadMP3Playlist_theSameTitleFiveTimes(self, mock_isFile:mock.MagicMock, mock_cover:mock.MagicMock, mock_yt:mock.MagicMock):
        mock_ydl_instance = MagicMock()
        mock_yt.return_value = mock_ydl_instance
        ytPlaylistInfoResponse5 = {"title": self.playlistName,"entries":[{"playlist_name":self.playlistName, "playlist_index":self.playlistIndex1, "url":self.firstUrl, "title":self.firstTitle},
                                                                {"playlist_name":self.playlistName, "playlist_index":self.playlistIndex2, "url":self.secondUrl, "title":self.secondTitle},
                                                                {"playlist_name":self.playlistName, "playlist_index":self.playlistIndex3, "url":self.thirdUrl, "title":self.thirdTitle},
                                                                {"playlist_name":self.playlistName, "playlist_index":self.playlistIndex4, "url":self.fourthUrl, "title":self.fourthTitle},
                                                                {"playlist_name":self.playlistName, "playlist_index":self.playlistIndex5, "url":self.fifthUrl, "title":self.fifthTitle}
                                                                ]}

        mock_ydl_instance.extract_info.side_effect=[ytPlaylistInfoResponse5]
        sideEffectOfIsFileMock = [True, True, False, False,
                                  True, True, True,  False, False,
                                  True, True, True,  True,  False, False,
                                  True, True, True,  True,  True,  False, False,
                                  True, True, True,  True,  True,  True, False
                                  ]
        mock_isFile.configure_mock(side_effect=sideEffectOfIsFileMock)
        self.ytManager._download_mp3 = mock.MagicMock()
        ytResultSong1 = ResultOfDownload(AudioData(str(self.musicPath+"/"+self.playlistName+"/"+
                                                   self.firstTitle+" (1).mp3"),
                                                   self.firstTitle,
                                                   self.firstHash,
                                                   self.firstArtist,
                                                   self.firstAlbumArtist))
        ytResultSong2 = ResultOfDownload(AudioData(str(self.musicPath+"/"+self.playlistName+"/"+
                                                   self.secondTitle+" (2).mp3"),
                                                   self.secondTitle,
                                                   self.secondHash,
                                                   self.secondArtist,
                                                   self.secondAlbumArtist))
        ytResultSong3 = ResultOfDownload(AudioData(str(self.musicPath+"/"+self.playlistName+"/"+
                                                   self.thirdTitle+" (3).mp3"),
                                                   self.thirdTitle,
                                                   self.thirdHash,
                                                   self.thirdArtist,
                                                   self.thirdAlbumArtist))
        ytResultSong4 = ResultOfDownload(AudioData(str(self.musicPath+"/"+self.playlistName+"/"+
                                                   self.fourthTitle+" (4).mp3"),
                                                   self.fourthTitle,
                                                   self.fourthHash,
                                                   self.fourthArtist,
                                                   self.fourthAlbumArtist))
        ytResultSong5 = ResultOfDownload(AudioData(str(self.musicPath+"/"+self.playlistName+"/"+
                                                   self.fifthTitle+" (5).mp3"),
                                                   self.fifthTitle,
                                                   self.fifthHash,
                                                   self.fifthArtist,
                                                   self.fifthAlbumArtist))
        self.ytManager._download_mp3.configure_mock(side_effect=[ytResultSong1, ytResultSong2, ytResultSong3, ytResultSong4, ytResultSong5])
        self.ytManager.addMetadataToPlaylist = mock.MagicMock()
        self.ytManager.addMetadataToPlaylist.configure_mock(side_effect=[
                                                  self.firstFilenameWithPath.replace(".mp3", " (1).mp3"),
                                                  self.firstFilenameWithPath.replace(".mp3", " (2).mp3"),
                                                  self.firstFilenameWithPath.replace(".mp3", " (3).mp3"),
                                                  self.firstFilenameWithPath.replace(".mp3", " (4).mp3"),
                                                  self.firstFilenameWithPath.replace(".mp3", " (5).mp3"),
                                                  ])


        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)


        self.assertEqual(self.ytManager._createDirIfNotExist.call_count, 1)
        self.ytManager._createDirIfNotExist.assert_called_with(self.musicPath+"/"+self.playlistName)
        self.assertEqual(mock_isFile.call_count, len(sideEffectOfIsFileMock))
        self.ytManager._download_mp3.assert_has_calls([
            mock.call(self.firstUrl,  self.musicPath+"/"+self.playlistName, '%(title)s (1).%(ext)s'),
            mock.call(self.secondUrl, self.musicPath+"/"+self.playlistName, '%(title)s (2).%(ext)s'),
            mock.call(self.thirdUrl,  self.musicPath+"/"+self.playlistName, '%(title)s (3).%(ext)s'),
            mock.call(self.fourthUrl, self.musicPath+"/"+self.playlistName, '%(title)s (4).%(ext)s'),
            mock.call(self.fifthUrl,  self.musicPath+"/"+self.playlistName, '%(title)s (5).%(ext)s')
        ])

        mock_yt.assert_has_calls([mock.call(self.getPlaylistInfoRequest)])

        self.assertEqual(mock_yt.call_count, 1)
        self.assertEqual(mock_ydl_instance.extract_info.call_count, 1)
        mock_ydl_instance.extract_info.assert_has_calls([
            mock.call(self.ytLink, download=False)
        ])

        self.assertEqual(mock_cover.call_count, 5)
        mock_cover.assert_has_calls([
                                    mock.call(self.firstFilenameWithPath.replace(".mp3", " (1).mp3"), self.firstHash),
                                    mock.call(self.firstFilenameWithPath.replace(".mp3", " (2).mp3"), self.secondHash),
                                    mock.call(self.firstFilenameWithPath.replace(".mp3", " (3).mp3"), self.thirdHash),
                                    mock.call(self.firstFilenameWithPath.replace(".mp3", " (4).mp3"), self.fourthHash),
                                    mock.call(self.firstFilenameWithPath.replace(".mp3", " (5).mp3"), self.fifthHash)
                                              ])

        self.assertEqual(self.ytManager.addMetadataToPlaylist.call_count, 5)
        self.ytManager.addMetadataToPlaylist.assert_has_calls([
            mock.call(self.musicPath, self.playlistName, self.firstFilename.replace(".mp3", " (1).mp3"),  str(self.numberOfArchiveSongs+1), self.firstTitle,  self.firstArtist,  self.firstAlbumArtist,  self.firstHash),
            mock.call(self.musicPath, self.playlistName, self.secondFilename.replace(".mp3", " (2).mp3"), str(self.numberOfArchiveSongs+2), self.secondTitle, self.secondArtist, self.secondAlbumArtist, self.secondHash),
            mock.call(self.musicPath, self.playlistName, self.thirdFilename.replace(".mp3", " (3).mp3"),  str(self.numberOfArchiveSongs+3), self.thirdTitle,  self.thirdArtist,  self.thirdAlbumArtist,  self.thirdHash),
            mock.call(self.musicPath, self.playlistName, self.fourthFilename.replace(".mp3", " (4).mp3"), str(self.numberOfArchiveSongs+4), self.fourthTitle, self.fourthArtist, self.fourthAlbumArtist, self.fourthHash),
            mock.call(self.musicPath, self.playlistName, self.fifthFilename.replace(".mp3", " (5).mp3"),  str(self.numberOfArchiveSongs+5), self.fifthTitle,  self.fifthArtist,  self.fifthAlbumArtist,  self.fifthHash)
            ])

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), 5)

    @mock.patch("yt_dlp.YoutubeDL")
    @mock.patch.object(metadata_mp3.MetadataManager, "addCoverOfYtMp3")
    @mock.patch("os.path.isfile")
    def test_downloadMP3Playlist_theSameTitleSixTimes(self, mock_isFile:mock.MagicMock, mock_cover:mock.MagicMock, mock_yt:mock.MagicMock):
        mock_ydl_instance = MagicMock()
        mock_yt.return_value = mock_ydl_instance
        ytPlaylistInfoResponse6 = {"title": self.playlistName,"entries":[{"playlist_name":self.playlistName, "playlist_index":self.playlistIndex1, "url":self.firstUrl, "title":self.firstTitle},
                                                                {"playlist_name":self.playlistName, "playlist_index":self.playlistIndex2, "url":self.secondUrl, "title":self.secondTitle},
                                                                {"playlist_name":self.playlistName, "playlist_index":self.playlistIndex3, "url":self.thirdUrl, "title":self.thirdTitle},
                                                                {"playlist_name":self.playlistName, "playlist_index":self.playlistIndex4, "url":self.fourthUrl, "title":self.fourthTitle},
                                                                {"playlist_name":self.playlistName, "playlist_index":self.playlistIndex5, "url":self.fifthUrl, "title":self.fifthTitle},
                                                                {"playlist_name":self.playlistName, "playlist_index":self.playlistIndex6, "url":self.sixthUrl, "title":self.sixthTitle}
                                                                ]}

        self.ytManager.addMetadataToPlaylist = mock.MagicMock()
        self.ytManager.addMetadataToPlaylist.configure_mock(side_effect=[
                                                  self.firstFilenameWithPath.replace(".mp3", " (1).mp3"),
                                                  self.firstFilenameWithPath.replace(".mp3", " (2).mp3"),
                                                  self.firstFilenameWithPath.replace(".mp3", " (3).mp3"),
                                                  self.firstFilenameWithPath.replace(".mp3", " (4).mp3"),
                                                  self.firstFilenameWithPath.replace(".mp3", " (5).mp3")
                                                  ])


        mock_ydl_instance.extract_info.side_effect=[ytPlaylistInfoResponse6]
        sideEffectOfIsFile = [True, True, False, False,
                                  True, True, True,  False, False,
                                  True, True, True,  True,  False, False,
                                  True, True, True,  True,  True,  False, False,
                                  True, True, True,  True,  True,  True, False,
                                  True, True, True,  True,  True,  True, True
                              ]
        mock_isFile.configure_mock(side_effect=sideEffectOfIsFile)
        self.ytManager._download_mp3 = mock.MagicMock()
        ytResultSong1 = ResultOfDownload(AudioData(str(self.musicPath+"/"+self.playlistName+"/"+
                                                   self.firstTitle+" (1).mp3"),
                                                   self.firstTitle,
                                                   self.firstHash,
                                                   self.firstArtist,
                                                   self.firstAlbumArtist))
        ytResultSong2 = ResultOfDownload(AudioData(str(self.musicPath+"/"+self.playlistName+"/"+
                                                   self.secondTitle+" (2).mp3"),
                                                   self.secondTitle,
                                                   self.secondHash,
                                                   self.secondArtist,
                                                   self.secondAlbumArtist))
        ytResultSong3 = ResultOfDownload(AudioData(str(self.musicPath+"/"+self.playlistName+"/"+
                                                   self.thirdTitle+" (3).mp3"),
                                                   self.thirdTitle,
                                                   self.thirdHash,
                                                   self.thirdArtist,
                                                   self.thirdAlbumArtist))
        ytResultSong4 = ResultOfDownload(AudioData(str(self.musicPath+"/"+self.playlistName+"/"+
                                                   self.fourthTitle+" (4).mp3"),
                                                   self.fourthTitle,
                                                   self.fourthHash,
                                                   self.fourthArtist,
                                                   self.fourthAlbumArtist))
        ytResultSong5 = ResultOfDownload(AudioData(str(self.musicPath+"/"+self.playlistName+"/"+
                                                   self.fifthTitle+" (5).mp3"),
                                                   self.fifthTitle,
                                                   self.fifthHash,
                                                   self.fifthArtist,
                                                   self.fifthAlbumArtist))
        ytResultSong6 = ResultOfDownload(AudioData(str(self.musicPath+"/"+self.playlistName+"/"+
                                                   self.sixthTitle+" (6).mp3"),
                                                   self.sixthTitle,
                                                   self.sixthHash,
                                                   self.sixthArtist,
                                                   self.sixthAlbumArtist))

        self.ytManager._download_mp3.configure_mock(side_effect=[ytResultSong1, ytResultSong2, ytResultSong3, ytResultSong4, ytResultSong5, ytResultSong6])


        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)


        self.assertEqual(self.ytManager._createDirIfNotExist.call_count, 1)
        self.ytManager._createDirIfNotExist.assert_called_with(self.musicPath+"/"+self.playlistName)

        # song number 6 is dropped
        self.assertEqual(mock_isFile.call_count, len(sideEffectOfIsFile))
        self.ytManager._download_mp3.assert_has_calls([
            mock.call(self.firstUrl,  self.musicPath+"/"+self.playlistName, '%(title)s (1).%(ext)s'),
            mock.call(self.secondUrl, self.musicPath+"/"+self.playlistName, '%(title)s (2).%(ext)s'),
            mock.call(self.thirdUrl,  self.musicPath+"/"+self.playlistName, '%(title)s (3).%(ext)s'),
            mock.call(self.fourthUrl, self.musicPath+"/"+self.playlistName, '%(title)s (4).%(ext)s'),
            mock.call(self.fifthUrl,  self.musicPath+"/"+self.playlistName, '%(title)s (5).%(ext)s')
        ])

        mock_yt.assert_has_calls([mock.call(self.getPlaylistInfoRequest)])
        self.assertEqual(mock_yt.call_count, 1)
        self.assertEqual(mock_ydl_instance.extract_info.call_count, 1)
        mock_ydl_instance.extract_info.assert_has_calls([
            mock.call(self.ytLink, download=False)
        ])

        self.assertEqual(self.ytManager.addMetadataToPlaylist.call_count, 5)
        self.ytManager.addMetadataToPlaylist.assert_has_calls([
            mock.call(self.musicPath, self.playlistName, self.firstFilename.replace(".mp3", " (1).mp3"),  str(self.numberOfArchiveSongs+1), self.firstTitle,  self.firstArtist,  self.firstAlbumArtist,  self.firstHash),
            mock.call(self.musicPath, self.playlistName, self.secondFilename.replace(".mp3", " (2).mp3"), str(self.numberOfArchiveSongs+2), self.secondTitle, self.secondArtist, self.secondAlbumArtist, self.secondHash),
            mock.call(self.musicPath, self.playlistName, self.thirdFilename.replace(".mp3", " (3).mp3"),  str(self.numberOfArchiveSongs+3), self.thirdTitle,  self.thirdArtist,  self.thirdAlbumArtist,  self.thirdHash),
            mock.call(self.musicPath, self.playlistName, self.fourthFilename.replace(".mp3", " (4).mp3"), str(self.numberOfArchiveSongs+4), self.fourthTitle, self.fourthArtist, self.fourthAlbumArtist, self.fourthHash),
            mock.call(self.musicPath, self.playlistName, self.fifthFilename.replace(".mp3", " (5).mp3"),  str(self.numberOfArchiveSongs+5), self.fifthTitle,  self.fifthArtist,  self.fifthAlbumArtist,  self.fifthHash)
            ])

        self.assertEqual(mock_cover.call_count, 5)
        mock_cover.assert_has_calls([
                                    mock.call(self.firstFilenameWithPath.replace(".mp3", " (1).mp3"), self.firstHash),
                                    mock.call(self.firstFilenameWithPath.replace(".mp3", " (2).mp3"), self.secondHash),
                                    mock.call(self.firstFilenameWithPath.replace(".mp3", " (3).mp3"), self.thirdHash),
                                    mock.call(self.firstFilenameWithPath.replace(".mp3", " (4).mp3"), self.fourthHash),
                                    mock.call(self.firstFilenameWithPath.replace(".mp3", " (5).mp3"), self.fifthHash)
                                              ])

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), 5)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadata")
    def test_downloadMP3Playlist_OneNewSongFromPlaylist(self, mock_metadata:mock.MagicMock, mock_extract_info:mock.MagicMock):

        self.ytManager.isMusicClipArchived = mock.MagicMock()
        self.ytManager.isMusicClipArchived.configure_mock(side_effect=[True, True, True, False])
        mock_extract_info.configure_mock(side_effect=[self.ytPlaylistInfoResponse4, self.ytDownloadMp3Response4])

        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)


        self.assertEqual(self.ytManager._createDirIfNotExist.call_count, 2)
        self.ytManager._createDirIfNotExist.assert_called_with(self.musicPath+"/"+self.playlistName)
        self.assertEqual(mock_extract_info.call_count, 2)
        mock_extract_info.assert_has_calls([mock.call(self.ytLink, download=False),
                                            mock.call(self.fourthUrl)
                                            ])

        self.assertEqual(mock_metadata.call_count, 1)
        mock_metadata.assert_called_once_with(os.path.join(self.musicPath, self.playlistName, self.fourthFilename), str(self.numberOfArchiveSongs+1),
                                              self.fourthTitle, self.fourthArtist, self.fourthAlbum, '', self.fourthWebsite, self.actualDate)

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), 1)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "addCoverOfYtMp3")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadata")
    def test_downloadMP3Playlist_oneSongFailed(self, mock_metadata:mock.MagicMock, mock_cover:mock.MagicMock, mock_extract_info:mock.MagicMock):
        errorMessage = "Failed to download from Youtube"
        mock_extract_info.configure_mock(side_effect=[self.ytPlaylistInfoResponse4, self.ytDownloadMp3Response1,
                                                      self.ytDownloadMp3Response2, utils.ExtractorError(errorMessage, expected=True), self.ytDownloadMp3Response4])
        mock_metadata.configure_mock(side_effect=[self.firstFilenameWithPath,
                                                  self.secondFilenameWithPath,
                                                  self.fourthFilenameWithPath
                                                  ])


        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)


        self.assertEqual(self.ytManager._createDirIfNotExist.call_count, 5)
        self.ytManager._createDirIfNotExist.assert_called_with(self.musicPath+"/"+self.playlistName)
        self.assertEqual(mock_extract_info.call_count, 5)
        mock_extract_info.assert_has_calls([mock.call(self.ytLink, download=False),
                                            mock.call(self.firstUrl),
                                            mock.call(self.secondUrl),
                                            mock.call(self.thirdUrl),
                                            mock.call(self.fourthUrl),
                                            ])

        self.assertEqual(mock_metadata.call_count, self.numberOfSongs-1)
        mock_metadata.assert_has_calls([mock.call(os.path.join(self.musicPath, self.playlistName, self.firstFilename),  str(self.numberOfArchiveSongs+1),  self.firstTitle,  self.firstArtist,  self.firstAlbum, '', self.firstWebsite,  self.actualDate),
                                        mock.call(os.path.join(self.musicPath, self.playlistName, self.secondFilename), str(self.numberOfArchiveSongs+2),  self.secondTitle, self.secondArtist, self.secondAlbum, '', self.secondWebsite, self.actualDate),
                                        mock.call(os.path.join(self.musicPath, self.playlistName, self.fourthFilename), str(self.numberOfArchiveSongs+3),  self.fourthTitle, self.fourthArtist, self.fourthAlbum, '', self.fourthWebsite, self.actualDate)])

        self.assertEqual(mock_cover.call_count, 3)
        mock_cover.assert_has_calls([
                                    mock.call(self.firstFilenameWithPath, self.firstHash),
                                    mock.call(self.secondFilenameWithPath, self.secondHash),
                                    mock.call(self.fourthFilenameWithPath, self.fourthHash)
                                              ])

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), self.numberOfSongs-1)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3Playlist_getInfoFailed(self, mock_extract_info:mock.MagicMock):
        errorMessage = "Failed to download from Youtube"
        mock_extract_info.configure_mock(side_effect=utils.ExtractorError(errorMessage, expected=True))

        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)

        self.ytManager._createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.assertTrue(result.IsFailed())
        self.assertEqual(result.error(), "download failed: "+errorMessage)


class MediaServerDownloaderPlaylistsTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.downloader = MediaServerDownloader("test.ini")
        self.downloader.ytConfig.initialize("test.ini", CustomConfigParser())
        self.downloader.downloadPlaylistMp3 = MagicMock()
        self.downloader.checkPlaylistStatus = MagicMock()
        self.downloader.updateTrackNumber = MagicMock()

    def test_downloadPlaylists(self):
        self.downloader._isDirForPlaylists = MagicMock()
        self.downloader._isDirForPlaylists.configure_mock(return_value=True)

        listOfPlaylistResult = [4, 15]
        lisOfResults = []
        expectedNumberOfDownloadedSongs = 0
        for x in range(CustomConfigParser.numberOfPlaylists):
            numberOfDonwloadedSongs = listOfPlaylistResult[x]
            expectedNumberOfDownloadedSongs += numberOfDonwloadedSongs
            lisOfResults.append(ResultOfDownload(numberOfDonwloadedSongs))
        self.downloader.downloadPlaylistMp3.configure_mock(side_effect=lisOfResults)

        result = self.downloader.download_playlists()

        self.assertEqual(result, expectedNumberOfDownloadedSongs)
        self.assertEqual(self.downloader._isDirForPlaylists.call_count, 1)
        self.downloader.downloadPlaylistMp3.assert_has_calls(
            [mock.call(CustomConfigParser.path, CustomConfigParser.playlist1Name, CustomConfigParser.playlist1Link),
             mock.call(CustomConfigParser.path, CustomConfigParser.playlist2Name, CustomConfigParser.playlist2Link)])

        self.downloader.checkPlaylistStatus.assert_has_calls(
            [mock.call(CustomConfigParser.path, CustomConfigParser.playlist1Name, CustomConfigParser.playlist1Link),
             mock.call(CustomConfigParser.path, CustomConfigParser.playlist2Name, CustomConfigParser.playlist2Link)])

    def test_downloadPlaylistsOnePlaylistFailed(self):
        self.downloader._isDirForPlaylists = MagicMock()
        self.downloader._isDirForPlaylists.configure_mock(return_value=True)

        lisOfResults = []
        expectedNumberOfDownloadedSongs = 4
        lisOfResults.append(ResultOfDownload(4))
        lisOfResults.append(ResultOfDownload("error"))
        self.downloader.downloadPlaylistMp3.configure_mock(side_effect=lisOfResults)

        result = self.downloader.download_playlists()

        self.assertEqual(result, expectedNumberOfDownloadedSongs)
        self.assertEqual(self.downloader._isDirForPlaylists.call_count, 1)

        self.downloader.downloadPlaylistMp3.assert_has_calls(
            [mock.call(CustomConfigParser.path, CustomConfigParser.playlist1Name, CustomConfigParser.playlist1Link),
             mock.call(CustomConfigParser.path, CustomConfigParser.playlist2Name, CustomConfigParser.playlist2Link)])

        self.downloader.checkPlaylistStatus.assert_has_calls(
            [mock.call(CustomConfigParser.path, CustomConfigParser.playlist1Name, CustomConfigParser.playlist1Link),
             mock.call(CustomConfigParser.path, CustomConfigParser.playlist2Name, CustomConfigParser.playlist2Link)])

    def test_downloadPlaylistsFailedWrongPath(self):
        self.downloader._isDirForPlaylists = MagicMock()
        self.downloader._isDirForPlaylists.configure_mock(return_value=False)

        result = self.downloader.download_playlists()

        self.assertEqual(result, 0)
        self.assertEqual(self.downloader._isDirForPlaylists.call_count, 1)
        self.downloader.downloadPlaylistMp3.assert_not_called()

    def test_checkPlaylistsSync(self):
        self.downloader._isDirForPlaylists = MagicMock()
        self.downloader._isDirForPlaylists.configure_mock(return_value=True)

        self.downloader.checkPlaylistsSync()

        self.downloader.checkPlaylistStatus.assert_has_calls(
            [mock.call(CustomConfigParser.path, CustomConfigParser.playlist1Name, CustomConfigParser.playlist1Link),
             mock.call(CustomConfigParser.path, CustomConfigParser.playlist2Name, CustomConfigParser.playlist2Link)])

    def test_checkPlaylistsSync_wrongPath(self):
        self.downloader._isDirForPlaylists = MagicMock()
        self.downloader._isDirForPlaylists.configure_mock(return_value=False)

        self.downloader.checkPlaylistsSync()

        self.assertEqual(self.downloader.checkPlaylistStatus.call_count, 0)

    def test_updateTrackNumberAllPlaylists(self):
        self.downloader._isDirForPlaylists = MagicMock()
        self.downloader._isDirForPlaylists.configure_mock(return_value=True)

        self.downloader.updateTrackNumberAllPlaylists()

        self.downloader.updateTrackNumber.assert_has_calls(
            [mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist1Name), CustomConfigParser.playlist1Link, False),
             mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist2Name), CustomConfigParser.playlist2Link, False)])

    def test_updateTrackNumberAllPlaylists_isSave(self):
        self.downloader._isDirForPlaylists = MagicMock()
        self.downloader._isDirForPlaylists.configure_mock(return_value=True)

        self.downloader.updateTrackNumberAllPlaylists(isSave=True)

        self.downloader.updateTrackNumber.assert_has_calls(
            [mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist1Name), CustomConfigParser.playlist1Link, True),
             mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist2Name), CustomConfigParser.playlist2Link, True)])

    def test_updateTrackNumberAllPlaylists_singleNumberOne(self):
        self.downloader._isDirForPlaylists = MagicMock()
        self.downloader._isDirForPlaylists.configure_mock(return_value=True)

        self.downloader.updateTrackNumberAllPlaylists(0,isSave=True)

        self.downloader.updateTrackNumber.assert_has_calls(
            [mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist1Name), CustomConfigParser.playlist1Link, True)])

    def test_updateTrackNumberAllPlaylists_singleNumberTwo(self):
        self.downloader._isDirForPlaylists = MagicMock()
        self.downloader._isDirForPlaylists.configure_mock(return_value=True)

        self.downloader.updateTrackNumberAllPlaylists(1)

        self.downloader.updateTrackNumber.assert_has_calls(
            [mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist2Name), CustomConfigParser.playlist2Link, False)])

    def test_updateTrackNumberAllPlaylists_wrongPath(self):
        self.downloader._isDirForPlaylists = MagicMock()
        self.downloader._isDirForPlaylists.configure_mock(return_value=False)

        self.downloader.updateTrackNumberAllPlaylists()

        self.assertEqual(self.downloader.updateTrackNumber.call_count, 0)

if __name__ == "__main__":
    unittest.main()
