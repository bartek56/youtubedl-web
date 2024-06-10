from typing import List
from youtubedlWeb import create_app, socketio
import unittest
import unittest.mock as mock
from unittest.mock import MagicMock

from youtubedlWeb.Common.SocketMessages import PlaylistInfo_response, PlaylistInfo, MediaFromPlaylist, DownloadMediaFromPlaylist_start
from youtubedlWeb.Common.SocketMessages import DownloadMediaFromPlaylist_finish, DownloadPlaylists_finish, PlaylistMediaInfo, MediaInfo
from youtubedlWeb.Common.SocketRequests import DownloadMediaRequest, DownloadPlaylistsRequest
from youtubedlWeb.Common.YoutubeManager import PlaylistConfig, ResultOfDownload, YoutubeManager, YoutubeConfig, AudioData

#from Common.YoutubeManager import YoutubeManager, YoutubeConfig, ResultOfDownload, PlaylistConfig
import youtubedlWeb.Common.YoutubeManager as YTManager
import youtubedlWeb.Common.SocketMessages as SocketMessages

class FlaskToolsForUT:
    playlistUrl = "https://www.youtube.com/playlist?list=PL6uhlddQJkfh4YsbxgPE70a6KeFOCDgG_"

    playlistsPath = "/home/music/youtube playlists"

    playlist1Name = "playlist1"
    playlist2Name = "playlist2"
    playlist3Name = "playlist3"
    playlist1Link = "https://www.youtube.com/playlist?list=PL111111111"
    playlist2Link = "https://www.youtube.com/playlist?list=PL222222222"
    playlist3Link = "https://www.youtube.com/playlist?list=PL333333333"
    playlistsConfiguration = [PlaylistConfig(playlist1Name,playlist1Link),
                              PlaylistConfig(playlist2Name,playlist2Link)]

    songTitle1FromPlaylist = "song1"
    songTitle2FromPlaylist = "song2"
    songTitle3FromPlaylist = "song3"
    songArtist1FromPlaylist = "artist1"
    songArtist2FromPlaylist = "artist2"
    songArtist3FromPlaylist = "artist3"
    songAlbum1FromPlaylist = "album1"
    songAlbum2FromPlaylist = "album2"
    songAlbum3FromPlaylist = "album3"

    songTitleAndArtist1FromPlaylist = songArtist1FromPlaylist +" - "+ songTitle1FromPlaylist
    songTitleAndArtist2FromPlaylist = songArtist2FromPlaylist +" - "+ songTitle2FromPlaylist
    songTitleAndArtist3FromPlaylist = songArtist3FromPlaylist +" - "+ songTitle3FromPlaylist

    songTitleAndArtist1FromPlaylistFilename = songTitleAndArtist1FromPlaylist + ".mp3"
    songTitleAndArtist2FromPlaylistFilename = songTitleAndArtist2FromPlaylist + ".mp3"
    songTitleAndArtist3FromPlaylistFilename = songTitleAndArtist3FromPlaylist + ".mp3"

    url1FromPlaylist = "https:/www.youtube.com/watch?v=11111"
    url2FromPlaylist = "https:/www.youtube.com/watch?v=22222"
    url3FromPlaylist = "https:/www.youtube.com/watch?v=33333"

    hash1FromPlaylist = "11111"
    hash2FromPlaylist = "22222"
    hash3FromPlaylist = "33333"

    index1FromPlaylist = "1"
    index2FromPlaylist = "2"
    index3FromPlaylist = "3"

    def getDataFromMessage(self, message, index):
        self.assertTrue(len(message) >= index)
        self.assertIn("data", message[index]["args"][0])
        return message[index]["args"][0]["data"]

    def getNameOfMessage(self, message, index):
        self.assertTrue(len(message) >= index)
        self.assertIn("name", message[index])
        return message[index]["name"]

