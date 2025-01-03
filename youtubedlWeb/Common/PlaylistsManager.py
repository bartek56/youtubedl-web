from __future__ import unicode_literals
import sys
import os
import getopt
import codecs
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import metadata_mp3

class PlaylistsManager:

    def __init__(self, playlistsDir):
        self.dir = playlistsDir

    def _generateHeaderOfM3u(self):
        return "#EXTM3U\n"

    def _generateM3UListOfFiles(self, files:list):
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

    def generateM3UListOfFiles(self, path:str):
        fullPath = os.path.join(self.dir, path)
        if not os.path.isdir(fullPath):
            print("Wrong path to generate M3U list")
            return ""

        fileNames = [f for f in os.listdir(fullPath) if f.endswith('.mp3')]

        filesNameWithPath = []
        for file in fileNames:
            filesNameWithPath.append(os.path.join(path, file))

        #TODO more options to sorting
        filesNameWithPath = sorted(filesNameWithPath, key= lambda f: (
                self.get_tracknumber(os.path.join(self.dir, f)),
                self.get_date(os.path.join(self.dir, f))
                ), reverse=True)

        textFile = self._generateM3UListOfFiles(filesNameWithPath)

        return textFile

    def generateM3UTextFromListOfMp3Files(self, files:list):
        textFile = self._generateHeaderOfM3u()
        textFile += self._generateM3UListOfFiles(files, self.dir)
        return textFile

    def _saveToFile(self, fileName, text):
        f = codecs.open(os.path.join(self.dir, fileName),"wb","utf-8")
        f.write(text)
        f.close()

    def createPlaylist(self, dirName):
        textFile = self._generateHeaderOfM3u()
        textFile += self.generateM3UListOfFiles(dirName)

        playlistFile = "%s.m3u"%(dirName)
        self._saveToFile(playlistFile, textFile)

    def createPlaylists(self):
        folders = [f for f in os.listdir(self.dir) if os.path.isdir(os.path.join(self.dir, f))]
        for i in folders:
            self.createPlaylist(i)

    def createPlaylistForGarmin(self, folders, listName):

        textFile=self._generateHeaderOfM3u()

        for folder in folders:
            #TODO sort al track by trackID, skip playlists sorting
            textFile += self.generateM3UListOfFiles(folder)

        playlistFile = "%s.m3u"%(listName)
        self._saveToFile(playlistFile, textFile)

    def createPlaylistForSandisk(self, folders, listName):
        textFile=self._generateHeaderOfM3u()

        for folder in folders:
            #TODO sort al track by trackID, skip playlists sorting
            textFile += self.generateM3UListOfFiles(folder)

        textFile.replace("\n", "\r\n")

        playlistFile = "%s.m3u"%(listName)
        self._saveToFile(playlistFile, textFile)

    def get_tracknumber(self, file_path):
            if not os.path.isfile(file_path):
                print("get_tracknumber: File", file_path, "doesn't exist")
                return 1
            try:
                audio = EasyID3(file_path)
                ret = audio.get("tracknumber", [""])[0]
    #            print(ret)
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

    def createPlaylistForMediaserver(self, listName):
        textFile = ""

        textFile = self._generateHeaderOfM3u()
        textFile += self.generateM3UListOfFiles(listName)

        playlistFile = "%s.m3u"%(listName)
        self._saveToFile(playlistFile, textFile)

    def generateTopOfM3UList(self, numberOfSongs):
            mp3_files = []

            for dirpath, dirnames, filenames in os.walk(self.dir):
                for file in filenames:
                    if file.lower().endswith('.mp3'):
                        fileNameWithPath = os.path.join(dirpath, file)
                        mp3_files.append(fileNameWithPath.replace(self.dir+"/", ""))


            mp3_files = sorted(mp3_files, key= lambda f: (self.get_date(os.path.join(self.dir, f))),
    #                                                      get_tracknumber(f)),
                               reverse=True)

            top100 = (mp3_files[:numberOfSongs])

            textFile = self._generateHeaderOfM3u()
            textFile += self._generateM3UListOfFiles(mp3_files[:numberOfSongs])

            return textFile

    def createTopOfMusicGarmin(self):
            numberOfSongs=30

            textFile = self.generateTopOfM3UList(numberOfSongs)

            playlistFile = "%s Top.m3u"%(str(numberOfSongs))

            self._saveToFile(playlistFile, textFile)

    def createTopOfMusic(self, numberOfSongs):
            textFile = self.generateTopOfM3UList(numberOfSongs)

            playlistFile = "%s Top.m3u"%(str(numberOfSongs))
            textFile.replace("\n", "\r\n")

            self._saveToFile(playlistFile, textFile)

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
            manager.createPlaylistForMediaserver(x)
        manager.createTopOfMusic(100)

    if isSandisk:
        folders=list()
        folders.append("Bachata")
        folders.append("Kizomba")
        folders.append("Semba")
        folders.append("salsa")
        manager.createPlaylistForSandisk(folders,"taniec")

        folders=list()
        folders.append("imprezka")
        folders.append("techno")
        folders.append("Rock-Electronic")
        folders.append("relaks")
        manager.createPlaylistForSandisk(folders,"trening")

        folders=list()
        folders.append("relaks")
        folders.append("chillout")
        folders.append("spokojne-sad")
        folders.append("Rock-Electronic")
        manager.createPlaylistForSandisk(folders,"praca")

        manager.createTopOfMusic(30)
        manager.createTopOfMusic(100)
        manager.createTopOfMusic(200)

    if isGarmin:
        manager.createPlaylists()
        folders=list()
        folders.append("imprezka")
        folders.append("techno")
        folders.append("Rock-Electronic")
        folders.append("relaks")
        manager.createPlaylistForGarmin(folders,"trening")

        folders=list()
        folders.append("relaks")
        folders.append("chillout")
        folders.append("spokojne-sad")
        manager.createPlaylistForGarmin(folders,"praca")

        manager.createTopOfMusicGarmin()


if __name__ == '__main__':
    main(sys.argv[1:])
