from __future__ import unicode_literals
import sys
import os
import argparse
import codecs
import configparser
from collections import defaultdict
from textwrap import dedent
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import metadata_mp3
import unicodedata
import re
import shutil

class PlaylistGenerationConfig:
    """Read global settings and playlist definitions for one target."""

    GLOBAL_SECTION = "GLOBAL"
    GROUPS_SECTION = "PLAYLIST_GROUPS"
    TOP_PLAYLISTS_SECTION = "TOP_PLAYLISTS"

    def __init__(self, config_file):
        if not os.path.isfile(config_file):
            raise FileNotFoundError(
                'playlist configuration file "%s" does not exist' % config_file
            )

        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(config_file)
        self._parser = parser

    def get_global_settings(self):
        """Return global PlaylistsManager settings from the INI file."""
        if self.GLOBAL_SECTION not in self._parser:
            return {
                "musicDir": None,
                "removeCovers": False,
                "isCrLfNeeded": False,
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
            }

        values = {
            key.lower().replace("_", ""): value
            for key, value in self._parser[self.GLOBAL_SECTION].items()
        }

        max_total_size = values.get("maxtotalsizemb", "").strip()
        try:
            max_total_size = float(max_total_size) if max_total_size else None
        except ValueError:
            max_total_size = None

        return {
            "musicDir": values.get("musicdir", "").strip() or None,
            "removeCovers": self._parse_boolean(values.get("removecovers", "false")),
            "isCrLfNeeded": self._parse_boolean(values.get("crlf", "false")),
            "checkMissingWebsite": self._parse_boolean(
                values.get("checkmissingwebsite", "false")
            ),
            "removePolishChars": self._parse_boolean(
                values.get("removepolishchars", "false")
            ),
            "checkCovers": self._parse_boolean(values.get("checkcovers", "false")),
            "checkDuplicates": self._parse_boolean(
                values.get("checkduplicates", "false")
            ),
            "checkTotalSize": self._parse_boolean(
                values.get("checktotalsize", "false")
            ),
            "maxTotalSizeMb": max_total_size,
            "windowsSlash": self._parse_boolean(
                values.get("windowsslash", "false")
            ),
            "garminRootDir": values.get("garminrootdir", "").strip() or None,
            "playlistsDir": values.get("playlistsdir", "").strip() or None,
            "createPlaylistsOfDirs": self._parse_boolean(
                values.get("createplaylistsofdirs", "false")
            ),
        }

    @staticmethod
    def _parse_boolean(value):
        return str(value).strip().lower() in ("1", "yes", "true", "on")

    def get_groups(self):
        """Return ``(playlist_name, folders)`` pairs in configuration order."""
        if self.GROUPS_SECTION not in self._parser:
            return []

        groups = []
        for playlist_name, folders_value in self._parser[self.GROUPS_SECTION].items():
            folders = [folder.strip() for folder in folders_value.split(",")]
            folders = [folder for folder in folders if folder]
            if folders:
                playlist_name = playlist_name.strip()
                limited_name = re.match(
                    r"^(.*)\s+(\d+)\s+hits$", playlist_name, re.IGNORECASE
                )
                if limited_name:
                    groups.append(
                        (
                            limited_name.group(1).strip(),
                            folders,
                            int(limited_name.group(2)),
                        )
                    )
                else:
                    groups.append((playlist_name, folders))
        return groups

    def get_top_playlist_sizes(self):
        """Return positive integer sizes configured for top playlists."""
        if self.TOP_PLAYLISTS_SECTION not in self._parser:
            return []

        sizes = []
        sizes_value = self._parser[self.TOP_PLAYLISTS_SECTION].get("sizes", "")
        for size_value in sizes_value.split(","):
            try:
                size = int(size_value.strip())
            except ValueError:
                continue
            if size > 0:
                sizes.append(size)
        return sizes

    def get_top_playlist_root_dir(self):
        """Return the root directory used for Top playlists, defaulting to the music root."""
        if self.TOP_PLAYLISTS_SECTION not in self._parser:
            return "."

        root_dir = self._parser[self.TOP_PLAYLISTS_SECTION].get("rootDir", ".")
        root_dir = str(root_dir).strip().replace("\\", "/")
        return root_dir or "."


