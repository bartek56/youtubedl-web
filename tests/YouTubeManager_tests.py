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
        self.read_string("[relaks]\nname = relaks\nlink = http://youtube.com/relaks\n[chillout]\nname = chillout\nlink = http://youtube.com/chillout\n")

class YouTubeManagerConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.ytConfig = YoutubeConfig("neverMind")

    def tearDown(self):
        pass

    @mock.patch('configparser.ConfigParser')
    def test_getPlaylists(self, mock_configParser):
        mock_configParser.configure_mock(side_effect=CustomConfigParser)
        playlists = self.ytConfig.getPlaylists()
        self.assertEqual(playlists[0], {"name":"relaks"})
        self.assertEqual(playlists[1], {"name":"chillout"})

    @mock.patch('configparser.ConfigParser')
    def test_getPlaylistsName(self, mock_configParser):
        mock_configParser.configure_mock(side_effect=CustomConfigParser)
        playlists = self.ytConfig.getPlaylistsName()
        self.assertEqual(playlists[0], "relaks")
        self.assertEqual(playlists[1], "chillout")

    @mock.patch.object(YoutubeConfig, "save")
    @mock.patch('configparser.ConfigParser')
    def test_addPlaylist(self, mock_configParser, mock_save):
        mock_configParser.configure_mock(side_effect=CustomConfigParser)
        self.assertTrue(self.ytConfig.addPlaylist({"name":"disco", "link":"https:/yt.com/disco"}))

        print(mock_configParser["disco"])
        mock_save.assert_called_once()
#        mock_save.assert_called_once_with("fg")


if __name__ == "__main__":
    unittest.main()
