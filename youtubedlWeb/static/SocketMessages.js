
class SocketManager
{
    constructor(socket)
    {
        this.socket = socket;
        socket.on('connect', function() {});
    }

    sendMessage(msg)
    {
        if (!(msg instanceof Message))
        {
            console.error("wrong data for send message")
            return
        }
        this.socket.emit(msg.messageKey, msg._messageContent)
    }
}

class MessageBase
{
    constructor(msg)
    {
        this.message = msg
        this.errorStr = "error"
        this.dataStr = "data"
    }

    isSuccess()
    {
        if (this.dataStr in this.message)
        {
            return true;
        }
        return false;
    }

    isError()
    {
        if(this.errorStr in this.message)
        {
            return true;
        }
        return false;
    }

    _getData(data)
    {
        return this.message[this.dataStr]
    }

    getData(){
        if (this.dataStr in this.message){
            this.data = this.message[this.dataStr]
            return this._getData();
        }
    }

    _getError()
    {
        return this.message[this.errorStr]
    }

    getError()
    {
        if (this.errorStr in this.message)
        {
            this.error = this.message[this.errorStr]
            return this._getError()
        }
    }
}


// ----------------- MediaInfo_response --------------------
class MediaInfo
{
    constructor(title, artist, hash){
        this.title = title;
        this.artist = artist;
        this.hash = hash;
    }
}

// data: {"artist", "title", "hash"}
class MediaInfo_response extends MessageBase{
    static Message = "getMediaInfo_response"
    constructor(msg)
    {
        super(msg)
    }

    _getData()
    {
        this.mediaInfo = new MediaInfo(this.data["title"], this.data["artist"], this.data["hash"])
        return this.mediaInfo
    }
}


// -------------- downloadMedia_finish ------------------------
// data: hash
class DownloadMedia_finish extends MessageBase{
    static Message = "downloadMedia_finish"
    constructor(msg)
    {
        super(msg)
    }
}


// --------------- getPlaylistInfo_response -----------------
class MediaFromPlaylist
{
    constructor(playlistIndex, url, title)
    {
        this.playlistIndex = playlistIndex
        this.url = url
        this.title = title
    }
}

class PlaylistInfo
{
    constructor(playlistName, listOfMedia)
    {
        this.playlistName = playlistName
        this.listofMedia = listOfMedia
    }
}

// data: playlistName, [{"playlist_index" "url" "title"}, ..]
class PlaylistInfo_response extends MessageBase{
    static Message = "getPlaylistInfo_response"
    constructor(msg)
    {
        super(msg)
    }

    _getData()
    {
        var playlistName = this.data[0]
        var playlist = this.data[1]
        var list = []
        for (const element of playlist) {
            list.push(new MediaFromPlaylist(element["playlist_index"], element["url"], element["title"]))
        }
        var playlistInfo = new PlaylistInfo(playlistName, list)
        return playlistInfo
    }
}


// ------------  getPlaylistMediaInfo_response ----------------
class PlaylistMediaInfo{
    constructor(playlistIndex, filename, hash)
    {
        this.playlistIndex = playlistIndex
        this.filename = filename
        this.hash = hash
    }
}

// data: {"playlist_index" "filename" "hash"}
class PlaylistMediaInfo_response extends MessageBase{
    static Message = "getPlaylistMediaInfo_response"
    constructor(msg)
    {
        super(msg)
    }

    _getData()
    {
        return new PlaylistMediaInfo(this.data["playlist_index"], this.data["filename"], this.data["hash"])
    }
}


// --------------  downloadMediaFromPlaylist_start ------------------
// data: {playlist_index, filename}
class DownloadMediaFromPlaylist_start extends MessageBase{
    static Message = "downloadMediaFromPlaylist_start"
    constructor(msg)
    {
        super(msg)
    }

    _getData()
    {
        return new PlaylistMediaInfo(this.data["playlist_index"], this.data["filename"])
    }
}


// --------------  downloadMediaFromPlaylist_finish ------------------
class DownloadMediaFromPlaylistError
{
    constructor(index, ytHash, title)
    {
        this.index = index
        this.ytHash = ytHash
        this.title = title
    }
}

// data: {playlist_index, filename}
class DownloadMediaFromPlaylist_finish extends MessageBase {
    static Message = "downloadMediaFromPlaylist_finish"
    constructor(msg) {
        super(msg)
    }

    _getData() {
        return new PlaylistMediaInfo(this.data["playlist_index"], this.data["filename"])
    }

    _getError() {
        return new DownloadMediaFromPlaylistError(this.error["index"], this.error["ytHash"], this.error["title"])
    }
}


// ----------------  downloadPlaylist_finish ------------------
// data: numberOfDownloadedPlaylists
class DownloadPlaylists_finish extends MessageBase{
    static Message = "downloadPlaylist_finish"
    constructor(msg)
    {
        super(msg)
    }
}