class PlaylistsManager:

    def _resolve_playlists_dir(self, playlists_dir):
        """Return a safe output directory under musicDir."""
        if playlists_dir is None or str(playlists_dir).strip() == "":
            return os.path.abspath(self.musicDir)

        music_root = os.path.abspath(self.musicDir)
        candidate = playlists_dir
        if not os.path.isabs(candidate):
            candidate = os.path.abspath(os.path.join(music_root, candidate))
        else:
            candidate = os.path.abspath(candidate)

        try:
            if os.path.commonpath([music_root, candidate]) != music_root:
                return music_root
        except ValueError:
            return music_root

        return candidate

    def __init__(self, musicDir, playlistsDir=None, windowsSlash=False,
                 playlistsConfigFile=None):
        self.musicDir = musicDir
        self.playlistsDir = None
        self.isCrLfNeeded = False
        self.windowsSlash = windowsSlash
        self.removeCoversEnabled = False
        self.checkMissingWebsiteEnabled = False
        self.removePolishCharsEnabled = False
        self.checkCoversEnabled = False
        self.checkDuplicatesEnabled = False
        self.checkTotalSizeEnabled = False
        self.maxTotalSizeMb = None
        self.garminRootDir = None
        self.createPlaylistsOfDirsEnabled = False
        self.topPlaylistRootDir = "."
        self.playlistsConfig = None

        if playlistsConfigFile is not None:
            self.playlistsConfig = PlaylistGenerationConfig(playlistsConfigFile)
            settings = self.playlistsConfig.get_global_settings()
            if self.musicDir is None:
                self.musicDir = settings.get("musicDir")
            self.isCrLfNeeded = settings["isCrLfNeeded"]
            self.windowsSlash = settings["windowsSlash"]
            self.removeCoversEnabled = settings["removeCovers"]
            self.checkMissingWebsiteEnabled = settings["checkMissingWebsite"]
            self.removePolishCharsEnabled = settings["removePolishChars"]
            self.checkCoversEnabled = settings["checkCovers"]
            self.checkDuplicatesEnabled = settings["checkDuplicates"]
            self.checkTotalSizeEnabled = settings["checkTotalSize"]
            self.maxTotalSizeMb = settings["maxTotalSizeMb"]
            self.garminRootDir = settings["garminRootDir"]
            self.createPlaylistsOfDirsEnabled = settings["createPlaylistsOfDirs"]
            self.topPlaylistRootDir = self.playlistsConfig.get_top_playlist_root_dir()
            if playlistsDir is None and settings.get("playlistsDir"):
                self.playlistsDir = self._resolve_playlists_dir(settings["playlistsDir"])

        if self.musicDir is None:
            raise ValueError("musicDir is required: pass --music-dir or set musicDir in [GLOBAL]")
        if self.playlistsDir is None:
            self.playlistsDir = self._resolve_playlists_dir(playlistsDir)

        #print("isCrLf:", self.isCrLfNeeded)
        #print("music root dir:", self.musicDir, "\n")

    def saveToFile(self, fileName, text):
        """
        Save given text to a file.

        :param fileName: name of the file where the text will be saved
        :param text: text to be saved
        :type fileName: str
        :type text: str
        """
        if self.isCrLfNeeded:
            text = text.replace('\n', '\r\n')
        os.makedirs(self.playlistsDir, exist_ok=True)
        f = codecs.open(os.path.join(self.playlistsDir, fileName),"wb","utf-8")
        f.write(text)
        f.close()

    def showId3Data(self, file_path):
        if not os.path.isfile(file_path):
            return f"ShowId2Data:File {file_path} is not exist"

        try:
            audio = EasyID3(file_path)
            #print(audio)
            return audio
        except Exception:
            print("Excetpion to read id3 data")
            return ""

    def generateHeaderOfM3u(self):
        """
        Generate the header of a M3U file.

        :return: The header of a M3U file as a string
        :rtype: str
        """
        return "#EXTM3U\n"

    def get_tracknumber(self, file_path):
        """
        Get track number from a given file.

        If the file doesn't exist, returns 1.
        If the file doesn't have a track number, returns 1.

        :param file_path: path to the file
        :type file_path: str
        :return: track number of the file
        :rtype: int
        """
        if not os.path.isfile(file_path):
            print("get_tracknumber: File", file_path, "doesn't exist")
            return 1
        try:
            audio = EasyID3(file_path)
            ret = audio.get("tracknumber", [""])[0]
            return int(ret) #audio.get(key, [""])[0]  # Zwraca wartość metadanej lub pusty string
        except Exception as e:
            print("file", file_path, "doesn't have a tracknumber")
            return 1

    def get_date(self, file_path):
        """
        Get date from a given file.

        If the file doesn't exist, returns "2050-01-01".
        If the file doesn't have a date, returns "2050-01-01".

        :param file_path: path to the file
        :type file_path: str
        :return: date of the file
        :rtype: str
        """
        if not os.path.isfile(file_path):
            print("get_date: File", file_path, "doesn't exist")
            return "2050-01-01"
        try:
            audio = EasyID3(file_path)
            ret = audio.get("date", [""])[0]
            return ret #audio.get(key, [""])[0]  # Zwraca wartość metadanej lub pusty string
        except Exception as e:
            print("file", file_path, "doesn't have a date")
            return "2050-01-01"

    def collectSongs(self, path):
        """
        Collect all MP3 files in a given directory and its subdirectories.

        :param path: path to the directory to collect songs from
        :type path: str
        :return: list of paths to MP3 files
        :rtype: list
        """
        filesNameWithPath = []
        fullPath = os.path.join(self.musicDir, path)
        if not os.path.isdir(fullPath):
            print("Wrong path to collect songs:", fullPath, " It was skipped")
            return filesNameWithPath

        for root, dirs, files in os.walk(fullPath):
            for file in files:
                if file.lower().endswith('.mp3'):
                    #print("root", root)
                    fileNameWithPath = os.path.relpath(
                        os.path.join(root, file), self.musicDir
                    )
                    #print("root2", fileNameWithPath)
                    filesNameWithPath.append(fileNameWithPath)

        return filesNameWithPath

    def collectSongsFromDirs(self, folders:list):
        """
        Collect all MP3 files in a given list of directories and its subdirectories.

        :param folders: list of paths to directories to collect songs from
        :type folders: list
        :return: list of paths to MP3 files
        :rtype: list
        """
        listOfFiles = []
        for folder in folders:
            listOfFiles += self.collectSongs(folder)
        return listOfFiles

    def generateM3UList(self, files:list):
        """
        Generate a M3U list from a given list of MP3 files.

        :param files: list of paths to MP3 files
        :type files: list
        :return: M3U list as a string
        :rtype: str
        """
        textFile = ""
        for fileName in files:
            fileNameWithFullPath = os.path.join(self.musicDir, fileName)
            if not os.path.isfile(fileNameWithFullPath):
                print("File", fileNameWithFullPath, "doesn't exist !")
                continue
            audio = MP3(fileNameWithFullPath)
            time = int(round(audio.info.length))
            songName = fileName.replace(".mp3","")
            songName = songName.split("/")[-1]
            textFile+="#EXTINF:%s,%s\n"%(time, songName)
            textFile+="%s\n"%(fileName)
            textFile+="\n"
        if self.windowsSlash:
            textFile = textFile.replace('/', '\\')

        return textFile

    def collectAndGenerateM3UList(self, path:str):
        """
        Collect all MP3 files in a given directory and its subdirectories,
        sort them by track number and generate a M3U list from them.

        :param path: path to the directory to collect songs from
        :type path: str
        :return: M3U list as a string
        :rtype: str
        """
        filesNameWithPath = self.collectSongs(path)
        # one kind of playlist so sort only by track number
        filesNameWithPath = sorted(filesNameWithPath, key= lambda f: (
                self.get_tracknumber(os.path.join(self.musicDir, f))
                ), reverse=True)

        textFile = self.generateM3UList(filesNameWithPath)

        return textFile

