import datetime
import inspect
from enum import Enum
from flask_socketio import SocketIO, emit

class LogLevel(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

class SocketLogger():
    def __init__(self):
        self.settings()

    def debug(self, *args):
        log = self.DEBUG(args)
        self.emitToSocket(log)

    def warning(self, *args):
        log = self.WARNING(args)
        self.emitToSocket(log)

    def error(self, *args):
        log = self.ERROR(args)
        self.emitToSocket(log)

    def emitToSocket(self, log):
        if log:
            emit("yt", log)

    def DEBUG(self, args):
        if self.logLevel.value <= LogLevel.DEBUG.value:
            log = self.getLog("DEBUG", args)
            if log != None:
                self.writeToFile(log)
                if self.isPrinting:
                    print(log)
                return log

    def INFO(self, *args):
        if self.logLevel.value <= LogLevel.INFO.value:
            log = self.getLog("INFO", args)
            if log != None:
                self.writeToFile(log)
                if self.isPrinting:
                    print(log)
                return log

    def WARNING(self, *args):
        if self.logLevel.value <= LogLevel.WARNING.value:
            log = self.getLog("WARNING", args)
            if log != None:
                self.writeToFile(log)
                if self.isPrinting:
                    print(log)
                return log

    def ERROR(self, *args):
        if self.logLevel.value <= LogLevel.ERROR.value:
            log = self.getLog("ERROR", args)
            if log != None:
                self.writeToFile(log)
                if self.isPrinting:
                    print(log)
                return log

    def getLog(self, level, args):
        log=""
        for x in self.skippingLogWith:
            for y in args:
               if x in str(y):
                   return None
        if self.showDate:
            log += self.getTime()
        if self.showFilename:
            if len(log) != 0:
                log+= " "
            log += "%s\t"%(self.getFilename())
        if self.showLogLevel:
            if len(log) != 0:
                log+= " "
            log += "%s:"%(level)
        if len(log) != 0:
            log+= " "
        log += self.getLogText(args)
        return log

    def getLogText(self, args):
        log = ""
        for x in args:
            log += str(x)
            log += " "
        return log

    def getTime(self):
        now = datetime.datetime.now()
        date_time = now.strftime("%Y/%m/%d %H:%M:%S")
        return date_time

    def getFilename(self):
        fullFilenameSplitted = inspect.stack()[4].filename.split('/')
        lineNumber = inspect.stack()[3].lineno
        filename = fullFilenameSplitted[len(fullFilenameSplitted)-1]
        result = "%s:%s"%(filename, lineNumber)
        return result

    def writeToFile(self, log):
        if(self.isSaveToFileEnable):
            f = open(self.fileNameWithPath,"a")
            f.write(log)
            f.write("\n")
            f.close()

    def settings(self, logLevel = LogLevel.DEBUG, showDate=True, showFilename=True, showLogLevel=True, print=True, saveToFile=False, fileNameWihPath="logger.log", skippingLogWith=[]):
        self.showDate = showDate
        self.isSaveToFileEnable = saveToFile
        self.fileNameWithPath = fileNameWihPath
        self.showFilename = showFilename
        self.showLogLevel = showLogLevel
        self.logLevel = logLevel
        self.isPrinting = print
        self.skippingLogWith = skippingLogWith
