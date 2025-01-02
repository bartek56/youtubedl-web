from __future__ import unicode_literals
import sys
import os
import getopt
import codecs
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import metadata_mp3

class PlaylistsManager:

    def __init__(self, youtubeplaylistsDir="."):
        self.dir = youtubeplaylistsDir


    def createPlaylist(dirName):
        PATH = os.path.abspath(os.getcwd())
        path = "%s/%s"%(PATH,dirName)
        fileNames = [f for f in os.listdir(path) if f.endswith('.mp3')]


        textFile="#EXTM3U\n"
        for fileName in fileNames:
            fileNameWithPath="%s/%s"%(dirName, fileName)
            fileNameWithFullPath="%s/%s"%(path, fileName)
            audio = MP3(fileNameWithFullPath)
            time = int(round(audio.info.length))
            songName = fileName.replace(".mp3","")
            textFile+="#EXTINF:%s,%s\n"%(time,songName)
            textFile+="%s\n"%(fileNameWithPath)
            textFile+="\n"

            playlistFile = "%s.m3u"%(dirName)
            f = codecs.open(playlistFile,"wb","utf-8")
            f.write(textFile)
            f.close()

    def createPlaylists(self):
        dirName = os.path.abspath(os.getcwd())
        folders = [f for f in os.listdir(dirName) if os.path.isdir(os.path.join(dirName, f))]
        for i in folders:
            self.createPlaylist(i)

    def createPlaylistForGarmin(self, folders, listName):
        PATH=os.path.abspath(os.getcwd())

        textFile="#EXTM3U\n"

        for folder in folders:
            path="%s/%s"%(PATH,folder)
            fileNames = [f for f in os.listdir(path) if f.endswith('.mp3')]

            for fileName in fileNames:
                fileNameWithPath="%s/%s"%(folder, fileName)
                fileNameWithFullPath="%s/%s"%(path, fileName)
                audio = MP3(fileNameWithFullPath)
                time = int(round(audio.info.length))
                songName = fileName.replace(".mp3","")
                textFile+="#EXTINF:%s,%s\n"%(time,songName)
                textFile+="%s\n"%(fileNameWithPath)
                textFile+="\n"

        playlistFile = "%s.m3u"%(listName)
        f = codecs.open(playlistFile,"w+","utf-8")
        f.write(textFile)
        f.close()


    def createPlaylistForSandisk(self, folders, listName):
        PATH=os.path.abspath(os.getcwd())

        textFile="#EXTM3U\r\n"

        for folder in folders:
            path="%s/%s"%(PATH,folder)
            fileNames = [f for f in os.listdir(path) if f.endswith('.mp3')]


            for fileName in fileNames:
                fileNameWithPath="%s/%s"%(folder, fileName)
                fileNameWithFullPath="%s/%s"%(path, fileName)
                audio = MP3(fileNameWithFullPath)
                time = int(round(audio.info.length))
                songName = fileName.replace(".mp3","")
                textFile+="#EXTINF:%s,%s\r\n"%(time,songName)
                textFile+="%s\r\n"%(fileNameWithPath)
                textFile+="\r\n"

        playlistFile = "%s.m3u"%(listName)
        f = codecs.open(playlistFile,"wb","utf-8")
        f.write(textFile)
        f.close()

    def get_tracknumber(self, file_path):
            try:
                audio = EasyID3(file_path)
                ret = audio.get("tracknumber", [""])[0]
    #            print(ret)
                return int(ret) #audio.get(key, [""])[0]  # Zwraca wartość metadanej lub pusty string
            except Exception as e:
                print("file", file_path, "doesn't have a tracknumber")
                return 1

    def get_date(self, file_path):
            try:
                audio = EasyID3(file_path)
                ret = audio.get("date", [""])[0]
    #            print(ret)
                return ret #audio.get(key, [""])[0]  # Zwraca wartość metadanej lub pusty string
            except Exception as e:
                print("file", file_path, "doesn't have a date")
                return "2050-01-01"


    def createPlaylistForMediaserver(self, folders, listName):

        textFile="#EXTM3U\r\n"

        for folder in folders:
            path="%s/%s"%(self.dir,folder)
            fileNames = [f for f in os.listdir(path) if f.endswith('.mp3')]

            filesList = []
            for fileName in fileNames:
                fileNameWithPath="%s/%s"%(folder, fileName)
                fileNameWithFullPath="%s/%s"%(path, fileName)
                filesList.append(fileNameWithFullPath)

            filesList = sorted(filesList, key= lambda f: (
                self.get_tracknumber(f),
                self.get_date(f)
                ), reverse=True)


            for fileName in filesList:
                audio = MP3(fileName)
                time = int(round(audio.info.length))
                fileName = fileName.replace(self.dir, ".")
                songName = fileName.replace(".mp3","")
                textFile+="#EXTINF:%s,%s\r\n"%(time,songName)
                textFile+="%s\r\n"%(fileName)
                textFile+="\r\n"

        playlistFile = "%s.m3u"%(listName)
        f = codecs.open(os.path.join(self.dir, playlistFile),"wb","utf-8")
        f.write(textFile)
        f.close()

    def createTopOfMusicGarmin(self):
            numberOfSongs=30
            mp3_files = []

            for dirpath, dirnames, filenames in os.walk(self.dir):
                for file in filenames:
                    if file.lower().endswith('.mp3'):
                        mp3_files.append(os.path.join(dirpath, file))


            mp3_files = sorted(mp3_files, key= lambda f: (self.get_date(f)),
    #                                                      get_tracknumber(f)),
                               reverse=True)

            top100 = (mp3_files[:numberOfSongs])
            textFile="#EXTM3U\n"

            for fileName in top100:
                audio = MP3(fileName)
                time = int(round(audio.info.length))
                songName = fileName.replace(".mp3","")
                textFile+="#EXTINF:%s,%s\n"%(time,songName)
                textFile+="%s\n"%(fileName)
                textFile+="\n"

            playlistFile = "%s Top.m3u"%(str(numberOfSongs))
            f = codecs.open(playlistFile,"wb","utf-8")
            f.write(textFile)
            f.close()

    def createTopOfMusic(self, numberOfSongs):
            mp3_files = []

            for dirpath, dirnames, filenames in os.walk(self.dir):
                for file in filenames:
                    if file.lower().endswith('.mp3'):
                        mp3_files.append(os.path.join(dirpath, file))


            mp3_files = sorted(mp3_files, key= lambda f: (self.get_date(f)),
    #                                                      get_tracknumber(f)),
                               reverse=True)

            top100 = (mp3_files[:numberOfSongs])
            textFile="#EXTM3U\r\n"

            for fileName in top100:
                audio = MP3(fileName)
                time = int(round(audio.info.length))
                fileName = fileName.replace(self.dir, ".")
                songName = fileName.replace(".mp3","")
                textFile+="#EXTINF:%s,%s\r\n"%(time,songName)
                textFile+="%s\r\n"%(fileName)
                textFile+="\r\n"

            playlistFile = "%s Top.m3u"%(str(numberOfSongs))
            f = codecs.open(os.path.join(self.dir, playlistFile), "wb","utf-8")
            f.write(textFile)
            f.close()

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

    manager = PlaylistsManager()

    if isMediaserver:
        listDir = [name for name in os.listdir(".") if os.path.isdir(os.path.join(".", name))]
        for x in listDir:
            manager.createPlaylistForMediaserver([x], x)
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

        manager.createTopOfMusic(100)

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
