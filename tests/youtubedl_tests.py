import youtubedl
import unittest
import unittest.mock as mock
from configparser import ConfigParser
from Common.mailManager import Mail
from Common.YouTubeManager import YoutubeDl


class FlaskClientTestCase(unittest.TestCase):

    def setUp(self):
        youtubedl.app.config['TESTING'] = True
        self.app = youtubedl.app.test_client()
        self.mailManager = youtubedl.mailManager
        self.ytManager = youtubedl.youtubeManager

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

    @mock.patch('configparser.ConfigParser')
    @mock.patch('youtubedl.saveConfigs')
    def test_update_playlists(self, mock_saveConfigs, mock_configParser):
        rv = self.app.post('/playlists', data=dict(add=True, playlist_name="test5",link="link_test"), follow_redirects=True)
        mock_saveConfigs.assert_called_once()
        assert rv.status_code == 200
        assert b'<title>Media Server</title>' in rv.data

    @mock.patch('configparser.ConfigParser.__getitem__')
    @mock.patch('configparser.ConfigParser.read')
    @mock.patch('youtubedl.saveConfigs')
    def test_add_playlist(self, mock_saveConfigs, mock_configParserRead, mock_getItem):
        rv = self.app.post('/playlists', data=dict(add=True, playlist_name="yt_playlist",link="https://youtube.com/link"), follow_redirects=True)
        self.assertEqual(mock_saveConfigs.call_count, 1)
        self.assertEqual(mock_configParserRead.call_count, 2)

        mock_getItem.assert_has_calls([mock.call('yt_playlist'), mock.call().__setitem__('name', 'yt_playlist'),
                                       mock.call('yt_playlist'), mock.call().__setitem__('link', 'https://youtube.com/link')])
        assert rv.status_code == 200
        assert b'<title>Media Server</title>' in rv.data

    @mock.patch('configparser.ConfigParser')
    @mock.patch('youtubedl.saveConfigs')
    def test_remove_playlist(self, mock_saveConfigs, mock_configParser):
        class CustomConfigParser(ConfigParser):
            def read(self, filename):
                self.read_string("[playlist_to_remove]\nname = playlist_to_remove\nlink = http://youtube.com/test\n[playlist]\nname = playlist\nlink = http://youtube.com/test\n")
        mock_configParser.configure_mock(side_effect=CustomConfigParser)
        rv = self.app.post('/playlists', data=dict(remove=True, playlists="playlist_to_remove"), follow_redirects=True)
        self.assertEqual(mock_configParser.call_count, 2)
        args = mock_saveConfigs.call_args
        configs = args[0][0]
        self.assertEqual(len(configs.sections()), 1)
        self.assertEqual(configs.sections()[0],"playlist")
        assert rv.status_code == 200
        assert b'<title>Media Server</title>' in rv.data

    @mock.patch('subprocess.check_output')
    @mock.patch('youtubedl.loadConfig')
    def test_load_alarm_config(self, mock_loadConfig , mock_proc_check_output):
        alarmsPlaylists = ["Favorites", "Alarm"]
        alarmPlaylistString = '\n'.join(str(e) for e in alarmsPlaylists) + '\n'
        alarmTime="06:30"
        checked="checked"
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
                    "minVolume="+str(minVolume),
                    "maxVolume="+str(maxVolume),
                    "defaultVolume="+str(defaultVolume),
                    "growingVolume="+str(growingVolume),
                    "growingSpeed="+str(growingSpeed),
                    "playlist=\"\"",
                    "theNewestSongs=true",
                    "",""]
                    ])

        alarmConfig = youtubedl.loadAlarmConfig()

        self.assertEqual(mock_proc_check_output.call_count, 2)
        self.assertEqual(mock_loadConfig.call_count, 2)

        self.assertEqual(alarmConfig["alarm_time"], alarmTime)
        self.assertEqual(alarmConfig["theNewestSongChecked"], checked)
        self.assertEqual(alarmConfig["playlistChecked"], "")
        self.assertListEqual(alarmConfig["alarm_playlists"], alarmsPlaylists)
        self.assertEqual(alarmConfig["alarm_playlist_name"], "")
        self.assertEqual(alarmConfig["alarm_active"], checked)
        self.assertEqual(alarmConfig["monday_checked"], checked)
        self.assertEqual(alarmConfig["tuesday_checked"], checked)
        self.assertEqual(alarmConfig["wednesday_checked"], checked)
        self.assertEqual(alarmConfig["thursday_checked"], checked)
        self.assertEqual(alarmConfig["friday_checked"], checked)
        self.assertEqual(alarmConfig["saturday_checked"], checked)
        self.assertEqual(alarmConfig["sunday_checked"], checked)
        self.assertEqual(alarmConfig["min_volume"], str(minVolume))
        self.assertEqual(alarmConfig["max_volume"], str(maxVolume))
        self.assertEqual(alarmConfig["default_volume"], str(defaultVolume))
        self.assertEqual(alarmConfig["growing_volume"], growingVolume)
        self.assertEqual(alarmConfig["growing_speed"], growingSpeed)


    @mock.patch('subprocess.check_output', side_effect=["Favorites\nAlarm\n", "active"])
    @mock.patch('youtubedl.loadConfig',
                 side_effect=[
                    ["[Unit]","Description=Alarm","","[Timer]","OnCalendar=Mon,Tue,Wed,Thu,Fri,Sat,Sun 06:50","","[Install]","WantedBy=multi-user.target",""],
                    ["#/bin/bash","minVolume=16","maxVolume=55","defaultVolume=11", "growingVolume=9", "growingSpeed=45","playlist=\"\"","theNewestSongs=true","", ""]
                    ])
    def test_alarm_web(self, mock_loadConfig , mock_proc_check_output):
        rv = self.app.get('/alarm.html')
        self.assertEqual(mock_proc_check_output.call_count, 2)
        self.assertEqual(mock_loadConfig.call_count, 2)

        assert rv.status_code == 200
        assert b'name="alarm_time" value="06:50"'               in rv.data
        assert b'name="alarm_mode" value="newest_song" checked>'       in rv.data
        assert b'name="alarm_mode" value="playlist" >'  in rv.data
        assert b'<option value="Alarm">Alarm</option>' in rv.data
        assert b'<option value="Favorites">Favorites</option>'  in rv.data
        assert b'name="alarm_active" value="checked" checked>'  in rv.data
        assert b'value="monday" checked>'                       in rv.data
        assert b'value="tueday" checked>'                       in rv.data
        assert b'value="wedday" checked>'                       in rv.data
        assert b'value="thuday" checked>'                       in rv.data
        assert b'value="friday" checked>'                       in rv.data
        assert b'value="satday" checked>'                       in rv.data
        assert b'value="sunday" checked>'                       in rv.data
        assert b'value="16" name="min_volume">'                 in rv.data
        assert b'value="55" name="max_volume">'                 in rv.data
        assert b'value="11" name="default_volume">'             in rv.data
        assert b'<title>Media Server</title>' in rv.data


if __name__ == '__main__':
    unittest.main()