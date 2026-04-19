from .AlarmEnums import AlarmConfigFlask, AlarmConfigLinux, SystemdCommand

import logging
logger = logging.getLogger(__name__)

class AlarmManager:
    def __init__(self, subprocess, alarmTimer:str, alarmScript:str):
        """
        Initializes the AlarmManager with the given subprocess, alarmTimer and alarmScript.

        Parameters:
        subprocess (subprocess): the subprocess module
        alarmTimer (str): the name of the alarm timer
        alarmScript (str): the name of the alarm script
        """
        self.ALARM_TIMER = alarmTimer
        self.ALARM_SCRIPT = alarmScript
        self.subprocess = subprocess

    def loadAlarmConfig(self):
        """
        Loads the alarm configuration from the timer and script.

        Returns:
            A dictionary with the alarm configuration.
        """
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
        nextAlarm = self.nextAlarmCheck()
        if len(nextAlarm) > 0:
            alarmIsOn = "checked"

        nextSnooze = self.nextSnoozeCheck()

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
                AlarmConfigFlask.NEXT_ALARM:nextAlarm,
                AlarmConfigFlask.NEXT_SNOOZE:nextSnooze}

    def loadConfig(self, configFile):
        """
        Loads the alarm configuration from a file.

        This function opens the specified file and reads it line by line. It then returns
        the list of lines.

        Args:
            configFile (str): The file path to the alarm configuration file.

        Returns:
            content (list): A list of strings representing the alarm configuration file.
        """
        f = open(configFile, "r")
        content = f.readlines()
        f.close()
        return content

    def nextSnoozeCheck(self):
        """
        Checks the status of the alarm snooze timer.

        This function checks if the alarm snooze timer is active. If it is active,
        it will return the time of the next snooze alarm. If the alarm snooze timer
        is disabled, it will return an empty string.

        Returns:
            nextSnooze (str): The time of the next snooze alarm, or an empty string if
                the alarm snooze timer is disabled.
        """
        nextSnooze = ""
        try:
            output = self.subprocess.check_output(SystemdCommand.IS_ACTIVE_ALARM_SNOOZE_TIMER, shell=True, text=True)
            #exception is called when alarm is disabled
            if "in" not in output:
                nextSnooze= "The next snooze alarm for:" + self.getTimeOfService(SystemdCommand.STATUS_ALARM_SNOOZE_TIMER)

        except self.subprocess.CalledProcessError as grepexc:
            logger.info("Exception - alarm_snooze is disabled")
        return nextSnooze

    def nextAlarmCheck(self):
        """
        Checks the status of the alarm timer.

        This function checks if the alarm timer is active. If it is active,
        it will return the time of the next alarm. If the alarm timer is disabled,
        it will return an empty string.

        Returns:
            nextAlarm (str): The time of the next alarm, or an empty string if
                the alarm timer is disabled.
        """
        nextAlarm=""
        try:
            output = self.subprocess.check_output(SystemdCommand.IS_ACTIVE_ALARM_TIMER, shell=True, text=True)
            #exception is called when alarm is disabled
            if "in" not in output:
                nextAlarm = "The next alarm for:" + self.getTimeOfService(SystemdCommand.STATUS_ALARM_TIMER)
        except self.subprocess.CalledProcessError as grepexc:
            logger.info("Exception - alarm is disabled")
        return nextAlarm

    def getTimeOfService(self, systemdService:SystemdCommand):
        """
        Gets the time of a given systemd service.

        This function gets the time of a given systemd service. It will run a
        command to get the time of the service and return it as a string.

        Parameters:
            systemdService (SystemdCommand): The systemd service to get the time of.

        Returns:
            str: The time of the given systemd service.
        """
        return str(self.subprocess.check_output(systemdService + " | grep \"Trigger:\" | cut -d';' -f2- | sed -e \"s/ left//\"", shell=True, text=True))

    def updateAlarmConfig(self, alarmDays, time, minVolume, maxVolume, defaultVolume,
              growingVolume, growingSpeed, alarmPlaylist, alarmMode):

        """
        Updates the alarm configuration.

        This function updates the alarm configuration. It will take the new alarm
        settings and update the alarm timer and alarm script. It will then save
        the updated configuration.

        Parameters:
            alarmDays (str): The days of the week to trigger the alarm.
            time (str): The time of the day to trigger the alarm.
            minVolume (int): The minimum volume of the alarm.
            maxVolume (int): The maximum volume of the alarm.
            defaultVolume (int): The default volume of the alarm.
            growingVolume (int): The growing volume of the alarm.
            growingSpeed (int): The growing speed of the alarm.
            alarmPlaylist (str): The playlist to play during the alarm.
            alarmMode (str): The mode of the alarm.

        Returns:
            None
        """
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
        """
        Saves the content to the config file.

        Args:
            configFile (str): The name of the config file.
            content (list): The content to be saved.

        Returns:
            None
        """
        f = open(configFile,"w")
        for x in content:
            f.write(x)
        f.close()

if __name__ == "__main__":
    import subprocess
    alarmManager = AlarmManager(subprocess, "", "")
    alarmManager.getTimeOfService(SystemdCommand.STATUS_ALARM_TIMER)