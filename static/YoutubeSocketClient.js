
$(document).ready(function () {
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
    socket.on('getMediaInfo_response', function (msg) {
        var table = document.getElementById("media_info");
        if ("error" in msg) {
            var row = table.insertRow();
            var cell1 = row.insertCell();
            cell1.innerHTML = msg["error"];
            return
        }
        var mediaInfo = ""
        var index = 1;
        var element = msg["data"];
        mediaInfo = element["artist"] + " - " + element["title"] + "\n";
        var row = table.insertRow();
        var cell1 = row.insertCell();
        cell1.style.textAlign = 'left'
        cell1.innerHTML = mediaInfo;
        var cell2 = row.insertCell();
        cell2.innerHTML = " ";
    });
    // playlist
    socket.on('getPlaylistInfo_response', function (msg) {
        var table = document.getElementById("media_info");
        if ("error" in msg)
        {
            var row = table.insertRow();
            var cell1 = row.insertCell();
            cell1.innerHTML = msg;
        }
        else
        {
            var playlistInfo = ""
            data = msg["data"]
            for (const element of data) {
                playlistInfo = " <a href=\"" + element["url"] + "\">" + element["playlist_index"] + "</a>" + ": " + element["title"] + "&nbsp;&nbsp;&nbsp;" + "\n";
                var row = table.insertRow();
                var cell1 = row.insertCell();
                cell1.style.textAlign = 'left'
                var cell2 = row.insertCell();
                cell1.innerHTML = playlistInfo;
                cell2.innerHTML = " ";
            }
        }
    });
    socket.on('getPlaylistMediaInfo_response', function (msg) {
        var table = document.getElementById("media_info");
        if ("error" in msg)
        {
            var index = msg["playlist_index"];
            var row = table.rows[index-1];
            row.deleteCell(1);
            var cell = row.insertCell(1);
            cell.innerHTML = "X";
            return
        }
        var data = msg["data"]
        var index = data["playlist_index"];
        downloadResult.push(data["filename"]);
        var row = table.rows[index-1];
        row.deleteCell(1);
        var cell = row.insertCell(1);
        var hash = data["hash"]
        cell.innerHTML = '<a href="/youtubedl/download/' + hash + '">V</a>';
        //cell.innerHTML = '<a href="/download/' + hash + '">V</a?>';
    });
    // a both
    socket.on('downloadMedia_finish', function (msg) {
        // stop spinner
        var loader = document.getElementById("spinner");
        loader.style.display = 'none';
        if ("error" in msg) {
            var table = document.getElementById("media_info");
            var row = table.insertRow();
            var cell1 = row.insertCell();
            cell1.innerHTML = msg["error"];
            var button = document.getElementById("btnFetch")
            button.disabled = false;
            return
        }
        var hash = msg["data"]
        var downloadLink = document.getElementById('downloadLink');
        downloadLink.innerHTML = '<a href="/youtubedl/download/' + hash + '">Download file</a>';
        //downloadLink.innerHTML = '<a href="/download/' + hash + '">Download file</a>';
    });
});
