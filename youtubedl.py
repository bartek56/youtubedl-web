import os
import logging
from flask import Flask, render_template, redirect, url_for, request, send_file, jsonify, send_from_directory, flash
import configparser
from Common.mailManager import Mail
from Common.YouTubeManager import YoutubeDl

app = Flask(__name__)
app.secret_key = "super_extra_key"
if app.debug == True: # pragma: no cover
    import sys
    sys.path.append("./tests")
    import subprocessDebug as subprocess
else:
    import subprocess
mailManager = Mail()
youtubeManager = YoutubeDl()

#logging.basicConfig(format="%(asctime)s %(levelname)s-%(message)s",filename='/var/log/youtubedlweb.log', level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE='/etc/mediaserver/youtubedl.ini'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

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

def loadAlarmConfigAlarmHTML():
    f = open("/etc/mediaserver/alarm.timer","r")
    content = f.readlines()

    mondayChecked = ""
    tuesdayChecked = ""
    wednesdayChecked = ""
    thursdayChecked = ""
    fridayChecked = ""
    saturdayChecked = ""
    sundayChecked = ""

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
    f.close()

    f = open("/etc/mediaserver/alarm.sh","r")
    content = f.readlines()

    for x in content:
        if len(x)>1:
            if "minVolume" in x:
                parameter = x.split("=")
                minVolume = parameter[1].rstrip()
            elif "maxVolume" in x:
                parameter = x.split("=")
                maxVolume = parameter[1].rstrip()
            elif "defaultVolume" in x:
                parameter = x.split("=")
                defaultVolume = parameter[1].rstrip()
            elif "growingVolume" in x:
                parameter = x.split("=")
                growingVolume = int(parameter[1].rstrip())
            elif "growingSpeed" in x:
                parameter = x.split("=")
                growingSpeed = int(parameter[1].rstrip())
            elif "playlist" in x:
                parameter = x.split("=")
                alarmPlaylistName = parameter[1].rstrip()
                alarmPlaylistName=alarmPlaylistName.replace('"','')
            elif "theNewestSongs" in x:
                parameter = x.split("=")
                if "true" in parameter[1]:
                    theNewestSongCheckBox = "checked"
                    playlistCheckbox = ""
                else:
                    theNewestSongCheckBox = ""
                    playlistCheckbox = "checked"

        else:
            break

    f.close()

    out = subprocess.check_output("mpc lsplaylists | grep -v m3u", shell=True, text=True)
    playlists = []
    musicPlaylistName=""
    for x in out:
        if x != '\n':
            musicPlaylistName += x
        else:
            playlists.append(musicPlaylistName)
            musicPlaylistName=""

    process = subprocess.run('systemctl is-active alarm.timer', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    if "in" in output:
        alarmIsOn = "unchecked"
    else:
        alarmIsOn = "checked"
    return render_template('alarm.html', alarm_time=time,
                                        theNewestSongChecked=theNewestSongCheckBox,
                                        playlistChecked=playlistCheckbox,
                                        alarm_playlists=playlists,
                                        alarm_playlist_name=alarmPlaylistName,
                                        alarm_active=alarmIsOn,
                                        monday_checked=mondayChecked,
                                        tuesday_checked=tuesdayChecked,
                                        wednesday_checked=wednesdayChecked,
                                        thursday_checked=thursdayChecked,
                                        friday_checked=fridayChecked,
                                        saturday_checked=saturdayChecked,
                                        sunday_checked=sundayChecked,
                                        min_volume=minVolume,
                                        max_volume=maxVolume,
                                        default_volume=defaultVolume,
                                        growing_volume=growingVolume,
                                        growing_speed=growingSpeed
                                        )

def saveConfigs(config):
    with open(CONFIG_FILE,'w') as fp:
        config.write(fp)

@app.route('/alarm.html')
def alarm():
    remoteAddress = request.remote_addr
    logger.info("alarm website")

    if ("192.168" in remoteAddress) or ("127.0.0.1" in remoteAddress):
        return loadAlarmConfigAlarmHTML()
    #elif os.path.isfile("/etc/mediaserver/alarm.timer") == False:
    #    return alert_info("Alarm timer doesn't exist")
    #elif os.path.isfile("/etc/mediaserver/alarm.sh") == False:
    #    return alert_info("Alarm script doesn't exist")
    else:
        return alert_info("You do not have access to alarm settings")

@app.route('/save_alarm', methods = ['POST', 'GET'])
def save_alarm():
    if request.method == 'POST':
        time = request.form['alarm_time']
        alarmMode = request.form['alarm_mode']
        alarmPlaylist = ""
        if "playlist" in alarmMode:
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

        minVolume=request.form['min_volume']
        maxVolume=request.form['max_volume']
        defaultVolume=request.form['default_volume']

        growingVolume = request.form['growing_volume']
        growingSpeed = request.form['growing_speed']
        alarmIsEnable = False
        if "alarm_active" in request.form:
            alarmIsEnable = True


        f = open("/etc/mediaserver/alarm.timer","r")
        content = f.readlines()
        f.close()
        for i in range(len(content)):
            if "OnCalendar" in content[i]:
                content[i] = "OnCalendar=%s %s \n"%(alarmDays, time)

        f = open("/etc/mediaserver/alarm.timer","w")

        for x in content:
            f.write(x)

        f.close()


        f = open("/etc/mediaserver/alarm.sh", "r")
        content = f.readlines()
        f.close()
        for i in range(len(content)):
            if i>0 and i<8:
                if "minVolume" in content[i]:
                    content[i] = "minVolume=%s\n"%(minVolume)
                elif "maxVolume" in content[i]:
                    content[i] = "maxVolume=%s\n"%(maxVolume)
                elif "defaultVolume" in content[i]:
                    content[i] = "defaultVolume=%s\n"%(defaultVolume)
                elif "growingVolume" in content[i]:
                    content[i] = "growingVolume=%s\n"%(growingVolume)
                elif "growingSpeed" in content[i]:
                    content[i] = "growingSpeed=%s\n"%(growingSpeed)
                elif "playlist" in content[i]:
                    content[i] = "playlist=\"%s\"\n"%(alarmPlaylist)
                elif "theNewestSong" in content[i]:
                    alarmType = "true"
                    if "playlist" in alarmMode:
                        alarmType = "false"
                    else:
                        alarmType = "true"
                    content[i] = "theNewestSongs=%s\n"%(alarmType)
            elif i >=8:
                break

        f = open("/etc/mediaserver/alarm.sh", "w")
        for x in content:
            f.write(x)
        f.close()
        if alarmIsEnable:
            p = subprocess.run('sudo /bin/systemctl stop alarm.timer', shell=True)
            if p.returncode != 0:
                flash("Failed to restart alarm timer", 'danger')
                return loadAlarmConfigAlarmHTML()

        p = subprocess.run('sudo /bin/systemctl daemon-reload', shell=True)
        if p.returncode != 0:
                flash("Failed to daemon-reload", 'danger')
                return loadAlarmConfigAlarmHTML()

        if alarmIsEnable:
            p = subprocess.run('sudo /bin/systemctl start alarm.timer', shell=True)
            if p.returncode != 0:
                flash("Failed to start alarm timer", 'danger')
                return loadAlarmConfigAlarmHTML()

        app.logger.info("alarm saved, systemctl daemon-reload")

        flash("Successfull saved alarm", 'success')

    return loadAlarmConfigAlarmHTML()

@app.route('/playlists.html')
def playlists():
    remoteAddress = request.remote_addr

    if ("192.168" in remoteAddress) or ("127.0.0.1" in remoteAddress):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        data = [{'name':'name'}]
        data.clear()

        for section_name in config.sections():
            if section_name != "GLOBAL":
                data.append({'name':config[section_name]['name'] })

        return render_template('playlists.html', playlists_data=data)
    else:
        return alert_info("You do not have access to Youtube playlists")

@app.route('/download',methods = ['POST', 'GET'])
def download():
    path=''
    info = {"path": "path"}

    if request.method == 'POST':
        link = request.form['link']
        app.logger.debug("link: %s",link)
        option = request.form['quickdownload']
        if option == 'mp3':
            app.logger.debug("mp3")
            info = youtubeManager.download_mp3(link)
            path = info["path"]
            del info["path"]
            info["Type"] = "MP3 audio"
        elif option == '360p':
            app.logger.debug("360p")
            info = youtubeManager.download_360p(link)
            path = info["path"]
            del info["path"]
            info["Type"] = "video"
        elif option == '720p':
            app.logger.debug("720p")
            info = youtubeManager.download_720p(link)
            path = info["path"]
            del info["path"]
            info["Type"] = "video"
        elif option == '4k':
            app.logger.debug("4k")
            info = youtubeManager.download_4k(link)
            path = info["path"]
            del info["path"]
            info["Type"] = "video"
    if not isFile(path):
        path = path.replace("|", "_")
        path = path.replace("\"", "'")
        path = path.replace(":", "-")
    if isFile(path):
        return render_template('download.html', full_path=path, file_info=info)
    else:
        app.logger.debug("error")
        return redirect('/')

@app.route('/download_file',methods = ['POST', 'GET'])
def downloadFile():
   path=''
   if request.method == 'POST':
      path = request.form['path']
      return send_file(path, as_attachment=True)
   else:
      app.logger.debug("error")
      return redirect('/')

@app.route('/playlists',methods = ['POST', 'GET'])
def playlist():
   if request.method == 'POST':
       config = configparser.ConfigParser()
       config.read(CONFIG_FILE)

       if 'add' in request.form:
           playlist_name = request.form['playlist_name']
           link = request.form['link']
           app.logger.debug("add playlist %s %s", playlist_name, link)
           config[playlist_name]={}
           config[playlist_name]['name']=playlist_name
           config[playlist_name]['link']=link

       if 'remove' in request.form:
           select = request.form['playlists']
           for i in config.sections():
               if i == str(select):
                   config.remove_section(i)
                   app.logger.debug("removed playlist %s", i)

       saveConfigs(config)
       return redirect('playlists.html')

   else:
       app.logger.debug("error")
       return redirect('playlists.html')

@app.route('/alarm_test_start')
def alarmTestStart():
    print('alarm test start')
    subprocess.run('sudo /bin/systemctl start alarm.service', shell=True)
    return "Nothing"

@app.route('/alarm_test_stop')
def alarmTestStop():
    print('alarm test stop')
    subprocess.run('sudo /bin/systemctl stop alarm.service', shell=True)
    subprocess.run('/usr/bin/mpc stop', shell=True)
#    return "Nothing"
    return loadAlarmConfigAlarmHTML()

@app.route('/alarm_on')
def alarmOn():
    print("alarm on")
    subprocess.run('sudo /bin/systemctl enable alarm.timer', shell=True)
    subprocess.run('sudo /bin/systemctl start alarm.timer', shell=True)
#    return "Nothing"
    return loadAlarmConfigAlarmHTML()

@app.route('/alarm_off')
def alarmOff():
    print('alarm off')
    subprocess.run('sudo /bin/systemctl stop alarm.timer', shell=True)
    subprocess.run('sudo /bin/systemctl disable alarm.timer', shell=True)

    return "Nothing"

def isFile(file):
    return os.path.isfile(file)

if __name__ == '__main__':
    app.run()

