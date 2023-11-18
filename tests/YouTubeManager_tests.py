import unittest
import unittest.mock as mock
from Common.YouTubeManager import YoutubeManager, YoutubeConfig
from configparser import ConfigParser
import yt_dlp
from yt_dlp import utils
import metadata_mp3
import logging

logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.FATAL)
class YouTubeManagerDlTestCase(unittest.TestCase):
    def setUp(self):
        self.ytManager = YoutubeManager()
        self.ytManager.createDirIfNotExist = mock.MagicMock()
        self.ytManager.openFile = mock.MagicMock()
        self.ytManager.lookingForFile = mock.MagicMock()

    def tearDown(self):
        pass

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
        mock_extractInfo.configure_mock(return_value={"title": "testPlaylist","entries":[{"playlist_name":"testPlaylist", "playlist_index":"1", "url":"https://www.youtube.com/watch?v=1111", "title":"firstTitle"},
                                                      {"playlist_name":"testPlaylist", "playlist_index":"2", "url":"https://www.youtube.com/watch?v=2222", "title":"secondTitle"}]})

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        data = self.ytManager.getPlaylistInfo(link)

        mock_extractInfo.assert_called_once_with(link, download=False)
        self.assertEqual(data[0]["playlist_name"], "testPlaylist")
        self.assertEqual(data[0]["playlist_index"], 1)
        self.assertEqual(data[0]["url"], "https://www.youtube.com/watch?v=1111")
        self.assertEqual(data[0]["title"], "firstTitle")

        self.assertEqual(data[1]["playlist_name"], "testPlaylist")
        self.assertEqual(data[1]["playlist_index"], 2)
        self.assertEqual(data[1]["url"], "https://www.youtube.com/watch?v=2222")
        self.assertEqual(data[1]["title"], "secondTitle")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getPlaylistInfoEmptyResult(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=None)

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        data = self.ytManager.getPlaylistInfo(link)

        mock_extractInfo.assert_called_once_with(link, download=False)
        self.assertEqual(data, "Failed to download")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getPlaylistInfoEmptyEntries(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value={"title": "testPlaylist", "entries":[{}, None]})

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        data = self.ytManager.getPlaylistInfo(link)

        mock_extractInfo.assert_called_once_with(link, download=False)
        self.assertEqual(data, "not extract_info in results")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_getPlaylistInfoException(self, mock_extractInfo):

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        data = self.ytManager.getPlaylistInfo(link)

        mock_extractInfo.assert_called_once_with(link, download=False)
        self.assertEqual(data, "Video unavailable")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getMediaInfo(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value={"original_url":"https://www.youtube.com/watch?v=1111", "title":"firstTitle", "title":"testTitle", "artist":"testArtist", "album":"testAlbum"})

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        data = self.ytManager.getMediaInfo(link)

        mock_extractInfo.assert_called_once_with(link, download=False)
        self.assertEqual(data["url"], "https://www.youtube.com/watch?v=1111")
        self.assertEqual(data["title"], "testTitle")
        self.assertEqual(data["artist"], "testArtist")
        self.assertEqual(data["album"], "testAlbum")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getMediaInfoEmptyResult(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=None)

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        data = self.ytManager.getMediaInfo(link)
        data = self.ytManager.getPlaylistInfo(link)

        mock_extractInfo.assert_has_calls([mock.call(link, download=False),
                                        mock.call(link, download=False)])
        self.assertEqual(data, "Failed to download")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_getMediaInfoException(self, mock_extractInfo):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        data = self.ytManager.getMediaInfo(link)
        data = self.ytManager.getPlaylistInfo(link)

        mock_extractInfo.assert_has_calls([mock.call(link, download=False),
                                        mock.call(link, download=False)])
        self.assertEqual(data, "Video unavailable")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "rename_and_add_metadata_to_song")
    def test_downloadMP3(self, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"title":"title_test", "artist":"artist_test", "album":"album_test"})
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_mp3(link)

        mock_extract_info.assert_called_once_with(link)
        mock_metadata.assert_called_with('/tmp/quick_download/', 'album_test', 'artist_test', 'title_test')

        self.assertEqual(result["title"], "title_test")
        self.assertEqual(result["artist"], "artist_test")
        self.assertEqual(result["album"], "album_test")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "rename_and_add_metadata_to_song", return_value=None)
    def test_downloadMP3_failedWithModyfiMetadata(self, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"title":"title_test", "artist":"artist_test", "album":"album_test"})
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_mp3(link)

        mock_extract_info.assert_called_once_with(link)
        mock_metadata.assert_called_with('/tmp/quick_download/', 'album_test', 'artist_test', 'title_test')

        self.assertEqual(result, "couldn't find a file")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title":"title_test", "artist":"", "album":"album_test"})
    @mock.patch.object(metadata_mp3.MetadataManager, "rename_and_add_metadata_to_song")
    def test_downloadMP3_without_artist(self, mock_metadata, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_mp3(link)

        mock_extract_info.assert_called_with(link)
        mock_metadata.assert_called_with('/tmp/quick_download/', 'album_test', '', 'title_test')

        self.assertEqual(result["title"], "title_test")
        self.assertEqual(result["artist"], "")
        self.assertEqual(result["album"], "album_test")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_emptyReturn(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=None)
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_mp3(link)

        mock_extract_info.assert_called_once_with(link)
        self.assertEqual(result, "Failed to download url: https://www.youtube.com/watch?v=yqq3p-brlyc")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_downloadMP3Exception(self, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_mp3(link)

        mock_extract_info.assert_called_once_with(link)
        self.assertEqual(result, "Video unavailable")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_onlyMetadata(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"title":"title_test", "artist":"artist_test", "album":"album_test"})
        self.ytManager.openFile.configure_mock(return_value="yqq3p-brlyc")
        self.ytManager.lookingForFile.configure_mock(return_value="/tmp/quick_download/title_test.mp3")

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_mp3(link)
        mock_extract_info.assert_called_once_with(link, download=False)
        self.ytManager.openFile.assert_called_with('/tmp/quick_download/', 'downloaded_songs.txt')
        self.ytManager.lookingForFile.assert_called_with('/tmp/quick_download/','title_test', 'artist_test')

        self.assertEqual(result["title"], "title_test")
        self.assertEqual(result["artist"], "artist_test")
        self.assertEqual(result["album"], "album_test")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_downloadMP3_onlyMetadata_exception(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"title":"title_test", "artist":"artist_test", "album":"album_test"})
        self.ytManager.openFile.configure_mock(return_value="yqq3p-brlyc")

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_mp3(link)
        mock_extract_info.assert_called_once_with(link, download=False)
        self.ytManager.openFile.assert_called_with('/tmp/quick_download/', 'downloaded_songs.txt')

        self.assertEqual(result, "Video unavailable")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_downloadMP3_onlyMetadata_NoneResult(self, mock_extract_info):
        self.ytManager.openFile.configure_mock(return_value="yqq3p-brlyc")

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_mp3(link)
        mock_extract_info.assert_called_once_with(link, download=False)
        self.ytManager.openFile.assert_called_with('/tmp/quick_download/', 'downloaded_songs.txt')

        self.assertEqual(result, "Failed to download url: https://www.youtube.com/watch?v=yqq3p-brlyc")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_onlyMetadata_FileNotFound(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"title":"title_test", "artist":"artist_test", "album":"album_test"})
        self.ytManager.openFile.configure_mock(return_value="yqq3p-brlyc")
        self.ytManager.lookingForFile.configure_mock(return_value=None)

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_mp3(link)
        mock_extract_info.assert_called_once_with(link, download=False)
        self.ytManager.openFile.assert_called_with('/tmp/quick_download/', 'downloaded_songs.txt')
        self.ytManager.lookingForFile.assert_called_with('/tmp/quick_download/','title_test', 'artist_test')

        self.assertEqual(result, "couldn't find a file")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "rename_and_add_metadata_to_playlist")
    def test_downloadMP3Playlist(self, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"entries":[
            {'playlist_index': "1","title":"first_title", "artist":"first_artist", "album":"first_album"},
            {'playlist_index': "2","title":"second_title", "album":"second_album"}
            ]})
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_playlist_mp3('/tmp/quick_download/', "test_playlist", link)

        mock_extract_info.assert_called_once_with(link)
        mock_metadata.assert_has_calls([mock.call('/tmp/quick_download/', '1', 'test_playlist', 'first_artist', 'first_title'),
                                        mock.call('/tmp/quick_download/', '2', 'test_playlist', '', 'second_title')])

        self.ytManager.createDirIfNotExist.assert_called_once_with("/tmp/quick_download/test_playlist")
        self.assertEqual(result, 2)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistEmptyResult(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=None)

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_playlist_mp3('/tmp/quick_download/', "test_playlist", link)

        mock_extract_info.assert_called_once_with(link)
        self.ytManager.createDirIfNotExist.assert_called_once_with("/tmp/quick_download/test_playlist")
        self.assertEqual(result, "Failed to download")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistWrongResult(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"fakeData":[]})

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_playlist_mp3('/tmp/quick_download/', "test_playlist", link)

        mock_extract_info.assert_called_once_with(link)
        self.ytManager.createDirIfNotExist.assert_called_once_with("/tmp/quick_download/test_playlist")
        self.assertEqual(result, "not entries in results")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistEmptyEntries(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"entries":[{},None]})

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_playlist_mp3('/tmp/quick_download/', "test_playlist", link)

        mock_extract_info.assert_called_once_with(link)
        self.ytManager.createDirIfNotExist.assert_called_once_with("/tmp/quick_download/test_playlist")
        self.assertEqual(result, "not extract_info in results")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_downloadMP3PlaylistException(self, mock_extract_info):

        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_playlist_mp3('/tmp/quick_download/', "test_playlist", link)

        mock_extract_info.assert_called_once_with(link)
        self.ytManager.createDirIfNotExist.assert_called_once_with("/tmp/quick_download/test_playlist")
        self.assertEqual(result, "Video unavailable")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title":"title_test", "artist":"artist_test", "ext":"mp4"})
    def test_download360p(self, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_360p(link)

        mock_extract_info.assert_called_with(link)

        self.assertEqual(result["title"], "title_test")
        self.assertEqual(result["path"], "/tmp/quick_download//title_test_360p.mp4")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_download360pFailed(self, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_360p(link)

        mock_extract_info.assert_called_with(link)
        error = "Failed to download url: " + link
        self.assertEqual(result, error)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title":"title_test", "artist":"artist_test", "ext":"mp4"})
    def test_download720p(self, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_720p(link)

        mock_extract_info.assert_called_with(link)

        self.assertEqual(result["title"], "title_test")
        self.assertEqual(result["path"], "/tmp/quick_download//title_test_720p.mp4")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_download720pFailed(self, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_720p(link)

        mock_extract_info.assert_called_with(link)
        error = "Failed to download url: " + link
        self.assertEqual(result, error)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title":"title_test", "artist":"artist_test", "ext":"mp4"})
    def test_download4k(self, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_4k(link)

        mock_extract_info.assert_called_with(link)

        self.assertEqual(result["title"], "title_test")
        self.assertEqual(result["path"], "/tmp/quick_download//title_test_4k.mp4")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_download4kFailed(self, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_4k(link)

        mock_extract_info.assert_called_with(link)
        error = "Failed to download url: " + link
        self.assertEqual(result, error)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=raiseYtError)
    def test_download4kFailedRaise(self, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_4k(link)

        mock_extract_info.assert_called_with(link)
        self.assertEqual(result, "Video unavailable")

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
        self.assertEqual(playlists[0], {"name":"relaks", "link":"http://youtube.com/relaks"})
        self.assertEqual(playlists[1], {"name":"chillout", "link":"http://youtube.com/chillout"})

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

if __name__ == "__main__":
    unittest.main()
