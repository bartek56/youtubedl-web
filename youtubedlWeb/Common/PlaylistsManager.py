from __future__ import unicode_literals
import sys
import os
import getopt
import codecs
from collections import defaultdict
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import metadata_mp3
import unicodedata
import re
import shutil


class PlaylistsManager:

    def __init__(self, playlistsDir, isCrLfNeeded=False, windowsSlash=False):
        self.dir = playlistsDir
        self.isCrLfNeeded = isCrLfNeeded
        self.windowsSlash = windowsSlash

        #print("isCrLf:", self.isCrLfNeeded)
        #print("root dir:", self.dir, "\n")

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
        f = codecs.open(os.path.join(self.dir, fileName),"wb","utf-8")
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
        fullPath = os.path.join(self.dir, path)
        if not os.path.isdir(fullPath):
            print("Wrong path to collect songs:", fullPath, " It was skipped")
            return filesNameWithPath

        for root, dirs, files in os.walk(fullPath):
            for file in files:
                if file.lower().endswith('.mp3'):
                    #print("root", root)
                    fileNameWithPath=os.path.join(root,file).replace(self.dir+"/", "")
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
            fileNameWithFullPath="%s/%s"%(self.dir, fileName)
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
                self.get_tracknumber(os.path.join(self.dir, f))
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
        folders = [f for f in os.listdir(self.dir) if os.path.isdir(os.path.join(self.dir, f))]
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
                self.get_date(os.path.join(self.dir, f)),
                self.get_tracknumber(os.path.join(self.dir,f))
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
    def generateTopOfM3UList(self, numberOfSongs):
        """
        Generate a M3U list from the top numberOfSongs songs in the music directory sorted by date and track number.

        :param numberOfSongs: maximum number of songs to include in the M3U list
        :type numberOfSongs: int
        :return: M3U list as a string
        :rtype: str
        """
        mp3_files = []

        for dirpath, dirnames, filenames in os.walk(self.dir):
            for file in filenames:
                if file.lower().endswith('.mp3'):
                    fileNameWithPath = os.path.join(dirpath, file)
                    mp3_files.append(fileNameWithPath.replace(self.dir+"/", ""))


        mp3_files = sorted(mp3_files, key= lambda f: (self.get_date(os.path.join(self.dir, f)),
                                                      self.get_tracknumber(os.path.join(self.dir, f))
                                                      ),
                           reverse=True)

        textFile = self.generateHeaderOfM3u()
        textFile += self.generateM3UList(mp3_files[:numberOfSongs])

        return textFile

    def createTopOfMusic(self, numberOfSongs, isCrLfNeeded=False):
        print("Create Top", numberOfSongs, "start")
        textFile = self.generateTopOfM3UList(numberOfSongs)
        playlistFile = "%s Top.m3u"%(str(numberOfSongs))

        self.saveToFile(playlistFile, textFile)
        print("Create Top", numberOfSongs, "end\n")


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

        for root, _, files in os.walk(self.dir):
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

        for root, dirs, files in os.walk(self.dir):
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

        for root, dirs, files in os.walk(self.dir):
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
        folders = [f for f in os.listdir(self.dir) if os.path.isdir(os.path.join(self.dir, f))]
        for folder in folders:
            files = [g for g in os.listdir(os.path.join(self.dir, folder)) if os.path.isfile(os.path.join(self.dir,folder, g))]
            for file in files:
                if ".mp3" in file:
                    metadataMng.removeCoverOfMp3(os.path.join(self.dir, folder, file))
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
        for root, dirs, files in os.walk(self.dir):
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

        for root, dirs, files in os.walk(self.dir):
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

    def __init__(self, playlistsDir, isCrLfNeeded=False, windowsSlash=False):
        super().__init__(playlistsDir, isCrLfNeeded=isCrLfNeeded, windowsSlash=windowsSlash)

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

        for root, dirs, files in os.walk(self.dir):
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
            oldSong = os.path.join(os.path.dirname(sourcePlaylist), song)
            website = self.get_website(oldSong)

            found = None
            if website:
                found = website_index.get(website)

            if found is None:
                found = filename_index.get(os.path.basename(song).lower())

            if found:
                rel = os.path.relpath(found, self.dir)
                rel = rel.replace("\\", "/")
                foundSongs.append(rel)
            else:
                print("NOT FOUND:", oldSong, self.showId3Data(oldSong))

        text = self.generateHeaderOfM3u()
        text += self.generateM3UList(foundSongs)

        outputPlaylist = "Garmin_" + os.path.basename(sourcePlaylist)
        self.saveToFile(outputPlaylist, text)
        print("Created:", outputPlaylist)


def test():
    manager = PlaylistsManager("/home/bartosz/Music/Sandisk_music_128", isCrLfNeeded=True)
#    manager.removeCovers()
#    manager.createPlaylists()
#    manager.createPlaylistAsGarmin("/home/bartosz/Music/Garmin5_music_128/Bachata.m3u")

    folders=["UrbanKiz"]
    manager.createGroupOfPlaylists("taniec", folders)

    manager.createTopOfMusic(30)
    manager.createTopOfMusic(100)
#    manager.syncFilesWithoutWebsite("/home/bartosz/Music/MediaServer", "/home/bartosz/Music/Sandisk_music")

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


def main(argv):
    isSandisk = False
    isGarmin = False
    isMediaserver = False
    HELP = "createPlaylists.py --garmin/--sandisk/--mediaserver"

    try:
        opts, args = getopt.getopt(argv,"hgs",["garmin","sandisk", "mediaserver"])
    except getopt.GetoptError:
        print (HELP)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print (HELP)
            sys.exit()
        elif opt in ("-g", "--garmin"):
            isGarmin=True
            print ("garmin")
        elif opt in ("-s", "--sandisk"):
            isSandisk = True
            print("sandisk")
        elif opt in ("-m", "--mediaserver"):
            isMediaserver = True
            print("MediaServer")
    path = os.path.abspath(os.getcwd())

    if isMediaserver:
        manager = PlaylistsManager(path)
        manager.createPlaylists()

        folders=["imprezka","techno","Rock-Electronic","relaks","stare hity"]
        manager.createGroupOfPlaylists("trening", folders)

        folders=["relaks","chillout","spokojne-sad","cafe","chillout"]
        manager.createGroupOfPlaylists("praca", folders)

        folders=["Bachata","Bachata Dominikana","Kizomba","latino","Semba"]
        manager.createGroupOfPlaylists("taniec", folders)

        manager.createTopOfMusic(100)

    if isSandisk:
        manager = PlaylistsManager(path, isCrLfNeeded=True)
        manager.removeCovers()
        manager.createPlaylists()

        folders=["UrbanKiz"]
        manager.createGroupOfPlaylists("taniec", folders)

        manager.createTopOfMusic(30)
        manager.createTopOfMusic(100)
        manager.createTopOfMusic(200)

    if isGarmin:
        manager = PlaylistsManager(path)
        manager.removeCovers()
        manager.createPlaylists()

        folders=["imprezka","techno","Rock-Electronic", "relaks"]
        manager.createGroupOfPlaylists("trening", folders)

        folders=["relaks","chillout","spokojne-sad"]
        manager.createGroupOfPlaylists("praca", folders)

        manager.createTopOfMusic(30)


if __name__ == '__main__':
    main(sys.argv[1:])
