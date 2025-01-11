import configparser
import os
import logging
from typing import List

from .YoutubeTypes import PlaylistConfig

logger = logging.getLogger(__name__)

class YoutubeConfig:
    def __init__(self):
        pass

    def initialize(self, configFile, parser = configparser.ConfigParser()):
        if not os.path.isfile(configFile):
            logger.error("Config file \"%s\" doesn't exist", configFile)
        self.CONFIG_FILE = configFile
        self.config = parser

    def getPath(self):
        path = None
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        if "GLOBAL" in self.config.sections():
            path = self.config["GLOBAL"]['path']
        return path

    def setPath(self, path):
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        if "GLOBAL" not in self.config:
            self.config.add_section("GLOBAL")
        self.config["GLOBAL"]["path"] = path
        self.save()

    def getPlaylists(self) -> List[PlaylistConfig]:
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        data = []

        for section_name in self.config.sections():
            if section_name != "GLOBAL":
                data.append(PlaylistConfig(self.config[section_name]['name'], self.config[section_name]['link']))
        return data

    def getPlaylistsName(self):
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        data = []

        for section_name in self.config.sections():
            if section_name != "GLOBAL":
                data.append(self.config[section_name]['name'])
        return data

    def addPlaylist(self, playlist:dict):
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
        playlistUrl = None
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        for section_name in self.config.sections():
            if section_name != "GLOBAL":
                if self.config[section_name]['name'] == playlistName:
                    playlistUrl = self.config[section_name]["link"]

        return playlistUrl

    def save(self): # pragma: no cover
        with open(self.CONFIG_FILE,'w') as fp:
            self.config.write(fp)
