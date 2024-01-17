from Common.AlarmEnums import AlarmConfigFlask, AlarmConfigLinux, SystemdCommand
from WebAPI.alarm import alarmManager
import WebAPI.alarm as alarm
from youtubedl import socketio
import youtubedl
import unittest
import unittest.mock as mock
from unittest.mock import MagicMock
from configparser import ConfigParser
from Common.mailManager import Mail
from Common.YouTubeManager import YoutubeManager, YoutubeConfig, ResultOfDownload, PlaylistConfig
import Common.YouTubeManager as YTManager
import Common.SocketMessages as SocketMessages

class FlaskSocketIO(unittest.TestCase):
    randomString = "ABCDEFGHI"
    randomString1 = "AAAAAAAA"
    randomString2 = "BBBBBBBB"
    randomString3 = "CCCCCCCC"
    empty = " "
    title = "test_title"
    artist = "test_artist"
    album = "test_album"
    extMp3 = "mp3"
    extMp4 = "mp4"
    path = "/tmp/" + title+".mp3"
    downloadDir = "/home/music"
    url = "https://www.youtube.com/watch?v=1Pl-FT0VCNs"
    playlistUrl = "https://www.youtube.com/playlist?list=PL6uhlddQJkfh4YsbxgPE70a6KeFOCDgG_"

    playlistsPath = "/home/music/youtube playlists"
    playlistName = "playlistNameTest"

    playlist1Name = "playlist1"
    playlist2Name = "playlist2"
    playlist3Name = "playlist3"
    playlist1Link = "https://www.youtube.com/playlist?list=PL111111111"
    playlist2Link = "https://www.youtube.com/playlist?list=PL222222222"
    playlist3Link = "https://www.youtube.com/playlist?list=PL333333333"
    playlistsConfiguration = [PlaylistConfig(playlist1Name,playlist1Link),
                              PlaylistConfig(playlist2Name,playlist2Link),
                              PlaylistConfig(playlist3Name,playlist3Link)]

    songTitle1FromPlaylist = "song1"
    songTitle2FromPlaylist = "song2"
    songTitle3FromPlaylist = "song3"
    songArtist1FromPlaylist = "artist1"
    songArtist2FromPlaylist = "artist2"
    songArtist3FromPlaylist = "artist3"
    songAlbum1FromPlaylist = "album1"
    songAlbum2FromPlaylist = "album2"
    songAlbum3FromPlaylist = "album3"


    url1FromPlaylist = "https:/www.youtube.com/watch?v=11111"
    url2FromPlaylist = "https:/www.youtube.com/watch?v=22222"
    url3FromPlaylist = "https:/www.youtube.com/watch?v=33333"

    index1FromPlaylist = "1"
    index2FromPlaylist = "2"
    index3FromPlaylist = "3"

    def __init__(self, *args, **kwargs):
        super(FlaskSocketIO, self).__init__(*args, **kwargs)

    def setUp(self):
        youtubedl.app.config['TESTING'] = True
        self.app = youtubedl.app
        self.socketio_test_client = socketio.test_client(self.app)
        self.mailManager = youtubedl.mailManager
        self.ytManager = youtubedl.youtubeManager
        self.ytConfig = youtubedl.youtubeConfig


    def getDataFromMessage(self, message):
        self.assertIn("data", message["args"][0])
        return message["args"][0]["data"]

