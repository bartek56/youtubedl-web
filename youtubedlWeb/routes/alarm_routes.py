from youtubedlWeb.Common.AlarmEnums import SystemdCommand, AlarmConfigFlask
from flask import Blueprint
from flask import current_app as app

from flask import render_template, request, flash, send_from_directory
from youtubedlWeb.Common import WebUtils

alarm_bp = Blueprint('alarm', __name__)

@alarm_bp.route('/alarm/manifest.json')
def manifest():
    return send_from_directory('static', 'alarm_manifest.json')

@alarm_bp.route('/alarm_test_start')
def alarmTestStart():
    app.logger.debug('alarm test start')
    app.subprocess.run(SystemdCommand.START_ALARM_SERVICE, shell=True)
    return "Nothing"

@alarm_bp.route('/alarm_test_stop')
def alarmTestStop():
    app.logger.debug('alarm test stop')
    app.subprocess.run(SystemdCommand.STOP_ALARM_SERVICE, shell=True)
    app.subprocess.run('/usr/bin/mpc stop', shell=True)
    return render_template("alarm.html", **app.alarmManager.loadAlarmConfig())

@alarm_bp.route('/alarm_on')
def alarmOn():
    app.logger.debug("alarm on")
    app.subprocess.run(SystemdCommand.ENABLE_ALARM_TIMER, shell=True)
    app.subprocess.run(SystemdCommand.START_ALARM_TIMER, shell=True)
    return render_template("alarm.html", **app.alarmManager.loadAlarmConfig())

@alarm_bp.route('/alarm_off')
def alarmOff():
    app.logger.debug('alarm off')
    app.subprocess.run(SystemdCommand.STOP_ALARM_TIMER, shell=True)
    app.subprocess.run(SystemdCommand.DISABLE_ALARM_TIMER, shell=True)
    return "Nothing"

@alarm_bp.route('/alarm.html')
def alarm():
    remoteAddress = request.remote_addr

    if ("192.168" in remoteAddress) or ("127.0.0.1" in remoteAddress):
        #if os.path.isfile("/etc/mediaserver/alarm.timer") == False:
        #    return alert_info2("Alarm timer doesn't exist")
        #elif os.path.isfile("/etc/mediaserver/alarm.sh") == False:
        #    return alert_info2("Alarm script doesn't exist")
        return render_template("alarm.html", **app.alarmManager.loadAlarmConfig())
    else:
        return WebUtils.alert_info("You do not have access to alarm settings")

@alarm_bp.route('/save_alarm', methods = ['POST', 'GET'])
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

        app.alarmManager.updateAlarmConfig(alarmDays,time,minVolume,maxVolume,defaultVolume,growingVolume,growingSpeed,
                        alarmPlaylist,alarmMode)

        if alarmIsEnable:
            p = app.subprocess.run(SystemdCommand.STOP_ALARM_TIMER, shell=True)
            if p.returncode != 0:
                flash("Failed to restart alarm timer", 'danger')
                return render_template("alarm.html", **app.alarmManager.loadAlarmConfig())

        p = app.subprocess.run(SystemdCommand.DAEMON_RELOAD, shell=True)
        if p.returncode != 0:
                flash("Failed to daemon-reload", 'danger')
                return render_template("alarm.html", **app.alarmManager.loadAlarmConfig())

        if alarmIsEnable:
            p = app.subprocess.run(SystemdCommand.START_ALARM_TIMER, shell=True)
            if p.returncode != 0:
                flash("Failed to start alarm timer", 'danger')
                return render_template("alarm.html", **app.alarmManager.loadAlarmConfig())

        app.logger.info("alarm saved, systemctl daemon-reload")

        flash("Successfull saved alarm", 'success')

    return render_template("alarm.html", **app.alarmManager.loadAlarmConfig())