class FlaskQuickDownload(unittest.TestCase, FlaskToolsForUT):
    randomString = "ABCDEFGHI"
    randomString1 = "AAAAAAAA"
    randomString2 = "BBBBBBBB"
    randomString3 = "CCCCCCCC"
    empty = " "
    title = "test_title"
    artist = "test_artist"
    album = "test_album"
    extMp3 = "mp3"
    extMp4 = "mp4"
    path = "/tmp/" + title+".mp3"
    downloadDir = "/home/music"
    url = "https://www.youtube.com/watch?v=1Pl-FT0VCNs"

    playlistsPath = "/home/music/youtube playlists"
    playlistName = "playlistNameTest"

    def __init__(self, *args, **kwargs):
        super(FlaskQuickDownload, self).__init__(*args, **kwargs)

    def setUp(self):
        self.mainApp = create_app(True)
        self.app = self.mainApp.test_client()
        self.socketio_test_client = socketio.test_client(self.mainApp)
        self.mailManager = self.mainApp.mailManager
        self.ytManager = self.mainApp.youtubeManager
        self.ytConfig = self.mainApp.youtubeConfig

    def checkGetPlaylistInfo_response(self, playlistInfoData, expectedPlaylistName, expectedMediaFromPlaylist:List[MediaFromPlaylist]):
        self.assertEqual(playlistInfoData[0], expectedPlaylistName)
        index = 0
        for playlist in expectedMediaFromPlaylist:
            self.assertEqual(playlistInfoData[1][index]["playlist_index"], playlist.playlistIndex)
            self.assertEqual(playlistInfoData[1][index]['url'], playlist.url)
            self.assertEqual(playlistInfoData[1][index]['title'], playlist.title)
            index = index + 1

    def checkMediaInfo_response(self, data, expectedMediaInfo:MediaInfo):
        self.assertEqual(data["title"], expectedMediaInfo.title)
        self.assertEqual(data["artist"], expectedMediaInfo.artist)

    def checkPlaylistMediaInfo_response(self, data, expectedPlaylistMediaInfo:PlaylistMediaInfo):
        self.assertEqual(data["playlist_index"], expectedPlaylistMediaInfo.playlistIndex)
        self.assertEqual(data["filename"], expectedPlaylistMediaInfo.filename)
        self.assertEqual(data["hash"], expectedPlaylistMediaInfo.hash)


    @mock.patch.object(YoutubeManager, 'download_mp3')
    @mock.patch.object(YoutubeManager, 'getMediaInfo')
    @mock.patch('youtubedlWeb.Common.WebUtils.getRandomString')
    def test_downloadMp3(self, mock_getRandomString:MagicMock, mock_getMediaInfo:MagicMock, mock_downloadMp3:MagicMock):
        mock_getMediaInfo.configure_mock(return_value=ResultOfDownload(YTManager.MediaInfo(self.title,self.artist,self.album,self.url)))
        mock_downloadMp3.configure_mock(return_value=ResultOfDownload(YTManager.AudioData(self.path, self.title, self.artist, self.album)))
        mock_getRandomString.configure_mock(return_value=self.randomString)

        self.socketio_test_client.emit(DownloadMediaRequest.message, {"link":self.url, "type":self.extMp3})

        mock_downloadMp3.assert_called_once_with(self.url)
        mock_getMediaInfo.assert_called_once_with(self.url)
        mock_getRandomString.assert_called_once()


        received = self.socketio_test_client.get_received()


        self.assertEqual(len(received), 2)

        self.assertEqual(self.getNameOfMessage(received, 0), SocketMessages.MediaInfo_response().message)
        self.checkMediaInfo_response(self.getDataFromMessage(received, 0), MediaInfo(self.title, self.artist))

        self.assertEqual(self.getNameOfMessage(received, 1), SocketMessages.DownloadMedia_finish().message)
        self.assertEqual(self.getDataFromMessage(received, 1), self.randomString)


    @mock.patch.object(YoutubeManager, 'download_mp3')
    @mock.patch.object(YoutubeManager, 'getPlaylistInfo')
    @mock.patch('youtubedlWeb.Common.WebUtils.getRandomString')
    @mock.patch('youtubedlWeb.Common.WebUtils.compressToZip')
    def test_downloadMp3Playlist(self, mock_zip:MagicMock, mock_getRandomString:MagicMock, mock_getPlaylistInfo:MagicMock, mock_downloadMp3:MagicMock):
        mock_getPlaylistInfo.configure_mock(return_value = ResultOfDownload(
            YTManager.PlaylistInfo(self.playlistName,
                                   [YTManager.MediaFromPlaylist(self.index1FromPlaylist, self.url1FromPlaylist, self.songTitle1FromPlaylist),
                                    YTManager.MediaFromPlaylist(self.index2FromPlaylist, self.url2FromPlaylist, self.songTitle2FromPlaylist),
                                    YTManager.MediaFromPlaylist(self.index3FromPlaylist, self.url3FromPlaylist, self.songTitle3FromPlaylist)])))
        mock_downloadMp3.configure_mock(side_effect=[ResultOfDownload(YTManager.AudioData(self.downloadDir+'/'+self.songTitle1FromPlaylist+'.'+self.extMp3, self.songTitle1FromPlaylist, self.songArtist1FromPlaylist, self.songAlbum1FromPlaylist)),
                                                     ResultOfDownload(YTManager.AudioData(self.downloadDir+'/'+self.songTitle2FromPlaylist+'.'+self.extMp3, self.songTitle2FromPlaylist, self.songArtist2FromPlaylist, self.songAlbum2FromPlaylist)),
                                                     ResultOfDownload(YTManager.AudioData(self.downloadDir+'/'+self.songTitle3FromPlaylist+'.'+self.extMp3, self.songTitle3FromPlaylist, self.songArtist3FromPlaylist, self.songAlbum3FromPlaylist))])
        mock_getRandomString.configure_mock(side_effect=[self.randomString1, self.randomString2, self.randomString3, self.randomString])

        # --------------------------------------------------------------------------------------------
        self.socketio_test_client.emit(DownloadMediaRequest.message, {"link":self.playlistUrl, "type":self.extMp3})
        # --------------------------------------------------------------------------------------------

        mock_getPlaylistInfo.assert_called_once_with(self.playlistUrl)
        mock_downloadMp3.assert_has_calls([mock.call(self.url1FromPlaylist),
                                           mock.call(self.url2FromPlaylist),
                                           mock.call(self.url3FromPlaylist)])
        self.assertEqual(mock_getRandomString.call_count, 4)
        mock_zip.assert_called_once_with([self.downloadDir+'/'+self.songTitle1FromPlaylist+'.'+self.extMp3,
                                          self.downloadDir+'/'+self.songTitle2FromPlaylist+'.'+self.extMp3,
                                          self.downloadDir+'/'+self.songTitle3FromPlaylist+'.'+self.extMp3], self.playlistName)

        received = self.socketio_test_client.get_received()
        self.assertEqual(len(received), 5)

        # getPlaylistInfo_response
        self.assertEqual(self.getNameOfMessage(received, 0), PlaylistInfo_response().message)
        self.checkGetPlaylistInfo_response(self.getDataFromMessage(received, 0), self.playlistName,
                                           [MediaFromPlaylist(self.index1FromPlaylist, self.url1FromPlaylist, self.songTitle1FromPlaylist),
                                            MediaFromPlaylist(self.index2FromPlaylist, self.url2FromPlaylist, self.songTitle2FromPlaylist),
                                            MediaFromPlaylist(self.index3FromPlaylist, self.url3FromPlaylist, self.songTitle3FromPlaylist)])

        # getPlaylistMediaInfo_response - three songs
        expectedData = [SocketMessages.PlaylistMediaInfo(self.index1FromPlaylist, self.songTitle1FromPlaylist+"."+self.extMp3, self.randomString1),
                        SocketMessages.PlaylistMediaInfo(self.index2FromPlaylist, self.songTitle2FromPlaylist+"."+self.extMp3, self.randomString2),
                        SocketMessages.PlaylistMediaInfo(self.index3FromPlaylist, self.songTitle3FromPlaylist+"."+self.extMp3, self.randomString3)]
        for x in range(3):
            self.assertEqual(self.getNameOfMessage(received, x+1), SocketMessages.PlaylistMediaInfo_response().message)
            self.checkPlaylistMediaInfo_response(self.getDataFromMessage(received, x+1), expectedData[x])

        # DwonloadMedia_finish
        self.assertEqual(self.getNameOfMessage(received, 4), SocketMessages.DownloadMedia_finish().message)
        self.assertEqual(self.getDataFromMessage(received, 4), self.randomString)


    @mock.patch.object(YoutubeManager, 'download_720p')
    @mock.patch.object(YoutubeManager, 'getMediaInfo')
    @mock.patch('youtubedlWeb.Common.WebUtils.getRandomString')
    def test_download720p(self, mock_randomString:MagicMock, mock_getMediaInfo:MagicMock, mock_download720p:MagicMock):
        mock_download720p.configure_mock(return_value=ResultOfDownload(YTManager.VideoData(self.downloadDir+"/"+self.title+"."+self.extMp4, self.title)))
        mock_getMediaInfo.configure_mock(return_value=ResultOfDownload(YTManager.MediaInfo(self.title, self.artist, self.album, self.url)))
        mock_randomString.configure_mock(return_value=self.randomString)

        # -----------------------------------------------------------------------------------------------------------
        self.socketio_test_client.emit(DownloadMediaRequest.message, {"link":self.url, "type":"720p"})
        # -----------------------------------------------------------------------------------------------------------

        mock_download720p.assert_called_once_with(self.url)
        mock_getMediaInfo.assert_called_once_with(self.url)


        received = self.socketio_test_client.get_received()


        self.assertEqual(len(received), 2)

        # getMediaInfo_response
        self.assertEqual(self.getNameOfMessage(received, 0), SocketMessages.MediaInfo_response().message)
        self.checkMediaInfo_response(self.getDataFromMessage(received, 0), MediaInfo(self.title, self.artist))

        # DownloadMedia_finish
        self.assertEqual(self.getNameOfMessage(received, 1), SocketMessages.DownloadMedia_finish().message)
        self.assertEqual(self.getDataFromMessage(received, 1), self.randomString)

