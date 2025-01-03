from __future__ import unicode_literals
import sys
import os
import getopt
import codecs
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

class PlaylistsManager:

    def __init__(self, playlistsDir):
        self.dir = playlistsDir

    def saveToFile(self, fileName, text):
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
            print("Wrong path to generate M3U list")
            return filesNameWithPath

        fileNames = [f for f in os.listdir(fullPath) if f.endswith('.mp3')]

        for file in fileNames:
            filesNameWithPath.append(os.path.join(path, file))
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

        filesNameWithPath = sorted(filesNameWithPath, key= lambda f: (
                self.get_tracknumber(os.path.join(self.dir, f)),
                self.get_date(os.path.join(self.dir, f))
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
        folders = [f for f in os.listdir(self.dir) if os.path.isdir(os.path.join(self.dir, f))]
        for i in folders:
            self.createPlaylist(i)

# -------------------------------------------------------------------------
    def collectAndGenerateGroupOfPlaylists(self, folders:list):
        songs = self.collectSongsFromDirs(folders)

        songs = sorted(songs, key= lambda f: (
                self.get_date(os.path.join(self.dir, f)),
                self.get_tracknumber(os.path.join(self.dir, f))
                ), reverse=True)

        textFile = self.generateHeaderOfM3u()
        textFile += self.generateM3UList(songs)
        return textFile

    def createGroupOfPlaylistsForGarmin(self, playlistName:str, folders:list):

        textFile = self.collectAndGenerateGroupOfPlaylists(folders)

        playlistFile = "%s.m3u"%(playlistName)
        self.saveToFile(playlistFile, textFile)

    def createGroupOfPlaylistsForSandisk(self, playlistName:str, folders:list):
        textFile = self.collectAndGenerateGroupOfPlaylists(folders)

        textFile.replace("\n", "\r\n")
        playlistFile = "%s.m3u"%(playlistName)
        self.saveToFile(playlistFile, textFile)

# -------------------------------------------------------------------------
    def generateTopOfM3UList(self, numberOfSongs):
            mp3_files = []

            for dirpath, dirnames, filenames in os.walk(self.dir):
                for file in filenames:
                    if file.lower().endswith('.mp3'):
                        fileNameWithPath = os.path.join(dirpath, file)
                        mp3_files.append(fileNameWithPath.replace(self.dir+"/", ""))


            mp3_files = sorted(mp3_files, key= lambda f: (self.get_date(os.path.join(self.dir, f))),
                               reverse=True)

            textFile = self.generateHeaderOfM3u()
            textFile += self.generateM3UList(mp3_files[:numberOfSongs])

            return textFile

    def createTopOfMusic(self, numberOfSongs):
            textFile = self.generateTopOfM3UList(numberOfSongs)

            playlistFile = "%s Top.m3u"%(str(numberOfSongs))

            self.saveToFile(playlistFile, textFile)

    def createTopOfMusicSandisk(self, numberOfSongs):
            textFile = self.generateTopOfM3UList(numberOfSongs)

            playlistFile = "%s Top.m3u"%(str(numberOfSongs))
            textFile.replace("\n", "\r\n")

            self.saveToFile(playlistFile, textFile)

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
    manager = PlaylistsManager(path)
    if isMediaserver:
        listDir = [name for name in os.listdir(".") if os.path.isdir(os.path.join(".", name))]
        for x in listDir:
            manager.createPlaylist(x)
        manager.createTopOfMusic(100)

    if isSandisk:
        folders=["Bachata","Kizomba","Semba","salsa"]
        manager.createGroupOfPlaylistsForSandisk("taniec", folders)

        folders=["imprezka","techno","Rock-Electronic", "relaks"]
        manager.createGroupOfPlaylistsForSandisk("trening", folders)

        folders=["relaks", "chillout", "spokojne-sad", "Rock-Electronic"]
        manager.createGroupOfPlaylistsForSandisk("praca", folders)

        manager.createTopOfMusicSandisk(30)
        manager.createTopOfMusicSandisk(100)
        manager.createTopOfMusicSandisk(200)

    if isGarmin:
        manager.createPlaylists()
        folders=["imprezka","techno","Rock-Electronic", "relaks"]
        manager.createGroupOfPlaylistsForGarmin("trening", folders)

        folders=["relaks", "chillout", "spokojne-sad"]
        manager.createGroupOfPlaylistsForGarmin("praca", folders)

        manager.createTopOfMusic(30)


if __name__ == '__main__':
    main(sys.argv[1:])
