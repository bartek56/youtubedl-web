from youtubedl import AlarmConfigFlask, AlarmConfigLinux, SystemdCommand
import youtubedl
import unittest
import unittest.mock as mock
from configparser import ConfigParser
from Common.mailManager import Mail
from Common.YouTubeManager import YoutubeDl, YoutubeConfig


class FlaskClientTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FlaskClientTestCase, self).__init__(*args, **kwargs)
        self.checked="checked"
        self.unchecked="unchecked"
        self.empty=""

    def setUp(self):
        youtubedl.app.config['TESTING'] = True
        self.app = youtubedl.app.test_client()
        self.mailManager = youtubedl.mailManager
        self.ytManager = youtubedl.youtubeManager
        self.ytConfig = youtubedl.youtubeConfig

    def tearDown(self):
        pass

    def test_home_page(self):
        rv = self.app.get('/index.html')
        assert rv.status_code == 200
        assert b'<title>Media Server</title>' in rv.data

    def test_wrong_page(self):
        rv = self.app.get('/zzzz')
        assert rv.status_code == 404
        assert b'404 Not Found' in rv.data

    @mock.patch.object(Mail, 'initialize', return_value=False)
    def test_contact_mailNotInitialized(self, mock_mail):
        rv = self.app.get('/contact.html')
        assert rv.status_code == 200
        assert b'<title>Media Server</title>' in rv.data
        assert b'Mail is not support' in rv.data

    @mock.patch.object(Mail, 'initialize', return_value=True)
    def test_contact_mailInitialized(self, mock_initialize_mail):
        rv = self.app.get('/contact.html')
        assert rv.status_code == 200
        mock_initialize_mail.assert_called_once()
        assert b'<title>Media Server</title>' in rv.data
        assert b'enter text here' in rv.data

    def mail(self, senderMail, textMail):
        return self.app.post('/mail', data=dict(
        sender=senderMail,
        message=textMail
    ), follow_redirects=True)

    @mock.patch.object(Mail, 'sendMail', autospec=True)
    def test_correct_mail(self, mock_sendMail):
        rv = self.mail('test@wp.pl', 'mail text')
        mock_sendMail.assert_called_with(self.mailManager, "bartosz.brzozowski23@gmail.com", "MediaServer", "You received message from test@wp.pl: mail text")
        self.assertEqual(rv.status_code, 200)
        assert b'Successfull send mail' in rv.data

    @mock.patch.object(Mail, 'sendMail', autospec=True)
    def test_wrong_mail(self, mock_Gmail):
        rv = self.mail('jkk', '')
        assert b'You have to fill in the fields' in rv.data

    def yt_dlp(self, url, type):
        return self.app.post('/download', data=dict(
        link=url,
        quickdownload=type
    ), follow_redirects=True)

    @mock.patch.object(YoutubeDl, 'download_mp3', return_value={"title": "song","path":"/home/music/song.mp3"})
    @mock.patch('youtubedl.isFile', return_value=False)
    def test_failed_download_mp3(self, mock_isFile, mock_mp3):
        ytLink = "https://youtu.be/q1MmYVcDyMs"
        rv = self.yt_dlp(ytLink, 'mp3')
        mock_mp3.assert_called_once_with(ytLink)
        self.assertEqual(mock_isFile.call_count, 2)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Failed downloaded', rv.data)

    @mock.patch.object(YoutubeDl, 'download_mp3', return_value={"title": "song example","path":"/home/music/song.mp3"})
    @mock.patch('youtubedl.isFile', return_value=True)
    def test_download_mp3(self, mock_isFile, mock_mp3):
        ytLink = "https://youtu.be/q1MmYVcDyMs"
        rv = self.yt_dlp(ytLink, 'mp3')
        mock_mp3.assert_called_once_with(ytLink)
        self.assertEqual(mock_isFile.call_count, 2)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'<form action="/download_file"', rv.data)
        self.assertIn(b'Type: MP3 audio', rv.data)
        self.assertIn(b'title: song example', rv.data)

    @mock.patch.object(YoutubeDl, 'download_360p', return_value={"title": "video example","path":"/home/music/wideo.mp4"})
    @mock.patch('youtubedl.isFile', return_value=True)
    def test_download_360p(self, mock_isFile, mock_download):
        ytLink = "https://youtu.be/q1MmYVcDyMs"
        rv = self.yt_dlp(ytLink, '360p')
        mock_download.assert_called_once_with(ytLink)
        self.assertEqual(mock_isFile.call_count, 2)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'<form action="/download_file"', rv.data)
        self.assertIn(b'Type: video', rv.data)
        self.assertIn(b'title: video example', rv.data)

    @mock.patch.object(YoutubeDl, 'download_720p', return_value={"title": "video example","path":"/home/music/wideo.mp4"})
    @mock.patch('youtubedl.isFile', return_value=True)
    def test_download_720p(self, mock_isFile, mock_download):
        ytLink = "https://youtu.be/q1MmYVcDyMs"
        rv = self.yt_dlp(ytLink, '720p')
        mock_download.assert_called_once_with(ytLink)
        self.assertEqual(mock_isFile.call_count, 2)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'<form action="/download_file"', rv.data)
        self.assertIn(b'Type: video', rv.data)
        self.assertIn(b'title: video example', rv.data)

    @mock.patch.object(YoutubeDl, 'download_4k', return_value={"title": "video example","path":"/home/music/wideo.mp4"})
    @mock.patch('youtubedl.isFile', return_value=True)
    def test_download_4k(self, mock_isFile, mock_download):
        ytLink = "https://youtu.be/q1MmYVcDyMs"
        rv = self.yt_dlp(ytLink, '4k')
        mock_download.assert_called_once_with(ytLink)
        self.assertEqual(mock_isFile.call_count, 2)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'<form action="/download_file"', rv.data)
        self.assertIn(b'Type: video', rv.data)
        self.assertIn(b'title: video example', rv.data)

    @mock.patch("flask.send_file")
    def test_download_file(self, mock):
        rv = self.app.post('/download_file', data=dict(path="/tmp/fileForDownload.mp4"))
        mock.assert_called_once_with("/tmp/fileForDownload.mp4", as_attachment=True)
        assert rv.status_code == 200

    @mock.patch.object(YoutubeConfig, 'getPlaylistsName', return_value=["playlist1, playlist2"])
    @mock.patch.object(YoutubeConfig, 'addPlaylist')
    def test_add_playlist(self, mock_addPLaylist, mock_getPlaylistsName):
        rv = self.app.post('/playlists', data=dict(add=True, playlist_name="yt_playlist", link="https://youtube.com/link"), follow_redirects=True)
        mock_getPlaylistsName.assert_called_once()
        mock_addPLaylist.assert_called_once_with({'name': 'yt_playlist', 'link': 'https://youtube.com/link'})
        assert rv.status_code == 200
        assert b'<title>Media Server</title>' in rv.data

    @mock.patch.object(YoutubeConfig, 'removePlaylist', return_value=True)
    def test_remove_playlist(self, mock_removePlaylist):
        class CustomConfigParser(ConfigParser):
            def read(self, filename):
                self.read_string("[playlist_to_remove]\nname = playlist_to_remove\nlink = http://youtube.com/test\n[playlist]\nname = playlist\nlink = http://youtube.com/test\n")
        self.ytConfig.initialize("testConfig.ini", CustomConfigParser())
        rv = self.app.post('/playlists', data=dict(remove=True, playlists="playlist_to_remove"), follow_redirects=True)
        mock_removePlaylist.assert_called_once_with("playlist_to_remove")
        assert rv.status_code == 200
        assert b'<title>Media Server</title>' in rv.data

    @mock.patch.object(YoutubeConfig, 'removePlaylist', return_value=True)
    @mock.patch.object(YoutubeConfig, 'getPlaylistsName', return_value=["playlist1", "playlist2"])
    def test_remove_playlist2(self, mock_getPlaylistsName, mock_removePlaylist):
        self.ytConfig.initialize("testConfig.ini")
        rv = self.app.post('/playlists', data=dict(remove=True, playlists="playlist_to_remove"), follow_redirects=True)
        mock_removePlaylist.assert_called_once_with("playlist_to_remove")
        mock_getPlaylistsName.assert_called_once()
        assert rv.status_code == 200
        #assert b'Sucesssful removed playlist' in rv.data
        assert b'<title>Media Server</title>' in rv.data

    @mock.patch.object(YoutubeConfig, 'removePlaylist', return_value=False)
    @mock.patch.object(YoutubeConfig, 'getPlaylistsName', return_value=["playlist1", "playlist2"])
    def test_remove_playlist_failed(self, mock_getPlaylistsName, mock_removePlaylist):
        self.ytConfig.initialize("testConfig.ini")
        rv = self.app.post('/playlists', data=dict(remove=True, playlists="playlist_to_remove"), follow_redirects=True)
        mock_removePlaylist.assert_called_once_with("playlist_to_remove")
        assert rv.status_code == 200
        assert b'<title>Media Server</title>' in rv.data
        assert b'Failed to remove Youtube playlist:' in rv.data

    @mock.patch('subprocess.check_output')
    @mock.patch('youtubedl.loadConfig')
    def test_load_alarm_config(self, mock_loadConfig , mock_proc_check_output):
        alarmsPlaylists = ["Favorites", "Alarm"]
        alarmPlaylistString = '\n'.join(str(e) for e in alarmsPlaylists) + '\n'
        alarmTime="06:30"
        minVolume=16
        maxVolume=55
        defaultVolume=11
        growingVolume=9
        growingSpeed=45

        mock_proc_check_output.configure_mock(side_effect=[alarmPlaylistString, "active"])

        mock_loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Mon,Tue,Wed,Thu,Fri,Sat,Sun "+alarmTime,"",
                    "[Install]","WantedBy=multi-user.target",""],
                    ["#/bin/bash",
                    AlarmConfigLinux.MIN_VOLUME+"="+str(minVolume),
                    AlarmConfigLinux.MAX_VOLUME+"="+str(maxVolume),
                    AlarmConfigLinux.DEFAULT_VOLUME+"="+str(defaultVolume),
                    AlarmConfigLinux.GROWING_VOLUME+"="+str(growingVolume),
                    AlarmConfigLinux.GROWING_SPEED+"="+str(growingSpeed),
                    AlarmConfigLinux.PLAYLIST+"=\"\"",
                    AlarmConfigLinux.THE_NEWEST_SONG+"=true",
                    "",""]
                    ])

        alarmConfig = youtubedl.loadAlarmConfig()

        self.assertEqual(mock_proc_check_output.call_count, 2)
        self.assertEqual(mock_loadConfig.call_count, 2)

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
        self.assertEqual(alarmConfig[AlarmConfigFlask.MIN_VOLUME], str(minVolume))
        self.assertEqual(alarmConfig[AlarmConfigFlask.MAX_VOLUME], str(maxVolume))
        self.assertEqual(alarmConfig[AlarmConfigFlask.DEFAULT_VOLUME], str(defaultVolume))
        self.assertEqual(alarmConfig[AlarmConfigFlask.GROWING_VOLUME], growingVolume)
        self.assertEqual(alarmConfig[AlarmConfigFlask.GROWING_SPEED], growingSpeed)

    @mock.patch('subprocess.check_output')
    @mock.patch('youtubedl.loadConfig')
    def test_load_alarm_config_2(self, mock_loadConfig , mock_proc_check_output):
        alarmsPlaylists = ["Favorites", "Alarm"]
        alarmPlaylistString = '\n'.join(str(e) for e in alarmsPlaylists) + '\n'
        alarmTime="06:30"
        minVolume=16
        maxVolume=55
        defaultVolume=11
        growingVolume=9
        growingSpeed=45

        mock_proc_check_output.configure_mock(side_effect=[alarmPlaylistString, "inactive"])

        mock_loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Mon,Tue,Wed,Thu,Fri,Sat,Sun "+alarmTime,"",
                    "[Install]","WantedBy=multi-user.target",""],
                    ["#/bin/bash",
                    AlarmConfigLinux.MIN_VOLUME+"="+str(minVolume),
                    AlarmConfigLinux.MAX_VOLUME+"="+str(maxVolume),
                    AlarmConfigLinux.DEFAULT_VOLUME+"="+str(defaultVolume),
                    AlarmConfigLinux.GROWING_VOLUME+"="+str(growingVolume),
                    AlarmConfigLinux.GROWING_SPEED+"="+str(growingSpeed),
                    AlarmConfigLinux.PLAYLIST+"=\""+alarmsPlaylists[0]+"\"",
                    AlarmConfigLinux.THE_NEWEST_SONG+"=false",
                    "",""]
                    ])

        alarmConfig = youtubedl.loadAlarmConfig()

        self.assertEqual(mock_proc_check_output.call_count, 2)
        self.assertEqual(mock_loadConfig.call_count, 2)

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
        self.assertEqual(alarmConfig[AlarmConfigFlask.MIN_VOLUME], str(minVolume))
        self.assertEqual(alarmConfig[AlarmConfigFlask.MAX_VOLUME], str(maxVolume))
        self.assertEqual(alarmConfig[AlarmConfigFlask.DEFAULT_VOLUME], str(defaultVolume))
        self.assertEqual(alarmConfig[AlarmConfigFlask.GROWING_VOLUME], growingVolume)
        self.assertEqual(alarmConfig[AlarmConfigFlask.GROWING_SPEED], growingSpeed)

    @mock.patch('youtubedl.loadConfig')
    @mock.patch('youtubedl.saveConfig')
    def test_update_alarm_config(self, mock_saveConfig, mock_loadConfig):
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
        mock_loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Sun 09:00","",
                    "[Install]","WantedBy=multi-user.target",""],
                    ["#/bin/bash",
                    AlarmConfigLinux.MIN_VOLUME+"=4",
                    AlarmConfigLinux.MAX_VOLUME+"=70",
                    AlarmConfigLinux.DEFAULT_VOLUME+"=10",
                    AlarmConfigLinux.GROWING_VOLUME+"=40",
                    AlarmConfigLinux.GROWING_SPEED+"=50",
                    AlarmConfigLinux.PLAYLIST+"=\"playlist_alarm\"",
                    AlarmConfigLinux.THE_NEWEST_SONG+"=true",
                    "",""]
                    ])

        youtubedl.updateAlarmConfig(alarmDays,time,minVolume,maxVolume,defaultVolume,growingVolume,growingSpeed,alarmPlaylist,alarmMode)
        mock_saveConfig.assert_has_calls([mock.call(youtubedl.ALARM_TIMER,
                                                    ['[Unit]', 'Description=Alarm', '',
                                                     '[Timer]', 'OnCalendar=' + alarmDays +' '+ time + ' \n', '',
                                                     '[Install]', 'WantedBy=multi-user.target', '']),
                                          mock.call(youtubedl.ALARM_SCRIPT,
                                                    ['#/bin/bash',
                                                    AlarmConfigLinux.MIN_VOLUME+'='+str(minVolume)+'\n',
                                                    AlarmConfigLinux.MAX_VOLUME+'='+str(maxVolume)+'\n',
                                                    AlarmConfigLinux.DEFAULT_VOLUME+'='+str(defaultVolume)+'\n',
                                                    AlarmConfigLinux.GROWING_VOLUME+'='+str(growingVolume)+'\n',
                                                    AlarmConfigLinux.GROWING_SPEED+'='+str(growingSpeed)+'\n',
                                                    AlarmConfigLinux.PLAYLIST+'="'+alarmPlaylist+'"\n',
                                                    AlarmConfigLinux.THE_NEWEST_SONG+'=false\n', '', ''])])

    @mock.patch('youtubedl.loadConfig')
    @mock.patch('youtubedl.saveConfig')
    def test_update_alarm_config_2(self, mock_saveConfig, mock_loadConfig):
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
        mock_loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Sun 09:00","",
                    "[Install]","WantedBy=multi-user.target",""],
                    ["#/bin/bash",
                    AlarmConfigLinux.MIN_VOLUME+"=4",
                    AlarmConfigLinux.MAX_VOLUME+"=70",
                    AlarmConfigLinux.DEFAULT_VOLUME+"=10",
                    AlarmConfigLinux.GROWING_VOLUME+"=40",
                    AlarmConfigLinux.GROWING_SPEED+"=50",
                    AlarmConfigLinux.PLAYLIST+"=\"playlist_alarm\"",
                    AlarmConfigLinux.THE_NEWEST_SONG+"=false",
                    "",""]
                    ])

        youtubedl.updateAlarmConfig(alarmDays,time,minVolume,maxVolume,defaultVolume,growingVolume,growingSpeed,alarmPlaylist,alarmMode)
        mock_saveConfig.assert_has_calls([mock.call(youtubedl.ALARM_TIMER,
                                                    ['[Unit]', 'Description=Alarm', '',
                                                     '[Timer]', 'OnCalendar=' + alarmDays +' '+ time + ' \n', '',
                                                     '[Install]', 'WantedBy=multi-user.target', '']),
                                          mock.call(youtubedl.ALARM_SCRIPT,
                                                    ['#/bin/bash',
                                                    AlarmConfigLinux.MIN_VOLUME+'='+str(minVolume)+'\n',
                                                    AlarmConfigLinux.MAX_VOLUME+'='+str(maxVolume)+'\n',
                                                    AlarmConfigLinux.DEFAULT_VOLUME+'='+str(defaultVolume)+'\n',
                                                    AlarmConfigLinux.GROWING_VOLUME+'='+str(growingVolume)+'\n',
                                                    AlarmConfigLinux.GROWING_SPEED+'='+str(growingSpeed)+'\n',
                                                    AlarmConfigLinux.PLAYLIST+'="'+alarmPlaylist+'"\n',
                                                    AlarmConfigLinux.THE_NEWEST_SONG+'=true\n', '', ''])])

    @mock.patch('subprocess.check_output', side_effect=["Favorites\nAlarm\n", "active"])
    @mock.patch('youtubedl.loadConfig')
    @mock.patch('youtubedl.saveConfig')
    @mock.patch('subprocess.run')
    def test_save_alarm_html(self, mock_subprocess_run, mock_saveConfig, mock_loadConfig, mock_subprocess_checkoutput):
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

        mock_loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","","[Timer]","OnCalendar=Mon,Tue,Wed,Thu,Fri,Sat,Sun 07:50",
                    "","[Install]","WantedBy=multi-user.target",""], #configuration before update
                    ["#/bin/bash",
                    AlarmConfigLinux.MIN_VOLUME+"=16",
                    AlarmConfigLinux.MAX_VOLUME+"=55",
                    AlarmConfigLinux.DEFAULT_VOLUME+"=11",
                    AlarmConfigLinux.GROWING_VOLUME+"=9",
                    AlarmConfigLinux.GROWING_SPEED+"=45",
                    AlarmConfigLinux.PLAYLIST+"=\"\"",
                    AlarmConfigLinux.THE_NEWEST_SONG+"=false",
                    "", ""], #configuration before update
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar="+alarmDays+" "+time,"",
                    "[Install]","WantedBy=multi-user.target",""],
                    ["#/bin/bash",
                    AlarmConfigLinux.MIN_VOLUME+"="+str(minVolume),
                    AlarmConfigLinux.MAX_VOLUME+"="+str(maxVolume),
                    AlarmConfigLinux.DEFAULT_VOLUME+"="+str(defaultVolume),
                    AlarmConfigLinux.GROWING_VOLUME+"="+str(growingVolume),
                    AlarmConfigLinux.GROWING_SPEED+"="+str(growingSpeed),
                    AlarmConfigLinux.PLAYLIST+"=\"\"",
                    AlarmConfigLinux.THE_NEWEST_SONG+"=true",
                    "", ""]
                    ])

        rv = self.app.post('/save_alarm',
                            data=dict(alarm_time=time, alarm_mode=alarmMode, playlists=alarmPlaylist,
                                    min_volume=str(minVolume), max_volume=str(maxVolume), default_volume=str(defaultVolume),
                                    growing_volume=str(growingVolume), growing_speed=str(growingSpeed),
                                    alarm_active="true", monday=['monday'], tueday=['tueday'], wedday=['wedday']),
                            follow_redirects=True)

        mock_saveConfig.assert_has_calls([mock.call(youtubedl.ALARM_TIMER,
                                                    ['[Unit]', 'Description=Alarm', '',
                                                     '[Timer]', 'OnCalendar=' + alarmDays +' '+ time + ' \n', '',
                                                     '[Install]', 'WantedBy=multi-user.target', '']),
                                          mock.call(youtubedl.ALARM_SCRIPT,
                                                    ['#/bin/bash',
                                                    AlarmConfigLinux.MIN_VOLUME+'='+str(minVolume)+'\n',
                                                    AlarmConfigLinux.MAX_VOLUME+'='+str(maxVolume)+'\n',
                                                    AlarmConfigLinux.DEFAULT_VOLUME+'='+str(defaultVolume)+'\n',
                                                    AlarmConfigLinux.GROWING_VOLUME+'='+str(growingVolume)+'\n',
                                                    AlarmConfigLinux.GROWING_SPEED+'='+str(growingSpeed)+'\n',
                                                    AlarmConfigLinux.PLAYLIST+'="'+alarmPlaylist+'"\n',
                                                    AlarmConfigLinux.THE_NEWEST_SONG+'=false\n', '', ''])])

        mock_subprocess_run.assert_has_calls([mock.call(SystemdCommand.STOP_ALARM_TIMER, shell=True),
                                              mock.call(SystemdCommand.DAEMON_RELOAD, shell=True),
                                              mock.call(SystemdCommand.START_ALARM_TIMER, shell=True)])

        mock_subprocess_checkoutput.assert_has_calls([mock.call('mpc lsplaylists | grep -v m3u', shell=True, text=True),
                                                      mock.call(SystemdCommand.IS_ACTIVE_ALARM_TIMER, shell=True, text=True)])


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
        assert str('value="'+str(minVolume)+'" name="'+AlarmConfigFlask.MIN_VOLUME+'">').encode()         in rv.data
        assert str('value="'+str(maxVolume)+'" name="'+AlarmConfigFlask.MAX_VOLUME+'">').encode()         in rv.data
        assert str('value="'+str(defaultVolume)+'" name="'+AlarmConfigFlask.DEFAULT_VOLUME+'">').encode() in rv.data
        assert b'<title>Media Server</title>' in rv.data

    @mock.patch('subprocess.check_output', side_effect=["Favorites\nAlarm\n", "active"])
    @mock.patch('youtubedl.loadConfig')
    @mock.patch('youtubedl.saveConfig')
    @mock.patch('subprocess.run')
    def test_save_alarm_html_2(self, mock_subprocess_run, mock_saveConfig, mock_loadConfig, mock_subprocess_checkoutput):
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

        mock_loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","","[Timer]","OnCalendar=Mon,Sat 07:50",
                    "","[Install]","WantedBy=multi-user.target",""], #configuration before update
                    ["#/bin/bash",
                    AlarmConfigLinux.MIN_VOLUME+"=16",
                    AlarmConfigLinux.MAX_VOLUME+"=55",
                    AlarmConfigLinux.DEFAULT_VOLUME+"=11",
                    AlarmConfigLinux.GROWING_VOLUME+"=9",
                    AlarmConfigLinux.GROWING_SPEED+"=45",
                    AlarmConfigLinux.PLAYLIST+"=\"\"",
                    AlarmConfigLinux.THE_NEWEST_SONG+"=false",
                    "", ""], #configuration before update
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar="+alarmDays+" "+time,"",
                    "[Install]","WantedBy=multi-user.target",""],
                    ["#/bin/bash",
                    AlarmConfigLinux.MIN_VOLUME+"="+str(minVolume),
                    AlarmConfigLinux.MAX_VOLUME+"="+str(maxVolume),
                    AlarmConfigLinux.DEFAULT_VOLUME+"="+str(defaultVolume),
                    AlarmConfigLinux.GROWING_VOLUME+"="+str(growingVolume),
                    AlarmConfigLinux.GROWING_SPEED+"="+str(growingSpeed),
                    AlarmConfigLinux.PLAYLIST+"=\"\"",
                    AlarmConfigLinux.THE_NEWEST_SONG+"=true",
                    "", ""]
                    ])

        rv = self.app.post('/save_alarm',
                            data=dict(alarm_time=time, alarm_mode=alarmMode, playlists=alarmPlaylist,
                                    min_volume=str(minVolume), max_volume=str(maxVolume), default_volume=str(defaultVolume),
                                    growing_volume=str(growingVolume), growing_speed=str(growingSpeed),
                                    alarm_active="true", monday=['monday'], tueday=['tueday'], wedday=['wedday'], thuday=['thuday'], friday=['friday'], satday=['satday'], sunday=['sunday'] ),
                            follow_redirects=True)

        mock_saveConfig.assert_has_calls([mock.call(youtubedl.ALARM_TIMER,
                                                    ['[Unit]', 'Description=Alarm', '',
                                                     '[Timer]', 'OnCalendar=' + alarmDays +' '+ time + ' \n', '',
                                                     '[Install]', 'WantedBy=multi-user.target', '']),
                                          mock.call(youtubedl.ALARM_SCRIPT,
                                                    ['#/bin/bash',
                                                    AlarmConfigLinux.MIN_VOLUME+'='+str(minVolume)+'\n',
                                                    AlarmConfigLinux.MAX_VOLUME+'='+str(maxVolume)+'\n',
                                                    AlarmConfigLinux.DEFAULT_VOLUME+'='+str(defaultVolume)+'\n',
                                                    AlarmConfigLinux.GROWING_VOLUME+'='+str(growingVolume)+'\n',
                                                    AlarmConfigLinux.GROWING_SPEED+'='+str(growingSpeed)+'\n',
                                                    AlarmConfigLinux.PLAYLIST+'="'+alarmPlaylist+'"\n',
                                                    AlarmConfigLinux.THE_NEWEST_SONG+'=true\n', '', ''])])

        mock_subprocess_run.assert_has_calls([mock.call(SystemdCommand.STOP_ALARM_TIMER, shell=True),
                                              mock.call(SystemdCommand.DAEMON_RELOAD, shell=True),
                                              mock.call(SystemdCommand.START_ALARM_TIMER, shell=True)])

        mock_subprocess_checkoutput.assert_has_calls([mock.call('mpc lsplaylists | grep -v m3u', shell=True, text=True),
                                                      mock.call(SystemdCommand.IS_ACTIVE_ALARM_TIMER, shell=True, text=True)])


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

    @mock.patch('subprocess.check_output')
    @mock.patch('youtubedl.loadConfig')
    def test_alarm_html(self, mock_loadConfig , mock_proc_check_output):
        alarm_time="06:50"
        minVolume=16
        maxVolume=55
        defaultVolume=11
        growingVolume=7
        growingSpeed=45

        mock_proc_check_output.configure_mock(side_effect=["Favorites\nAlarm\n", "active"])
        mock_loadConfig.configure_mock(side_effect=[
                    ["[Unit]","Description=Alarm","",
                    "[Timer]","OnCalendar=Mon,Tue,Wed,Thu,Fri,Sat,Sun "+alarm_time,"",
                    "[Install]","WantedBy=multi-user.target",""],
                    ["#/bin/bash",
                    AlarmConfigLinux.MIN_VOLUME+"="+str(minVolume),
                    AlarmConfigLinux.MAX_VOLUME+"="+str(maxVolume),
                    AlarmConfigLinux.DEFAULT_VOLUME+"="+str(defaultVolume),
                    AlarmConfigLinux.GROWING_VOLUME+"="+str(growingVolume),
                    AlarmConfigLinux.GROWING_SPEED+"="+str(growingSpeed),
                    AlarmConfigLinux.PLAYLIST+"=\"\"",
                    AlarmConfigLinux.THE_NEWEST_SONG+"=true",
                    ""]
                    ])

        rv = self.app.get('/alarm.html')
        self.assertEqual(mock_proc_check_output.call_count, 2)
        self.assertEqual(mock_loadConfig.call_count, 2)

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
        assert b'<title>Media Server</title>' in rv.data


if __name__ == '__main__':
    unittest.main()