import youtubedl
import unittest
import unittest.mock as mock
from configparser import ConfigParser
from Common.mailManager import Mail
from Common.YouTubeManager import YoutubeDl

class CustomConfigParser(ConfigParser):
    def read(self, filename):
        self.read_string("[playlist_to_remove]\nname = playlist_to_remove\nlink = http://youtube.com/test\n[playlist]\nname = playlist\nlink = http://youtube.com/test\n")

#    def write(self, fp, space_around_delimiters=True):
#        return "działa"

    def write(self):
        return self.sections()


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

    def test_contact_page(self):
        rv = self.app.get('/contact.html')
        assert rv.status_code == 200
        assert b'<title>Media Server</title>' in rv.data

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

    def retTrue(self, input):
        return True

    @mock.patch.object(YoutubeDl, 'download_mp3', return_value={"title": "song","path":"/home/music/song.mp3"})
    @mock.patch.object(YoutubeDl, 'isFile', retTrue)
    def test_download_mp3(self, mock_mp3):
        ytLink = "https://youtu.be/q1MmYVcDyMs"
        rv = self.yt_dlp(ytLink, 'mp3')
        mock_mp3.assert_called_once_with(ytLink)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'<form action="/download_file"', rv.data)

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


    @mock.patch('configparser.ConfigParser', side_effect=CustomConfigParser)
    @mock.patch('youtubedl.saveConfigs')
    def test_remove_playlist(self, mock_saveConfigs, mock_configParser):
        rv = self.app.post('/playlists', data=dict(remove=True, playlists="playlist_to_remove"), follow_redirects=True)

        args = mock_saveConfigs.call_args
        configs = args[0][0]
        self.assertEqual(len(configs.sections()), 1)
        self.assertEqual(configs.sections()[0],"playlist")

        assert rv.status_code == 200
        assert b'<title>Media Server</title>' in rv.data

if __name__ == '__main__':
    unittest.main()