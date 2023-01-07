
class Mail():
    def initialize(self):
        result = False
        try:
            from simplegmail import Gmail
            self.gmail = Gmail()
            result = True
        except ModuleNotFoundError:
            result = False
        return result

    def sendMail(self, address, subject, text, attachments=[]):

        params = {
              "to": address,
              "sender": "iprecorder.server@gmail.com",
              "subject": subject,
              "msg_html": text,
              "signature": True  # use my account signature
        }
        message = self.gmail.send_message(**params)  # equivalent to send_message(to="you@youremail.com", sender=...)

if __name__ == "__main__":
    mail = Mail()
    if mail.initialize():
        mail.sendMail("bartosz.brzozowski23@gmail.com", "IPRecorder", "everything perfectly work")
