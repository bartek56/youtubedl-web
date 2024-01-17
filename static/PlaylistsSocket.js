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

    socket.on(DownloadPlaylist_response.Message, function (msg) {
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

    })

    socket.on('yt', function (msg) {
        var table = document.getElementById("playlists_info");
        var row = table.insertRow();
        var cell1 = row.insertCell();
        cell1.style.textAlign = 'left'
        cell1.innerHTML = msg;
    });
});