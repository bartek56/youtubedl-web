from Common.AlarmEnums import SystemdCommand, AlarmConfigFlask
from youtubedl import app, logger, alarmManager

from flask import render_template, request, flash

if app.debug == True: # pragma: no cover
    import sys
    sys.path.append("./tests")
    import subprocessDebug as subprocess
else:
    import subprocess

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
    return render_template("alarm.html", **alarmManager.loadAlarmConfig())

@app.route('/alarm_on')
def alarmOn():
    logger.debug("alarm on")
    subprocess.run(SystemdCommand.ENABLE_ALARM_TIMER, shell=True)
    subprocess.run(SystemdCommand.START_ALARM_TIMER, shell=True)
    return render_template("alarm.html", **alarmManager.loadAlarmConfig())

@app.route('/alarm_off')
def alarmOff():
    logger.debug('alarm off')
    subprocess.run(SystemdCommand.STOP_ALARM_TIMER, shell=True)
    subprocess.run(SystemdCommand.DISABLE_ALARM_TIMER, shell=True)

    return "Nothing"

@app.route('/alarm.html')
def alarm():
    remoteAddress = request.remote_addr

    if ("192.168" in remoteAddress) or ("127.0.0.1" in remoteAddress):
        #if os.path.isfile("/etc/mediaserver/alarm.timer") == False:
        #    return alert_info2("Alarm timer doesn't exist")
        #elif os.path.isfile("/etc/mediaserver/alarm.sh") == False:
        #    return alert_info2("Alarm script doesn't exist")
        return render_template("alarm.html", **alarmManager.loadAlarmConfig())
    else:
        return webUtils.alert_info("You do not have access to alarm settings")

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

        alarmManager.updateAlarmConfig(alarmDays,time,minVolume,maxVolume,defaultVolume,growingVolume,growingSpeed,
                        alarmPlaylist,alarmMode)

        if alarmIsEnable:
            p = subprocess.run(SystemdCommand.STOP_ALARM_TIMER, shell=True)
            if p.returncode != 0:
                flash("Failed to restart alarm timer", 'danger')
                return render_template("alarm.html", **alarmManager.loadAlarmConfig())

        p = subprocess.run(SystemdCommand.DAEMON_RELOAD, shell=True)
        if p.returncode != 0:
                flash("Failed to daemon-reload", 'danger')
                return render_template("alarm.html", **alarmManager.loadAlarmConfig())

        if alarmIsEnable:
            p = subprocess.run(SystemdCommand.START_ALARM_TIMER, shell=True)
            if p.returncode != 0:
                flash("Failed to start alarm timer", 'danger')
                return render_template("alarm.html", **alarmManager.loadAlarmConfig())

        logger.info("alarm saved, systemctl daemon-reload")

        flash("Successfull saved alarm", 'success')

    return render_template("alarm.html", **alarmManager.loadAlarmConfig())
