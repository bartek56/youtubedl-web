from youtubedlWeb.Common.SocketMessages import *
from flask import session
from flask import current_app as app
import uuid

class SocketManager:
    def __init__(self):
        #if 'user_id' in session:
        #    print("!!!!!!", session['user_id'])
        self.activeUsersId = {}

    def connection(self, sid):
        app.logger.debug("--- Connection ---")
        session['sid'] = sid

        # check if session in the client browser still exist
        if 'user_id' not in session:
            app.logger.debug("new connection, create user_id")
            newUserID = str(uuid.uuid4())
            session['user_id'] = newUserID
            self.activeUsersId[newUserID] = []
            return
        userId = session['user_id']
        app.logger.debug("user_id : %s", userId)
        if userId not in self.activeUsersId.keys():
            app.logger.debug("Session exists, add new active user %s", userId)
            self.activeUsersId[userId] = []
            return
        messageQueueList = self.activeUsersId[userId]
        for message in messageQueueList:
            msg:Message = message[0]()
            dataOfMessage = message[1]
            app.logger.debug("send %s message with data: %s from history", msg.message, dataOfMessage)
            msg.sendMessage(dataOfMessage)

    def newSession(self, sid):
        session['sid'] = sid
        if 'user_id' not in session:
            app.logger.warning("user_id key doesn't exist in session")
        userId = session['user_id']
        self.activeUsersId[userId] = []

    def disconnection(self, sid):
        app.logger.debug("--- Disconnection ---")
        if 'user_id' in session:
            userId = session['user_id']
            app.logger.debug("session exist: %s", userId)
            #self.activeUsersId.pop(userId)

    def getId(self):
        if 'user_id' not in session:
            newUserID = str(uuid.uuid4())
            session['user_id'] = newUserID
            self.activeUsersId[newUserID] = []
            return newUserID
        return session['user_id']

    def addMessageToQueue(self, msg):
        app.logger.debug("Add message to the queue")
        id = self.getId()
        self.activeUsersId[id].append(msg)
        for key, value in self.activeUsersId.items():
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

    def playlistInfo_response(self, playlistInfoMsg:PlaylistInfo):
        self.addMessageToQueue((PlaylistInfo_response, playlistInfoMsg))
        PlaylistInfo_response().sendMessage(playlistInfoMsg)

    def playlistMediaInfo_response(self, playlistMediaInfoMsg:PlaylistMediaInfo):
        self.addMessageToQueue((PlaylistMediaInfo_response, playlistMediaInfoMsg))
        PlaylistMediaInfo_response().sendMessage(playlistMediaInfoMsg)
