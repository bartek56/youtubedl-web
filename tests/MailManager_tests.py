import unittest
from Common.MailManager import Mail
from unittest import mock

class MailManagerTest(Mail):
        def __init__(self, senderMail, mock1):
            self.gmail = mock.MagicMock()
            self.gmail.send_message = mock1
            self.senderMail = senderMail
            self.isInitialize = False

        def initialize(self):
            self.isInitialize = True

class MailManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.senderMail = "sender@gmail.com"
        self.destinationMail = "destination@gmail.com"
        self.subjectTest = "test mail"
        self.textTest = "Hello World"

    def test_sendMailWithinitialize(self):
        gmailMock = mock.Mock()
        mailManager = MailManagerTest(self.senderMail, gmailMock)
        mailManager.initialize()
        self.assertTrue(mailManager.sendMail(self.destinationMail, self.subjectTest, self.textTest))
        gmailMock.assert_has_calls([mock.call(to=self.destinationMail, sender=self.senderMail, subject=self.subjectTest, msg_html=self.textTest, signature=True)])

    def test_sendMainWithoutInitialize(self):
        gmailMock = mock.MagicMock()
        mailManager = MailManagerTest(gmailMock, self.senderMail)
        self.assertFalse(mailManager.sendMail("fds", "fdsf", "sdf"))
        gmailMock.assert_not_called()

if __name__ == "__main__":
    unittest.main()
