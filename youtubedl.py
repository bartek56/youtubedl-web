import os
import logging
import zipfile
from flask import Flask, render_template, redirect, url_for, request, jsonify, send_from_directory, flash, session
from flask_socketio import SocketIO, emit
from Common.mailManager import Mail
from Common.YouTubeManager import YoutubeManager, YoutubeConfig
from Common.SocketLogger import SocketLogger, LogLevel
from Common.SocketMessages import PlaylistInfo_response, MediaInfo_response, DownloadPlaylist_response, PlaylistMediaInfo_response
from Common.SocketMessages import DownloadMedia_finish, DownloadPlaylist_finish
import flask
import random
import string
from flask_session import Session
import Common.YouTubeManager as YTManager
import Common.SocketMessages as SocketMessages

class AlarmConfigFlask():
    ALARM_TIME =          "alarm_time"
    ALARM_MODE =          "alarm_mode"
    ALARM_MODE_NEWEST =   "newest_song"
    ALARM_MODE_PLAYLIST = "playlist"
    THE_NEWEST_SONG =     "theNewestSongChecked"
    PLAYLIST_CHECKED =    "playlistChecked"
    ALARM_PLAYLISTS =     "alarm_playlists"
    ALARM_PLATLIST_NAME = "alarm_playlist_name"
    ALARM_ACTIVE =        "alarm_active"
    MONDAY =    "monday_checked"
    TUESDAY =   "tuesday_checked"
    WEDNESDEY = "wednesday_checked"
    THURSDAY =  "thursday_checked"
    FRIDAY =    "friday_checked"
    SATURDAY =  "saturday_checked"
    SUNDAY =    "sunday_checked"
    MIN_VOLUME = "min_volume"
    MAX_VOLUME = "max_volume"
    DEFAULT_VOLUME = "default_volume"
    GROWING_VOLUME = "growing_volume"
    GROWING_SPEED =  "growing_speed"

class AlarmConfigLinux():
    THE_NEWEST_SONG =     "theNewestSongs"
    PLAYLIST =            "playlist"
    MIN_VOLUME =   "minVolume"
    MAX_VOLUME =   "maxVolume"
    DEFAULT_VOLUME = "defaultVolume"
    GROWING_VOLUME = "growingVolume"
    GROWING_SPEED =  "growingSpeed"

class SystemdCommand():
    START_ALARM_TIMER =     "sudo /bin/systemctl start alarm.timer"
    START_ALARM_SERVICE =   "sudo /bin/systemctl start alarm.service"
    STOP_ALARM_TIMER =      "sudo /bin/systemctl stop alarm.timer"
    STOP_ALARM_SERVICE =    "sudo /bin/systemctl stop alarm.service"
    ENABLE_ALARM_TIMER =    "sudo /bin/systemctl enable alarm.timer"
    DISABLE_ALARM_TIMER =   "sudo /bin/systemctl disable alarm.timer"
    DAEMON_RELOAD =         "sudo /bin/systemctl daemon-reload"
    IS_ACTIVE_ALARM_TIMER = "systemctl is-active alarm.timer"

app = Flask(__name__)

if app.debug == True: # pragma: no cover
    import sys
    sys.path.append("./tests")
    import subprocessDebug as subprocess
else:
    import subprocess

app.secret_key = "super_extra_key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True

Session(app)

mailManager = Mail()
socketio = SocketIO(app, manage_session=False)

socketLogger = SocketLogger()
socketLogger.settings(saveToFile=False, print=True, fileNameWihPath="/var/log/youtubedlweb_mylogger.log",
                      logLevel=LogLevel.ERROR, showFilename=True, showLogLevel=False, showDate=False,
                      skippingLogWith=["[youtube:tab]", "B/s ETA", "[ExtractAudio]", "B in 00:00:00", "100% of",
                                       "[info]", "Downloading item", "[dashsegments]", "Deleting original file", "Downloading android player", "Downloading webpage"])
#logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s",filename='/var/log/youtubedlweb.log', level=logging.INFO)
if app.debug == True: # pragma: no cover
    logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
else:
    logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.FATAL)