# -------------------------------------------------------------------------
    def createPlaylist(self, dirName, playlistName=None):
        textFile = self.generateHeaderOfM3u()
        textFile += self.collectAndGenerateM3UList(dirName)

        playlistFile = "%s.m3u"%(dirName)
        if playlistName is not None:
            playlistFile = "%s.m3u"%(playlistName)
        self.saveToFile(playlistFile, textFile)

    def createPlaylists(self):
        """
        Create playlists for all directories in the given path.

        :return: None
        :rtype: None
        """
        print("Create playlists for dirs start")
        folders = [f for f in os.listdir(self.musicDir) if os.path.isdir(os.path.join(self.musicDir, f))]
        for i in folders:
            self.createPlaylist(i)
        print("Create playlists for dirs end\n")

# -------------------------------------------------------------------------
    def collectAndGenerateGroupOfPlaylists(self, folders:list, limitOfSongs=None):
        """
        Collect all MP3 files in a given list of directories, sort them by date and track number,
        and generate a M3U list from them.

        :param folders: list of directories to collect songs from
        :type folders: list
        :param limitOfSongs: maximum number of songs to include in the M3U list
        :type limitOfSongs: int
        :return: M3U list as a string
        :rtype: str
        """
        songs = self.collectSongsFromDirs(folders)

        songs = sorted(songs, key= lambda f: (
                self.get_date(os.path.join(self.musicDir, f)),
                self.get_tracknumber(os.path.join(self.musicDir,f))
                ), reverse=True)

        if limitOfSongs is not None:
            songs = songs[:limitOfSongs]

        textFile = self.generateHeaderOfM3u()
        textFile += self.generateM3UList(songs)
        return textFile

    def createGroupOfPlaylists(self, playlistName:str, folders:list, limitOfSongs=None):
        """
        Create a group of playlists from a given list of directories, sort them by date and track number,
        and generate a M3U list from them.

        :param playlistName: name of the playlist
        :type playlistName: str
        :param folders: list of directories to collect songs from
        :type folders: list
        :param limitOfSongs: maximum number of songs to include in the M3U list
        :type limitOfSongs: int
        :return: None
        :rtype: None
        """
        print("Create group", playlistName, "start")

        textFile = self.collectAndGenerateGroupOfPlaylists(folders, limitOfSongs)
        if limitOfSongs is not None:
            playlistName = playlistName+" "+str(limitOfSongs)+" hits"

        playlistFile = "%s.m3u"%(playlistName)
        self.saveToFile(playlistFile, textFile)
        print("Create group", playlistName, "end\n")

