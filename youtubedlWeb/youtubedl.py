import logging
from flask import Flask, render_template
#from flask_socketio import SocketIO
from Common.MailManager import Mail
from Common.YoutubeManager import YoutubeManager, YoutubeConfig
from Common.AlarmManager import AlarmManager
from flask_session import Session
#from youtubedlWeb import socketio


## server configuration
app = Flask(__name__)
app.secret_key = "super_extra_key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True

if app.debug == True: # pragma: no cover
    import sys
    sys.path.append("./tests")
    import SubprocessDebug as subprocess
else:
    import subprocess

## Initialize component
CONFIG_FILE="/etc/mediaserver/youtubedl.ini"
ALARM_TIMER="/etc/mediaserver/alarm.timer"
ALARM_SCRIPT="/etc/mediaserver/alarm.sh"

app.mailManager = Mail()

app.youtubeConfig = YoutubeConfig()
app.youtubeConfig.initialize(CONFIG_FILE)

app.youtubedlManager = YoutubeManager()
app.alarmMAnager = AlarmManager(subprocess, ALARM_TIMER, ALARM_SCRIPT)


from routes.main_routes import main_bp
from routes.youtubedlPlaylists_routes import auth_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)

Session(app)
#socketio.init_app(app)


#logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s",filename='/var/log/youtubedlweb.log', level=logging.INFO)
handler = logging.StreamHandler()
if app.debug == True: # pragma: no cover
    formater = logging.Formattter("%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s")
    handler.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
else:
    formater = logging.Formatter("%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s")
    handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
handler.setFormatter(formater)

app.logger.addHandler(handler)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


## import subsides
#import WebAPI.Alarm
#import WebAPI.YoutubeDownloader
#import WebAPI.YoutubePlaylists
#import WebAPI.Mail

## --------------------------------------



#@socketio.event
def connect():
    pass

def main():
    app.run()

if __name__ == '__main__':
    main()
