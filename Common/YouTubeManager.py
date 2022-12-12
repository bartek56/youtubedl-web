import os
import yt_dlp
import metadata_mp3

class YoutubeDl:
    def __init__(self, tests=False):
        self.MUSIC_PATH='/tmp/music/quick_download/'
        self.VIDEO_PATH='/tmp/video/quick_download/'
        self.PLAYLISTS_PATH='/tmp/music/Youtube list/'

        if not tests:
            if os.path.isfile("/etc/mediaserver/minidlna.conf"):
                f = open("/etc/mediaserver/minidlna.conf","r")
                content = f.readlines()

                for x in content:
                    if "media_dir=A" in x:
                        parameter = x.split("A,")
                        musicPath = parameter[1]
                        musicPath=musicPath.replace('\n','')
                        musicPath=musicPath.replace('\r','')
                        self.MUSIC_PATH="%s/quick download/"%(musicPath)
                        self.PLAYLISTS_PATH="%s/Youtube list/"%(musicPath)
                    if "media_dir=V" in x:
                        parameter = x.split("V,")
                        musicPath = parameter[1]
                        self.VIDEO_PATH="%s/quick download/"%(musicPath)
                        self.VIDEO_PATH=self.VIDEO_PATH.replace('\n','')
                        self.VIDEO_PATH=self.VIDEO_PATH.replace('\r','')
                f.close()

    def download_mp3(self, url):
        path=self.MUSIC_PATH
        if not os.path.exists(path):
          os.makedirs(path)

        info = "[INFO] start download MP3 from link %s "%(url)
        print(info)

        ydl_opts = {
              'format': 'bestaudio/best',
              'addmetadata': True,
              'outtmpl': path+'/'+'%(title)s.%(ext)s',
              'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                 }],
              'ignoreerrors': True,
              'noplaylist': True
              }
        result = yt_dlp.YoutubeDL(ydl_opts).extract_info(url)

        songTitle = ""
        artist = ""
        album = ""

        if "title" in result:
            songTitle = result['title']
        if "artist" in result:
            artist = result['artist']
        if "album" in result:
            album = result['album']

        full_path = metadata_mp3.add_metadata_song(self.MUSIC_PATH, album, artist, songTitle)

        metadata = {"path": full_path}
        if(artist is not None):
            metadata["artist"] = artist
        metadata["title"] = songTitle
        if(album is not None):
            metadata["album"] = album

        return metadata

    def download_4k(self, url):
        path=self.VIDEO_PATH
        if not os.path.exists(path):
          os.makedirs(path)

        info = "[INFO] start download video [high quality] from link %s "%(url)
        print(info)

        ydl_opts = {
              'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
              'addmetadata': True,
              'outtmpl': path+'/'+'%(title)s_4k.%(ext)s',
              'ignoreerrors': True
              }
        result = yt_dlp.YoutubeDL(ydl_opts).extract_info(url)
        full_path= "%s/%s_4k.%s"%(path,result['title'],result['ext'])


        metadata = {"title": result['title'],
                     "path": full_path }
        return metadata

    def download_720p(self, url):
        path=self.VIDEO_PATH
        if not os.path.exists(path):
          os.makedirs(path)

        info = "[INFO] start download video [medium quality] from link %s "%(url)
        print(info)

        ydl_opts = {
              'format': 'bestvideo[height=720]/mp4',
              'addmetadata': True,
              'outtmpl': path+'/'+'%(title)s_720p.%(ext)s',
              'ignoreerrors': True
              }
        result = yt_dlp.YoutubeDL(ydl_opts).extract_info(url)

        full_path = "%s/%s_720p.%s"%(path,result['title'],result['ext'])
        metadata = {"title": result['title'],
                     "path": full_path }
        return metadata

    def download_360p(self, url):
        path=self.VIDEO_PATH
        if not os.path.exists(path):
          os.makedirs(path)

        info = "[INFO] start download video [low quality] from link %s "%(url)
        print(info)

        ydl_opts = {
              'format': 'worse[height<=360]/mp4',
              'addmetadata': True,
              'outtmpl': path+'/'+'%(title)s_360p.%(ext)s',
              'ignoreerrors': True
              }

        result = yt_dlp.YoutubeDL(ydl_opts).extract_info(url)
        full_path = "%s/%s_360p.%s"%(path,result['title'],result['ext'])

        metadata = {"title": result['title'],
                     "path": full_path }
        return metadata

    def isFile(self, path):
        return os.path.isfile(path)

if __name__ == "__main__":
    yt = YoutubeDl()
    yt.download_mp3("https://www.youtube.com/watch?v=J9LgHNf2Qy0")