# -------------------------------------------------------------------------
    def generateTopOfM3UList(self, numberOfSongs, rootDir="."):
        """
        Generate a M3U list from the top numberOfSongs songs in the selected root directory
        sorted by date and track number.

        :param numberOfSongs: maximum number of songs to include in the M3U list
        :type numberOfSongs: int
        :param rootDir: subdirectory under musicDir to scan; default is the whole musicDir
        :type rootDir: str
        :return: M3U list as a string
        :rtype: str
        """
        mp3_files = []
        root_path = self.musicDir if not rootDir or rootDir == "." else os.path.join(self.musicDir, rootDir)
        if not os.path.isdir(root_path):
            return self.generateHeaderOfM3u()

        for dirpath, dirnames, filenames in os.walk(root_path):
            for file in filenames:
                if file.lower().endswith('.mp3'):
                    fileNameWithPath = os.path.join(dirpath, file)
                    mp3_files.append(os.path.relpath(fileNameWithPath, self.musicDir))

        mp3_files = sorted(mp3_files, key= lambda f: (self.get_date(os.path.join(self.musicDir, f)),
                                                      self.get_tracknumber(os.path.join(self.musicDir, f))
                                                      ),
                           reverse=True)

        textFile = self.generateHeaderOfM3u()
        textFile += self.generateM3UList(mp3_files[:numberOfSongs])

        return textFile

    def createTopOfMusic(self, numberOfSongs, isCrLfNeeded=False, rootDir="."):
        print("Create Top", numberOfSongs, "start")
        textFile = self.generateTopOfM3UList(numberOfSongs, rootDir=rootDir)
        playlistFile = "%s Top.m3u"%(str(numberOfSongs))

        self.saveToFile(playlistFile, textFile)
        print("Create Top", numberOfSongs, "end\n")

    def createPlaylistsFromConfig(self, updatedFolders=None):
        """Create configured group and top playlists.

        :param updatedFolders: optional folders changed in the current run;
            only groups containing one of them are generated
        """
        if self.playlistsConfig is None:
            raise ValueError("playlistsConfigFile is required to create configured playlists")

        generationConfig = self.playlistsConfig
        updatedFoldersSet = None if updatedFolders is None else set(updatedFolders)

        root_dir = generationConfig.get_top_playlist_root_dir()
        for numberOfSongs in generationConfig.get_top_playlist_sizes():
            if root_dir == ".":
                self.createTopOfMusic(numberOfSongs)
            else:
                self.createTopOfMusic(numberOfSongs, rootDir=root_dir)

        for group in generationConfig.get_groups():
            playlistName, folders = group[:2]
            limitOfSongs = group[2] if len(group) > 2 else None
            if updatedFoldersSet is not None and not updatedFoldersSet.intersection(folders):
                continue
            if limitOfSongs is None:
                self.createGroupOfPlaylists(playlistName, folders)
            else:
                self.createGroupOfPlaylists(playlistName, folders, limitOfSongs)