class FlaskQuickDownloadPlaylists(unittest.TestCase, FlaskToolsForUT):

    def __init__(self, *args, **kwargs):
        super(FlaskQuickDownloadPlaylists, self).__init__(*args, **kwargs)

    def setUp(self):
        self.mainApp = create_app(True)
        self.app = self.mainApp.test_client()
        self.socketio_test_client = socketio.test_client(self.mainApp)
        self.mailManager = self.mainApp.mailManager
        self.ytManager = self.mainApp.youtubeManager
        self.ytConfig = self.mainApp.youtubeConfig

    def checkGetPlaylistInfo_response(self, playlistInfoData, expectedPlaylistName, expectedMediaFromPlaylist:List[MediaFromPlaylist]):
        self.assertEqual(playlistInfoData[0], expectedPlaylistName)
        index = 0
        for playlist in expectedMediaFromPlaylist:
            self.assertEqual(playlistInfoData[1][index]["playlist_index"], playlist.playlistIndex)
            self.assertEqual(playlistInfoData[1][index]['url'], playlist.url)
            self.assertEqual(playlistInfoData[1][index]['title'], playlist.title)
            index = index + 1

    def checkDownloadMediaFromPlaylist_start(self, data, expectedPlaylistMediaInfo:PlaylistMediaInfo):
        self.assertEqual(data["playlist_index"], expectedPlaylistMediaInfo.playlistIndex)
        self.assertEqual(data["filename"], expectedPlaylistMediaInfo.filename)
        # TODO
        #self.assertEqual(data["hash"], expectedPlaylistMediaInfo.hash)

    def checkDownloadMediaFromPlaylist_finish(self, data, expectedPlaylistMediaInfo:PlaylistMediaInfo):
        self.assertEqual(data["playlist_index"], expectedPlaylistMediaInfo.playlistIndex)
        self.assertEqual(data["filename"], expectedPlaylistMediaInfo.filename)
        # TODO
        #self.assertEqual(data["hash"], expectedPlaylistMediaInfo.hash)


    @mock.patch.object(YoutubeManager, 'getPlaylistInfo')
    @mock.patch.object(YoutubeManager, 'createDirIfNotExist')
    @mock.patch.object(YoutubeManager, '_isMusicClipArchived')
    @mock.patch.object(YoutubeManager, '_download_mp3')
    @mock.patch.object(YoutubeManager, '_addMetadataToPlaylist')
    @mock.patch.object(YoutubeConfig, 'getPlaylists')
    @mock.patch.object(YoutubeConfig, 'getPath')
    def test_downloadTwoPlaylistsOneSongABoth(self,
                               mock_getPath:MagicMock, mock_getPlaylists:MagicMock,
                               mock_addMetadataToPlaylist:MagicMock, mock_downloadMp3:MagicMock,
                               mock_isMusicArchive:MagicMock, mock_createDirIfNotExist:MagicMock,
                               mock_getPlaylistInfo:MagicMock):
        mock_getPlaylists.configure_mock(return_value=self.playlistsConfiguration)
        mock_getPlaylistInfo.configure_mock(side_effect=[ResultOfDownload(PlaylistInfo(self.playlist1Name,
                                                                      [MediaFromPlaylist(0,self.url1FromPlaylist, self.songTitle1FromPlaylist)])),
                                                         ResultOfDownload(PlaylistInfo(self.playlist2Name,
                                                                      [MediaFromPlaylist(0,self.url2FromPlaylist, self.songTitle2FromPlaylist)]))])
        mock_isMusicArchive.configure_mock(return_value=False)
        mock_downloadMp3.configure_mock(side_effect=[
            ResultOfDownload(AudioData("11111",self.songTitle1FromPlaylist, self.hash1FromPlaylist, self.songArtist1FromPlaylist, self.songAlbum1FromPlaylist)),
            ResultOfDownload(AudioData("11111",self.songTitle2FromPlaylist, self.hash2FromPlaylist, self.songArtist2FromPlaylist, self.songAlbum2FromPlaylist))])
        mock_getPath.configure_mock(return_value=self.playlistsPath)
        mock_addMetadataToPlaylist.configure_mock(side_effect=[self.songTitleAndArtist1FromPlaylistFilename, self.songTitleAndArtist2FromPlaylistFilename])

        self.socketio_test_client.emit(DownloadPlaylistsRequest.message, '')


        mock_getPath.assert_called_once()
        mock_getPlaylists.assert_called_once()

        mock_addMetadataToPlaylist.assert_has_calls([mock.call(self.playlistsPath, 0, self.playlist1Name, self.songArtist1FromPlaylist, self.songAlbum1FromPlaylist, self.songTitle1FromPlaylist, self.hash1FromPlaylist),
                                                     mock.call(self.playlistsPath, 0, self.playlist2Name, self.songArtist2FromPlaylist, self.songAlbum2FromPlaylist, self.songTitle2FromPlaylist, self.hash2FromPlaylist)])
        mock_downloadMp3.assert_has_calls([mock.call(self.url1FromPlaylist, self.playlistsPath+"/"+self.playlist1Name),
                                           mock.call(self.url2FromPlaylist, self.playlistsPath+"/"+self.playlist2Name)])
        mock_isMusicArchive.assert_has_calls([mock.call(self.playlistsPath+"/"+self.playlist1Name, self.url1FromPlaylist),
                                              mock.call(self.playlistsPath+"/"+self.playlist2Name, self.url2FromPlaylist)])
        mock_createDirIfNotExist.assert_has_calls([mock.call(self.playlistsPath+"/"+self.playlist1Name),
                                                   mock.call(self.playlistsPath+"/"+self.playlist2Name)])
        mock_getPlaylistInfo.assert_has_calls([mock.call(self.playlist1Link),
                                               mock.call(self.playlist2Link)])
        #TODO check session variables


        received = self.socketio_test_client.get_received()
        self.assertEqual(len(received), 7)


        # -------------- playlist 1 ----------------
        # ------------ getPlaylistInfo_response --------------
        self.assertEqual(self.getNameOfMessage(received, 0), PlaylistInfo_response.message)
        self.checkGetPlaylistInfo_response(self.getDataFromMessage(received, 0), self.playlist1Name,
                                           [MediaFromPlaylist(0, self.url1FromPlaylist, self.songTitle1FromPlaylist)])

        # ------------ downloadMediaFromPlaylist_start --------------
        self.assertEqual(self.getNameOfMessage(received, 1), DownloadMediaFromPlaylist_start.message)
        self.checkDownloadMediaFromPlaylist_start(self.getDataFromMessage(received, 1),
                                                  PlaylistMediaInfo(0, self.songTitle1FromPlaylist, self.hash1FromPlaylist))

        # ------------ downloadMediaFromPlaylist_finish --------------
        self.assertEqual(self.getNameOfMessage(received, 2), DownloadMediaFromPlaylist_finish.message)
        self.checkDownloadMediaFromPlaylist_finish(self.getDataFromMessage(received, 2),
                                                   PlaylistMediaInfo(0, self.songTitleAndArtist1FromPlaylist, self.hash1FromPlaylist))

        # -------------- playlist 2 ----------------
        # ------------ getPlaylistInfo_response --------------
        self.assertEqual(self.getNameOfMessage(received, 3), PlaylistInfo_response.message)
        self.checkGetPlaylistInfo_response(self.getDataFromMessage(received, 3), self.playlist2Name,
                                           [MediaFromPlaylist(0,self.url2FromPlaylist, self.songTitle2FromPlaylist)])

        # ------------ downloadMediaFromPlaylist_start --------------
        self.assertEqual(self.getNameOfMessage(received, 4), DownloadMediaFromPlaylist_start.message)
        self.checkDownloadMediaFromPlaylist_start(self.getDataFromMessage(received, 4),
                                                  PlaylistMediaInfo(0,self.songTitle2FromPlaylist, self.hash2FromPlaylist))

        # ------------ downloadMediaFromPlaylist_finish --------------
        self.assertEqual(self.getNameOfMessage(received, 5), DownloadMediaFromPlaylist_finish.message)
        self.checkDownloadMediaFromPlaylist_finish(self.getDataFromMessage(received, 5),
                                                   PlaylistMediaInfo(0,self.songTitleAndArtist2FromPlaylist, self.hash2FromPlaylist))

        # ------------ downloadPlaylist_finish ---------------------
        self.assertEqual(self.getNameOfMessage(received, 6), DownloadPlaylists_finish.message)
        self.assertEqual(self.getDataFromMessage(received, 6), 2)

