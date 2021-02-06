import os
import youtube_dl
import metadata_mp3
from flask import Flask, render_template, redirect, url_for, request, send_file, logging
from configparser import ConfigParser

app = Flask(__name__)
#log = logging.create_logger(app)


CONFIG_FILE='/etc/mediaserver/youtubedl.ini'
MUSIC_PATH=''
VIDEO_PATH=''
PLAYLISTS_PATH=''

f = open("/etc/mediaserver/minidlna.conf","r")
content = f.readlines()

for x in content:
    if "media_dir=A" in x:
        parameter = x.split("A,")
        musicPath = parameter[1]
        musicPath=musicPath.replace('\n','')
        musicPath=musicPath.replace('\r','')
        MUSIC_PATH="%s/quick download/"%(musicPath)
        PLAYLISTS_PATH="%s/Youtube list/"%(musicPath)
    if "media_dir=V" in x:
        parameter = x.split("V,")
        musicPath = parameter[1]
        VIDEO_PATH="%s/quick download/"%(musicPath)
        VIDEO_PATH=VIDEO_PATH.replace('\n','')
        VIDEO_PATH=VIDEO_PATH.replace('\r','')


#MUSIC_PATH='/tmp/music/quick_download/'
#VIDEO_PATH='/tmp/video/quick_download/'
#PLAYLISTS_PATH='/tmp/music/Youtube list/'

@app.route('/favicon.ico')
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/playlists.html')
def playlists():
    config = ConfigParser()
    config.read(CONFIG_FILE)
    data = [{'name':'name'}]
    data.clear()

    for section_name in config.sections():
        if section_name != "GLOBAL":
            data.append({'name':config[section_name]['name'] })

    return render_template('playlists.html', playlists_data=data)



@app.route('/download',methods = ['POST', 'GET'])
def login():
   path='' 
   if request.method == 'POST':
      link = request.form['link']
#      log.logger.debug("link: %s",link)
      option = request.form['quickdownload']
      if option == 'mp3':
#          log.logger.debug("mp3")
          path = download_mp3(link)
      elif option == '360p':
#          log.logger.debug("360p")
          path = download_360p(link)
      elif option == '720p':
#          log.logger.debug("720p")
          path = download_720p(link)
      elif option == '4k':
#          log.logger.debug("4k")
          path = download_4k(link)

      downloadToHost = request.form.getlist('download_file')
      if downloadToHost:
          if not os.path.isfile(path):
              path = path.replace("|", "_")
              path = path.replace("\"", "'")
              path = path.replace(":", "-")
          
#          log.logger.debug("download To Host %s", path)
          return send_file(path, as_attachment=True)

      return redirect('/')
   else:
#      log.logger.debug("error")
      return redirect('/')


@app.route('/playlists',methods = ['POST', 'GET'])
def playlist():
   if request.method == 'POST':
       config = ConfigParser()
       config.read(CONFIG_FILE)
       
       select = request.form.get('playlists')
#       log.logger.debug(select)

       if 'add' in request.form:
#           log.logger.debug("add")
           playlist_name = request.form['playlist_name']
           link = request.form['link']
           config[playlist_name]={}
           config[playlist_name]['name']=playlist_name
           config[playlist_name]['link']=link

       if 'remove' in request.form:
 #          log.logger.debug("remove")
           for i in config.sections():
               if i == str(select):
#                   log.logger.debug(i)
                   config.remove_section(str(select))

       with open(CONFIG_FILE,'w') as fp:
           config.write(fp)

       return redirect('playlists.html')

   else:
#       log.logger.debug("error")
       return redirect('playlists.html')



def download_mp3(url):
    path=MUSIC_PATH
    if not os.path.exists(path):
      os.makedirs(path)
    
#    info = "[INFO] start download MP3 from link %s "%(url)
#    log.logger.debug(info)

    ydl_opts = {
          'format': 'bestaudio/best',
          'download_archive': path+'/downloaded_songs.txt',
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
    result = youtube_dl.YoutubeDL(ydl_opts).extract_info(url)

    songTitle = result['title'] 
    artist = result['artist']
    album = result['album']
        
    return metadata_mp3.add_metadata_song(MUSIC_PATH, album, artist, songTitle)


def download_4k(url):
    path=VIDEO_PATH
    if not os.path.exists(path):
      os.makedirs(path)
    
#    info = "[INFO] start download video [high quality] from link %s "%(url)
#    log.logger.debug(info)

    ydl_opts = {
          'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
          'addmetadata': True,
          'outtmpl': path+'/'+'%(title)s_4k.%(ext)s',
          'ignoreerrors': True
          }  
    result = youtube_dl.YoutubeDL(ydl_opts).extract_info(url)
    return "%s/%s_4k.%s"%(path,result['title'],result['ext'])


def download_720p(url):
    path=VIDEO_PATH
    if not os.path.exists(path):
      os.makedirs(path)
    
#    info = "[INFO] start download video [medium quality] from link %s "%(url)
#    log.logger.debug(info)

    ydl_opts = {
          'format': 'bestvideo[height=720]/mp4',
          'addmetadata': True,
          'outtmpl': path+'/'+'%(title)s_720p.%(ext)s',
          'ignoreerrors': True
          }  
    result = youtube_dl.YoutubeDL(ydl_opts).extract_info(url)
    return "%s/%s_720p.%s"%(path,result['title'],result['ext'])


def download_360p(url):
    path=VIDEO_PATH
    if not os.path.exists(path):
      os.makedirs(path)
    
#    info = "[INFO] start download video [low quality] from link %s "%(url)
#    log.logger.debug(info)

    ydl_opts = {
          'format': 'worse[height<=360]/mp4',
          'addmetadata': True,
          'outtmpl': path+'/'+'%(title)s_360p.%(ext)s',
          'ignoreerrors': True
          }

    result = youtube_dl.YoutubeDL(ydl_opts).extract_info(url)
    return "%s/%s_360p.%s"%(path,result['title'],result['ext'])

if __name__ == '__main__':
    app.run()

