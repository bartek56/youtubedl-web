import unittest
import unittest.mock as mock
from Common.YouTubeManager import YoutubeDl, YoutubeConfig
from configparser import ConfigParser
import yt_dlp
import metadata_mp3

class YouTubeManagerDlTestCase(unittest.TestCase):
    def setUp(self):
        self.ytManager = YoutubeDl()
        self.ytManager.createDirIfNotExist = mock.MagicMock()

    def tearDown(self):
        pass

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

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title":"title_test", "artist":"artist_test", "ext":"mp4"})
    def test_download360p(self, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_360p(link)

        mock_extract_info.assert_called_with(link)

        self.assertEqual(result["title"], "title_test")
        self.assertEqual(result["path"], "/tmp/quick_download//title_test_360p.mp4")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title":"title_test", "artist":"artist_test", "ext":"mp4"})
    def test_download720p(self, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_720p(link)

        mock_extract_info.assert_called_with(link)

        self.assertEqual(result["title"], "title_test")
        self.assertEqual(result["path"], "/tmp/quick_download//title_test_720p.mp4")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title":"title_test", "artist":"artist_test", "ext":"mp4"})
    def test_download4k(self, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_4k(link)

        mock_extract_info.assert_called_with(link)

        self.assertEqual(result["title"], "title_test")
        self.assertEqual(result["path"], "/tmp/quick_download//title_test_4k.mp4")

class CustomConfigParser(ConfigParser):
    def read(self, filename):
        self.read_string("[GLOBAL]\npath = /tmp/muzyka/Youtube list\n[relaks]\nname = relaks\nlink = http://youtube.com/relaks\n[chillout]\nname = chillout\nlink = http://youtube.com/chillout\n")

    def setMockForRemoveSection(self, mock):
        self.remove_section = mock

class YouTubeManagerConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.ytConfig = YoutubeConfig()

    def tearDown(self):
        pass

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

    def test_getUrlOfPLaylist(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        url = self.ytConfig.getUrlOfPlaylist("relaks")
        self.assertEqual(url, "http://youtube.com/relaks")

    def test_getUrlOfPLaylist(self):
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
