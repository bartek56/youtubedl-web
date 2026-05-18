from .AlarmEnums import AlarmConfigFlask, AlarmConfigLinux, SystemdCommand

import logging
import configparser
logger = logging.getLogger(__name__)

class AlarmManager:
    def __init__(self, subprocess, alarmTimer:str, alarmConfig:str):
        """
        Initializes the AlarmManager with the given subprocess, alarmTimer and alarmScript.

        Parameters:
        subprocess (subprocess): the subprocess module
        alarmTimer (str): the name of the alarm timer
        alarmConfig (str): the name of the alarm script
        """
        self.ALARM_TIMER = alarmTimer
        self.ALARM_CONFIG = alarmConfig
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

        minVolume = 7
        maxVolume = 69
        defaultVolume = 11
        growingVolume = 5
        growingSpeed = 55
        alarmPlaylistName = ""
        theNewestSong = True

        theNewestSongCheckBox = "checked"
        playlistCheckbox = ""

        config = configparser.ConfigParser()
        fileIsCorrect = False
        try:
            config.read(self.ALARM_CONFIG)
            fileIsCorrect = True
        except:
            logger.error("Config file \"%s\" doesn't exist", self.ALARM_CONFIG)

        if fileIsCorrect and "alarm" in config:
            cfg = config["alarm"]

            minVolume = cfg.getint("min_volume", fallback=7)
            maxVolume = cfg.getint("max_volume", fallback=69)
            defaultVolume = cfg.getint("default_volume", fallback=11)
            growingVolume = cfg.getint("growing_volume", fallback=5)
            growingSpeed = cfg.getint("growing_speed", fallback=55)
            alarmPlaylistName = cfg.get("playlist", fallback="")
            theNewestSong = cfg.getboolean("the_newest_songs", fallback=True)
            if theNewestSong:
                theNewestSongCheckBox = "checked"
                playlistCheckbox = ""
            else:
                theNewestSongCheckBox = ""
                playlistCheckbox = "checked"

        isMpcSupported = True

        playlists = []
        try:
            #TODO use python-mpc2 library
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

        if AlarmConfigFlask.ALARM_MODE_PLAYLIST in alarmMode:
            alarmNewestModeIsEnable = "false"
        else:
            alarmNewestModeIsEnable = "true"

        config = configparser.ConfigParser()
        config["alarm"] = {
            AlarmConfigLinux.MIN_VOLUME: str(minVolume),
            AlarmConfigLinux.MAX_VOLUME: str(maxVolume),
            AlarmConfigLinux.DEFAULT_VOLUME: str(defaultVolume),
            AlarmConfigLinux.GROWING_VOLUME: str(growingVolume),
            AlarmConfigLinux.GROWING_SPEED: str(growingSpeed),
            AlarmConfigLinux.PLAYLIST: alarmPlaylist,
            AlarmConfigLinux.THE_NEWEST_SONG: alarmNewestModeIsEnable
            if AlarmConfigFlask.ALARM_MODE_PLAYLIST in alarmMode
            else "true",
        }
        with open(self.ALARM_CONFIG, "w") as f:
            config.write(f)

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