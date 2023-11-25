class MessageManager{
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
    constructor(listOfMedia)
    {
        this.listofMedia = listOfMedia
    }
}

// data: [{"url" "playlist_index" "title"}, ..]
class PlaylistInfo_response{
    static Message = "getPlaylistInfo_response"
    constructor(data)
    {
        var list = []
        for (const element of data) {
            list.push(new MediaFromPlaylist(element["playlist_index"], element["url"], element["title"]))
        }
        this.playlistInfo = new PlaylistInfo(list)
    }
}

class PlaylistMediaInfo{
    constructor(playlistIndex, filename, hash)
    {
        this.playlistIndex = playlistIndex
        this.filename = filename
        this.hash = hash
    }
}

// data: [{"url" "playlist_index" "title"}, ..]
class PlaylistMediaInfo_response{
    static Message = "getPlaylistMediaInfo_response"
    constructor(data)
    {
        this.playlistMediaInfo = new PlaylistMediaInfo(data["playlist_index"], data["url"], data["hash"])
    }
}

class DownloadMedia{
    constructor(hash)
    {
        this.hash = hash
    }
}

class DownloadMedia_finish{
    static Message = "downloadMedia_finish"
    constructor(data)
    {
        this.downloadMedia = new DownloadMedia(data)

    }
}
