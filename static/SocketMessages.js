class Message
{
    constructor(messageKey)
    {
        this.messageKey = messageKey
        this.message = {}
        this._messageContent = {}
    }

    _setMessage(data)
    {
        throw new Error("set Message has to be called from message type");
    }

    setMessage(data)
    {
        this._setMessage(data)
        this._messageContent = this.message
    }

    get messageContent() {
        return this._messageContent;
    }
}

class DownloadMediaData
{
    constructor(link, type)
    {
        this._link = link;
        this._type = type;
    }

    get link()
    {
        return this._link;
    }

    get type()
    {
        return this._type;
    }
}

class DownloadMediaRequest extends Message
{
    constructor()
    {
        super("downloadMedia");
    }

    _setMessage(data)
    {
        if (!(data instanceof DownloadMediaData))
        {
            console.error("wrong data for message")
            return
        }
        this.message["link"] = data.link
        this.message["type"] = data.type
    }
}

class SocketManager
{
    constructor(socket)
    {
        this.socket = socket;
        socket.on('connect', function() {});
    }

    sendMessage(msg)
    {
        this.socket.emit(msg.messageKey, msg._messageContent)
    }
}

class MessageManager
{
    isSuccess(msg)
    {
        if ("data" in msg)
        {
            return true;
        }
        return false;
    }

    isError(msg)
    {
        if("error" in msg)
        {
            return true;
        }
        return false;
    }

    getData(msg){
        if ("data" in msg){
            return msg["data"];
        }
    }

    getError(msg)
    {
        if ("error" in msg){
            return msg["error"];
        }
    }
}


// ----------------- MediaInfo_response --------------------
class MediaInfo
{
    constructor(title, artist){
        this.title = title;
        this.artist = artist;
    }
}

// data: {"artist", "title"}
class MediaInfo_response{
    static Message = "getMediaInfo_response"
    constructor(data)
    {
        this.mediaInfo = new MediaInfo(data["title"], data["artist"])
    }
}


// -------------- downloadMedia_finish ------------------------
class DownloadMedia{
    constructor(hash)
    {
        this.hash = hash
    }
}

// data: hash
class DownloadMedia_finish{
    static Message = "downloadMedia_finish"
    constructor(data)
    {
        this.downloadMedia = new DownloadMedia(data)
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
class PlaylistInfo_response{
    static Message = "getPlaylistInfo_response"
    constructor(data)
    {
        var playlistName = data[0]
        var playlist = data[1]
        var list = []
        for (const element of playlist) {
            list.push(new MediaFromPlaylist(element["playlist_index"], element["url"], element["title"]))
        }
        this.playlistInfo = new PlaylistInfo(playlistName, list)
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
class PlaylistMediaInfo_response{
    static Message = "getPlaylistMediaInfo_response"
    constructor(data)
    {
        this.playlistMediaInfo = new PlaylistMediaInfo(data["playlist_index"], data["filename"], data["hash"])
    }
}


// --------------  downloadMediaFromPlaylist_start ------------------
// data: {playlist_index, filename}
class DownloadMediaFromPlaylist_start{
    static Message = "downloadMediaFromPlaylist_start"
    constructor(data)
    {
        this.playlistMediaInfo = new PlaylistMediaInfo(data["playlist_index"], data["filename"])
    }
}


// --------------  downloadMediaFromPlaylist_finish ------------------
// data: {playlist_index, filename}
class DownloadMediaFromPlaylist_finish{
    static Message = "downloadMediaFromPlaylist_finish"
    constructor(data)
    {
        this.playlistMediaInfo = new PlaylistMediaInfo(data["playlist_index"], data["filename"])
    }
}


// ----------------  downloadPlaylist_finish ------------------
// data: numberOfDownloadedPlaylists
class DownloadPlaylists_finish{
    static Message = "downloadPlaylist_finish"
    constructor(data)
    {
        this.numberOfDownloadedPlaylists = data
    }
}
