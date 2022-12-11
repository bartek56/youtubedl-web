import unittest
import unittest.mock as mock
from YouTubeManager import YoutubeDl
import yt_dlp
import metadata_mp3


class YouTubeManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.ytManager = YoutubeDl()

    def tearDown(self):
        pass

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value={"title":"title_test", "artist":"artist_test", "album":"album_test"})
    @mock.patch.object(metadata_mp3, "add_metadata_song")
    def test_downloadMP3(self, mock_metadata, mock_extract_info):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_mp3(link)

        mock_extract_info.assert_called_with(link)
        mock_metadata.assert_called_with('/tmp/music/quick_download/', 'album_test', 'artist_test', 'title_test')

        self.assertEqual(result["title"],"title_test")
        self.assertEqual(result["artist"],"artist_test")
        self.assertEqual(result["album"],"album_test")

if __name__ == "__main__":
    unittest.main()
