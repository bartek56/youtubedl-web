import youtubedl
import tempfile
import unittest
import os
import unittest.mock as mock
from NotificationManager.mailManager import Mail

class FlaskClientTestCase(unittest.TestCase):

    def setUp(self):        
        youtubedl.app.config['TESTING'] = True
        self.app = youtubedl.app.test_client()
        self.mailManager = youtubedl.mailManager

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

    def mail(self, senderMail, textMail):
        return self.app.post('/mail', data=dict(
        sender=senderMail,
        message=textMail
    ), follow_redirects=True)
    
    @mock.patch.object(Mail, 'sendMail', autospec=True)
    def test_correct_mail(self, mock_sendMail):
        rv = self.mail('test@wp.pl', 'mail text')        
        mock_sendMail.assert_called_with(self.mailManager, "bartosz.brzozowski23@gmail.com", "MediaServer", "You received message from test@wp.pl: mail text")
        assert b'Successfull send mail' in rv.data
    
    @mock.patch('NotificationManager.mailManager.Gmail')
    def test_wrong_mail(self, mock_Gmail):
        rv = self.mail('jkk', '')
        assert b'You have to fill in the fields' in rv.data    

if __name__ == '__main__':
    unittest.main()