class PlaylistsManagerPlayer(PlaylistsManager):
    """Intermediate manager for metadata and file integrity checks."""

    def get_website(self, file_path):
        if not os.path.isfile(file_path):
            return ""

        try:
            audio = EasyID3(file_path)
            #print(audio)
            return audio.get("website", [""])[0].strip()
        except Exception:
            return ""

    def check_missing_website(self):
        """
        Wypisuje wszystkie MP3, które nie mają tagu 'website'.
        """
        missing = []

        for root, _, files in os.walk(self.musicDir):
            for file in files:
                if not file.lower().endswith(".mp3"):
                    continue

                path = os.path.join(root, file)
                website = self.get_website(path)

                if not website:
                    missing.append(path)

        if not missing:
            return []

        print(f"Brak 'website' w {len(missing)} plikach:\n")
        for path in missing:
            print(path)
        return missing

    def getTotalSize(self):
        """
        Zwraca łączny rozmiar wszystkich plików MP3 w MB.
        """
        total_size = 0

        for root, dirs, files in os.walk(self.musicDir):
            for file in files:
                if not file.lower().endswith(".mp3"):
                    continue

                try:
                    total_size += os.path.getsize(os.path.join(root, file))
                except OSError as e:
                    print(f"Cannot read size of {file}: {e}")

        totalSizeMb = total_size / (1024 * 1024)
        return round(totalSizeMb, 2)

    def checkCovers(self, skip_dirs = []):
        metadataMng = metadata_mp3.MetadataManager()
        filesWithoutCovers = []

        for root, dirs, files in os.walk(self.musicDir):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for file in files:
                if not file.lower().endswith(".mp3"):
                    continue

                file_path = os.path.join(root, file)

                hasCover = metadataMng.isCoverOfMp3(file_path)
                if not hasCover:
                    filesWithoutCovers.append(file_path)
                    print("No cover:", file_path)

        return filesWithoutCovers

