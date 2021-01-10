import os
import youtube_dl
import metadata_mp3
from flask import Flask, render_template, redirect, url_for, request, send_file
from configparser import ConfigParser

app = Flask(__name__)

MUSIC_PATH='/tmp/music/quick_download/'
VIDEO_PATH='/tmp/video/quick_download/'
PLAYLISTS_PATH='/tmp/music/Youtube list/'
CONFIG_FILE='/etc/mediaserver/youtubedl_test.ini'

@app.route('/')
def index():
    config = ConfigParser()
    config.read("/etc/mediaserver/youtubedl.ini")
    data = [{'name':'name'}]
    data.clear()

    for section_name in config.sections():
        if section_name != "GLOBAL":
            data.append({'name':config[section_name]['name'] })

    return render_template('index.html', playlists_data=data)

@app.route('/download',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      link = request.form['link']
      app.logger.debug("link: %s",link)
      option = request.form['quickdownload']
      if option == 'mp3':
          app.logger.debug("mp3")
          path = download_mp3(link)
      elif option == '360p':
          app.logger.debug("360p")
          path = download_360p(link)
      elif option == '720p':
          app.logger.debug("720p")
          path = download_720p(link)
      elif option == '4k':
          app.logger.debug("4k")
          path = download_4k(link)

      downloadToHost = request.form.getlist('download_file')
      if downloadToHost:
          app.logger.debug("download To Host")
          return send_file(path, as_attachment=True)

      return redirect('/')
   else:
      app.logger.debug("error")
      return redirect('/')


@app.route('/playlists',methods = ['POST', 'GET'])
def playlist():
   if request.method == 'POST':
       config = ConfigParser()
       config.read("/etc/mediaserver/youtubedl.ini")
       
       select = request.form.get('playlists')       
       if 'add' in request.form:
           app.logger.debug("add")
           playlist_name = request.form['playlist_name']
           link = request.form['link']
           config[playlist_name]={}
           config[playlist_name]['name']=playlist_name
           config[playlist_name]['link']=link


       if 'remove' in request.form:
           app.logger.debug("remove")
           for i in data_2:
               if i['name'] == str(select):
                   app.logger.debug(i['name'])
                   config.remove_section(str(select))

       with open("/etc/mediaserver/youtubedl.ini",'w') as fp:
           config.write(fp)

       return redirect('/')
   else:
       app.logger.debug("error")
       return redirect('/')


def download_mp3(url):
    path=MUSIC_PATH
    if not os.path.exists(path):
      os.makedirs(path)
    
    info = "[INFO] start download MP3 from link %s "%(url)
#    print (bcolors.OKGREEN + info + bcolors.ENDC)

    ydl_opts = {
          'format': 'bestaudio/best',
          'addmetadata': True,
          'outtmpl': path+'/'+'%(title)s.%(ext)s',
          'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
             }],
          'ignoreerrors': True
          }  
    result = youtube_dl.YoutubeDL(ydl_opts).extract_info(url)

    songTitle = result['title'] 
    artist = result['artist']
    album = result['album']
        
    fileNameWithPath = metadata_mp3.add_metadata_song(MUSIC_PATH, album, artist, songTitle)
    return fileNameWithPath


def download_4k(url):
    path=VIDEO_PATH
    if not os.path.exists(path):
      os.makedirs(path)
    
    info = "[INFO] start download video [high quality] from link %s "%(url)
#    print (bcolors.OKGREEN + info + bcolors.ENDC)

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
    
    info = "[INFO] start download video [medium quality] from link %s "%(url)
#    print (bcolors.OKGREEN + info + bcolors.ENDC)

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
    
    info = "[INFO] start download video [low quality] from link %s "%(url)
#    print (bcolors.OKGREEN + info + bcolors.ENDC)

    ydl_opts = {
          'format': 'worse[height<=360]/mp4',
          'addmetadata': True,
          'outtmpl': path+'/'+'%(title)s_360p.%(ext)s',
          'ignoreerrors': True
          }

    result = youtube_dl.YoutubeDL(ydl_opts).extract_info(url)
    return "%s/%s_360p.%s"%(path,result['title'],result['ext'])

