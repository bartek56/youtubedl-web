import logging
from flask import Flask
from flask_socketio import SocketIO
from flask_session import Session
from .config import Config
from .Common.YoutubeManager import YoutubeManager, YoutubeConfig
from .Common.AlarmManager import AlarmManager
from .Common.MailManager import Mail

socketio = SocketIO(manage_session=False)

CONFIG_FILE="/etc/mediaserver/youtubedl.ini"
ALARM_TIMER="/etc/mediaserver/alarm.timer"
ALARM_SCRIPT="/etc/mediaserver/alarm.sh"

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    Session(app)
    socketio.init_app(app)

    if app.debug == True: # pragma: no cover
        import sys
        sys.path.append("./tests")
        import SubprocessDebug as subprocess
    else:
        import subprocess

    app.subprocess = subprocess
    app.desktop = False

    app.mailManager = Mail()
    app.youtubeConfig = YoutubeConfig()
    app.youtubeConfig.initialize(CONFIG_FILE)

    app.youtubeManager = YoutubeManager()
    app.alarmManager = AlarmManager(subprocess, ALARM_TIMER, ALARM_SCRIPT)

    if len(app.logger.handlers) == 1:
        handler = app.logger.handlers[0]
        formater = logging.Formatter("%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s")
        handler.setFormatter(formater)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    if app.debug == True: # pragma: no cover
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)

    #app.logger.setLevel(logging.DEBUG)

    from .routes.main_routes import main_bp
    from .routes.youtubedlPlaylists_routes import youtubePlaylists_bp, register_socketio_youtubePlaylist
    from .routes.youtubeDownloader_routes import youtubeDwonlaoder_bp, register_socketio_youtubeDownlaoder, register_socketio_youtubeDownloadFile
    from .routes.alarm_routes import alarm_bp
    from .routes.mail_routes import mail_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(youtubePlaylists_bp)
    app.register_blueprint(youtubeDwonlaoder_bp)
    app.register_blueprint(alarm_bp)
    app.register_blueprint(mail_bp)

    register_socketio_youtubeDownlaoder(socketio)
    register_socketio_youtubePlaylist(socketio)
    register_socketio_youtubeDownloadFile(socketio)

    return app
