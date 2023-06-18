import os
import yt_dlp
import metadata_mp3
import configparser

class YoutubeConfig():
    def __init__(self):
        pass

    def initialize(self, configFile, parser = configparser.ConfigParser()):
        self.CONFIG_FILE = configFile
        self.config = parser

    def getPath(self):
        path = None
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        if "GLOBAL" in self.config.sections():
            path = self.config["GLOBAL"]['path']
        return path

    def getPlaylists(self):
        self.config.clear()
        self.config.read(self.CONFIG_FILE)
        data = []

        for section_name in self.config.sections():
            if section_name != "GLOBAL":
                data.append({'name':self.config[section_name]['name'], 'link':self.config[section_name]['link']})
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

    def save(self):
        with open(self.CONFIG_FILE,'w') as fp:
            self.config.write(fp)

class YoutubeDl:
    def __init__(self, logger=None):
        self.metadataManager = metadata_mp3.MetadataManager()
        self.logger = logger
        self.MUSIC_PATH='/tmp/quick_download/'
        self.VIDEO_PATH='/tmp/quick_download/'

    def getPlaylistInfo(self, url):

        ydl_opts = {
              'format': 'best/best',
              'logger': self.logger,
              'extract_flat': 'in_playlist',
              'addmetadata': True,
              'ignoreerrors': False,
              'quiet':False
              }
        results = None
        try:
            results = yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
        except Exception as e:
            return self.removeTagFromLogger(str(e))

        if results is None:
            return "Failed to download url: "+ url

        for i in results['entries']:
            if i is None:
                warningInfo="not extract_info in results"
                return warningInfo

        data = []
        playlistTitle = results['title']
        playlistIndex = 1
        for i in results['entries']:
            dictData = {}
            dictData['playlist_name'] = playlistTitle
            dictData['playlist_index'] = playlistIndex
            dictData['url'] = i['url']
            dictData['title'] = i['title']
            data.append(dictData)
            playlistIndex+=1

        return data

    def getMediaInfo(self, url):

        ydl_opts = {
              'format': 'best/best',
              'logger': self.logger,
              'addmetadata': True,
              'ignoreerrors': False,
              'quiet':True
              }
        result = None
        try:
            result = yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=False)
        except Exception as e:
            return self.removeTagFromLogger(str(e))

        if result is None:
            return "Failed to download url: "+ url

        mediaInfo = {}
        mediaInfo['url'] = result['original_url']

        if "title" in result:
            mediaInfo['title'] = result['title']
        if "artist" in result:
            mediaInfo['artist'] = result['artist']
        if "album" in result:
            mediaInfo['album'] = result['album']

        return mediaInfo

    def download_mp3(self, url):
        path=self.MUSIC_PATH
        self.createDirIfNotExist(path)

        info = "[INFO] start download MP3 from link %s "%(url)
        print(info)

        ydl_opts = {
              'format': 'bestaudio/best',
              'addmetadata': True,
              'logger': self.logger,
              'outtmpl': path+'/'+'%(title)s.%(ext)s',
              'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                 }],
              'ignoreerrors': False,
               # TODO handle errors
               #'download_archive': path+'/downloaded_songs.txt',
              'continue': True,
              'no-overwrites': True,
              'noplaylist': True
              }

        try:
            result = yt_dlp.YoutubeDL(ydl_opts).extract_info(url)
        except Exception as e:
            return self.removeTagFromLogger(str(e))

        if result is None:
            return "Failed to download url: "+ url

        songTitle = ""
        artist = ""
        album = ""

        if "title" in result:
            songTitle = result['title']
        if "artist" in result:
            artist = result['artist']
        if "album" in result:
            album = result['album']

        fileName = "%s.mp3"%(songTitle)
        if not os.path.isfile(os.path.join(path, fileName)):
            print("[WARNING] File doesn't exist. Sanitize is require")
            songTitle = yt_dlp.utils.sanitize_filename(songTitle)
        full_path = self.metadataManager.rename_and_add_metadata_to_song(self.MUSIC_PATH, album, artist, songTitle)

        metadata = {}
        metadata["path"] = full_path
        if(artist is not None):
            metadata["artist"] = artist
        metadata["title"] = songTitle
        if(album is not None):
            metadata["album"] = album

        return metadata

    def download_4k(self, url):
        path=self.VIDEO_PATH
        self.createDirIfNotExist(path)
        info = "[INFO] start download video [high quality] from link %s "%(url)
        print(info)

        ydl_opts = {
              'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
              'addmetadata': True,
              'logger': self.logger,
              'outtmpl': path+'/'+'%(title)s_4k.%(ext)s',
              'no-overwrites': True,
              'ignoreerrors': True
              }
        result = self.downloadVideo(ydl_opts, url)
        if type(result) == str:
            return result

        full_path= "%s/%s_4k.%s"%(path,yt_dlp.utils.sanitize_filename(result['title']),result['ext'])
        result["path"] = full_path
        return result

    def download_720p(self, url):
        path=self.VIDEO_PATH
        self.createDirIfNotExist(path)
        info = "[INFO] start download video [medium quality] from link %s "%(url)
        print(info)

        ydl_opts = {
              'format': 'bestvideo[height=720]/mp4',
              'addmetadata': True,
              'logger': self.logger,
              'no-overwrites': True,
              'outtmpl': path+'/'+'%(title)s_720p.%(ext)s',
              'ignoreerrors': True
              }
        result = self.downloadVideo(ydl_opts, url)
        if type(result) == str:
            return result

        full_path = "%s/%s_720p.%s"%(path,yt_dlp.utils.sanitize_filename(result['title']),result['ext'])
        result["path"] = full_path
        return result

    def download_360p(self, url):
        path=self.VIDEO_PATH
        self.createDirIfNotExist(path)

        info = "[INFO] start download video [low quality] from link %s "%(url)
        print(info)

        ydl_opts = {
              'format': 'worse[height<=360]/mp4',
              'addmetadata': True,
              'logger': self.logger,
              'no-overwrites': True,
              'outtmpl': path+'/'+'%(title)s_360p.%(ext)s',
              'ignoreerrors': True
              }

        result = self.downloadVideo(ydl_opts, url)

        if type(result) == str:
            return result

        full_path = "%s/%s_360p.%s"%(path, yt_dlp.utils.sanitize_filename(result['title']), result['ext'])
        result["path"] = full_path
        return result

    def downloadVideo(self, yt_args, url):
        try:
            result = yt_dlp.YoutubeDL(yt_args).extract_info(url)
        except Exception as e:
            return self.removeTagFromLogger(str(e))

        if result is None:
            return "Failed to download url: "+ url

        metadata = {}
        metadata["title"] = result['title']
        metadata["ext"] = result['ext']
        return metadata

    def download_playlist_mp3(self, playlistDir, playlistName, url):
        path=os.path.join(playlistDir, playlistName)
        if not os.path.exists(path):
            os.makedirs(path)

        ydl_opts = {
              'format': 'bestaudio/best',
              'download_archive': path+'/downloaded_songs.txt',
              'addmetadata': True,
              'logger': self.logger,
              'outtmpl': path+'/'+'%(title)s.%(ext)s',
              'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                    }],
              'ignoreerrors': True,
              'quiet': True
              }
        results = None
        try:
            results = yt_dlp.YoutubeDL(ydl_opts).extract_info(url)
        except Exception as e:
            return self.removeTagFromLogger(str(e))

        if results is None:
            return "Failed to download url: "+ url

        for i in results['entries']:
            if i is None:
                warningInfo="not extract_info in results"
                return warningInfo

        info = "[INFO] started download playlist %s"%(playlistName)
        print (info)

        for i in results['entries']:
            if i is None:
                warningInfo="ERROR: not extract_info in results"
                return warningInfo

        artistList = []
        playlistIndexList = []
        songsTitleList = []

        for i in results['entries']:
            playlistIndexList.append(i['playlist_index'])
            songsTitleList.append(i['title'])

            if "artist" in i:
                artistList.append(i['artist'])
            else:
                artistList.append("")

        songCounter=0
        for x in range(len(songsTitleList)):
            songTitle = songsTitleList[x]
            fileName="%s%s"%(songTitle, ".mp3")
            if not os.path.isfile(os.path.join(path,fileName)):
                print("[WARNING] File doesn't exist. Sanitize is require")
                songTitle = yt_dlp.utils.sanitize_filename(songTitle)
            self.metadataManager.rename_and_add_metadata_to_playlist(playlistDir, playlistIndexList[x], playlistName, artistList[x], songTitle)
            songCounter+=1

        return songCounter

    def createDirIfNotExist(self, path):
        if not os.path.exists(path): # pragma: no cover
            os.makedirs(path)

    def removeTagFromLogger(self, log:str):
        ENDC = '\033[0m'
        splittedLog = log.split(ENDC)
        return splittedLog[1]

if __name__ == "__main__":
    yt = YoutubeDl()
    yt.download_mp3("https://www.youtube.com/watch?v=J9LgHNf2Qy0")
