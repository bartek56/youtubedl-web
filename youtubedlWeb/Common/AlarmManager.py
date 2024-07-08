from .AlarmEnums import AlarmConfigFlask, AlarmConfigLinux, SystemdCommand

import logging
logger = logging.getLogger(__name__)

class AlarmManager:
    def __init__(self, subprocess, alarmTimer:str, alarmScript:str):
        self.ALARM_TIMER = alarmTimer
        self.ALARM_SCRIPT = alarmScript
        self.subprocess = subprocess

    def loadAlarmConfig(self):
        mondayChecked = ""
        tuesdayChecked = ""
        wednesdayChecked = ""
        thursdayChecked = ""
        fridayChecked = ""
        saturdayChecked = ""
        sundayChecked = ""

        content = self.loadConfig(self.ALARM_TIMER)

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

        content = self.loadConfig(self.ALARM_SCRIPT)

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

        isMpcSupported = True

        playlists = []
        try:
            out = self.subprocess.check_output("mpc lsplaylists | grep -v m3u", shell=True, text=True)
        except:
            isMpcSupported = False
        if isMpcSupported:
            musicPlaylistName=""
            for x in out:
                if x != '\n':
                    musicPlaylistName += x
                else:
                    playlists.append(musicPlaylistName)
                    musicPlaylistName=""

        alarmIsOn = "unchecked"
        nextAlarm = ""
        try:
            output = self.subprocess.check_output(SystemdCommand.IS_ACTIVE_ALARM_TIMER, shell=True, text=True)
            #exception is called when alarm is disabled
            if "in" in output:
                alarmIsOn = "unchecked"
            else:
                alarmIsOn = "checked"
                nextAlarm = "The next alarm for:" + self.getTimeOfNextAlarm()
        except self.subprocess.CalledProcessError as grepexc:
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
                AlarmConfigFlask.GROWING_SPEED:growingSpeed,
                AlarmConfigFlask.NEXT_ALARM:nextAlarm}

    def loadConfig(self, configFile):
        f = open(configFile, "r")
        content = f.readlines()
        f.close()
        return content

    def getTimeOfNextAlarm(self):
        return str(self.subprocess.check_output(SystemdCommand.STATUS_ALARM_TIMER + " | grep \"Trigger:\" | cut -d';' -f2- | sed -e \"s/ left//\"", shell=True, text=True))

    def updateAlarmConfig(self, alarmDays, time, minVolume, maxVolume, defaultVolume,
              growingVolume, growingSpeed, alarmPlaylist, alarmMode):

        content = self.loadConfig(self.ALARM_TIMER)
        for i in range(len(content)):
            if "OnCalendar" in content[i]:
                content[i] = "OnCalendar=%s %s \n"%(alarmDays, time)

        self.saveConfig(self.ALARM_TIMER, content)

        content = self.loadConfig(self.ALARM_SCRIPT)
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

        self.saveConfig(self.ALARM_SCRIPT, content)

    def saveConfig(self, configFile:str, content:list):
        f = open(configFile,"w")
        for x in content:
            f.write(x)
        f.close()

if __name__ == "__main__":
    import subprocess
    alarmManager = AlarmManager(subprocess, "", "")
    alarmManager.getTimeOfNextAlarm()