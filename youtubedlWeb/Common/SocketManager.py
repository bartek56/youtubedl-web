from youtubedlWeb.Common.SocketMessages import *
from flask import session
from flask import current_app as app
import uuid

class SocketManager:
    def __init__(self):
        #if 'user_id' in session:
        #    print("!!!!!!", session['user_id'])
        self.sessions = {}

    def connection(self):
        app.logger.debug("-- Connection --")

        if 'user_id' not in session:
            newUserID = str(uuid.uuid4())
            session['user_id'] = newUserID
            self.sessions[newUserID] = []

            app.logger.debug("new connection")
            return
        userId = session['user_id']
        app.logger.debug("user_id : %s", userId)
        if userId not in self.sessions.keys():
            self.sessions[userId] = []
            app.logger.debug("User with id: %s doesn't exist", userId)
            return
        messageQueueList = self.sessions[userId]
        for message in messageQueueList:
            msg:Message = message[0]()
            dataOfMessage = message[1]
            app.logger.debug("send %s message with data: %s from history", msg.message, dataOfMessage)
            msg.sendMessage(dataOfMessage)

    def getId(self):
        if 'user_id' not in session:
            newUserID = str(uuid.uuid4())
            session['user_id'] = newUserID
            self.sessions[newUserID] = []
            return newUserID
        return session['user_id']

    def addMessageToQueue(self, msg):
        app.logger.debug("Add message to the queue")
        id = self.getId()
        self.sessions[id].append(msg)
        for key, value in self.sessions.items():
            print(key, value)

    def downloadMedia_finish(self, hash):
        self.addMessageToQueue((DownloadMedia_finish, hash))
        DownloadMedia_finish().sendMessage(hash)

    def downloadMedia_finish_error(self, error):
        self.addMessageToQueue((DownloadMedia_finish, error))
        DownloadMedia_finish().sendError(error)

    def mediaInfo_response(self, mediaInfo:MediaInfo):
        self.addMessageToQueue((MediaInfo_response, mediaInfo))
        MediaInfo_response().sendMessage(mediaInfo)
