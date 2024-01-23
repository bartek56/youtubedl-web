$(document).ready(function () {
    var rowForSong=0;
    var loader = document.getElementById("spinner");
    var line = "--------------------------------------------------------------------------"
    loader.style.display = 'none';
    var playlistName = ""

    var socket = io.connect();
    var socketManager = new SocketManager(socket)

    $('form#downloadPlaylists').submit(function(msg) {
        // disable button
        var button = document.getElementById("submitButton");
        button.disabled = true;

        var loader = document.getElementById("spinner");
        loader.style.display = 'block';

        var table = document.getElementById("playlists_info");
        table.innerHTML = '';
        var result = document.getElementById("result");
        result.innerHTML = '';
        socketManager.sendMessage(new DownloadPlaylistsRequest())
        return false;
    });

    socket.on(PlaylistInfo_response.Message, function (msg) {
        var playlistInfo_response = new PlaylistInfo_response(msg)
        var table = document.getElementById("playlists_info");
        if (playlistInfo_response.isError())
        {
            console.log("error", playlistInfo_response.getError())
            return
        }

        var playlistInfo = playlistInfo_response.getData()
        if (table.rows.length > 0)
        {
            var row = table.insertRow();
            var cell1 = row.insertCell();
            cell1.innerHTML = line
        }

        var row = table.insertRow();
        var cell1 = row.insertCell();

        cell1.style.textAlign = 'center'
        playlistName = playlistInfo.playlistName
        cell1.innerHTML = "<h4>"+playlistName+"<h4>"
    });

    socket.on(DownloadMediaFromPlaylist_start.Message, function (msg) {
        var downloadMediaFromPlaylist_start = new DownloadMediaFromPlaylist_start(msg)
        var table = document.getElementById("playlists_info");
        if (downloadMediaFromPlaylist_start.isError())
        {
            return
        }
        var row = table.insertRow();
        rowForSong = table.rows.length - 1
        var cell1 = row.insertCell();
        cell1.style.textAlign = 'left'
        var info = downloadMediaFromPlaylist_start.getData();
        cell1.innerHTML = info.playlistIndex + ". "
        cell1.innerHTML += info.filename
    });

    socket.on(DownloadMediaFromPlaylist_finish.Message, function (msg) {
        var downloadMediaFromPlaylist_finish = new DownloadMediaFromPlaylist_finish(msg)
        var table = document.getElementById("playlists_info");
        if (downloadMediaFromPlaylist_finish.isError())
        {
            var row = table.rows[rowForSong];
            var cell = row.insertCell(1);
            var button = document.createElement('button');
            button.innerHTML = 'X';

            cell.appendChild(button);
            m_playlistName = playlistName

            button.addEventListener('click', function() {
                data = downloadMediaFromPlaylist_finish.getError()
                index = data.index
                ytHash = data.ytHash
                title = data.title
                for (var i = 0; i < table.rows.length; i++) {
                    var komorka = table.rows[i].cells[0]

                    if (komorka.innerHTML.indexOf(title) !== -1) {
                      table.deleteRow(i);
                      break;
                    }
                }
                var archiveSongRequest  = new ArchiveSongRequest()
                archiveSongRequest.setMessage(new ArchiveSong(ytHash, index, m_playlistName))

                socketManager.sendMessage(archiveSongRequest)
            });
            return
        }
        var row = table.rows[rowForSong];
        row.deleteCell(0);

        var data = downloadMediaFromPlaylist_finish.getData()
        console.log(data)
        var cell1 = row.insertCell();
        cell1.style.textAlign = 'left'
        var info = downloadMediaFromPlaylist_finish.getData();
        cell1.innerHTML = info.playlistIndex + ". "
        cell1.innerHTML += info.filename

        var cell2 = row.insertCell()
        cell2.innerHTML = 'V';
    })

    socket.on(DownloadPlaylists_finish.Message, function(msg) {
        // enable button
        document.getElementById("submitButton").disabled = false;
        // stop spinner
        var loader = document.getElementById("spinner");
        loader.style.display = 'none';

        var table = document.getElementById("playlists_info");
        var downloadPlaylists_finish = new DownloadPlaylists_finish(msg);
        if (downloadPlaylists_finish.isError())
        {
            var row = table.insertRow();
            var cell1 = row.insertCell();
            cell1.innerHTML = downloadPlaylists_finish.getError();
            return;
        }
        var row = table.insertRow();
        var cell1 = row.insertCell();
        cell1.innerHTML = line;
        var response = downloadPlaylists_finish.getData();
        var result = document.getElementById("result");
        result.innerHTML = "Successfull updated Your music collection<br>";
        result.innerHTML += "Number of new songs: " + response;
    })
});