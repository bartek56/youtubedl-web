import os
import yt_dlp
import metadata_mp3

class YoutubeDl:
    def __init__(self):
        self.metadataManager = metadata_mp3.MetadataManager()
        self.MUSIC_PATH='/tmp/quick_download/'
        self.VIDEO_PATH='/tmp/quick_download/'

    def download_mp3(self, url):
        path=self.MUSIC_PATH
        self.createDirIfNotExist(path)

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

        fileName = "%s.mp3"%(songTitle)
        if not os.path.isfile(os.path.join(path, fileName)):
            print("[WARNING] File doesn't exist. Sanitize is require")
            songTitle = yt_dlp.utils.sanitize_filename(songTitle)
        full_path = self.metadataManager.rename_and_add_metadata_to_song(self.MUSIC_PATH, album, artist, songTitle)

        metadata = {"path": full_path}
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
        self.createDirIfNotExist(path)
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
        self.createDirIfNotExist(path)

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

    def createDirIfNotExist(self, path):
        if not os.path.exists(path): # pragma: no cover
            os.makedirs(path)

if __name__ == "__main__":
    yt = YoutubeDl()
    yt.download_mp3("https://www.youtube.com/watch?v=J9LgHNf2Qy0")
