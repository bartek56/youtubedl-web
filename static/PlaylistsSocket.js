$(document).ready(function () {
    var msgManager = new MessageManager()
    var downloadResult = [];
    var loader = document.getElementById("spinner");
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
        console.log(PlaylistInfo_response.Message)
        var table = document.getElementById("playlists_info");
        if (msgManager.isError(msg))
        {
            console.log("error", msgManager.getError(msg))
            return
        }

        console.log(msgManager.getData(msg))
        var playlistInfo = new PlaylistInfo_response(msgManager.getData(msg))
        table.insertRow();
        var row = table.insertRow();
        var cell1 = row.insertCell();
        cell1.style.textAlign = 'center'
        var response = new PlaylistMediaInfo_response(msgManager.getData(msg));
        info = response.playlistMediaInfo
        cell1.innerHTML = playlistInfo.playlistInfo.playlistName

    });

    socket.on(PlaylistMediaInfo_response.Message, function (msg) {
        console.log(PlaylistMediaInfo_response.Message)

        var table = document.getElementById("playlists_info");
        if (msgManager.isError(msg))
        {
            console.log("error", msgManager.getError(msg))
        }
        else
        {
            console.log(msgManager.getData(msg))
            var row = table.insertRow();
            var cell1 = row.insertCell();
            cell1.style.textAlign = 'left'
            var response = new PlaylistMediaInfo_response(msgManager.getData(msg));
            info = response.playlistMediaInfo
            cell1.innerHTML = info.playlistIndex + ". "
            cell1.innerHTML += info.filename
        }
    });

    socket.on(DownloadPlaylist_response.Message, function (msg) {
        console.log(DownloadPlaylist_response.Message)
        if (msgManager.isError(msg)) {
            var table = document.getElementById("playlists_info");
            var row = table.insertRow();
            var cell = row.insertCell();
            cell.innerHTML = msg["error"];
            return;
        }
        var table = document.getElementById("playlists_info");
        var row = table.insertRow();
        var cell = row.insertCell();
        cell.innerHTML = "-------------------------------------------------"
   })

    socket.on(DownloadPlaylist_finish.Message, function(msg) {
        console.log(DownloadPlaylist_finish.Message)
        // enable button
        document.getElementById("submitButton").disabled = false;
        // stop spinner
        var loader = document.getElementById("spinner");
        loader.style.display = 'none';

        if (msgManager.isError(msg))
        {
            var table = document.getElementById("playlists_info");
            var row = table.insertRow();
            var cell1 = row.insertCell();
            cell1.innerHTML = msg["error"];
            return;
        }

        var result = document.getElementById("result");
        var response = new DownloadPlaylist_finish(msgManager.getData(msg))
        result.innerHTML = "Successfull updated Your music collection<br>"
        result.innerHTML += "Number of new songs: " +response.numberOfDownloadedPlaylists
    })

    socket.on('yt', function (msg) {
        var table = document.getElementById("playlists_info");
        var row = table.insertRow();
        var cell1 = row.insertCell();
        cell1.style.textAlign = 'left'
        cell1.innerHTML = msg;
    });
});