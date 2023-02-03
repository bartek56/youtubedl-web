import unittest
import unittest.mock as mock
from Common.YouTubeManager import YoutubeDl
import yt_dlp
import metadata_mp3
import os.path

class YouTubeManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.ytManager = YoutubeDl()
        self.ytManager.createDirIfNotExist = mock.MagicMock()

    def tearDown(self):
        pass

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3, "add_metadata_song")
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
    @mock.patch.object(metadata_mp3, "add_metadata_song")
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


if __name__ == "__main__":
    unittest.main()
