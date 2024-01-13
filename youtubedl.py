import logging
from flask import Flask, render_template, redirect, url_for, request, jsonify, send_from_directory, flash, session
from flask_socketio import SocketIO, emit
from Common.mailManager import Mail
from Common.YouTubeManager import YoutubeManager, YoutubeConfig
from Common.SocketLogger import SocketLogger, LogLevel
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
    import subprocessDebug as subprocess
else:
    import subprocess

## logger configuration
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


## Initialize component
CONFIG_FILE="/etc/mediaserver/youtubedl.ini"

mailManager = Mail()

youtubeManager = YoutubeManager(logger=socketLogger)

youtubeConfig = YoutubeConfig()
youtubeConfig.initialize(CONFIG_FILE)


## import subsides
import alarm
import youtubeDownloader

## --------------------------------------

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/contact.html')
def contactHTML():
    if mailManager.initialize():
        return render_template('contact.html')
    else:
        return render_template('alert.html', alert="Mail is not supported")

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

@socketio.event
def connect():
    pass

if __name__ == '__main__':
    socketio.run(app)
