
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


// --------------  downloadPlaylist_response ------------------
// data: index
class DownloadPlaylist_response{
    static Message = "downloadPlaylist_response"
    constructor(data)
    {
        this.index = data
    }
}


// ----------------  downloadPlaylist_finish ------------------
// data: numberOfDownloadedPlaylists
class DownloadPlaylist_finish{
    static Message = "downloadPlaylist_finish"
    constructor(data)
    {
        this.numberOfDownloadedPlaylists = data
    }
}
