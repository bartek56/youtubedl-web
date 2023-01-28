import unittest

from Common.YouTubeManager import YoutubeDl

class YouTubeManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.ytManager = YoutubeDl()

    def tearDown(self):
        pass

    def test_download_4k(self):
        link = "https://www.youtube.com/watch?v=yqq3p-brlyc"
        result = self.ytManager.download_4k(link)
        self.assertEqual(result["title"], "test_title")
        self.assertEqual(result["path"], "/tmp/video/quick_download//test_title_4k.mp4")

if __name__ == "__main__":
    unittest.main()
