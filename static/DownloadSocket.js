
$(document).ready(function () {

    var downloadResult = [];
    var loader = document.getElementById("spinner");
    loader.style.display = 'none';

    var socket = io.connect();
    var socketManager = new SocketManager(socket)

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


        var request = new DownloadMediaRequest()
        request.setMessage(new DownloadMediaData(url, downloadType))
        socketManager.sendMessage(request)

        return false;
    });

    // single media
    socket.on(MediaInfo_response.Message, function (msg) {

        var table = document.getElementById("media_info");
        var mediaInfo_response = new MediaInfo_response(msg)
        if (mediaInfo_response.isError()) {
            var downloadLink = document.getElementById("downloadLink");
            downloadLink.innerHTML = mediaInfo_response.getError();
            return;
        }
        var mediaInfo = mediaInfo_response.getData()

        var mediaInfoHtml = mediaInfo.artist + " - " + mediaInfo.title + "\n";
        var row = table.insertRow();
        var cell1 = row.insertCell();
        cell1.innerHTML = mediaInfoHtml;
        var cell2 = row.insertCell();
        cell2.innerHTML = " ";
    });

    // playlist
    socket.on(PlaylistInfo_response.Message, function (msg) {
        var playlistInfo_response = new PlaylistInfo_response(msg)
        var table = document.getElementById("media_info");
        if (playlistInfo_response.isError())
        {
            var downloadLink = document.getElementById("downloadLink");
            downloadLink.innerHTML = playlistInfo_response.getError();
        }
        else
        {
            var playlistInfo = ""
            var playlistInfoData = playlistInfo_response.getData()
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
        var playlistMediaInfo_response = new PlaylistMediaInfo_response(msg)
        if (playlistMediaInfo_response.isError())
        {
            return
        }

        var data = playlistMediaInfo_response.getData()
        var index = data.playlistIndex
        downloadResult.push(data.filename);
        var row = table.rows[index-1];
        row.deleteCell(1);
        var cell = row.insertCell(1);
        cell.innerHTML = '<a href="/download/' + data.hash + '">V</a>';
        //cell.innerHTML = '<a href="/download/' + data.hash + '">V</a?>';
    });

    // a both
    socket.on(DownloadMedia_finish.Message, function (msg) {
        // stop spinner
        var loader = document.getElementById("spinner");
        loader.style.display = 'none';
        var downloadMedia_Finish = new DownloadMedia_finish(msg)
        if (downloadMedia_Finish.isError()){
            var downloadLink = document.getElementById("downloadLink");
            downloadLink.innerHTML = downloadMedia_Finish.getError();
            var button = document.getElementById("btnFetch")
            button.disabled = false;
            return
        }
        var hash = downloadMedia_Finish.getData()
        var downloadLink = document.getElementById('downloadLink');
        downloadLink.innerHTML = '<a href="/download/' + hash + '">Download file</a>';
        //downloadLink.innerHTML = '<a href="/download/' + hash + '">Download file</a>';
    });

});