from youtubedlWeb.Common.SocketMessages import *
from flask import current_app as app
import uuid

class SocketManager:
    def __init__(self):
        self.activeUsersId = {}
        self.session_to_sid = {}

    def updateSessionSid(self, sessionId, sid):
        self.session_to_sid[sessionId] = sid

    def connection(self, session_id, sid):
        app.logger.debug("--- Connection ---")
        self.session_to_sid[session_id] = sid
        app.logger.debug("session_id: %s, sid: %s", session_id, sid)
        if session_id not in self.activeUsersId.keys():
            app.logger.debug("Add new active user %s", session_id)
            self.activeUsersId[session_id] = []
            return
        messageQueueList = self.activeUsersId[session_id]
        if len(messageQueueList) > 0 :
            Resume().sendMessage("", sid)
        for message in messageQueueList:
            msg:Message = message[0]()
            dataOfMessage = message[1]
            msg.sendMessage(dataOfMessage,sid)

    def disconnection(self, sid):
        app.logger.debug("--- Disconnection ---")
        #TODO

    def getSessionId(self, sid):
        sessionId = None
        for sessionId_, sid_ in self.session_to_sid.items():
            if sid_ == sid:
                sessionId = sessionId_
                break
        app.logger.debug("SessionId: %s, sid: %s", sessionId, sid)
        return sessionId

    def addMessageToQueue(self, msg, session_id):
        app.logger.debug("Add message to the queue")
        self.activeUsersId[session_id].append(msg)

    def downloadMedia_finish(self, hash, session_id):
        self.addMessageToQueue((DownloadMedia_finish, hash), session_id)
        DownloadMedia_finish().sendMessage(hash, self.session_to_sid[session_id])

    def downloadMedia_finish_error(self, error, session_id):
        self.addMessageToQueue((DownloadMedia_finish, error), session_id)
        DownloadMedia_finish().sendError(error, self.session_to_sid[session_id])

    def mediaInfo_response(self, mediaInfo:MediaInfo, session_id):
        self.addMessageToQueue((MediaInfo_response, mediaInfo), session_id)
        MediaInfo_response().sendMessage(mediaInfo, self.session_to_sid[session_id])

    def playlistInfo_response(self, playlistInfoMsg:PlaylistInfo, session_id):
        self.addMessageToQueue((PlaylistInfo_response, playlistInfoMsg), session_id)
        PlaylistInfo_response().sendMessage(playlistInfoMsg, self.session_to_sid[session_id])

    def playlistMediaInfo_response(self, playlistMediaInfoMsg:PlaylistMediaInfo, session_id):
        self.addMessageToQueue((PlaylistMediaInfo_response, playlistMediaInfoMsg), session_id)
        PlaylistMediaInfo_response().sendMessage(playlistMediaInfoMsg, self.session_to_sid[session_id])
