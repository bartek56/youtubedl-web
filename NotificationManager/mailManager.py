from simplegmail import Gmail

class Mail():    
    def initialize(self):
        self.gmail = Gmail()

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
    mail.initialize()
    mail.sendMail("bartosz.brzozowski23@gmail.com", "IPRecorder", "everything perfectly work")
