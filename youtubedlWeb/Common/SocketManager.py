from youtubedlWeb.Common.SocketMessages import *
from flask import current_app as app
import time

class SocketManager:
    def __init__(self):
        """
        Initialize SocketManager object.

        This object stores information about active users and
        manages session lifetime.

        Attributes:
            activeUsersId (dict): mapping of session_id to list of messages to send
            session_to_sid (dict): mapping of session_id to sid
            sessionLifetime (dict): mapping of session_id to timestamp of last message
            SESSION_TIMEOUT (int): time in seconds after which session is considered inactive
        """
        self.activeUsersId = {}
        self.session_to_sid = {}
        self.sessionLifetime = {}
        self.SESSION_TIMEOUT = 180 #sec

    def updateSessionSid(self, sessionId, sid):
        """
        Update session_id to sid mapping.

        Args:
            sessionId (str): session id of user
            sid (str): socket id of user
        """
        self.session_to_sid[sessionId] = sid

    def connection(self, session_id, sid):
        """
        Handle connection event.

        This method is called when user connects to the socket server.
        It stores session_id to sid mapping and updates session lifetime.

        Args:
            session_id (str): session id of user
            sid (str): socket id of user
        """
        app.logger.debug("--- Connection ---")
        self.session_to_sid[session_id] = sid
        self.sessionLifetime[session_id] = time.time()
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
            isError = not message[2]
            if isError:
                msg.sendError(dataOfMessage, sid)
            else:
                msg.sendMessage(dataOfMessage,sid)

    def disconnection(self, sid):
        """
        Handle disconnection event.

        This method is called when user disconnects from the socket server.
        It removes session_id to sid mapping and updates session lifetime.

        Args:
            sid (str): socket id of user
        """
        app.logger.debug("--- Disconnection ---")
        now = time.time()
        for sessionId in list(self.sessionLifetime):
            lastTimePoint = self.sessionLifetime[sessionId]
            if now - lastTimePoint > self.SESSION_TIMEOUT:
                app.logger.debug("Clean session_id: %s", sessionId)
                # TODO one object
                self.activeUsersId.pop(sessionId)
                self.sessionLifetime.pop(sessionId)
                self.session_to_sid.pop(sessionId)


    def clearQueue(self, session_id):
        """
        Clear the message queue for a given session_id.

        Args:
            session_id (str): session id of user
        """
        app.logger.debug("--- clear queue ---")
        self.activeUsersId[session_id] = []

    def getSessionId(self, sid):
        """
        Get the session_id for a given sid.

        Args:
            sid (str): socket id of user

        Returns:
            str: session id of user
        """
        sessionId = None
        for sessionId_, sid_ in self.session_to_sid.items():
            if sid_ == sid:
                sessionId = sessionId_
                break
        app.logger.debug("SessionId: %s, sid: %s", sessionId, sid)
        return sessionId

    def addMessageToQueue(self, msg, session_id):
        """
        Add a message to the message queue for a given session_id.

        Args:
            msg (tuple): tuple of (messageType, messageData)
            session_id (str): session id of user

        The message is added to the queue associated with the session_id.
        The session lifetime is updated to the current time.
        """
        app.logger.debug("Add message %s to the queue", msg)
        # TODO heartbeat
        self.sessionLifetime[session_id] = time.time()
        msgToQueue = (msg[0], msg[1], True)
        self.activeUsersId[session_id].append(msgToQueue)

    def addErrorToQueue(self, msg, session_id):
        """
        Add an error to the message queue for a given session_id.

        Args:
            msg (tuple): tuple of (messageType, messageData)
            session_id (str): session id of user

        The error is added to the queue associated with the session_id.
        The session lifetime is updated to the current time.
        """
        app.logger.debug("Add error %s to the queue", msg)
        # TODO heartbeat
        self.sessionLifetime[session_id] = time.time()
        msgToQueue = (msg[0], msg[1], False)
        self.activeUsersId[session_id].append(msgToQueue)

    def downloadMedia_finish(self, hash, session_id):
        """
        Send a downloadMedia_finish message to the client with the given hash.

        Args:
            hash (str): hash of the downloaded file
            session_id (str): session id of user

        The message is added to the queue associated with the session_id.
        The session lifetime is updated to the current time.
        """
        self.addMessageToQueue((DownloadMedia_finish, hash), session_id)
        DownloadMedia_finish().sendMessage(hash, self.session_to_sid[session_id])

    def downloadMedia_finish_error(self, error, session_id):
        """
        Send a downloadMedia_finish error message to the client with the given error.

        Args:
            error (str): error message to send to the client
            session_id (str): session id of user

        The error is added to the queue associated with the session_id.
        The session lifetime is updated to the current time.
        """
        self.addErrorToQueue((DownloadMedia_finish, error), session_id)
        DownloadMedia_finish().sendError(error, self.session_to_sid[session_id])

    def mediaInfo_response(self, mediaInfo:MediaInfo, session_id):
        """
        Send a mediaInfo_response message to the client with the given mediaInfo.

        Args:
            mediaInfo (MediaInfo): media info to send to the client
            session_id (str): session id of user

        The message is added to the queue associated with the session_id.
        The session lifetime is updated to the current time.
        """
        self.addMessageToQueue((MediaInfo_response, mediaInfo), session_id)
        MediaInfo_response().sendMessage(mediaInfo, self.session_to_sid[session_id])

    def playlistInfo_response(self, playlistInfoMsg:PlaylistInfo, session_id):
        """
        Send a playlistInfo_response message to the client with the given playlistInfo.

        Args:
            playlistInfoMsg (PlaylistInfo): playlist info to send to the client
            session_id (str): session id of user

        The message is added to the queue associated with the session_id.
        The session lifetime is updated to the current time.
        """
        self.addMessageToQueue((PlaylistInfo_response, playlistInfoMsg), session_id)
        PlaylistInfo_response().sendMessage(playlistInfoMsg, self.session_to_sid[session_id])

    def playlistMediaInfo_response(self, playlistMediaInfoMsg:PlaylistMediaInfo, session_id):
        """
        Send a playlistMediaInfo_response message to the client with the given playlistMediaInfo.

        Args:
            playlistMediaInfoMsg (PlaylistMediaInfo): playlist media info to send to the client
            session_id (str): session id of user

        The message is added to the queue associated with the session_id.
        The session lifetime is updated to the current time.
        """
        self.addMessageToQueue((PlaylistMediaInfo_response, playlistMediaInfoMsg), session_id)
        PlaylistMediaInfo_response().sendMessage(playlistMediaInfoMsg, self.session_to_sid[session_id])

    def playlistMediaInfo_response_error(self, error, session_id):
        """
        Send a playlistMediaInfo_response error message to the client with the given error.

        Args:
            error (str): error message to send to the client
            session_id (str): session id of user

        The error is added to the queue associated with the session_id.
        The session lifetime is updated to the current time.
        """
        self.addErrorToQueue((PlaylistMediaInfo_response, error), session_id)
        PlaylistMediaInfo_response().sendError(error, self.session_to_sid[session_id])
