
$(document).ready(function () {

    var msgManager = new MessageManager()
    var downloadResult = [];
    var loader = document.getElementById("spinner");
    loader.style.display = 'none';

    var socket = io.connect();
    socket.on('connect', function() {});

    var form = document.getElementById("downloadForm");
    form.addEventListener("submit", function (event) {
        event.preventDefault();
        var table = document.getElementById("media_info");
        table.innerHTML = ' ';
        var downloadLink = document.getElementById("downloadLink");
        downloadLink.innerHTML = ' '
        downloadResult = [];
        var downloadType = ""
        var rbDownloadType = document.getElementsByName("quickdownload");
        for (var i = 0; i < rbDownloadType.length; i++) {
            if (rbDownloadType[i].checked) {
                var downloadType = rbDownloadType[i].value;
                break;
            }
        }
        // disable button
        var button = document.getElementById("btnFetch")
        button.disabled = true;
        var loader = document.getElementById("spinner");
        loader.style.display = 'block';

        var playlists = document.getElementById("linkInput");
        var url = playlists.value;
        socket.emit('downloadMedia', { url: url, type: downloadType});

        return false;
    });

    // single media
    socket.on(MediaInfo_response.Message, function (msg) {

        var table = document.getElementById("media_info");
        if (msgManager.isError(msg)) {
            var downloadLink = document.getElementById("downloadLink");
            downloadLink.innerHTML = msgManager.getError(msg);
            return;
        }
        var data = msgManager.getData(msg)
        var mediaInfo = new MediaInfo_response(msgManager.getData(msg)).mediaInfo;

        var mediaInfoHtml = mediaInfo.artist + " - " + mediaInfo.title + "\n";
        var row = table.insertRow();
        var cell1 = row.insertCell();
        cell1.innerHTML = mediaInfoHtml;
        var cell2 = row.insertCell();
        cell2.innerHTML = " ";
    });

    // playlist
    socket.on(PlaylistInfo_response.Message, function (msg) {
        var table = document.getElementById("media_info");
        if (msgManager.isError(msg))
        {
            var downloadLink = document.getElementById("downloadLink");
            downloadLink.innerHTML = msgManager.getError(msg);
        }
        else
        {
            var playlistInfo = ""
            var playlistInfoData = new PlaylistInfo_response(msgManager.getData(msg)).playlistInfo
            var listOfMedia = playlistInfoData.listofMedia
            for (const element of listOfMedia) {
                playlistInfo = " <a href=\"" + element.url + "\">" + element.playlistIndex + "</a>" + ": " + element.title + "&nbsp;&nbsp;&nbsp;" + "\n";
                var row = table.insertRow();
                var cell1 = row.insertCell();
                cell1.style.textAlign = 'left'
                var cell2 = row.insertCell();
                cell1.innerHTML = playlistInfo;
                cell2.innerHTML = " ";
            }
        }
    });

    socket.on(PlaylistMediaInfo_response.Message, function (msg) {
        var table = document.getElementById("media_info");
        if (msgManager.isError(msg))
        {
            return
        }
        var data = new PlaylistMediaInfo_response(msgManager.getData(msg)).playlistMediaInfo
        var index = data.playlistIndex
        downloadResult.push(data.filename);
        var row = table.rows[index-1];
        row.deleteCell(1);
        var cell = row.insertCell(1);
        cell.innerHTML = '<a href="/youtubedl/download/' + data.hash + '">V</a>';
        //cell.innerHTML = '<a href="/download/' + data.hash + '">V</a?>';
    });

    // a both
    socket.on('downloadMedia_finish', function (msg) {
        // stop spinner
        var loader = document.getElementById("spinner");
        loader.style.display = 'none';
        if (msgManager.isError(msg)){
            var downloadLink = document.getElementById("downloadLink");
            downloadLink.innerHTML = msgManager.getError(msg);
            var button = document.getElementById("btnFetch")
            button.disabled = false;
            return
        }
        var downloadMedia = new DownloadMedia_finish(msgManager.getData(msg)).downloadMedia
        var hash = downloadMedia.hash
        var downloadLink = document.getElementById('downloadLink');
        downloadLink.innerHTML = '<a href="/youtubedl/download/' + hash + '">Download file</a>';
        //downloadLink.innerHTML = '<a href="/download/' + hash + '">Download file</a>';
    });

});