class FlaskClientConfigurePlaylists(unittest.TestCase):
    checked="checked"
    unchecked="unchecked"
    empty=""

    playlistnameToRemove = "playlist_to_remove"
    playlistname1 = "playlist1"
    playlistname2 = "playlist2"
    successfullRemovedPlaylistMsg = b'Sucesssful removed playlist'
    failedRemovedPlaylistMsg = b'Failed to remove Youtube playlist:'
    mediaserverTitle = b'<title>Media Server</title>'
    statusCodeSuccess = 200

    def __init__(self, *args, **kwargs):
        super(FlaskClientConfigurePlaylists, self).__init__(*args, **kwargs)

    def setUp(self):
        self.mainApp = create_app(True)
        self.app = self.mainApp.test_client()

    @mock.patch.object(YoutubeConfig, 'removePlaylist')
    @mock.patch.object(YoutubeConfig, 'getPlaylistsName')
    def test_remove_playlist(self, mock_getPlaylistsName:MagicMock, mock_removePlaylist:MagicMock):
        mock_removePlaylist.configure_mock(return_value=True)
        mock_getPlaylistsName.configure_mock(return_value=[self.playlistname1, self.playlistname1])

        rv = self.app.post('/playlists', data=dict(remove=True, playlists=self.playlistnameToRemove), follow_redirects=True)

        mock_removePlaylist.assert_called_once_with(self.playlistnameToRemove)
        mock_getPlaylistsName.assert_called_once()
        self.assertEqual(rv.status_code, self.statusCodeSuccess)

        assert self.successfullRemovedPlaylistMsg in rv.data
        assert self.mediaserverTitle in rv.data

    @mock.patch.object(YoutubeConfig, 'removePlaylist')
    @mock.patch.object(YoutubeConfig, 'getPlaylistsName')
    def test_remove_playlist2(self, mock_getPlaylistsName:MagicMock, mock_removePlaylist:MagicMock):
        mock_removePlaylist.configure_mock(return_value=True)
        mock_getPlaylistsName.configure_mock(return_value=[self.playlistname1, self.playlistname1])

        rv = self.app.post('/playlists', data=dict(remove=True, playlists=self.playlistnameToRemove), follow_redirects=True)

        mock_removePlaylist.assert_called_once_with(self.playlistnameToRemove)
        mock_getPlaylistsName.assert_called_once()
        self.assertEqual(rv.status_code, self.statusCodeSuccess)

        assert self.successfullRemovedPlaylistMsg in rv.data
        assert self.mediaserverTitle in rv.data

    @mock.patch.object(YoutubeConfig, 'removePlaylist')
    @mock.patch.object(YoutubeConfig, 'getPlaylistsName')
    def test_remove_playlist_failed(self, mock_getPlaylistsName:MagicMock, mock_removePlaylist:MagicMock):
        mock_removePlaylist.configure_mock(return_value=False)

        rv = self.app.post('/playlists', data=dict(remove=True, playlists=self.playlistnameToRemove), follow_redirects=True)

        mock_removePlaylist.assert_called_once_with(self.playlistnameToRemove)
        mock_getPlaylistsName.assert_not_called()
        self.assertEqual(rv.status_code, self.statusCodeSuccess)

        assert self.failedRemovedPlaylistMsg in rv.data
        assert self.mediaserverTitle in rv.data

if __name__ == '__main__':
    unittest.main()