# -------------------------------------------------------------------------
    def removeCovers(self):
        """
        Remove all covers from all .mp3 files in all subdirectories of the given path.

        :return: None
        :rtype: None
        """
        print("Remove covers start")
        metadataMng = metadata_mp3.MetadataManager()
        folders = [f for f in os.listdir(self.musicDir) if os.path.isdir(os.path.join(self.musicDir, f))]
        for folder in folders:
            files = [g for g in os.listdir(os.path.join(self.musicDir, folder)) if os.path.isfile(os.path.join(self.musicDir,folder, g))]
            for file in files:
                if ".mp3" in file:
                    metadataMng.removeCoverOfMp3(os.path.join(self.musicDir, folder, file))
        print("Remove covers end\n")



    def clean_filename(self, name):
        """
        Clean a filename by removing diacritics, combining characters, non-ASCII characters, and replacing spaces with underscores.

        :param name: the filename to clean
        :return: a cleaned filename
        :rtype: str
        """
        new_name = unicodedata.normalize('NFKD', name)
        # Usuń znaki diakrytyczne (łączone)
        new_name = ''.join(c for c in new_name if not unicodedata.combining(c))
        # Zamień znaki, które nie są rozkładane (np. ł → l)
        new_name = new_name.replace('ł', 'l').replace('Ł', 'L')
        # 2. Usuwanie niedozwolonych znaków
        # Znaki zabronione w nazwach plików w Windows
        invalid_chars = r'[^a-zA-Z0-9 _\-.,()]'
        new_name = re.sub(invalid_chars, '', new_name)

        # 3. Usuwanie nadmiarowych spacji
        new_name = re.sub(r'\s+', ' ', new_name).strip()
        return new_name

    def removePolishChars(self):
        """
        Remove polish characters from all files and directories in the given path.

        :return: None
        :rtype: None
        """
        print("Remove polish chars start")
        for root, dirs, files in os.walk(self.musicDir):
            for name in files:
                new_name = self.clean_filename(name)
                if new_name != name:
                    src = os.path.join(root, name)
                    dst = os.path.join(root, new_name)
                    try:
                        os.rename(src, dst)
                        print(f"Renamed: {name} -> {new_name}")
                    except Exception as e:
                        print(f"Error renaming {name}: {e}")
            for name in dirs:
                new_name = self.clean_filename(name)
                if new_name != name:
                    src = os.path.join(root, name)
                    dst = os.path.join(root, new_name)
                    try:
                        os.rename(src, dst)
                        print(f"Renamed folder: {name} -> {new_name}")
                    except Exception as e:
                        print(f"Error renaming folder {name}: {e}")
        print("Remove polish chars end\n")



    def syncFilesWithoutWebsite(self, sourceDir, destinationDir):
        """
        sourceDir      - katalog z poprawnymi plikami (np. Muzyka)
        destinationDir - katalog do synchronizacji (np. Muzyka Sandisk)

        Jeżeli plik w destination nie ma tagu website, zostaje
        zastąpiony plikiem z source o tej samej nazwie.
        """
        print("Synchronizing files without website tag")

        sourceFiles = {}
        for root, dirs, files in os.walk(sourceDir):
            for file in files:
                if file.lower().endswith(".mp3"):
                    sourceFiles[file.lower()] = os.path.join(root, file)

        copied = 0
        missing = 0

        for root, dirs, files in os.walk(destinationDir):
            for file in files:
                if not file.lower().endswith(".mp3"):
                    continue

                dstPath = os.path.join(root, file)
                website = self.get_website(dstPath)

                if website:
                    continue

                srcPath = sourceFiles.get(file.lower())
                if srcPath is None:
                    print(f"Not found in source: {file}")
                    missing += 1
                    continue

                try:
                    shutil.copy2(srcPath, dstPath)
                    copied += 1
                    print(f"Copied: {srcPath} -> {dstPath}")
                except Exception as e:
                    print(f"Error copying {file}: {e}")

        print(f"\nCopied: {copied}")
        print(f"Missing: {missing}")

    def checkDuplicates(self):
        """
        Sprawdza:
          - duplikaty nazw plików,
          - duplikaty tagu website,
          - pliki bez tagu website.
        """
        filename_index = defaultdict(list)
        website_index = defaultdict(list)

        duplicate_filenames = {}
        duplicate_websites = {}
        missing_websites = []

        for root, dirs, files in os.walk(self.musicDir):
            for file in files:
                if not file.lower().endswith(".mp3"):
                    continue

                fullpath = os.path.join(root, file)
                filename_index[file.lower()].append(fullpath)

                website = self.get_website(fullpath)
                if website:
                    website_index[website].append(fullpath)
                else:
                    missing_websites.append(fullpath)

        for filename, paths in filename_index.items():
            if len(paths) > 1:
                duplicate_filenames[filename] = paths

        for website, paths in website_index.items():
            if len(paths) > 1:
                duplicate_websites[website] = paths

        if missing_websites:
            print("\n========== FILES WITHOUT WEBSITE ==========")
            for path in sorted(missing_websites):
                print(path)

        if duplicate_filenames:
            print("\n========== DUPLICATE FILENAMES ==========")
            for filename in sorted(duplicate_filenames):
                print(f"\n{filename}")
                for path in duplicate_filenames[filename]:
                    print(f"    {path}")

        if duplicate_websites:
            print("\n========== DUPLICATE WEBSITE ==========")
            for website in sorted(duplicate_websites):
                print(f"\n{website}")
                for path in duplicate_websites[website]:
                    print(f"    {path}")

        return duplicate_filenames, duplicate_websites, missing_websites


