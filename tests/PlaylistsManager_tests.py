import importlib
import os
import tempfile
import unittest
from unittest.mock import call, patch

from youtubedlWeb.Common.PlaylistsManager.PlaylistsManager import (
    PlaylistsManager,
    PlaylistGenerationConfig,
)

playlists_manager_module = importlib.import_module(
    "youtubedlWeb.Common.PlaylistsManager.PlaylistsManager"
)


class PlaylistsManagerTestCase(unittest.TestCase):

    def test_initialization_and_save_to_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = PlaylistsManager(temp_dir)

            self.assertEqual(manager.musicDir, temp_dir)
            self.assertEqual(manager.playlistsDir, temp_dir)
            self.assertFalse(manager.isCrLfNeeded)
            self.assertFalse(manager.windowsSlash)

            manager.saveToFile("test_playlist.m3u", "#EXTM3U\n")

            saved_path = os.path.join(temp_dir, "test_playlist.m3u")
            self.assertTrue(os.path.isfile(saved_path))
            with open(saved_path, "r", encoding="utf-8") as handle:
                self.assertEqual(handle.read(), "#EXTM3U\n")

    def test_playlists_dir_must_stay_inside_music_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            music_dir = os.path.join(temp_dir, "music")
            os.makedirs(music_dir)
            outside_dir = os.path.join(temp_dir, "outside")
            config_text = """
[GLOBAL]
playlistsDir = %s
""" % outside_dir
            with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as handle:
                handle.write(config_text)
                config_path = handle.name

            try:
                manager = PlaylistsManager(music_dir, playlistsConfigFile=config_path)
                self.assertEqual(manager.playlistsDir, music_dir)
                self.assertTrue(os.path.commonpath([music_dir, manager.playlistsDir]) == music_dir)
            finally:
                os.unlink(config_path)

    def test_music_and_playlist_directories_can_be_separated_only_inline(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            music_dir = os.path.join(temp_dir, "music")
            playlists_dir = os.path.join(music_dir, "playlists")
            os.makedirs(music_dir)

            manager = PlaylistsManager(music_dir, playlists_dir)
            manager.saveToFile("test_playlist.m3u", "#EXTM3U\nrock/song.mp3\n")

            os.makedirs(os.path.join(music_dir, "rock", "live"))
            song_path = os.path.join(music_dir, "rock", "live", "song.mp3")
            with open(song_path, "wb") as handle:
                handle.write(b"")
            self.assertEqual(manager.collectSongs("rock"), ["rock/live/song.mp3"])

            with patch("youtubedlWeb.Common.PlaylistsManager.PlaylistsManager.MP3") as mp3:
                mp3.return_value.info.length = 1
                generated = manager.generateM3UList(["rock/live/song.mp3"])
            self.assertIn("rock/live/song.mp3\n", generated)

            self.assertEqual(manager.musicDir, music_dir)
            self.assertEqual(manager.playlistsDir, playlists_dir)
            self.assertTrue(os.path.isfile(os.path.join(playlists_dir, "test_playlist.m3u")))
            self.assertFalse(os.path.exists(os.path.join(music_dir, "test_playlist.m3u")))

            with open(os.path.join(playlists_dir, "test_playlist.m3u"), "r", encoding="utf-8") as handle:
                self.assertEqual(handle.read(), "#EXTM3U\nrock/song.mp3\n")

    def test_playlist_generation_config(self):
        config_text = """
[PLAYLIST_GROUPS]
training = folder one, Rock-Electronic
empty =

[TOP_PLAYLISTS]
sizes = 20, invalid, 0, 100

[GLOBAL]
removeCovers = yes
crlf = true
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as handle:
            handle.write(config_text)
            config_path = handle.name

        try:
            config = PlaylistGenerationConfig(config_path)
            self.assertEqual(
                config.get_global_settings(),
                {
                    "removeCovers": True,
                    "isCrLfNeeded": True,
                    "checkMissingWebsite": False,
                    "removePolishChars": False,
                    "checkCovers": False,
                    "checkDuplicates": False,
                    "checkTotalSize": False,
                    "maxTotalSizeMb": None,
                    "windowsSlash": False,
                    "garminRootDir": None,
                    "playlistsDir": None,
                    "createPlaylistsOfDirs": False,
                },
            )
            manager = PlaylistsManager("/tmp/music", playlistsConfigFile=config_path)
            self.assertTrue(manager.removeCoversEnabled)
            self.assertTrue(manager.isCrLfNeeded)
            self.assertEqual(
                config.get_groups(),
                [("training", ["folder one", "Rock-Electronic"])],
            )
            self.assertEqual(config.get_top_playlist_sizes(), [20, 100])
            config_only_manager = PlaylistsManager(
                "/tmp/music", playlistsConfigFile=config_path
            )
            self.assertTrue(config_only_manager.removeCoversEnabled)
            self.assertTrue(config_only_manager.isCrLfNeeded)
            self.assertFalse(config_only_manager.checkMissingWebsiteEnabled)
            self.assertFalse(config_only_manager.removePolishCharsEnabled)
            self.assertFalse(config_only_manager.checkCoversEnabled)
            self.assertFalse(config_only_manager.checkDuplicatesEnabled)
            self.assertFalse(config_only_manager.checkTotalSizeEnabled)
            self.assertIsNone(config_only_manager.garminRootDir)
            self.assertFalse(config_only_manager.createPlaylistsOfDirsEnabled)
        finally:
            os.unlink(config_path)

    def test_directory_playlist_generation_is_configured_in_ini(self):
        config_text = """
[GLOBAL]
createPlaylistsOfDirs = true

[PLAYLIST_GROUPS]
training = techno, relaks
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as handle:
            handle.write(config_text)
            config_path = handle.name

        try:
            config = PlaylistGenerationConfig(config_path)
            self.assertTrue(config.get_global_settings()["createPlaylistsOfDirs"])

            manager = PlaylistsManager("/tmp/music", playlistsConfigFile=config_path)
            self.assertTrue(manager.createPlaylistsOfDirsEnabled)

            with patch.object(manager, "createPlaylists") as create_playlists:
                if manager.createPlaylistsOfDirsEnabled:
                    manager.createPlaylists()

            create_playlists.assert_called_once_with()
        finally:
            os.unlink(config_path)


    def test_create_playlists_from_config_uses_only_changed_groups(self):
        config_text = """
[PLAYLIST_GROUPS]
training = techno, relaks
dance = Bachata, Kizomba

[TOP_PLAYLISTS]
sizes = 20, 100
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as handle:
            handle.write(config_text)
            config_path = handle.name

        try:
            manager = PlaylistsManager("/tmp/music", playlistsConfigFile=config_path)
            self.assertFalse(manager.removeCoversEnabled)
            self.assertFalse(manager.isCrLfNeeded)
            self.assertFalse(manager.checkMissingWebsiteEnabled)
            self.assertFalse(manager.removePolishCharsEnabled)

            self.assertFalse(manager.checkCoversEnabled)
            self.assertFalse(manager.checkDuplicatesEnabled)
            self.assertFalse(manager.checkTotalSizeEnabled)
            self.assertIsNone(manager.garminRootDir)
            with patch.object(manager, "createTopOfMusic") as create_top, \
                    patch.object(manager, "createGroupOfPlaylists") as create_group:
                manager.createPlaylistsFromConfig(["relaks"])

            create_top.assert_has_calls([call(20), call(100)])
            create_group.assert_called_once_with("training", ["techno", "relaks"])
        finally:
            os.unlink(config_path)

    def test_top_playlist_root_dir_is_used_from_config(self):
        config_text = """
[TOP_PLAYLISTS]
sizes = 30, 50
rootDir = jazz
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as handle:
            handle.write(config_text)
            config_path = handle.name

        try:
            config = PlaylistGenerationConfig(config_path)
            self.assertEqual(config.get_top_playlist_sizes(), [30, 50])
            self.assertEqual(config.get_top_playlist_root_dir(), "jazz")

            manager = PlaylistsManager("/tmp/music", playlistsConfigFile=config_path)
            with patch.object(manager, "createTopOfMusic") as create_top:
                manager.createPlaylistsFromConfig()

            create_top.assert_has_calls([call(30, rootDir="jazz"), call(50, rootDir="jazz")])
        finally:
            os.unlink(config_path)

    def test_extended_target_options_are_read_from_config(self):
        config_text = """
[GLOBAL]
checkCovers = true
checkDuplicates = true
checkTotalSize = true
maxTotalSizeMb = 1400
windowsSlash = true
garminRootDir = /garmin/playlists

[PLAYLIST_GROUPS]
trening = techno, relaks
trening 40 hits = techno, relaks
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as handle:
            handle.write(config_text)
            config_path = handle.name

        try:
            config = PlaylistGenerationConfig(config_path)
            settings = config.get_global_settings()
            self.assertTrue(settings["checkCovers"])
            self.assertTrue(settings["checkDuplicates"])
            self.assertTrue(settings["checkTotalSize"])
            self.assertEqual(settings["maxTotalSizeMb"], 1400.0)
            self.assertTrue(settings["windowsSlash"])
            self.assertEqual(settings["garminRootDir"], "/garmin/playlists")
            self.assertEqual(
                config.get_groups(),
                [
                    ("trening", ["techno", "relaks"]),
                    ("trening", ["techno", "relaks"], 40),
                ],
            )

            manager = PlaylistsManager("/tmp/music", playlistsConfigFile=config_path)
            self.assertTrue(manager.checkCoversEnabled)
            self.assertTrue(manager.checkDuplicatesEnabled)
            self.assertTrue(manager.checkTotalSizeEnabled)
            self.assertEqual(manager.maxTotalSizeMb, 1400.0)
            self.assertTrue(manager.windowsSlash)
            self.assertEqual(manager.garminRootDir, "/garmin/playlists")
        finally:
            os.unlink(config_path)

    def test_music_dir_cli_argument_is_required(self):
        config_text = """
[GLOBAL]
removeCovers = false
CrLf = false
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as handle:
            handle.write(config_text)
            config_path = handle.name

        try:
            with patch.object(playlists_manager_module, "PlaylistsManagerPlayer") as manager_class:
                manager_class.return_value.checkMissingWebsiteEnabled = False
                manager_class.return_value.checkCoversEnabled = False
                manager_class.return_value.removeCoversEnabled = False
                manager_class.return_value.removePolishCharsEnabled = False
                manager_class.return_value.checkDuplicatesEnabled = False
                manager_class.return_value.checkTotalSizeEnabled = False
                manager_class.return_value.garminRootDir = None
                playlists_manager_module.main(
                    ["--config", config_path, "--music-dir", "/custom/music"]
                )
                self.assertEqual(
                    manager_class.call_args.args[0],
                    "/custom/music",
                )

                with self.assertRaises(SystemExit) as error:
                    playlists_manager_module.main(["--config", config_path])
                self.assertEqual(error.exception.code, 2)
        finally:
            os.unlink(config_path)

if __name__ == "__main__":
    unittest.main()
