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
        this.message = data
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


// ------------------ downloadMedia -------------------
class DownloadMedia
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
        if (!(data instanceof DownloadMedia))
        {
            console.error("wrong data for message")
            return
        }
        this.message["link"] = data.link
        this.message["type"] = data.type
    }
}


// ------------------ downloadPlaylists -------------------
class DownloadPlaylistsRequest extends Message
{
    constructor()
    {
        super("downloadPlaylists");
    }
}


// ------------------ archiveSong -------------------
class ArchiveSong
{
    constructor(ytHash, index, playlistName)
    {
        this.ytHash = ytHash;
        this.index = index;
        this.playlistName = playlistName;
    }
}

class ArchiveSongRequest extends Message
{
    constructor()
    {
        super("archiveSong")
    }

    _setMessage(data)
    {
        if (!(data instanceof ArchiveSong))
        {
            console.error("wrong data for message")
            return
        }
        this.message["ytHash"] = data.ytHash
        this.message["index"] = data.index
        this.message["playlistName"] = data.playlistName
    }
}

