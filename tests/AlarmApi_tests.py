from typing import List
from youtubedlWeb.Common.AlarmEnums import AlarmConfigFlask, AlarmConfigLinux, SystemdCommand
from youtubedlWeb.Common.AlarmManager import AlarmConfig, AlarmManager
import unittest
import unittest.mock as mock
from unittest.mock import MagicMock
import logging
import tempfile
import os
import subprocess
from youtubedlWeb import create_app, ALARM_CONFIG, ALARM_TIMER
from youtubedlWeb.config import ConfigTesting

class AlarmTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(AlarmTestCase, self).__init__(*args, **kwargs)
        logging.disable(logging.CRITICAL)
        self.checked="checked"
        self.unchecked="unchecked"
        self.empty=""

    def setUp(self):
        self.subprocessMock = MagicMock()
        self.alarmManager = AlarmManager(self.subprocessMock, ALARM_TIMER, ALARM_CONFIG)
        self.alarmManager._loadConfig = MagicMock()
        self.alarmManager._saveConfig = MagicMock()
        self.alarmManager._loadAlarmConfig = MagicMock()
        self.alarmManager._saveAlarmConfig = MagicMock()

    def tearDown(self):
        pass

    def test_load_alarm_config(self):
        alarmsPlaylists = ["Favorites", "Alarm"]
        alarmPlaylistString = '\n'.join(str(e) for e in alarmsPlaylists) + '\n'
        alarmTime="06:30"
        minVolume=16
        maxVolume=55
        defaultVolume=11
        growingVolume=9
        growingSpeed=45
        nextAlarm=" 4h"
        nextSnooze=""

        self.subprocessMock.check_output.configure_mock(side_effect=[alarmPlaylistString, "active", nextAlarm, "inactive", nextSnooze])

        self.alarmManager._loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Mon,Tue,Wed,Thu,Fri,Sat,Sun "+alarmTime,"",
                    "[Install]","WantedBy=multi-user.target",""]])
        self.alarmManager._loadAlarmConfig.configure_mock(side_effect=[
            AlarmConfig(minVolume, maxVolume, defaultVolume, growingVolume,
                           growingSpeed, "", True)
        ])

        alarmConfig = self.alarmManager.loadAlarmConfig()

        self.assertEqual(self.subprocessMock.check_output.call_count, 4)
        self.assertEqual(self.alarmManager._loadConfig.call_count, 1)
        self.assertEqual(self.alarmManager._loadAlarmConfig.call_count, 1)

        self.assertEqual(alarmConfig[AlarmConfigFlask.ALARM_TIME], alarmTime)
        self.assertEqual(alarmConfig[AlarmConfigFlask.THE_NEWEST_SONG], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.PLAYLIST_CHECKED], "")
        self.assertListEqual(alarmConfig[AlarmConfigFlask.ALARM_PLAYLISTS], alarmsPlaylists)
        self.assertEqual(alarmConfig[AlarmConfigFlask.ALARM_PLATLIST_NAME], "")
        self.assertEqual(alarmConfig[AlarmConfigFlask.ALARM_ACTIVE], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.MONDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.TUESDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.WEDNESDEY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.THURSDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.FRIDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.SATURDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.SUNDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.MIN_VOLUME], minVolume)
        self.assertEqual(alarmConfig[AlarmConfigFlask.MAX_VOLUME], maxVolume)
        self.assertEqual(alarmConfig[AlarmConfigFlask.DEFAULT_VOLUME], defaultVolume)
        self.assertEqual(alarmConfig[AlarmConfigFlask.GROWING_VOLUME], growingVolume)
        self.assertEqual(alarmConfig[AlarmConfigFlask.GROWING_SPEED], growingSpeed)
        self.assertEqual(alarmConfig[AlarmConfigFlask.NEXT_ALARM], "The next alarm for:" + nextAlarm)

    def test_load_alarm_config_2(self):
        alarmsPlaylists = ["Favorites", "Alarm"]
        alarmPlaylistString = '\n'.join(str(e) for e in alarmsPlaylists) + '\n'
        alarmTime="06:30"
        minVolume=16
        maxVolume=55
        defaultVolume=11
        growingVolume=9
        growingSpeed=45

        self.subprocessMock.check_output.configure_mock(side_effect=[alarmPlaylistString, "inactive", "inactive"])

        self.alarmManager._loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Mon,Tue,Wed,Thu,Fri,Sat,Sun "+alarmTime,"",
                    "[Install]","WantedBy=multi-user.target",""]])

        self.alarmManager._loadAlarmConfig.configure_mock(side_effect=[
            AlarmConfig(minVolume, maxVolume, defaultVolume, growingVolume,
                           growingSpeed, alarmsPlaylists[0], False)
        ])


        alarmConfig = self.alarmManager.loadAlarmConfig()


        self.assertEqual(self.subprocessMock.check_output.call_count, 3)
        self.assertEqual(self.alarmManager._loadConfig.call_count, 1)
        self.assertEqual(self.alarmManager._loadAlarmConfig.call_count, 1)

        self.assertEqual(alarmConfig[AlarmConfigFlask.ALARM_TIME], alarmTime)
        self.assertEqual(alarmConfig[AlarmConfigFlask.THE_NEWEST_SONG], self.empty)
        self.assertEqual(alarmConfig[AlarmConfigFlask.PLAYLIST_CHECKED], self.checked)
        self.assertListEqual(alarmConfig[AlarmConfigFlask.ALARM_PLAYLISTS], alarmsPlaylists)
        self.assertEqual(alarmConfig[AlarmConfigFlask.ALARM_PLATLIST_NAME], alarmsPlaylists[0])
        self.assertEqual(alarmConfig[AlarmConfigFlask.ALARM_ACTIVE], self.unchecked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.MONDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.TUESDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.WEDNESDEY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.THURSDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.FRIDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.SATURDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.SUNDAY], self.checked)
        self.assertEqual(alarmConfig[AlarmConfigFlask.MIN_VOLUME], minVolume)
        self.assertEqual(alarmConfig[AlarmConfigFlask.MAX_VOLUME], maxVolume)
        self.assertEqual(alarmConfig[AlarmConfigFlask.DEFAULT_VOLUME], defaultVolume)
        self.assertEqual(alarmConfig[AlarmConfigFlask.GROWING_VOLUME], growingVolume)
        self.assertEqual(alarmConfig[AlarmConfigFlask.GROWING_SPEED], growingSpeed)

    def test_update_alarm_config(self):
        alarmDays="Mon,Tue,Wed"
        time="06:30"
        minVolume=5
        maxVolume=50
        defaultVolume=10
        growingVolume=5
        growingSpeed=45
        alarmPlaylist="Alarm"
        alarmMode=AlarmConfigFlask.ALARM_MODE_PLAYLIST

        #settings before saving
        self.alarmManager._loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Sun 09:00","",
                    "[Install]","WantedBy=multi-user.target"]])
        self.alarmManager._loadAlarmConfig.configure_mock(side_effect=[AlarmConfig(minVolume+1, maxVolume+1, defaultVolume+1, growingVolume+1,
                       growingSpeed+1, alarmPlaylist+"aaa", True)])


        self.alarmManager.updateAlarmConfig(alarmDays,time,minVolume,maxVolume,defaultVolume,growingVolume,growingSpeed,alarmPlaylist,alarmMode)


        self.assertEqual(self.alarmManager._saveConfig.call_count, 1)
        self.assertEqual(self.alarmManager._saveAlarmConfig.call_count, 1)

        self.alarmManager._saveConfig.assert_has_calls([mock.call(ALARM_TIMER,
                                ['[Unit]', 'Description=Alarm', '',
                                 '[Timer]', 'OnCalendar=' + alarmDays +' '+ time + '', '',
                                 '[Install]', 'WantedBy=multi-user.target'])])
        self.alarmManager._saveAlarmConfig.assert_called_once_with(minVolume, maxVolume, defaultVolume, growingVolume, growingSpeed, alarmPlaylist, 'false')

    def test_update_alarm_config_2(self):
        alarmDays="Mon,Tue,Wed,Thu,Fri,Sat,Sun"
        time="04:20"
        minVolume=5
        maxVolume=43
        defaultVolume=17
        growingVolume=9
        growingSpeed=55
        alarmPlaylist="Alarm"
        alarmMode=AlarmConfigFlask.ALARM_MODE_NEWEST

        #settings before saving
        self.alarmManager._loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Sun 09:00","",
                    "[Install]","WantedBy=multi-user.target",""]])


        self.alarmManager.updateAlarmConfig(alarmDays,time,minVolume,maxVolume,defaultVolume,growingVolume,growingSpeed,alarmPlaylist,alarmMode)


        self.assertEqual(self.alarmManager._saveConfig.call_count, 1)
        self.assertEqual(self.alarmManager._saveAlarmConfig.call_count, 1)
        self.alarmManager._saveConfig.assert_has_calls([mock.call(ALARM_TIMER,
                                ['[Unit]', 'Description=Alarm', '',
                                 '[Timer]', 'OnCalendar=' + alarmDays +' '+ time + '', '',
                                 '[Install]', 'WantedBy=multi-user.target'])])
        self.alarmManager._saveAlarmConfig.assert_called_with(minVolume, maxVolume, defaultVolume, growingVolume, growingSpeed, alarmPlaylist, 'true')



class AlarmConfigsFilesTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(AlarmConfigsFilesTestCase, self).__init__(*args, **kwargs)
        logging.disable(logging.CRITICAL)
        self.checked="checked"
        self.unchecked="unchecked"
        self.empty=""

    def setUp(self):
        self.subprocessMock = MagicMock()
        self.alarmManager = AlarmManager(self.subprocessMock, ALARM_TIMER, ALARM_CONFIG)

    def tearDown(self):
        pass

    def test_get_time_of_service(self):
        """_getTimeOfService should return the exact output from subprocess.check_output as string."""
        # simulate systemd status output
        status_output = " 3h"
        self.subprocessMock.check_output.configure_mock(return_value=status_output)

        result = self.alarmManager._getTimeOfService(SystemdCommand.STATUS_ALARM_TIMER)
        self.assertEqual(result, status_output)

    def test_next_alarm_check_inactive(self):
        """If subprocess.check_output raises CalledProcessError, nextAlarmCheck returns empty string."""
        # ensure the manager's subprocess module has the CalledProcessError attribute
        self.subprocessMock.CalledProcessError = subprocess.CalledProcessError
        # simulate CalledProcessError when checking active status
        self.subprocessMock.check_output.configure_mock(side_effect=subprocess.CalledProcessError(1, 'cmd'))

        result = self.alarmManager.nextAlarmCheck()
        self.assertEqual(result, "")

    def test_save_and_load_alarm_config_file_roundtrip(self):
        """Write alarm config to a temp file via _saveAlarmConfig and read it back with _loadAlarmConfig."""
        fd, path = tempfile.mkstemp(prefix="test_alarm_", suffix=".ini")
        os.close(fd)
        try:
            # create a fresh manager that uses the temp path for ALARM_CONFIG
            manager = AlarmManager(self.subprocessMock, ALARM_TIMER, path)

            minV, maxV, defV, growV, growS = 3, 77, 33, 8, 12
            playlist = "MyList"
            newest = 'true'

            manager._saveAlarmConfig(minV, maxV, defV, growV, growS, playlist, newest)

            loaded = manager._loadAlarmConfig()
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.min_volume, minV)
            self.assertEqual(loaded.max_volume, maxV)
            self.assertEqual(loaded.default_volume, defV)
            self.assertEqual(loaded.growing_volume, growV)
            self.assertEqual(loaded.growing_speed, growS)
            self.assertEqual(loaded.playlist, playlist)
            # configparser stores booleans and _loadAlarmConfig returns boolean
            self.assertTrue(isinstance(loaded.newest_song_mode, bool))
        finally:
            try:
                os.remove(path)
            except Exception:
                pass

class FlaskClientAlarmTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FlaskClientAlarmTestCase, self).__init__(*args, **kwargs)
        logging.disable(logging.CRITICAL)
        self.checked="checked"
        self.unchecked="unchecked"
        self.empty=""

    def setUp(self):
        self.mainApp = create_app(config=ConfigTesting)
        self.app = self.mainApp.test_client()
        self.mainApp.alarmManager._loadConfig = MagicMock()
        self.mainApp.alarmManager._saveConfig = MagicMock()
        self.mainApp.alarmManager._loadAlarmConfig = MagicMock()
        self.mainApp.alarmManager._saveAlarmConfig = MagicMock()

    def tearDown(self):
        pass


    @mock.patch('subprocess.check_output')
    def test_alarm_html(self, mock_proc_check_output):
        alarm_time="06:50"
        minVolume=16
        maxVolume=55
        defaultVolume=11
        growingVolume=7
        growingSpeed=45

        mock_proc_check_output.configure_mock(side_effect=["Favorites\nAlarm\n", "active", " 8h", " inactive"])
        self.mainApp.alarmManager._loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Mon,Tue,Wed,Thu,Fri,Sat,Sun "+alarm_time,"",
                    "[Install]","WantedBy=multi-user.target",""]
                    ])
        self.mainApp.alarmManager._loadAlarmConfig.configure_mock(side_effect=[
            AlarmConfig(minVolume, maxVolume, defaultVolume, growingVolume,
                           growingSpeed, "", True)
        ])

        rv = self.app.get('/alarm.html')
        self.assertEqual(mock_proc_check_output.call_count, 4)
        self.assertEqual(self.mainApp.alarmManager._loadConfig.call_count, 1)
        self.assertEqual(self.mainApp.alarmManager._loadAlarmConfig.call_count, 1)

        assert rv.status_code == 200
        assert str('name="'+AlarmConfigFlask.ALARM_TIME+'" value="'+alarm_time+'"').encode() in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_MODE+'" value="'+AlarmConfigFlask.ALARM_MODE_NEWEST+'" checked>').encode() in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_MODE+'" value="'+AlarmConfigFlask.ALARM_MODE_PLAYLIST+'" >').encode()      in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_ACTIVE+'" value="checked" checked>').encode()                              in rv.data
        assert b'<option value="Alarm">Alarm</option>'                               in rv.data
        assert b'<option value="Favorites">Favorites</option>'                       in rv.data
        assert b'value="monday" checked>'                                            in rv.data
        assert b'value="tueday" checked>'                                            in rv.data
        assert b'value="wedday" checked>'                                            in rv.data
        assert b'value="thuday" checked>'                                            in rv.data
        assert b'value="friday" checked>'                                            in rv.data
        assert b'value="satday" checked>'                                            in rv.data
        assert b'value="sunday" checked>'                                            in rv.data
        assert str('value="'+str(minVolume)+'" name="'+AlarmConfigFlask.MIN_VOLUME+'">').encode()         in rv.data
        assert str('value="'+str(maxVolume)+'" name="'+AlarmConfigFlask.MAX_VOLUME+'">').encode()         in rv.data
        assert str('value="'+str(defaultVolume)+'" name="'+AlarmConfigFlask.DEFAULT_VOLUME+'">').encode() in rv.data
        assert b'The next alarm for: 8h' in rv.data
        assert b'<div id="next_alarm">' in rv.data
        assert b'<div id="next_snooze" hidden="true">' in rv.data
        assert b'<title>Media Server</title>' in rv.data

    @mock.patch('subprocess.check_output')
    def test_snooze_alarm_html(self, mock_proc_check_output):
        alarm_time="06:50"
        minVolume=16
        maxVolume=55
        defaultVolume=11
        growingVolume=7
        growingSpeed=45

        mock_proc_check_output.configure_mock(side_effect=["Favorites\nAlarm\n", "active", " 8h", "active", " 7 minutes"])
        self.mainApp.alarmManager._loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Mon,Tue,Wed,Thu,Fri,Sat,Sun "+alarm_time,"",
                    "[Install]","WantedBy=multi-user.target",""],
                    ])
        self.mainApp.alarmManager._loadAlarmConfig.configure_mock(side_effect=[
            AlarmConfig(minVolume, maxVolume, defaultVolume, growingVolume,
                           growingSpeed, "", True)
        ])

        rv = self.app.get('/alarm.html')
        self.assertEqual(mock_proc_check_output.call_count, 5)
        self.assertEqual(self.mainApp.alarmManager._loadConfig.call_count, 1)

        assert rv.status_code == 200
        assert str('name="'+AlarmConfigFlask.ALARM_TIME+'" value="'+alarm_time+'"').encode() in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_MODE+'" value="'+AlarmConfigFlask.ALARM_MODE_NEWEST+'" checked>').encode() in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_MODE+'" value="'+AlarmConfigFlask.ALARM_MODE_PLAYLIST+'" >').encode()      in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_ACTIVE+'" value="checked" checked>').encode()                              in rv.data
        assert b'<option value="Alarm">Alarm</option>'                               in rv.data
        assert b'<option value="Favorites">Favorites</option>'                       in rv.data
        assert b'value="monday" checked>'                                            in rv.data
        assert b'value="tueday" checked>'                                            in rv.data
        assert b'value="wedday" checked>'                                            in rv.data
        assert b'value="thuday" checked>'                                            in rv.data
        assert b'value="friday" checked>'                                            in rv.data
        assert b'value="satday" checked>'                                            in rv.data
        assert b'value="sunday" checked>'                                            in rv.data
        assert str('value="'+str(minVolume)+'" name="'+AlarmConfigFlask.MIN_VOLUME+'">').encode()         in rv.data
        assert str('value="'+str(maxVolume)+'" name="'+AlarmConfigFlask.MAX_VOLUME+'">').encode()         in rv.data
        assert str('value="'+str(defaultVolume)+'" name="'+AlarmConfigFlask.DEFAULT_VOLUME+'">').encode() in rv.data
        assert b'The next snooze alarm for: 7 minutes' in rv.data
        assert b'The next alarm for: 8h' in rv.data
        assert b'<div id="next_alarm" hidden="true">' in rv.data
        assert b'<div id="next_snooze">' in rv.data
        assert b'<title>Media Server</title>' in rv.data

    @mock.patch('subprocess.check_output', side_effect=["Favorites\nAlarm\n", "active", " for 4h", "inactive"])
    @mock.patch('subprocess.run')
    def test_save_alarm_html(self, mock_subprocess_run, mock_subprocess_checkoutput):
        alarmDays="Mon,Tue,Wed"
        time="06:30"
        minVolume=5
        maxVolume=50
        defaultVolume=10
        growingVolume=5
        growingSpeed=45
        alarmPlaylist="Alarm"
        alarmMode=AlarmConfigFlask.ALARM_MODE_PLAYLIST

        returnCode = mock.MagicMock()
        returnCode.returncode = 0
        mock_subprocess_run.configure_mock(return_value=returnCode)

        self.mainApp.alarmManager._loadConfig.configure_mock(side_effect=[
                ["[Unit]","Description=Alarm","",
                "[Timer]","OnCalendar="+alarmDays+" "+time,"",
                "[Install]","WantedBy=multi-user.target",""]
                ])

        self.mainApp.alarmManager._loadAlarmConfig.configure_mock(side_effect=[
            AlarmConfig(minVolume, maxVolume, defaultVolume, growingVolume,
                       growingSpeed, "", True)
        ])


        rv = self.app.post('/save_alarm',
                            data=dict(alarm_time=time, alarm_mode=alarmMode, playlists=alarmPlaylist,
                                    min_volume=str(minVolume), max_volume=str(maxVolume), default_volume=str(defaultVolume),
                                    growing_volume=str(growingVolume), growing_speed=str(growingSpeed),
                                    alarm_active="true", monday=['monday'], tueday=['tueday'], wedday=['wedday']),
                            follow_redirects=True)


        self.assertEqual(rv.status_code, 200)
        self.assertEqual(self.mainApp.alarmManager._saveConfig.call_count, 1)
        self.assertEqual(self.mainApp.alarmManager._saveAlarmConfig.call_count, 1)
        self.assertEqual(self.mainApp.alarmManager._loadAlarmConfig.call_count, 1)
        self.assertEqual(self.mainApp.alarmManager._loadConfig.call_count, 1)


        self.mainApp.alarmManager._saveConfig.assert_has_calls([mock.call(ALARM_TIMER,
                    ['[Unit]', 'Description=Alarm', '',
                     '[Timer]', 'OnCalendar=' + alarmDays +' '+ time + '', '',
                 '[Install]', 'WantedBy=multi-user.target'])])
        self.mainApp.alarmManager._saveAlarmConfig.assert_called_once_with(str(minVolume), str(maxVolume), str(defaultVolume), str(growingVolume), str(growingSpeed), alarmPlaylist, 'false')

        mock_subprocess_run.assert_has_calls([mock.call(SystemdCommand.STOP_ALARM_TIMER, shell=True),
                                              mock.call(SystemdCommand.DAEMON_RELOAD, shell=True),
                                              mock.call(SystemdCommand.START_ALARM_TIMER, shell=True)])


        self.assertEqual(mock_subprocess_checkoutput.call_count, 4)
        mock_subprocess_checkoutput.assert_has_calls([mock.call('mpc lsplaylists | grep -v m3u', shell=True, text=True),
                                                      mock.call(SystemdCommand.IS_ACTIVE_ALARM_TIMER, shell=True, text=True),
                                                      mock.call(SystemdCommand.STATUS_ALARM_TIMER+" | grep \"Trigger:\" | cut -d\';\' -f2- | sed -e \"s/ left//\"", shell=True, text=True)])


        assert rv.status_code == 200
        assert str('name="'+AlarmConfigFlask.ALARM_TIME+'" value="'+time+'"').encode()                    in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_MODE+'" value="'+AlarmConfigFlask.ALARM_MODE_NEWEST+'" checked>').encode()    in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_MODE+'" value="'+AlarmConfigFlask.ALARM_MODE_PLAYLIST+'" >').encode()         in rv.data
        assert b'<option value="Alarm">Alarm</option>'                               in rv.data
        assert b'<option value="Favorites">Favorites</option>'                       in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_ACTIVE+'" value="checked" checked>').encode()          in rv.data
        assert b'value="monday" checked>'                                            in rv.data
        assert b'value="tueday" checked>'                                            in rv.data
        assert b'value="wedday" checked>'                                            in rv.data
        assert b'value="thuday" >'                                                   in rv.data
        assert b'value="friday" >'                                                   in rv.data
        assert b'value="satday" >'                                                   in rv.data
        assert b'value="sunday" >'                                                   in rv.data
        assert b' for 4h'                                                            in rv.data
        assert str('value="'+str(minVolume)+'" name="'+AlarmConfigFlask.MIN_VOLUME+'">').encode()         in rv.data
        assert str('value="'+str(maxVolume)+'" name="'+AlarmConfigFlask.MAX_VOLUME+'">').encode()         in rv.data
        assert str('value="'+str(defaultVolume)+'" name="'+AlarmConfigFlask.DEFAULT_VOLUME+'">').encode() in rv.data
        assert b'<title>Media Server</title>' in rv.data

    @mock.patch('subprocess.check_output', side_effect=["Favorites\nAlarm\n", "active", " for 4h", "inactive"])
    @mock.patch('subprocess.run')
    def test_save_alarm_html_2(self, mock_subprocess_run, mock_subprocess_checkoutput):
        alarmDays="Mon,Tue,Wed,Thu,Fri,Sat,Sun"
        time="06:30"
        minVolume=5
        maxVolume=50
        defaultVolume=10
        growingVolume=7
        growingSpeed=45
        alarmPlaylist=""
        alarmMode=AlarmConfigFlask.ALARM_MODE_NEWEST

        returnCode = mock.MagicMock()
        returnCode.returncode = 0
        mock_subprocess_run.configure_mock(return_value=returnCode)

        self.mainApp.alarmManager._loadConfig.configure_mock(side_effect=[
                ["[Unit]","Description=Alarm","",
                "[Timer]","OnCalendar="+alarmDays+" "+time,"",
                "[Install]","WantedBy=multi-user.target",""]
                ])
        self.mainApp.alarmManager._loadAlarmConfig.configure_mock(side_effect=[
            AlarmConfig(minVolume, maxVolume, defaultVolume, growingVolume,
                       growingSpeed, "", True)
        ])


        rv = self.app.post('/save_alarm',
                            data=dict(alarm_time=time, alarm_mode=alarmMode, playlists=alarmPlaylist,
                                    min_volume=str(minVolume), max_volume=str(maxVolume), default_volume=str(defaultVolume),
                                    growing_volume=str(growingVolume), growing_speed=str(growingSpeed),
                                    alarm_active="true", monday=['monday'], tueday=['tueday'], wedday=['wedday'], thuday=['thuday'], friday=['friday'], satday=['satday'], sunday=['sunday'] ),
                            follow_redirects=True)



        self.assertEqual(rv.status_code, 200)
        self.assertEqual(self.mainApp.alarmManager._saveConfig.call_count, 1)
        self.assertEqual(self.mainApp.alarmManager._saveAlarmConfig.call_count, 1)
        self.assertEqual(self.mainApp.alarmManager._loadAlarmConfig.call_count, 1)
        self.assertEqual(self.mainApp.alarmManager._loadConfig.call_count, 1)

        self.mainApp.alarmManager._saveConfig.assert_has_calls([mock.call(self.mainApp.alarmManager. ALARM_TIMER,
                                ['[Unit]', 'Description=Alarm', '',
                                 '[Timer]', 'OnCalendar=' + alarmDays +' '+ time + '', '',
                                 '[Install]', 'WantedBy=multi-user.target'])])
        self.mainApp.alarmManager._saveAlarmConfig.assert_called_with(str(minVolume), str(maxVolume), str(defaultVolume), str(growingVolume), str(growingSpeed), alarmPlaylist, 'true')

        mock_subprocess_run.assert_has_calls([mock.call(SystemdCommand.STOP_ALARM_TIMER, shell=True),
                                              mock.call(SystemdCommand.DAEMON_RELOAD, shell=True),
                                              mock.call(SystemdCommand.START_ALARM_TIMER, shell=True)])

        self.assertEqual(mock_subprocess_checkoutput.call_count, 4)

        mock_subprocess_checkoutput.assert_has_calls([mock.call('mpc lsplaylists | grep -v m3u', shell=True, text=True),
                                                      mock.call(SystemdCommand.IS_ACTIVE_ALARM_TIMER, shell=True, text=True),
                                                      mock.call(SystemdCommand.STATUS_ALARM_TIMER+" | grep \"Trigger:\" | cut -d\';\' -f2- | sed -e \"s/ left//\"", shell=True, text=True)])


        assert rv.status_code == 200
        assert str('name="'+AlarmConfigFlask.ALARM_TIME+'" value="'+time+'"').encode() in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_MODE+'" value="'+AlarmConfigFlask.ALARM_MODE_NEWEST+'" checked>').encode() in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_MODE+'" value="'+AlarmConfigFlask.ALARM_MODE_PLAYLIST+'" >').encode()      in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_ACTIVE+'" value="checked" checked>').encode()                              in rv.data
        assert b'<option value="Alarm">Alarm</option>'                               in rv.data
        assert b'<option value="Favorites">Favorites</option>'                       in rv.data
        assert b'value="monday" checked>'                                            in rv.data
        assert b'value="tueday" checked>'                                            in rv.data
        assert b'value="wedday" checked>'                                            in rv.data
        assert b'value="thuday" checked>'                                            in rv.data
        assert b'value="friday" checked>'                                            in rv.data
        assert b'value="satday" checked>'                                            in rv.data
        assert b'value="sunday" checked>'                                            in rv.data
        assert str('value="'+str(minVolume)+'" name="'+AlarmConfigFlask.MIN_VOLUME+'">').encode()         in rv.data
        assert str('value="'+str(maxVolume)+'" name="'+AlarmConfigFlask.MAX_VOLUME+'">').encode()         in rv.data
        assert str('value="'+str(defaultVolume)+'" name="'+AlarmConfigFlask.DEFAULT_VOLUME+'">').encode() in rv.data
        assert b'<title>Media Server</title>' in rv.data

    @mock.patch('subprocess.check_output', side_effect=["Favorites\nAlarm\n", "inactive", " for 4h", "inactive"])
    @mock.patch('subprocess.run')
    def test_save_alarm_inactive(self, mock_subprocess_run, mock_subprocess_checkoutput):
        """Save alarm when systemd reports timer inactive: ALARM_ACTIVE should not be checked."""
        alarmDays="Mon,Tue,Wed"
        time="06:30"
        minVolume=5
        maxVolume=50
        defaultVolume=10
        growingVolume=5
        growingSpeed=45
        alarmPlaylist="Alarm"
        alarmMode=AlarmConfigFlask.ALARM_MODE_PLAYLIST

        returnCode = mock.MagicMock()
        returnCode.returncode = 0
        mock_subprocess_run.configure_mock(return_value=returnCode)

        self.mainApp.alarmManager._loadConfig.configure_mock(side_effect=[
                ["[Unit]","Description=Alarm","",
                "[Timer]","OnCalendar="+alarmDays+" "+time,"",
                "[Install]","WantedBy=multi-user.target",""]
                ])

        self.mainApp.alarmManager._loadAlarmConfig.configure_mock(side_effect=[
            AlarmConfig(minVolume, maxVolume, defaultVolume, growingVolume,
                       growingSpeed, "", True)
        ])

        rv = self.app.post('/save_alarm',
                            data=dict(alarm_time=time, alarm_mode=alarmMode, playlists=alarmPlaylist,
                                    min_volume=str(minVolume), max_volume=str(maxVolume), default_volume=str(defaultVolume),
                                    growing_volume=str(growingVolume), growing_speed=str(growingSpeed),
                                    monday=['monday'], tueday=['tueday'], wedday=['wedday']),
                            follow_redirects=True)

        self.assertEqual(rv.status_code, 200)
        # since subprocess returned "inactive", the alarm active checkbox should not be rendered as checked
        assert str('name="'+AlarmConfigFlask.ALARM_ACTIVE+'" value="checked" checked>').encode() not in rv.data

    @mock.patch('subprocess.check_output', side_effect=["Favorites\nAlarm\n", "inactive", " for 4h", "inactive"])
    @mock.patch('subprocess.run')
    def test_save_alarm_playlist_mode(self, mock_subprocess_run, mock_subprocess_checkoutput):
        """Save alarm in playlist mode and ensure playlist radio is selected (playlist mode checked)."""
        alarmDays="Mon,Tue,Wed"
        time="07:15"
        minVolume=6
        maxVolume=45
        defaultVolume=12
        growingVolume=4
        growingSpeed=30
        alarmPlaylist="Alarm"
        alarmMode=AlarmConfigFlask.ALARM_MODE_PLAYLIST

        returnCode = mock.MagicMock()
        returnCode.returncode = 0
        mock_subprocess_run.configure_mock(return_value=returnCode)

        self.mainApp.alarmManager._loadConfig.configure_mock(side_effect=[
                ["[Unit]","Description=Alarm","",
                "[Timer]","OnCalendar="+alarmDays+" "+time,"",
                "[Install]","WantedBy=multi-user.target",""]
                ])

        self.mainApp.alarmManager._loadAlarmConfig.configure_mock(side_effect=[
            AlarmConfig(minVolume, maxVolume, defaultVolume, growingVolume,
                       growingSpeed, "", True)
        ])

        rv = self.app.post('/save_alarm',
                            data=dict(alarm_time=time, alarm_mode=alarmMode, playlists=alarmPlaylist,
                                    min_volume=str(minVolume), max_volume=str(maxVolume), default_volume=str(defaultVolume),
                                    growing_volume=str(growingVolume), growing_speed=str(growingSpeed),
                                    alarm_active="true", monday=['monday'], tueday=['tueday'], wedday=['wedday']),
                            follow_redirects=True)

        self.assertEqual(rv.status_code, 200)
        # verify the manager was asked to save playlist-mode (last arg 'false')
        self.mainApp.alarmManager._saveAlarmConfig.assert_called_once_with(str(minVolume), str(maxVolume), str(defaultVolume), str(growingVolume), str(growingSpeed), alarmPlaylist, 'false')
        # playlist option must be present in the resulting page
        assert b'<option value="Alarm">Alarm</option>' in rv.data

    @mock.patch('subprocess.check_output')
    def test_load_alarm_html_playlist_selected(self, mock_proc_check_output):
        """Load alarm page when stored config is in playlist mode: playlist radio should be checked."""
        alarm_time="06:50"
        minVolume=10
        maxVolume=60
        defaultVolume=20
        growingVolume=5
        growingSpeed=15

        mock_proc_check_output.configure_mock(side_effect=["Favorites\nAlarm\n", "inactive", " 8h", "inactive"])
        self.mainApp.alarmManager._loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Mon,Tue,Wed,Thu,Fri,Sat,Sun "+alarm_time,"",
                    "[Install]","WantedBy=multi-user.target",""]
                    ])
        # AlarmConfig: last parameter False means playlist mode (not newest)
        self.mainApp.alarmManager._loadAlarmConfig.configure_mock(side_effect=[
            AlarmConfig(minVolume, maxVolume, defaultVolume, growingVolume,
                           growingSpeed, "Alarm", False)
        ])

        rv = self.app.get('/alarm.html')
        assert rv.status_code == 200
        # playlist mode should be checked, newest should not
        assert str('name="'+AlarmConfigFlask.ALARM_MODE+'" value="'+AlarmConfigFlask.ALARM_MODE_PLAYLIST+'" checked>').encode() in rv.data
        assert str('name="'+AlarmConfigFlask.ALARM_MODE+'" value="'+AlarmConfigFlask.ALARM_MODE_NEWEST+'" >').encode() in rv.data


if __name__ == "__main__":
    unittest.main()
