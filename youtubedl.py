import logging
from flask import Flask, render_template
from flask_socketio import SocketIO
from Common.MailManager import Mail
from Common.YoutubeManager import YoutubeManager, YoutubeConfig
from Common.AlarmManager import AlarmManager
from flask_session import Session

## server configuration
app = Flask(__name__)
app.secret_key = "super_extra_key"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True

Session(app)
socketio = SocketIO(app, manage_session=False)
if app.debug == True: # pragma: no cover
    import sys
    sys.path.append("./tests")
    import SubprocessDebug as subprocess
else:
    import subprocess

#logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s",filename='/var/log/youtubedlweb.log', level=logging.INFO)
if app.debug == True: # pragma: no cover
    logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.DEBUG)
else:
    logging.basicConfig(format="%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


## Initialize component
CONFIG_FILE="/etc/mediaserver/youtubedl.ini"
ALARM_TIMER="/etc/mediaserver/alarm.timer"
ALARM_SCRIPT="/etc/mediaserver/alarm.sh"

mailManager = Mail()

youtubeManager = YoutubeManager()

youtubeConfig = YoutubeConfig()
youtubeConfig.initialize(CONFIG_FILE)

alarmManager = AlarmManager(subprocess, ALARM_TIMER, ALARM_SCRIPT)

## import subsides
import WebAPI.Alarm
import WebAPI.YoutubeDownloader
import WebAPI.YoutubePlaylists
import WebAPI.Mail

## --------------------------------------

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@socketio.event
def connect():
    pass

if __name__ == '__main__':
    socketio.run(app)
