from __future__ import unicode_literals
import sys
import os
import getopt
import codecs
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import metadata_mp3
import unicodedata
import re

class PlaylistsManager:

    def __init__(self, playlistsDir, isCrLfNeeded=False):
        self.dir = playlistsDir
        self.isCrLfNeeded = isCrLfNeeded

        #print("isCrLf:", self.isCrLfNeeded)
        #print("root dir:", self.dir, "\n")

    def saveToFile(self, fileName, text):
        if self.isCrLfNeeded:
            text = text.replace('\n', '\r\n')
        f = codecs.open(os.path.join(self.dir, fileName),"wb","utf-8")
        f.write(text)
        f.close()

    def generateHeaderOfM3u(self):
        return "#EXTM3U\n"

    def get_tracknumber(self, file_path):
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
        listOfFiles = []
        for folder in folders:
            listOfFiles += self.collectSongs(folder)
        return listOfFiles

    def generateM3UList(self, files:list):
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

        return textFile

    def collectAndGenerateM3UList(self, path:str):

        filesNameWithPath = self.collectSongs(path)
        # one kind of playlist so sort only by track number
        filesNameWithPath = sorted(filesNameWithPath, key= lambda f: (
                self.get_tracknumber(os.path.join(self.dir, f))
                ), reverse=True)

        textFile = self.generateM3UList(filesNameWithPath)

        return textFile

# -------------------------------------------------------------------------
    def createPlaylist(self, dirName):
        textFile = self.generateHeaderOfM3u()
        textFile += self.collectAndGenerateM3UList(dirName)

        playlistFile = "%s.m3u"%(dirName)
        self.saveToFile(playlistFile, textFile)

    def createPlaylists(self):
        print("Create playlists for dirs start")
        folders = [f for f in os.listdir(self.dir) if os.path.isdir(os.path.join(self.dir, f))]
        for i in folders:
            self.createPlaylist(i)
        print("Create playlists for dirs end\n")

# -------------------------------------------------------------------------
    def removeCovers(self):
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

# -------------------------------------------------------------------------
    def collectAndGenerateGroupOfPlaylists(self, folders:list, limitOfSongs=None):
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
        print("Create group", playlistName, "start")

        textFile = self.collectAndGenerateGroupOfPlaylists(folders, limitOfSongs)
        if limitOfSongs is not None:
            playlistName = playlistName+" "+str(limitOfSongs)+" hits"

        playlistFile = "%s.m3u"%(playlistName)
        self.saveToFile(playlistFile, textFile)
        print("Create group", playlistName, "end\n")

# -------------------------------------------------------------------------
    def generateTopOfM3UList(self, numberOfSongs):
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