logger = logging.getLogger(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

youtubeManager = YoutubeManager(logger=socketLogger)
youtubeConfig = YoutubeConfig()

CONFIG_FILE="/etc/mediaserver/youtubedl.ini"
ALARM_TIMER="/etc/mediaserver/alarm.timer"
ALARM_SCRIPT="/etc/mediaserver/alarm.sh"

youtubeConfig.initialize(CONFIG_FILE)

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/contact.html')
def contactHTML():
    if mailManager.initialize():
        return render_template('contact.html')
    else:
        return alert_info("Mail is not support")

@app.route('/mail', methods = ['POST', 'GET'])
def mail():
    if request.method == 'POST':
        sender = request.form['sender']
        message = request.form['message']
        if(len(sender)>2 and len(message)>2):
            fullMessage = "You received message from " + sender + ": " + message
            mailManager.sendMail("bartosz.brzozowski23@gmail.com", "MediaServer", fullMessage)
            flash("Successfull send mail",'success')
        else:
            flash("You have to fill in the fields", 'danger')

    return render_template('contact.html')

def alert_info(info):
    return render_template('alert.html', alert=info)

def loadConfig(configFile):
    f = open(configFile, "r")
    content = f.readlines()
    f.close()
    return content

def saveConfig(configFile:str, content:list):
    f = open(configFile,"w")
    for x in content:
        f.write(x)
    f.close()

def loadAlarmConfig():
    mondayChecked = ""
    tuesdayChecked = ""
    wednesdayChecked = ""
    thursdayChecked = ""
    fridayChecked = ""
    saturdayChecked = ""
    sundayChecked = ""

    content = loadConfig(ALARM_TIMER)

    for x in content:
        if "OnCalendar" in x:
            parameter = x.split("=")
            parameter2 = parameter[1].split(" ")
            weekDays = parameter2[0]
            time = parameter2[1].rstrip()

            if "Mon" in weekDays:
                mondayChecked = "checked"
            if "Tue" in weekDays:
                tuesdayChecked = "checked"
            if "Wed" in weekDays:
                wednesdayChecked = "checked"
            if "Thu" in weekDays:
                thursdayChecked = "checked"
            if "Fri" in weekDays:
                fridayChecked = "checked"
            if "Sat" in weekDays:
                saturdayChecked = "checked"
            if "Sun" in weekDays:
                sundayChecked = "checked"

    content = loadConfig(ALARM_SCRIPT)

    for x in content:
        if len(x)>1:
            if AlarmConfigLinux.MIN_VOLUME in x:
                parameter = x.split("=")
                minVolume = parameter[1].rstrip()
            elif AlarmConfigLinux.MAX_VOLUME in x:
                parameter = x.split("=")
                maxVolume = parameter[1].rstrip()
            elif AlarmConfigLinux.DEFAULT_VOLUME in x:
                parameter = x.split("=")
                defaultVolume = parameter[1].rstrip()
            elif AlarmConfigLinux.GROWING_VOLUME in x:
                parameter = x.split("=")
                growingVolume = int(parameter[1].rstrip())
            elif AlarmConfigLinux.GROWING_SPEED in x:
                parameter = x.split("=")
                growingSpeed = int(parameter[1].rstrip())
            elif AlarmConfigLinux.PLAYLIST in x:
                parameter = x.split("=")
                alarmPlaylistName = parameter[1].rstrip()
                alarmPlaylistName=alarmPlaylistName.replace('"','')
            elif AlarmConfigLinux.THE_NEWEST_SONG in x:
                parameter = x.split("=")
                if "true" in parameter[1]:
                    theNewestSongCheckBox = "checked"
                    playlistCheckbox = ""
                else:
                    theNewestSongCheckBox = ""
                    playlistCheckbox = "checked"
        else:
            break

    out = subprocess.check_output("mpc lsplaylists | grep -v m3u", shell=True, text=True)
    playlists = []
    musicPlaylistName=""
    for x in out:
        if x != '\n':
            musicPlaylistName += x
        else:
            playlists.append(musicPlaylistName)
            musicPlaylistName=""

    alarmIsOn = "unchecked"
    try:
        output = subprocess.check_output(SystemdCommand.IS_ACTIVE_ALARM_TIMER, shell=True, text=True)
        #exception is called when alarm is disabled
        if "in" in output:
            alarmIsOn = "unchecked"
        else:
            alarmIsOn = "checked"
    except subprocess.CalledProcessError as grepexc:
        logger.info("Exception - alarm is disabled")
        alarmIsOn = "unchecked"

    return {AlarmConfigFlask.ALARM_TIME: time,
            AlarmConfigFlask.THE_NEWEST_SONG:theNewestSongCheckBox,
            AlarmConfigFlask.PLAYLIST_CHECKED:playlistCheckbox,
            AlarmConfigFlask.ALARM_PLAYLISTS:playlists,
            AlarmConfigFlask.ALARM_PLATLIST_NAME:alarmPlaylistName,
            AlarmConfigFlask.ALARM_ACTIVE:alarmIsOn,
            AlarmConfigFlask.MONDAY:mondayChecked,
            AlarmConfigFlask.TUESDAY:tuesdayChecked,
            AlarmConfigFlask.WEDNESDEY:wednesdayChecked,
            AlarmConfigFlask.THURSDAY:thursdayChecked,
            AlarmConfigFlask.FRIDAY:fridayChecked,
            AlarmConfigFlask.SATURDAY:saturdayChecked,
            AlarmConfigFlask.SUNDAY:sundayChecked,
            AlarmConfigFlask.MIN_VOLUME:minVolume,
            AlarmConfigFlask.MAX_VOLUME:maxVolume,
            AlarmConfigFlask.DEFAULT_VOLUME:defaultVolume,
            AlarmConfigFlask.GROWING_VOLUME:growingVolume,
            AlarmConfigFlask.GROWING_SPEED:growingSpeed}

@app.route('/alarm.html')
def alarm():
    remoteAddress = request.remote_addr

    if ("192.168" in remoteAddress) or ("127.0.0.1" in remoteAddress):
        return render_template("alarm.html", **loadAlarmConfig())

    #elif os.path.isfile("/etc/mediaserver/alarm.timer") == False:
    #    return alert_info("Alarm timer doesn't exist")
    #elif os.path.isfile("/etc/mediaserver/alarm.sh") == False:
    #    return alert_info("Alarm script doesn't exist")
    else:
        return alert_info("You do not have access to alarm settings")

@app.route('/save_alarm', methods = ['POST', 'GET'])
def save_alarm_html():
    if request.method == 'POST':
        time = request.form[AlarmConfigFlask.ALARM_TIME]
        alarmMode = request.form[AlarmConfigFlask.ALARM_MODE]
        alarmPlaylist = ""
        if AlarmConfigFlask.ALARM_MODE_PLAYLIST in alarmMode:
            alarmPlaylist = request.form['playlists']
        alarmDays = ""
        if len(request.form.getlist('monday')) > 0:
            alarmDays += "Mon,"
        if len(request.form.getlist('tueday')) > 0:
            alarmDays += "Tue,"
        if len(request.form.getlist('wedday')) > 0:
            alarmDays += "Wed,"
        if len(request.form.getlist('thuday')) > 0:
            alarmDays += "Thu,"
        if len(request.form.getlist('friday')) > 0:
            alarmDays += "Fri,"
        if len(request.form.getlist('satday')) > 0:
            alarmDays += "Sat,"
        if len(request.form.getlist('sunday')) > 0:
            alarmDays += "Sun,"

        if len(alarmDays) > 0:
            alarmDays = alarmDays[:-1]

        minVolume=request.form[AlarmConfigFlask.MIN_VOLUME]
        maxVolume=request.form[AlarmConfigFlask.MAX_VOLUME]
        defaultVolume=request.form[AlarmConfigFlask.DEFAULT_VOLUME]

        growingVolume = request.form[AlarmConfigFlask.GROWING_VOLUME]
        growingSpeed = request.form[AlarmConfigFlask.GROWING_SPEED]
        alarmIsEnable = False
        if "alarm_active" in request.form:
            alarmIsEnable = True

        updateAlarmConfig(alarmDays,time,minVolume,maxVolume,defaultVolume,growingVolume,growingSpeed,
                        alarmPlaylist,alarmMode)

        if alarmIsEnable:
            p = subprocess.run(SystemdCommand.STOP_ALARM_TIMER, shell=True)
            if p.returncode != 0:
                flash("Failed to restart alarm timer", 'danger')
                return render_template("alarm.html", **loadAlarmConfig())

        p = subprocess.run(SystemdCommand.DAEMON_RELOAD, shell=True)
        if p.returncode != 0:
                flash("Failed to daemon-reload", 'danger')
                return render_template("alarm.html", **loadAlarmConfig())

        if alarmIsEnable:
            p = subprocess.run(SystemdCommand.START_ALARM_TIMER, shell=True)
            if p.returncode != 0:
                flash("Failed to start alarm timer", 'danger')
                return render_template("alarm.html", **loadAlarmConfig())

        logger.info("alarm saved, systemctl daemon-reload")

        flash("Successfull saved alarm", 'success')

    return render_template("alarm.html", **loadAlarmConfig())

def updateAlarmConfig(alarmDays, time, minVolume, maxVolume, defaultVolume,
              growingVolume, growingSpeed, alarmPlaylist, alarmMode):

        content = loadConfig(ALARM_TIMER)
        for i in range(len(content)):
            if "OnCalendar" in content[i]:
                content[i] = "OnCalendar=%s %s \n"%(alarmDays, time)

        saveConfig(ALARM_TIMER, content)

        content = loadConfig(ALARM_SCRIPT)
        for i in range(len(content)):
            if i>0 and i<8:
                if AlarmConfigLinux.MIN_VOLUME in content[i]:
                    content[i] = "%s=%s\n"%(AlarmConfigLinux.MIN_VOLUME, minVolume)
                elif AlarmConfigLinux.MAX_VOLUME in content[i]:
                    content[i] = "%s=%s\n"%(AlarmConfigLinux.MAX_VOLUME, maxVolume)
                elif AlarmConfigLinux.DEFAULT_VOLUME in content[i]:
                    content[i] = "%s=%s\n"%(AlarmConfigLinux.DEFAULT_VOLUME, defaultVolume)
                elif AlarmConfigLinux.GROWING_VOLUME in content[i]:
                    content[i] = "%s=%s\n"%(AlarmConfigLinux.GROWING_VOLUME, growingVolume)
                elif AlarmConfigLinux.GROWING_SPEED in content[i]:
                    content[i] = "%s=%s\n"%(AlarmConfigLinux.GROWING_SPEED, growingSpeed)
                elif AlarmConfigLinux.PLAYLIST in content[i]:
                    content[i] = "%s=\"%s\"\n"%(AlarmConfigLinux.PLAYLIST, alarmPlaylist)
                elif AlarmConfigLinux.THE_NEWEST_SONG in content[i]:
                    alarmNewestModeIsEnable = ""
                    if AlarmConfigFlask.ALARM_MODE_PLAYLIST in alarmMode:
                        alarmNewestModeIsEnable = "false"
                    else:
                        alarmNewestModeIsEnable = "true"
                    content[i] = "%s=%s\n"%(AlarmConfigLinux.THE_NEWEST_SONG, alarmNewestModeIsEnable)
            elif i >=8:
                break

        saveConfig(ALARM_SCRIPT, content)

@app.route('/playlists.html')
def playlists():
    remoteAddress = request.remote_addr

    if ("192.168" in remoteAddress) or ("127.0.0.1" in remoteAddress):
        playlistsName = youtubeConfig.getPlaylistsName()
        data = []

        for playlistName in playlistsName:
            data.append({'name':playlistName})

        return render_template('playlists.html', playlists_data=data)
    else:
        return alert_info("You do not have access to Youtube playlists")

@app.route('/download_file',methods = ['POST', 'GET'])
def downloadFile():
   path=''
   if request.method == 'POST':
      path = request.form['path']
      return flask.send_file(path, as_attachment=True)
   else:
      app.logger.debug("error")
      return redirect('/')

@app.route('/playlists',methods = ['POST', 'GET'])
def playlist():
   if request.method == 'POST':
       if 'add' in request.form:
           playlist_name = request.form['playlist_name']
           link = request.form['link']
           app.logger.debug("add playlist %s %s", playlist_name, link)
           youtubeConfig.addPlaylist({"name":playlist_name, "link":link})

       if 'remove' in request.form:
           playlistToRemove = str(request.form['playlists'])
           result = youtubeConfig.removePlaylist(playlistToRemove)
           if result:
                app.logger.debug("removed playlist %s", playlistToRemove)
                info = "Sucesssful removed playlist %s"%(playlistToRemove)
                flash(info, 'success')
           else:
               info = "Failed to remove Youtube playlist: %s"%(playlistToRemove)
               return alert_info(info)

       return redirect('playlists.html')

   else:
       app.logger.debug("error")
       return redirect('playlists.html')

@app.route('/alarm_test_start')
def alarmTestStart():
    logger.debug('alarm test start')
    subprocess.run(SystemdCommand.START_ALARM_SERVICE, shell=True)
    return "Nothing"

@app.route('/alarm_test_stop')
def alarmTestStop():
    logger.debug('alarm test stop')
    subprocess.run(SystemdCommand.STOP_ALARM_SERVICE, shell=True)
    subprocess.run('/usr/bin/mpc stop', shell=True)
    return render_template("alarm.html", **loadAlarmConfig())

@app.route('/alarm_on')
def alarmOn():
    logger.debug("alarm on")
    subprocess.run(SystemdCommand.ENABLE_ALARM_TIMER, shell=True)
    subprocess.run(SystemdCommand.START_ALARM_TIMER, shell=True)
    return render_template("alarm.html", **loadAlarmConfig())

@app.route('/alarm_off')
def alarmOff():
    logger.debug('alarm off')
    subprocess.run(SystemdCommand.STOP_ALARM_TIMER, shell=True)
    subprocess.run(SystemdCommand.DISABLE_ALARM_TIMER, shell=True)

    return "Nothing"

def isFile(file):
    return os.path.isfile(file)

@socketio.on('downloadPlaylists')
def handle_message(msg):
    playlists = youtubeConfig.getPlaylists()
    path = youtubeConfig.getPath()

    for playlist in playlists:
        response = youtubeManager.downloadPlaylistMp3Fast(path, playlist["name"], playlist["link"])
        if response.IsFailed():
            logger.error("Failed to download playlist %s from link %s - %s", playlist["name"], playlist["link"], response.error())
        numberOfDownloadedSongs:int = response.data()
        DownloadPlaylist_response().sendMessage(numberOfDownloadedSongs)

    DownloadPlaylist_finish().sendMessage(numberOfDownloadedSongs)

def downloadMediaOfType(url, type):
    if type == "mp3":
        return youtubeManager.download_mp3(url)
    elif type == "360p":
        return youtubeManager.download_360p(url)
    elif type == "720p":
        return youtubeManager.download_720p(url)
    elif type =="4k":
        return youtubeManager.download_4k(url)

@socketio.on('downloadMedia')
def downloadMedia(msg):
    url = msg['url']
    downloadType = str(msg['type'])
    if "playlist?list" in url and "watch?v" not in url:
        downloadedFiles = []
        resultOfPLaylist = youtubeManager.getPlaylistInfo(url)

        if resultOfPLaylist.IsFailed():
            DownloadMedia_finish().sendError("Failed to get info playlist")

            logger.info("Error to download media: %s", resultOfPLaylist.error())
            return

        ytData:YTManager.PlaylistInfo = resultOfPLaylist.data()

        PlaylistInfo_response().sendMessage(SocketMessages.PlaylistInfo(ytData.playlistName, ytData.listOfMedia))
        index = 0
        for x in ytData.listOfMedia:
            index += 1
            resultOfMedia = downloadMediaOfType(x.url, downloadType)
            if resultOfMedia.IsFailed():
                error = "Failed to download song with index " + str(index)
                #TODO
                #PlaylistMediaInfo_response().sendError(error)
                logger.error(error)
                continue
            data:YTManager.YoutubeClipData = resultOfMedia.data()
            downloadedFiles.append(data.path)
            filename = data.path.split("/")[-1]
            randomHash = getRandomString()
            session[randomHash] = filename
            PlaylistMediaInfo_response().sendMessage(SocketMessages.PlaylistMediaInfo(x.playlistIndex, filename, randomHash))
        playlistName = ytData.playlistName
        compressToZip(downloadedFiles, playlistName)
        randomHash = getRandomString()
        session[randomHash] = "%s.zip"%playlistName

        DownloadMedia_finish().sendMessage(randomHash)
    else:
        result = youtubeManager.getMediaInfo(url)
        if result.IsFailed():
            DownloadMedia_finish().sendError(result.error())
            logger.error("Failed download from url %s - error: %s", url, result.error())
            return
        mediaInfo:YTManager.MediaInfo = result.data()

        MediaInfo_response().sendMessage(SocketMessages.MediaInfo(mediaInfo.title, mediaInfo.artist))
        result2 = downloadMediaOfType(url, downloadType)

        if result2.IsFailed():
            logger.error("Failed with download media %s - %s", url, result2.error())
            DownloadMedia_finish().sendError("problem with download media: " + result2.error())
            return

        data:YTManager.YoutubeClipData = result2.data()
        filename = data.path.split("/")[-1]
        randomHash = getRandomString()
        session[randomHash] = filename
        DownloadMedia_finish().sendMessage(randomHash)

def compressToZip(files, playlistName):
    # TODO zip fileName
    zipFileName = "%s.zip"%playlistName
    zipFileWithPath = os.path.join("/tmp/quick_download", zipFileName)
    with zipfile.ZipFile(zipFileWithPath, 'w') as zipf:
        for file_path in files:
            arcname = file_path.split("/")[-1]
            zipf.write(file_path, arcname)

@app.route('/download/<name>')
def download_file(name):
    if name not in session.keys():
        app.logger.error("key for download_file doesn't exist !!!!")
        return render_template('index.html')
    fileToDownload = session[name]
    fullPath = "/tmp/quick_download/" + fileToDownload
    return flask.send_file(fullPath, as_attachment=True)

@socketio.event
def connect():
    pass

def getRandomString():
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(8))
    return result_str

if __name__ == '__main__':
    socketio.run(app)
