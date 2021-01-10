import os
import youtube_dl
from flask import Flask, render_template, redirect, url_for, request, send_file
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
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
        
    fileNameWithPath = add_metadata_song(album, artist, songTitle)
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


def add_metadata_song(albumName, artist, songName):
    path=MUSIC_PATH

    mp3ext=".mp3"
    fileName="%s%s"%(songName,mp3ext)
      
    if not os.path.isfile(os.path.join(path, fileName)):
        songName = songName.replace("/", "_")
        songName = songName.replace("|", "_")
        songName = songName.replace("\"", "'")
        songName = songName.replace(":", "-")
        fileName="%s%s"%(songName,mp3ext)
    if not os.path.isfile(os.path.join(path, fileName)):
        songName = rename_song_name(songName)
        fileName="%s%s"%(songName,mp3ext)
    if not os.path.isfile(os.path.join(path, fileName)):
        warningInfo="WARNING: %s not exist"%(fileName)
        print (bcolors.WARNING + warningInfo + bcolors.ENDC)
        return

    newFileName = rename_song_file(path, fileName)
    newSongName = newFileName.replace(".mp3", "")

    metadataSongName = convert_songname_on_metadata(newSongName)
    newFileNameWithPath = os.path.join(path, newFileName)
        
    metatag = EasyID3(newFileNameWithPath)
    if albumName is not None:
        metatag['album'] = albumName
    if artist is not None:
        metatag['artist'] = artist
    else:
        metatag['artist'] = metadataSongName['artist']
    metatag['title'] = metadataSongName['title']
    metatag.save()
#    print (bcolors.OKGREEN + "[ID3] Added metadata" + bcolors.ENDC)
#    print (newFileNameWithPath)
    audio = MP3(newFileNameWithPath, ID3=EasyID3)
    app.logger.debug(audio.pprint())
    return newFileNameWithPath


def convert_songname_on_metadata(songName):
    slots = songName.split(" - ")
    metadata ={ 'tracknumber': "1",}
    if len(slots) == 2:
      metadata['artist'] = slots[0]
      metadata['title'] = slots[1]
    elif len(slots) < 2:
      slots = songName.split("-")
      if len(slots) == 2:
        metadata['artist'] = slots[0]
        metadata['title'] = slots[1]
      else:
        metadata['title'] = songName
        metadata['artist'] = ""
    else:
      metadata['artist'] = slots[0]
      name=""
      i=0
      for slots2 in slots:
        if i > 0:
          if i > 1:
            name+="-"
          name+=slots[i]
        i=i+1
      metadata['title'] = name

    return metadata


def rename_song_file(path, fileName):

    originalFileName = fileName 
    
    fileName = convert_song_name(fileName)

    fileName = fileName.replace("  .mp3", ".mp3")
    fileName = fileName.replace(" .mp3", ".mp3")

    originalFileNameWithPath=os.path.join(path, originalFileName)
    fileNameWithPath = os.path.join(path, fileName)
    os.rename(originalFileNameWithPath, fileNameWithPath)

    return fileName


def convert_song_name(songName):
    songName = songName.replace(" -", " - ")
    songName = songName.replace("- ", " - ")

    songName = songName.replace("(Oficial Video HD)", "")
    songName = songName.replace("(Official Video HD)", "")
    songName = songName.replace("[Official Video HD]", "")
    songName = songName.replace("[Official Music Video]", "")
    songName = songName.replace("(Official Music Video)", "")

    songName = songName.replace("(Official Lyric Video)", "")

    songName = songName.replace("( Official Video )", "")
    songName = songName.replace("(Official Video)", "")
    songName = songName.replace("[Official Video]", "")
    songName = songName.replace("(official video)", "")
    songName = songName.replace("(Official video)", "")
    songName = songName.replace("[OFFICIAL VIDEO]", "")
    songName = songName.replace("(OFFICIAL VIDEO)", "")
    songName = songName.replace("(Video Official)", "")
    songName = songName.replace("[Video Official]", "")
    songName = songName.replace("(VIDEO OFFICIAL)", "")
      
    songName = songName.replace("(Oficial Video)", "")
    songName = songName.replace("[Oficial Video]", "")
    songName = songName.replace("(OFICIAL VIDEO)", "")
    songName = songName.replace("(Video Oficial)", "")
    songName = songName.replace("[Video Oficial]", "")
    songName = songName.replace("(VIDEO OFICIAL)", "")
  
    songName = songName.replace("Video Oficial", "")
    songName = songName.replace("Video Official", "")
    songName = songName.replace("Oficial Video", "")
    songName = songName.replace("Official Video", "")

    songName = songName.replace("(Audio)", "")
    
    songName = songName.replace("(Official Audio)", "")
    songName = songName.replace("[Official Audio]", "")

    songName = songName.replace("   ", " ")   
    songName = songName.replace("  ", " ")   
    songName = songName.replace("  ", " ")   
    songName = songName.replace(" _", "")

    return songName


def rename_song_name(songName):
    songName = convert_song_name(songName)
    ext = ".xyz"
    songName = "%s%s"%(songName,ext)

    songName = songName+".xyz"
    songName = songName.replace("  .xyz", ".xyz")
    songName = songName.replace(" .xyz", ".xyz")
    songName = songName.replace(".xyz", "")
    
    return songName


