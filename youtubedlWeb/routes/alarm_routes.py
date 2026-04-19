from youtubedlWeb.Common.AlarmEnums import SystemdCommand, AlarmConfigFlask
from flask import Blueprint, jsonify
from flask import current_app as app

from flask import render_template, request, flash, send_from_directory
from youtubedlWeb.Common import WebUtils

alarm_bp = Blueprint('alarm', __name__)

@alarm_bp.route('/alarm/manifest.json')
def manifest():
    """
    Returns the manifest file for the alarm web page.

    This file is used by browsers to determine how to handle the web page
    when it is added to the home screen.

    Returns:
        The contents of the manifest file.

    """
    return send_from_directory('static', 'alarm_manifest.json')

@alarm_bp.route('/alarm_test_start')
def alarmTestStart():
    """
    Starts the alarm service.

    This function is used for testing the alarm service. It will start the
    alarm service and return "Nothing".

    Returns:
        A string containing "Nothing".
    """
    app.logger.debug('alarm test start')
    app.subprocess.run(SystemdCommand.START_ALARM_SERVICE, shell=True)
    return "Nothing"

@alarm_bp.route('/alarm_test_stop')
def alarmTestStop():
    """
    Stops the alarm service.

    This function is used for testing the alarm service. It will stop the
    alarm service and return the contents of the alarm web page.

    Returns:
        The contents of the alarm web page.

    """
    app.logger.debug('alarm test stop')
    app.subprocess.run(SystemdCommand.STOP_ALARM_SERVICE, shell=True)
    app.subprocess.run('/usr/bin/mpc stop', shell=True)
    return render_template("alarm.html", **app.alarmManager.loadAlarmConfig())

@alarm_bp.route('/alarm_on')
def alarmOn():
    """
    Enables and starts the alarm timer.

    This function is used to enable and start the alarm timer. It will
    enable the alarm timer, start the alarm timer, and return the next
    alarm time.

    Returns:
        A JSON object containing the next alarm time.

    """
    app.logger.debug("alarm on")
    app.subprocess.run(SystemdCommand.ENABLE_ALARM_TIMER, shell=True)
    app.subprocess.run(SystemdCommand.START_ALARM_TIMER, shell=True)
    nextAlarm = app.alarmManager.nextAlarmCheck()
    return jsonify(nextAlarm)

@alarm_bp.route('/alarm_off')
def alarmOff():
    """
    Disables and stops the alarm timer.

    This function is used to disable and stop the alarm timer. It will
    disable the alarm timer, stop the alarm timer, and return an empty
    JSON object.

    Returns:
        An empty JSON object.
    """
    app.logger.debug('alarm off')
    app.subprocess.run(SystemdCommand.STOP_ALARM_TIMER, shell=True)
    app.subprocess.run(SystemdCommand.DISABLE_ALARM_TIMER, shell=True)
    return jsonify()

@alarm_bp.route('/alarm_snooze_off')
def alarmSnoozeOff():
    """
    Disables and stops the alarm snooze timer.

    This function is used to disable and stop the alarm snooze timer. It will
    disable the alarm snooze timer, stop the alarm snooze timer, and return an
    empty JSON object.

    Returns:
        An empty JSON object.
    """
    app.logger.debug('alarm_snooze_off')
    app.subprocess.run(SystemdCommand.STOP_ALARM_SNOOZE_TIMER, shell=True)
    return jsonify()

@alarm_bp.route('/alarm.html')
def alarm():
    """
    Renders the alarm.html page with the alarm settings.

    This function is used to render the alarm.html page with the alarm
    settings. It will check if the remote address is in the local
    network (192.168 or 127.0.0.1) and if so, it will render the
    page with the alarm settings. If the remote address is not in the
    local network, it will return an alert info page with the message
    "You do not have access to alarm settings".

    Returns:
        A rendered HTML page with the alarm settings if the remote address
        is in the local network, otherwise an alert info page with the
        message "You do not have access to alarm settings".
    """
    remoteAddress = request.remote_addr

    if ("192.168" in remoteAddress) or ("127.0.0.1" in remoteAddress):
        #if os.path.isfile("/etc/mediaserver/alarm.timer") == False:
        #    return WebUtils.alert_info("Alarm timer doesn't exist")
        #elif os.path.isfile("/etc/mediaserver/alarm.sh") == False:
        #    return WebUtils.alert_info("Alarm script doesn't exist")
        return render_template("alarm.html", **app.alarmManager.loadAlarmConfig())
    else:
        return WebUtils.alert_info("You do not have access to alarm settings")

@alarm_bp.route('/save_alarm', methods = ['POST', 'GET'])
def save_alarm_html():
    """
    Saves the alarm settings.

    This function is used to save the alarm settings. It will get the alarm
    settings from the request form and update the alarm configuration. If the
    alarm is enabled, it will stop the alarm timer, daemon-reload, and start
    the alarm timer. If any of the above steps fails, it will flash an error
    message and return the alarm.html page with the current alarm settings.

    Returns:
        A rendered HTML page with the alarm settings.
    """
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
