import unittest
import unittest.mock as mock
from Common.YouTubeManager import YoutubeManager, YoutubeConfig, PlaylistInfo, MediaFromPlaylist, MediaInfo, AudioData, VideoData, ResultOfDownload
from configparser import ConfigParser
import yt_dlp
from yt_dlp import utils
import metadata_mp3
import logging

logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.FATAL)

class YouTubeManagerDlTestCase(unittest.TestCase):
    musicPath = "/media/music"
    videoPath = "/media/video"

    empty  = ""

    ytLink      = "https://www.youtube.com/watch?v=yqq3p-brlyc"
    ytMediaHash = "yqq3p-brlyc"

    artist = "artist_test"
    title  = "title_test"
    album  = "album_test"
    playlistName = "test_playlist"

    foundMp3File = musicPath+title+".mp3"

    ytMp3ArchiveFilename = "songsArchive.txt"

    ytPlaylistInfoResponse = {"title": "testPlaylist","entries":[{"playlist_name":"testPlaylist", "playlist_index":"1", "url":"https://www.youtube.com/watch?v=1111", "title":"firstTitle"},
                                                                     {"playlist_name":"testPlaylist", "playlist_index":"2", "url":"https://www.youtube.com/watch?v=2222", "title":"secondTitle"}]}
    ytMediaInfoResponse = {"original_url":ytLink, "title":"firstTitle", "title":"testTitle", "artist":"testArtist", "album":"testAlbum"}
    ytMp3Data ={"title":title, "artist":artist, "album":album}
    ytMp3DataWithoutArtist = {"title":title, "artist":empty, "album":album}
    ytEmptyPlaylist = {"title": playlistName, "entries":[{}, None]}

    playlistIndex1 = "1"
    firstTitle     = "first_title"
    firstArtist    = "first_artist"
    firstAlbum     = "first_album"
    playlistIndex2 = "2"
    secondTitle    = "second_title"
    secondArtist   = "second_artist"
    secondAlbum    = "second_album"

    ytDownloadMp3PlaylistResponse = {"entries":[
            {'playlist_index': playlistIndex1,"title":firstTitle,  "artist":firstArtist, "album":firstAlbum},
            {'playlist_index': playlistIndex2,"title":secondTitle, "album":secondAlbum}]}

    extMp4 = "mp4"
    resolution360p = "360p"
    resolution720p = "720p"
    resolution4k   = "4k"
    ytDownloadVideoResponse={"title":title, "artist":artist, "ext":extMp4}

    def setUp(self):
        self.ytManager = YoutubeManager(videoPath=self.videoPath, musicPath=self.musicPath, mp3ArchiveFilename=self.ytMp3ArchiveFilename)
        self.ytManager.createDirIfNotExist = mock.MagicMock()
        self.ytManager.openFile = mock.MagicMock()
        self.ytManager.lookingForFile = mock.MagicMock()

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

    def checkVideoData(self, data:VideoData, ytResponse, videoResolution):
        self.assertEqual(data.title, ytResponse["title"])
        self.assertEqual(data.path, self.videoPath+"/"+ytResponse["title"]+"_"+videoResolution+"."+ytResponse["ext"])

    def raiseYtError(param, **kwargs):
        #message = f'Video unavailable: {", ".join(playability_errors)}'
        message = "Video unavailable"
        raise utils.ExtractorError(message, expected=True)

    def test_getMediaHash(self):
        hash = self.ytManager.getMediaHashFromLink("https://www.youtube.com/watch?v=Lr4x3sCH7l0&list=PL6uhlddQJkfh4YsbxgPE70a6KeFOCDgG")
        self.assertEqual(hash, "Lr4x3sCH7l0")

    def test_getMediaHash(self):
        hash = self.ytManager.getMediaHashFromLink("https://www.youtube.com/watch?v=Lr4x3sCH7l0")
        self.assertEqual(hash, "Lr4x3sCH7l0")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getPlaylistInfo(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=self.ytPlaylistInfoResponse)

        result = self.ytManager.getPlaylistInfo(self.ytLink)

        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertTrue(result.IsSuccess())
        self.checkPlaylist(result.data(), self.ytPlaylistInfoResponse)

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

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_getPlaylistInfoException(self, mock_extractInfo):
        result = self.ytManager.getPlaylistInfo(self.ytLink)

        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertFalse(result.IsSuccess())

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

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_getMediaInfoException(self, mock_extractInfo):
        result = self.ytManager.getMediaInfo(self.ytLink)

        mock_extractInfo.assert_has_calls([mock.call(self.ytLink, download=False)])
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToSong")
    def test_downloadMP3(self, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3Data)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        mock_metadata.assert_called_with(self.musicPath, self.album, self.artist, self.title)
        self.assertTrue(result.IsSuccess())
        self.checkAudioData(result.data(), self.ytMp3Data)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToSong", return_value=None)
    def test_downloadMP3_failedWithModyfiMetadata(self, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3Data)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        mock_metadata.assert_called_with(self.musicPath, self.album, self.artist, self.title)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToSong")
    def test_downloadMP3_without_artist(self, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DataWithoutArtist)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        mock_metadata.assert_called_with(self.musicPath, self.album, self.empty, self.title)
        self.assertTrue(result.IsSuccess())
        self.checkAudioData(result.data(), self.ytMp3DataWithoutArtist)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_emptyReturn(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=None)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_downloadMP3Exception(self, mock_extract_info):
        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_onlyMetadata(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3Data)
        self.ytManager.openFile.configure_mock(return_value=self.ytMediaHash)
        self.ytManager.lookingForFile.configure_mock(return_value=self.foundMp3File)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.ytManager.openFile.assert_called_with(self.musicPath, self.ytMp3ArchiveFilename)
        self.ytManager.lookingForFile.assert_called_with(self.musicPath, self.title, self.artist)
        self.assertTrue(result.IsSuccess())
        data = result.data()
        self.checkAudioData(data, self.ytMp3Data)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_downloadMP3_onlyMetadata_exception(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3Data)
        self.ytManager.openFile.configure_mock(return_value=self.ytMediaHash)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.ytManager.openFile.assert_called_with(self.musicPath, self.ytMp3ArchiveFilename)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_downloadMP3_onlyMetadata_NoneResult(self, mock_extract_info):
        self.ytManager.openFile.configure_mock(return_value=self.ytMediaHash)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.ytManager.openFile.assert_called_with(self.musicPath, self.ytMp3ArchiveFilename)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_onlyMetadata_FileNotFound(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3Data)
        self.ytManager.openFile.configure_mock(return_value=self.ytMediaHash)
        self.ytManager.lookingForFile.configure_mock(return_value=None)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.ytManager.openFile.assert_called_with(self.musicPath, self.ytMp3ArchiveFilename)
        self.ytManager.lookingForFile.assert_called_with(self.musicPath,self.title, self.artist)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToPlaylist")
    def test_downloadMP3Playlist(self, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytDownloadMp3PlaylistResponse)

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        self.ytManager.createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        mock_extract_info.assert_called_once_with(self.ytLink)
        mock_metadata.assert_has_calls([mock.call(self.musicPath, self.playlistIndex1, self.playlistName,self.firstArtist, self.firstTitle),
                                        mock.call(self.musicPath, self.playlistIndex2, self.playlistName, self.empty, self.secondTitle)])
        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), 2)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistEmptyResult(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=None)

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager.createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistWrongResult(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"fakeData":[]})

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager.createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistEmptyEntries(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"entries":[{},None]})

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager.createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_downloadMP3PlaylistException(self, mock_extract_info):

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager.createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())

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

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_download4kFailedRaise(self, mock_extract_info):

        result = self.ytManager.download_4k(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertFalse(result.IsSuccess())

class CustomConfigParser(ConfigParser):
    def read(self, filename):
        self.read_string("[GLOBAL]\npath = /tmp/muzyka/Youtube list\n[relaks]\nname = relaks\nlink = http://youtube.com/relaks\n[chillout]\nname = chillout\nlink = http://youtube.com/chillout\n")

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
        self.assertEqual(path, "/tmp/muzyka/Youtube list")

    def test_getPathFailed(self):
        self.ytConfig.initialize("neverMind", CustomConfigParserEmptyPath())
        path = self.ytConfig.getPath()
        self.assertEqual(path, None)

    def test_getPlaylists(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        playlists = self.ytConfig.getPlaylists()
        self.assertEqual(len(playlists), 2)
        self.assertEqual(playlists[0].name, "relaks")
        self.assertEqual(playlists[0].link, "http://youtube.com/relaks")

        self.assertEqual(playlists[1].name, "chillout")
        self.assertEqual(playlists[1].link, "http://youtube.com/chillout")

    def test_getPlaylistsName(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        playlists = self.ytConfig.getPlaylistsName()
        self.assertEqual(len(playlists), 2)
        self.assertEqual(playlists[0], "relaks")
        self.assertEqual(playlists[1], "chillout")

    def test_getUrlOfPaylist(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        url = self.ytConfig.getUrlOfPlaylist("relaks")
        self.assertEqual(url, "http://youtube.com/relaks")

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
        self.assertTrue(self.ytConfig.removePlaylist("chillout"))
        self.assertEqual(mock_save.call_count, 1)
        self.assertEqual(mock_removeSection.call_count, 1)
        mock_removeSection.assert_called_once_with("chillout")

    @mock.patch.object(YoutubeConfig, "save")
    def test_removePlaylist2(self, mock_save):
        configParser = CustomConfigParser()
        removeSectionMock = mock.MagicMock()
        configParser.setMockForRemoveSection(removeSectionMock)

        self.ytConfig.initialize("neverMind", configParser)
        self.assertTrue(self.ytConfig.removePlaylist("chillout"))
        self.assertEqual(mock_save.call_count, 1)
        removeSectionMock.assert_called_once_with("chillout")

    @mock.patch.object(YoutubeConfig, "save")
    def test_removePlaylistWrongName(self, mock_save):
        configParser = CustomConfigParser()
        removeSectionMock = mock.MagicMock()
        configParser.setMockForRemoveSection(removeSectionMock)

        self.ytConfig.initialize("neverMind", configParser)
        self.assertFalse(self.ytConfig.removePlaylist("wrongName"))
        self.assertEqual(mock_save.call_count, 0)
        self.assertEqual(removeSectionMock.call_count, 0)

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

if __name__ == "__main__":
    unittest.main()