class GarminPlaylistsManager(PlaylistsManagerPlayer):
    """Garmin-specific playlist helpers extracted from PlaylistsManager."""

    def __init__(self, musicDir, playlistsDir=None, windowsSlash=False,
                 playlistsConfigFile=None):
        super().__init__(musicDir, playlistsDir=playlistsDir,
                         windowsSlash=windowsSlash,
                         playlistsConfigFile=playlistsConfigFile)

    def createPlaylistsAsGarmin(self, garminRootDir):
        count = 0

        for root, dirs, files in os.walk(garminRootDir):
            for file in files:
                if not file.lower().endswith(".m3u"):
                    continue

                playlist = os.path.join(root, file)
                print(f"\nProcessing: {playlist}")
                self.createPlaylistAsGarmin(playlist)
                count += 1

        print(f"\nFinished. Recreated {count} playlists.")

    def createPlaylistAsGarmin(self, sourcePlaylist):
        """
        Create a Garmin-compatible playlist from an existing M3U playlist.
        """
        print("Creating playlists according to:", sourcePlaylist)

        songs = []
        with codecs.open(sourcePlaylist, "r", "utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                songs.append(line)

        print("Songs in playlist:", len(songs))
        print("Indexing music...")

        website_index = {}
        filename_index = {}

        for root, dirs, files in os.walk(self.musicDir):
            for file in files:
                if not file.lower().endswith(".mp3"):
                    continue

                fullpath = os.path.join(root, file)
                website = self.get_website(fullpath)

                if website:
                    website_index[website] = fullpath

                filename_index[file.lower()] = fullpath

        print("Looking for te same songs...")
        foundSongs = []

        for song in songs:
            # Playlist entries are relative to musicDir. Fall back to the
            # source playlist directory for older playlists created before
            # musicDir and playlistsDir were separated.
            oldSong = os.path.join(self.musicDir, song)
            if not os.path.isfile(oldSong):
                oldSong = os.path.join(os.path.dirname(sourcePlaylist), song)
            website = self.get_website(oldSong)

            found = None
            if website:
                found = website_index.get(website)

            if found is None:
                found = filename_index.get(os.path.basename(song).lower())

            if found:
                rel = os.path.relpath(found, self.musicDir)
                rel = rel.replace("\\", "/")
                foundSongs.append(rel)
            else:
                print("NOT FOUND:", oldSong, self.showId3Data(oldSong))

        text = self.generateHeaderOfM3u()
        text += self.generateM3UList(foundSongs)

        outputPlaylist = "Garmin_" + os.path.basename(sourcePlaylist)
        self.saveToFile(outputPlaylist, text)
        print("Created:", outputPlaylist)


CONFIG_HELP = dedent(
    """
    FORMAT PLIKU KONFIGURACYJNEGO
    =============================

    Przykładowy kompletny plik playlists.ini:

    # Ustawienia wspólne dla generatora playlist.
    [GLOBAL]
    # Główny katalog z plikami MP3. Można podać tutaj albo w argumencie --music-dir.
    musicDir = /ścieżka/muzyka
    # Usuń osadzone okładki z plików MP3.
    removeCovers = false
    # Zapisuj pliki M3U z zakończeniami linii CRLF.
    CrLf = false
    # Wyświetl pliki MP3 bez tagu "website".
    checkMissingWebsite = false
    # Usuń polskie znaki i niedozwolone znaki z nazw plików i katalogów.
    removePolishChars = false
    # Wyświetl pliki MP3 bez okładek.
    checkCovers = false
    # Sprawdź duplikaty nazw plików i tagów "website".
    checkDuplicates = false
    # Sprawdź łączny rozmiar plików MP3.
    checkTotalSize = false
    # Maksymalny rozmiar w MB; działa razem z checkTotalSize = true.
    maxTotalSizeMb =
    # Używaj ukośników Windows (\\) w ścieżkach playlist M3U.
    windowsSlash = false
    # Twórz playlisty z nazw katalogów (po jednym pliku .m3u na katalog).
    # Wymagane tylko wtedy, gdy chcesz generować playlisty typu folder/
    # katalog-muzyka.
    createPlaylistsOfDirs = false
    # Katalog, do którego zapisane będą wygenerowane playlisty.
    # Domyślnie używany jest ten sam katalog co musicDir.
    # Dopuszczalny jest tylko katalog wewnątrz musicDir.
    playlistsDir = /ścieżka/do/playlist
    # Katalog z playlistami źródłowymi dla generatora playlist Garmin.
    # Pozostaw pusty, jeśli playlisty Garmin nie mają być tworzone.
    garminRootDir =

    # Każdy wpis tworzy playlistę z plików MP3 z wymienionych katalogów.
    # Katalogi oddziel przecinkami; nazwa po lewej stronie jest nazwą playlisty.
    [PLAYLIST_GROUPS]
    trening = imprezka, techno, relaks
    praca = relaks, chillout
    # Sufiks "N hits" ogranicza playlistę do N utworów.
    trening 40 hits = imprezka, techno, relaks

    # Twórz playlisty Top z N najnowszych/najwyżej sklasyfikowanych utworów.
    # rootDir ogranicza skanowanie do wybranego katalogu wewnątrz musicDir.
    # Domyślnie rootDir = . (cały musicDir).
    [TOP_PLAYLISTS]
    sizes = 20, 100, 200
    rootDir = .

    URUCHOMIENIE
    ============

    playlists-manager \\
      --config /ścieżka/playlists.ini \\
      --music-dir /ścieżka/muzyka

    Wartości globalne z [GLOBAL] mogą zawierać m.in.:
    - createPlaylistsOfDirs — gdy ustawione na true, tworzy osobne playlisty dla każdego katalogu w musicDir,
    - playlistsDir — miejsce zapisu wygenerowanych playlist M3U,
    - garminRootDir — katalog z playlistami źródłowymi Garmin,
    - windowsSlash, CrLf i inne flagi formatowania oraz kontroli.

    Więcej informacji o formacie:
    - [GLOBAL] zawiera ustawienia kontroli, czyszczenia, katalogu docelowego i formatowania playlist,
    - [PLAYLIST_GROUPS] mapuje nazwę playlisty na listę katalogów z muzyką,
    - [TOP_PLAYLISTS] definiuje rozmiary playlist Top oraz opcjonalny rootDir do ograniczenia skanowania do jednego katalogu wewnątrz musicDir.
    """
).strip()


def test(configFile, musicPath):
    manager = PlaylistsManager(musicPath, playlistsConfigFile=configFile)
    manager.createPlaylistsFromConfig()

def testCover():
    manager = PlaylistsManager("/media/bartosz/MB57/Music")
    #manager = PlaylistsManager("/mnt/kingston/media/muzyka/")
    metadataManager = metadata_mp3.MetadataManager()

    songsNoCovers = manager.checkCovers(skip_dirs=["taniec", "wesele", "świąteczne", "z filmów"])
#    for x in songsNoCovers:
#        website = manager.get_website(x)
#        if website:
#            hash = website.split("/")[-1]
#            metadataManager.addCoverOfYtMp3(x, hash)
#        else:
#            print("File:", x, "Website:", website)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="playlists-manager",
        description=(
            "Generuje playlisty M3U na podstawie plików MP3 oraz konfiguracji INI. "
            "Może również wykonać kontrole plików, przygotować playlisty Top "
            "i utworzyć playlisty zgodne z Garminem."
        ),
        epilog=(
            "Przykład:\n"
            "  playlists-manager --config /ścieżka/playlists.ini "
            "--music-dir /ścieżka/muzyka\n\n"
            "Plik INI może zawierać sekcje [GLOBAL], [PLAYLIST_GROUPS] "
            "i [TOP_PLAYLISTS]."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="FILE",
        help="ścieżka do pliku konfiguracyjnego INI",
    )
    parser.add_argument(
        "-d",
        "--musicDir",
        "--music-dir",
        dest="music_dir",
        metavar="DIR",
        help="główny katalog z plikami MP3",
    )
    parser.add_argument(
        "--config-help",
        action="store_true",
        help="wyświetl szczegółowy opis formatu INI i kompletny przykład konfiguracji",
    )

    args = parser.parse_args(argv)

    if args.config_help:
        print(CONFIG_HELP)
        return

    if args.config is None:
        parser.error("argument -c/--config jest wymagany")

    configFile = args.config
    if not os.path.isfile(configFile):
        parser.error("plik konfiguracyjny nie istnieje: %s" % configFile)

    config_values = PlaylistGenerationConfig(configFile).get_global_settings()
    musicDirArgument = args.music_dir or config_values.get("musicDir")
    if musicDirArgument is None:
        parser.error(
            "argument -d/--music-dir jest wymagany albo musi być ustawiony w [GLOBAL] musicDir"
        )

    manager = PlaylistsManagerPlayer(
        musicDirArgument,
        playlistsConfigFile=configFile,
    )
    if manager.checkMissingWebsiteEnabled:
        manager.check_missing_website()
    if manager.checkCoversEnabled:
        manager.checkCovers()
    if manager.removeCoversEnabled:
        manager.removeCovers()
    if manager.removePolishCharsEnabled:
        manager.removePolishChars()
    if manager.createPlaylistsOfDirsEnabled:
        manager.createPlaylists()
    manager.createPlaylistsFromConfig()
    if manager.checkDuplicatesEnabled:
        manager.checkDuplicates()
    if manager.checkTotalSizeEnabled:
        totalSize = manager.getTotalSize()
        print("Total size:", totalSize, "Mb")
        if manager.maxTotalSizeMb is not None and totalSize > manager.maxTotalSizeMb:
            print(
                "Warning, total size is greater than",
                manager.maxTotalSizeMb,
                "Mb",
            )
            return
    if manager.garminRootDir:
        garminManager = GarminPlaylistsManager(
            musicDirArgument,
            playlistsConfigFile=configFile,
        )
        garminManager.createPlaylistsAsGarmin(manager.garminRootDir)


if __name__ == '__main__':
    main(sys.argv[1:])
