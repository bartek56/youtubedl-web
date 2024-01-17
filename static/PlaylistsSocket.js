$(document).ready(function () {
    var msgManager = new MessageManager()
    var rowForSong=0;
    var loader = document.getElementById("spinner");
    var line = "--------------------------------------------------------------------------"
    loader.style.display = 'none';

    var socket = io.connect();
        socket.on('connect', function() {
    });

    $('form#downloadPlaylists').submit(function(msg) {
        // disable button
        var button = document.getElementById("submitButton");
        button.disabled = true;

        var loader = document.getElementById("spinner");
        loader.style.display = 'block';

        var table = document.getElementById("playlists_info");
        table.innerHTML = '';

        socket.emit('downloadPlaylists', '');
        return false;
    });

    socket.on(PlaylistInfo_response.Message, function (msg) {
        var table = document.getElementById("playlists_info");
        if (msgManager.isError(msg))
        {
            console.log("error", msgManager.getError(msg))
            return
        }

        console.log(msgManager.getData(msg))
        var playlistInfo = new PlaylistInfo_response(msgManager.getData(msg))
        if (table.rows.length > 0)
        {
            var row = table.insertRow();
            var cell1 = row.insertCell();
            cell1.innerHTML = line
        }

        var row = table.insertRow();
        var cell1 = row.insertCell();

        cell1.style.textAlign = 'center'
        var response = new PlaylistMediaInfo_response(msgManager.getData(msg));
        info = response.playlistMediaInfo
        cell1.innerHTML = "<h4>"+playlistInfo.playlistInfo.playlistName+"<h4>"
    });

    socket.on(DownloadMediaFromPlaylist_start.Message, function (msg) {
        var table = document.getElementById("playlists_info");
        if (msgManager.isError(msg))
        {
            return
        }
        var row = table.insertRow();
        rowForSong = table.rows.length - 1
        var cell1 = row.insertCell();
        cell1.style.textAlign = 'left'
        var response = new PlaylistMediaInfo_response(msgManager.getData(msg));
        info = response.playlistMediaInfo
        cell1.innerHTML = info.playlistIndex + ". "
        cell1.innerHTML += info.filename
    });

    socket.on(DownloadMediaFromPlaylist_finish.Message, function (msg) {
        var table = document.getElementById("playlists_info");
        if (msgManager.isError(msg))
        {
            var row = table.rows[rowForSong];
            var cell = row.insertCell(1);
            cell.innerHTML = 'X';
            return
        }
        var row = table.rows[rowForSong];
        var cell = row.insertCell();
        cell.innerHTML = 'V';
    })

    socket.on(DownloadPlaylists_finish.Message, function(msg) {
        // enable button
        document.getElementById("submitButton").disabled = false;
        // stop spinner
        var loader = document.getElementById("spinner");
        loader.style.display = 'none';

        var table = document.getElementById("playlists_info");
        if (msgManager.isError(msg))
        {
            var row = table.insertRow();
            var cell1 = row.insertCell();
            cell1.innerHTML = msg["error"];
            return;
        }
        var row = table.insertRow();
        var cell1 = row.insertCell();
        cell1.innerHTML = line
        var result = document.getElementById("result");
        var response = new DownloadPlaylists_finish(msgManager.getData(msg))
        result.innerHTML = "Successfull updated Your music collection<br>"
        result.innerHTML += "Number of new songs: " +response.numberOfDownloadedPlaylists
    })
});