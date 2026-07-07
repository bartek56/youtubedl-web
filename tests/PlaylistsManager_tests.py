import os
import tempfile
import unittest

from youtubedlWeb.Common.PlaylistsManager import PlaylistsManager


class PlaylistsManagerTestCase(unittest.TestCase):

    def test_initialization_and_save_to_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = PlaylistsManager(temp_dir)

            self.assertEqual(manager.dir, temp_dir)
            self.assertFalse(manager.isCrLfNeeded)
            self.assertFalse(manager.windowsSlash)

            manager.saveToFile("test_playlist.m3u", "#EXTM3U\n")

            saved_path = os.path.join(temp_dir, "test_playlist.m3u")
            self.assertTrue(os.path.isfile(saved_path))
            with open(saved_path, "r", encoding="utf-8") as handle:
                self.assertEqual(handle.read(), "#EXTM3U\n")


if __name__ == "__main__":
    unittest.main()