#    @mock.patch.object(YoutubeManager, 'downloadPlaylistMp3')
#    @mock.patch.object(YoutubeConfig, 'getPlaylists')
#    @mock.patch.object(YoutubeConfig, 'getPath')
#    def test_downloadPlaylists(self, mock_getPath:MagicMock, mock_getPlaylists:MagicMock, mock_downloadPlaylistMp3:MagicMock):
#        mock_getPlaylists.configure_mock(return_value=self.playlistsConfiguration)
#        mock_downloadPlaylistMp3.configure_mock(side_effect=[ResultOfDownload(1),ResultOfDownload(2),ResultOfDownload(3)])
#        mock_getPath.configure_mock(return_value=self.playlistsPath)
#
#        self.socketio_test_client.emit('downloadPlaylists', '')
#
#        mock_getPath.assert_called_once()
#        mock_getPlaylists.assert_called_once()
#        mock_downloadPlaylistMp3.assert_has_calls([mock.call(self.playlistsPath, self.playlist1Name, self.playlist1Link),
#                                                   mock.call(self.playlistsPath, self.playlist2Name, self.playlist2Link),
#                                                   mock.call(self.playlistsPath, self.playlist3Name, self.playlist3Link)])
#        received = self.socketio_test_client.get_received()
#        self.assertEqual(len(received), 4)
#
#        for x in range(3):
#            self.assertEqual(received[x]["name"], SocketMessages.DownloadPlaylist_response().message)
#            numberOfDownloadedSongs = self.getDataFromMessage(received[x])
#            self.assertEqual(numberOfDownloadedSongs, x+1)
#
#        self.assertEqual(received[3]["name"], SocketMessages.DownloadPlaylists_finish().message)
#        numberOfDownloadedPlaylists = self.getDataFromMessage(received[3])
#        self.assertEqual(numberOfDownloadedPlaylists, 3)


    @mock.patch.object(YoutubeManager, 'download_mp3')
    @mock.patch.object(YoutubeManager, 'getMediaInfo')
    @mock.patch('WebAPI.webUtils.getRandomString')
    def test_downloadMp3(self, mock_getRandomString:MagicMock, mock_getMediaInfo:MagicMock, mock_downloadMp3:MagicMock):
        mock_getMediaInfo.configure_mock(return_value=ResultOfDownload(YTManager.MediaInfo(self.title,self.artist,self.album,self.url)))
        mock_downloadMp3.configure_mock(return_value=ResultOfDownload(YTManager.AudioData(self.path, self.title, self.artist, self.album)))
        mock_getRandomString.configure_mock(return_value=self.randomString)

        self.socketio_test_client.emit('downloadMedia', {"url":self.url, "type":self.extMp3})

        mock_downloadMp3.assert_called_once_with(self.url)
        mock_getMediaInfo.assert_called_once_with(self.url)
        mock_getRandomString.assert_called_once()


        received = self.socketio_test_client.get_received()
        self.assertEqual(len(received), 2)

        firstEmit = received[0]
        self.assertEqual(firstEmit["name"], SocketMessages.MediaInfo_response().message)
        mediaData = self.getDataFromMessage(firstEmit)
        self.assertEqual(mediaData["title"], self.title)
        self.assertEqual(mediaData["artist"], self.artist)


        secondEmit = received[1]
        self.assertEqual(secondEmit["name"], SocketMessages.DownloadMedia_finish().message)
        hashData = self.getDataFromMessage(received[1])
        self.assertEqual(hashData, self.randomString)


    @mock.patch.object(YoutubeManager, 'download_mp3')
    @mock.patch.object(YoutubeManager, 'getPlaylistInfo')
    @mock.patch('WebAPI.webUtils.getRandomString')
    @mock.patch('WebAPI.youtubeDownloader.compressToZip')
    def test_downloadMp3Playlist(self, mock_zip:MagicMock, mock_getRandomString:MagicMock, mock_getPlaylistInfo:MagicMock, mock_downloadMp3:MagicMock):
        mock_getPlaylistInfo.configure_mock(return_value = ResultOfDownload(
            YTManager.PlaylistInfo(self.playlistName,
                                   [YTManager.MediaFromPlaylist(self.index1FromPlaylist, self.url1FromPlaylist, self.songTitle1FromPlaylist),
                                    YTManager.MediaFromPlaylist(self.index2FromPlaylist, self.url2FromPlaylist, self.songTitle2FromPlaylist),
                                    YTManager.MediaFromPlaylist(self.index3FromPlaylist, self.url3FromPlaylist, self.songTitle3FromPlaylist)])))
        mock_downloadMp3.configure_mock(side_effect=[ResultOfDownload(YTManager.AudioData(self.downloadDir+'/'+self.songTitle1FromPlaylist+'.'+self.extMp3, self.songTitle1FromPlaylist, self.songArtist1FromPlaylist, self.songAlbum1FromPlaylist)),
                                                     ResultOfDownload(YTManager.AudioData(self.downloadDir+'/'+self.songTitle2FromPlaylist+'.'+self.extMp3, self.songTitle2FromPlaylist, self.songArtist2FromPlaylist, self.songAlbum2FromPlaylist)),
                                                     ResultOfDownload(YTManager.AudioData(self.downloadDir+'/'+self.songTitle3FromPlaylist+'.'+self.extMp3, self.songTitle3FromPlaylist, self.songArtist3FromPlaylist, self.songAlbum3FromPlaylist))])
        mock_getRandomString.configure_mock(side_effect=[self.randomString1, self.randomString2, self.randomString3, self.randomString])

        # --------------------------------------------------------------------------------------------
        self.socketio_test_client.emit('downloadMedia', {"url":self.playlistUrl, "type":self.extMp3})
        # --------------------------------------------------------------------------------------------

        mock_getPlaylistInfo.assert_called_once_with(self.playlistUrl)
        mock_downloadMp3.assert_has_calls([mock.call(self.url1FromPlaylist),
                                           mock.call(self.url2FromPlaylist),
                                           mock.call(self.url3FromPlaylist)])
        self.assertEqual(mock_getRandomString.call_count, 4)
        mock_zip.assert_called_once_with([self.downloadDir+'/'+self.songTitle1FromPlaylist+'.'+self.extMp3,
                                          self.downloadDir+'/'+self.songTitle2FromPlaylist+'.'+self.extMp3,
                                          self.downloadDir+'/'+self.songTitle3FromPlaylist+'.'+self.extMp3], self.playlistName)

        received = self.socketio_test_client.get_received()
        self.assertEqual(len(received), 5)

        # getPlaylistInfo_response
        playlistInfoMessage = received[0]
        self.assertEqual(playlistInfoMessage["name"], SocketMessages.PlaylistInfo_response().message)
        expectedData = [SocketMessages.MediaFromPlaylist(self.index1FromPlaylist, self.url1FromPlaylist, self.songTitle1FromPlaylist),
                        SocketMessages.MediaFromPlaylist(self.index2FromPlaylist, self.url2FromPlaylist, self.songTitle2FromPlaylist),
                        SocketMessages.MediaFromPlaylist(self.index3FromPlaylist, self.url3FromPlaylist, self.songTitle3FromPlaylist)]

        playlistInfo = self.getDataFromMessage(playlistInfoMessage)
        playlistName = playlistInfo[0]
        playlistData = playlistInfo[1]
        for x in range(3):
            dataOfPlaylistInfoMessage = playlistData[x]
            expected = expectedData[x]
            self.assertEqual(dataOfPlaylistInfoMessage["playlist_index"], expected.playlistIndex)
            self.assertEqual(dataOfPlaylistInfoMessage["title"], expected.title)
            self.assertEqual(dataOfPlaylistInfoMessage["url"], expected.url)

        # getPlaylistMediaInfo_response - three songs
        expectedData = [SocketMessages.PlaylistMediaInfo(self.index1FromPlaylist, self.songTitle1FromPlaylist+"."+self.extMp3, self.randomString1),
                        SocketMessages.PlaylistMediaInfo(self.index2FromPlaylist, self.songTitle2FromPlaylist+"."+self.extMp3, self.randomString2),
                        SocketMessages.PlaylistMediaInfo(self.index3FromPlaylist, self.songTitle3FromPlaylist+"."+self.extMp3, self.randomString3)]
        for x in range(3):
            playlistMediaInfoMessage = received[x+1]
            self.assertEqual(playlistMediaInfoMessage["name"], SocketMessages.PlaylistMediaInfo_response().message)
            expected = expectedData[x]
            dataOfPlaylistMediaInfoMessage = self.getDataFromMessage(playlistMediaInfoMessage)

            self.assertEqual(dataOfPlaylistMediaInfoMessage["playlist_index"], expected.playlistIndex)
            self.assertEqual(dataOfPlaylistMediaInfoMessage["filename"], expected.filename)
            self.assertEqual(dataOfPlaylistMediaInfoMessage["hash"], expected.hash)

        # DwonloadMedia_finish
        downloadMediaFinishMessage = received[4]
        self.assertEqual(downloadMediaFinishMessage["name"], SocketMessages.DownloadMedia_finish().message)
        dataOfDownloadMediaFinish = self.getDataFromMessage(downloadMediaFinishMessage)
        self.assertEqual(dataOfDownloadMediaFinish, self.randomString)


    @mock.patch.object(YoutubeManager, 'download_720p')
    @mock.patch.object(YoutubeManager, 'getMediaInfo')
    @mock.patch('WebAPI.webUtils.getRandomString')
    def test_download720p(self, mock_randomString:MagicMock, mock_getMediaInfo:MagicMock, mock_download720p:MagicMock):
        mock_download720p.configure_mock(return_value=ResultOfDownload(YTManager.VideoData(self.downloadDir+"/"+self.title+"."+self.extMp4, self.title)))
        mock_getMediaInfo.configure_mock(return_value=ResultOfDownload(YTManager.MediaInfo(self.title, self.artist, self.album, self.url)))
        mock_randomString.configure_mock(return_value=self.randomString)

        # -----------------------------------------------------------------------------------------------------------
        self.socketio_test_client.emit('downloadMedia', {"url":self.url, "type":"720p"})
        # -----------------------------------------------------------------------------------------------------------

        mock_download720p.assert_called_once_with(self.url)
        mock_getMediaInfo.assert_called_once_with(self.url)

        received = self.socketio_test_client.get_received()
        self.assertEqual(len(received), 2)

        # getMediaInfo_response
        self.assertEqual(received[0]["name"], SocketMessages.MediaInfo_response().message)
        mediaData = self.getDataFromMessage(received[0])
        self.assertEqual(mediaData["title"], self.title)
        self.assertEqual(mediaData["artist"], self.artist)

        # DownloadMedia_finish
        self.assertEqual(received[1]["name"], SocketMessages.DownloadMedia_finish().message)
        hashData = self.getDataFromMessage(received[1])
        self.assertEqual(hashData, self.randomString)

class FlaskClientMailTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FlaskClientMailTestCase, self).__init__(*args, **kwargs)
        self.checked="checked"
        self.unchecked="unchecked"
        self.empty=""

    def setUp(self):
        youtubedl.app.config['TESTING'] = True
        self.app = youtubedl.app.test_client()
        self.mailManager = youtubedl.mailManager

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

    @mock.patch.object(Mail, 'sendMail')
    def test_correct_mail(self, mock_sendMail):
        #rv = self.mail('test@wp.pl', 'mail text')
        #mock_sendMail.assert_called_with(self.mailManager, "bartosz.brzozowski23@gmail.com", "MediaServer", "You received message from test@wp.pl: mail text")
        rv = self.app.post('/mail', data=dict(
        sender="test@gmail.com",
        message="text"))
        self.assertEqual(rv.status_code, 200)
        assert b'Successfull send mail' in rv.data

    @mock.patch.object(Mail, 'sendMail', autospec=True)
    def test_wrong_mail(self, mock_Gmail):
        rv = self.mail('jkk', '')
        assert b'You have to fill in the fields' in rv.data

class FlaskClientConfigurePlaylists(unittest.TestCase):
    checked="checked"
    unchecked="unchecked"
    empty=""

    def __init__(self, *args, **kwargs):
        super(FlaskClientConfigurePlaylists, self).__init__(*args, **kwargs)

    def setUp(self):
        youtubedl.app.config['TESTING'] = True
        self.app = youtubedl.app.test_client()
        self.ytConfig = youtubedl.youtubeConfig

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

class FlaskClientAlarmTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FlaskClientAlarmTestCase, self).__init__(*args, **kwargs)
        self.checked="checked"
        self.unchecked="unchecked"
        self.empty=""

    def setUp(self):
        youtubedl.app.config['TESTING'] = True
        self.app = youtubedl.app.test_client()
        alarm.alarmManager.loadConfig = MagicMock()
        alarm.alarmManager.saveConfig = MagicMock()

    def tearDown(self):
        pass

    @mock.patch('subprocess.check_output')
    def test_load_alarm_config(self, mock_proc_check_output):
        alarmsPlaylists = ["Favorites", "Alarm"]
        alarmPlaylistString = '\n'.join(str(e) for e in alarmsPlaylists) + '\n'
        alarmTime="06:30"
        minVolume=16
        maxVolume=55
        defaultVolume=11
        growingVolume=9
        growingSpeed=45

        mock_proc_check_output.configure_mock(side_effect=[alarmPlaylistString, "active"])

        alarm.alarmManager.loadConfig.configure_mock(side_effect=[
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

        alarmConfig = alarmManager.loadAlarmConfig()

        self.assertEqual(mock_proc_check_output.call_count, 2)
        self.assertEqual(alarm.alarmManager.loadConfig.call_count, 2)

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
    def test_load_alarm_config_2(self, mock_proc_check_output):
        alarmsPlaylists = ["Favorites", "Alarm"]
        alarmPlaylistString = '\n'.join(str(e) for e in alarmsPlaylists) + '\n'
        alarmTime="06:30"
        minVolume=16
        maxVolume=55
        defaultVolume=11
        growingVolume=9
        growingSpeed=45

        mock_proc_check_output.configure_mock(side_effect=[alarmPlaylistString, "inactive"])

        alarm.alarmManager.loadConfig.configure_mock(side_effect=[
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

        alarmConfig = alarmManager.loadAlarmConfig()

        self.assertEqual(mock_proc_check_output.call_count, 2)
        self.assertEqual(alarm.alarmManager.loadConfig.call_count, 2)

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
        alarm.alarmManager.loadConfig.configure_mock(side_effect=[
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

        alarm.alarmManager.updateAlarmConfig(alarmDays,time,minVolume,maxVolume,defaultVolume,growingVolume,growingSpeed,alarmPlaylist,alarmMode)
        alarm.alarmManager.saveConfig.assert_has_calls([mock.call(youtubedl.ALARM_TIMER,
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
        alarm.alarmManager.loadConfig.configure_mock(side_effect=[
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

        alarm.alarmManager.updateAlarmConfig(alarmDays,time,minVolume,maxVolume,defaultVolume,growingVolume,growingSpeed,alarmPlaylist,alarmMode)
        alarm.alarmManager.saveConfig.assert_has_calls([mock.call(youtubedl.ALARM_TIMER,
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

        alarm.alarmManager.loadConfig.configure_mock(side_effect=[
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

        alarm.alarmManager.saveConfig.assert_has_calls([mock.call(youtubedl.ALARM_TIMER,
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

        alarm.alarmManager.loadConfig.configure_mock(side_effect=[
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

        alarm.alarmManager.saveConfig.assert_has_calls([mock.call(alarmManager. ALARM_TIMER,
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
    def test_alarm_html(self, mock_proc_check_output):
        alarm_time="06:50"
        minVolume=16
        maxVolume=55
        defaultVolume=11
        growingVolume=7
        growingSpeed=45

        mock_proc_check_output.configure_mock(side_effect=["Favorites\nAlarm\n", "active"])
        alarm.alarmManager.loadConfig.configure_mock(side_effect=[
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
        self.assertEqual(alarm.alarmManager.loadConfig.call_count, 2)

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