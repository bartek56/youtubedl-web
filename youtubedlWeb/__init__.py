import logging
from flask import Flask
from flask_socketio import SocketIO
from flask_session import Session
#from config import Config
from .Common.YoutubeManager import YoutubeManager, YoutubeConfig
from .Common.AlarmManager import AlarmManager
from .Common.MailManager import Mail

socketio = SocketIO(manage_session=False)

def create_app():
    app = Flask(__name__)
    #app.config.from_object(Config) #TODO
    app.secret_key = "super_extra_key"
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = True

    # Inicjalizacja rozszerzeń

    Session(app)
    socketio.init_app(app)

    ## Initialize component
    CONFIG_FILE="/etc/mediaserver/youtubedl.ini"
    ALARM_TIMER="/etc/mediaserver/alarm.timer"
    ALARM_SCRIPT="/etc/mediaserver/alarm.sh"
    if app.debug == True: # pragma: no cover
        import sys
        sys.path.append("./tests")
        import SubprocessDebug as subprocess
    else:
        import subprocess
    app.mailManager = Mail()

    app.subprocess = subprocess

    app.youtubeConfig = YoutubeConfig()
    app.youtubeConfig.initialize(CONFIG_FILE)

    app.youtubeManager = YoutubeManager()
    app.alarmManager = AlarmManager(subprocess, ALARM_TIMER, ALARM_SCRIPT)

    handler = app.logger.handlers[0]
    if app.debug == True: # pragma: no cover
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
    formater = logging.Formatter("%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d - %(message)s")
    handler.setFormatter(formater)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    # Import i rejestracja blueprintów
    from .routes.main_routes import main_bp
    from .routes.youtubedlPlaylists_routes import youtubePlaylists_bp
    from .routes.youtubeDownloader_routes import youtubeDwonlaoder_bp
    from .routes.alarm_routes import alarm_bp
    from .routes.mail_routes import mail_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(youtubePlaylists_bp)
    app.register_blueprint(youtubeDwonlaoder_bp)
    app.register_blueprint(alarm_bp)
    app.register_blueprint(mail_bp)

    return app
