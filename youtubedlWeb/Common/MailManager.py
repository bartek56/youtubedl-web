
class Mail():
    def initialize(self): # pragma: no cover
        """ Initialize mail sender.

        This function sets up the mail sender. It imports the Gmail module from simplegmail and creates a Gmail object. If the import fails, it returns False. Otherwise, it returns True.

        Returns:
            bool: Success of the initialization.
        """
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
        """Sends a mail.

        This function sends a mail using the Gmail module. It takes four parameters: the address of the recipient, the subject of the mail, the text of the mail, and a list of attachments. If the mail sender is not initialized, it returns False. Otherwise, it returns True.

        Parameters:
            address (str): the address of the recipient
            subject (str): the subject of the mail
            text (str): the text of the mail
            attachments (list): a list of attachments

        Returns:
            bool: success of the mail sending
        """
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
