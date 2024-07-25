# ------------------------- downloadMedia -------------------------
class DownloadMedia:
    def __init__(self, link, type):
        self.link = link
        self.type = type

class DownloadMediaRequest:
    message = "downloadMedia"

    def __init__(self, msg):
        self.downloadMedia = DownloadMedia(msg["link"], msg["type"])

# --------------------- downloadPlaylists ----------------------------
class DownloadPlaylists:
    def __init__(self, link, name):
        self.link = link
        self.playlistName = name

class DownloadPlaylistsRequest:
    message = "downloadPlaylists"
    def __init__(self, msg):
        self.downloadPlaylists = DownloadPlaylists(msg["link"], msg["name"])

# ------------------------- downloadFile -------------------------
class DownloadFile:
    def __init__(self, hash):
        self.hash = hash

class DownloadFileRequest:
    message = "downloadFile"

    def __init__(self, msg):
        self.downloadFile = DownloadFile(msg["hash"])
        print(self.downloadFile.hash)

# ------------------------ archiveSong -------------------------------
class ArchiveSong:
    def __init__(self, ytHash, index, playlistName):
        self.ytHash = ytHash
        self.index = index
        self.platlistName = playlistName

class ArchiveSongRequest:
    message = "archiveSong"
    def __init__(self, msg):
        self.archiveSong = ArchiveSong(msg["ytHash"], msg["index"], msg["playlistName"])
