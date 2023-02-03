
class Mail():
    def initialize(self): # pragma: no cover
        self.senderMail = "iprecorder.server@gmail.com"
        result = False
        self.isInitialize = False
        try:
            from simplegmail import Gmail
            self.gmail = Gmail()
            self.isInitialize = True
            result = True
        except ModuleNotFoundError:
            result = False
        return result

    def sendMail(self, address, subject, text, attachments=[]):
        if self.isInitialize:
            params = {
              "to": address,
              "sender": self.senderMail,
              "subject": subject,
              "msg_html": text,
              "signature": True  # use my account signature
            }
            message = self.gmail.send_message(**params)  # equivalent to send_message(to="you@youremail.com", sender=...)
            return True
        else:
            return False

if __name__ == "__main__":
    mail = Mail()
    if mail.initialize():
        mail.sendMail("bartosz.brzozowski23@gmail.com", "IPRecorder", "everything perfectly work")
