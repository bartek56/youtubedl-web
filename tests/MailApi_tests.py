from typing import List
import unittest
import unittest.mock as mock
from youtubedlWeb.Common.MailManager import Mail
from youtubedlWeb import create_app
from youtubedlWeb.config import ConfigTesting

class FlaskClientMailTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FlaskClientMailTestCase, self).__init__(*args, **kwargs)
        self.checked="checked"
        self.unchecked="unchecked"
        self.empty=""

    def setUp(self):
        self.mainApp = create_app(config=ConfigTesting)
        self.app = self.mainApp.test_client()
        self.mailManager = self.mainApp.mailManager

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

if __name__ == "__main__":
    unittest.main()