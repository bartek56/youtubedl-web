import configparser
import os
import logging
from typing import List

from .YoutubeTypes import PlaylistConfig

logger = logging.getLogger(__name__)

class YoutubeConfig:
    def __init__(self):
        """
        Initializes a YoutubeConfig object.

        YoutubeConfig is a class that manages the configuration file of the program.
        It loads the configuration file, reads the settings from it and saves the changes.
        """
        pass

    def initialize(self, configFile, parser = configparser.ConfigParser()):
        """
        Initializes a YoutubeConfig object with the given configuration file.

        Args:
            configFile (str): Path to the configuration file.
            parser (configparser.ConfigParser): Parser to use for reading the configuration file.

        Raises:
            None

        Returns:
            None
        """
        if not os.path.isfile(configFile):
            logger.error("Config file \"%s\" doesn't exist", configFile)
        self.CONFIG_FILE = configFile
        self.config = parser

    def getPath(self):
        """
        Gets the path to the directory where the program saves the downloaded songs.

        Returns:
            str: The path to the directory where the program saves the downloaded songs.
        """
        path = None
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        if "GLOBAL" in self.config.sections():
            path = self.config["GLOBAL"]['path']
        return path

    def setPath(self, path):
        """
        Sets the path to the directory where the program saves the downloaded songs.

        Args:
            path (str): The path to the directory where the program saves the downloaded songs.

        Returns:
            None
        """
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        if "GLOBAL" not in self.config:
            self.config.add_section("GLOBAL")
        self.config["GLOBAL"]["path"] = path
        self.save()

    def getPlaylists(self) -> List[PlaylistConfig]:
        """
        Gets the list of playlists to download.

        Returns:
            List[PlaylistConfig]: A list of PlaylistConfig objects, each containing the name and link of a playlist.
        """
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        data = []

        for section_name in self.config.sections():
            if section_name != "GLOBAL":
                data.append(PlaylistConfig(self.config[section_name]['name'], self.config[section_name]['link']))
        return data

    def getPlaylistsName(self):
        """
        Gets the list of names of playlists to download.

        Returns:
            List[str]: A list of names of playlists to download.
        """
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        data = []

        for section_name in self.config.sections():
            if section_name != "GLOBAL":
                data.append(self.config[section_name]['name'])
        return data

    def addPlaylist(self, playlist:dict):
        """
        Adds a new playlist to download.

        Args:
            playlist (dict): A dictionary containing the name and link of the playlist.

        Returns:
            bool: True if the playlist was added successfully, False otherwise.
        """
        keys = playlist.keys()
        if not "name" in keys or not "link" in keys:
            return False
        self.config.read(self.CONFIG_FILE)
        playlistName = playlist["name"]
        playlistLink = playlist["link"]

        self.config[playlistName]={}
        self.config[playlistName]["name"]=playlistName
        self.config[playlistName]["link"]=playlistLink
        self.save()
        return True

    def removePlaylist(self, playlistName:str):
        """
        Removes a playlist from the list of playlists to download.

        Args:
            playlistName (str): The name of the playlist to remove.

        Returns:
            bool: True if the playlist was removed successfully, False otherwise.
        """
        result = False
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        for i in self.config.sections():
               if i == playlistName:
                   self.config.remove_section(i)
                   self.save()
                   result = True
                   break
        return result

    def getUrlOfPlaylist(self, playlistName):
        """
        Gets the URL of the playlist with the given name.

        Args:
            playlistName (str): The name of the playlist.

        Returns:
            str: The URL of the playlist, or None if the playlist doesn't exist.
        """
        playlistUrl = None
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        for section_name in self.config.sections():
            if section_name != "GLOBAL":
                if self.config[section_name]['name'] == playlistName:
                    playlistUrl = self.config[section_name]["link"]

        return playlistUrl

    def save(self): # pragma: no cover
        """
        Saves the configuration to the config file.

        Returns:
            None
        """
        with open(self.CONFIG_FILE,'w') as fp:
            self.config.write(fp)
