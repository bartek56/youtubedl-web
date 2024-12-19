import unittest
import unittest.mock as mock
from unittest.mock import MagicMock
from youtubedlWeb.Common.YoutubeManager import YoutubeManager, MediaServerDownloader
from youtubedlWeb.Common.YoutubeConfig import YoutubeConfig
from youtubedlWeb.Common.YoutubeTypes import PlaylistInfo, MediaFromPlaylist, MediaInfo, AudioData, VideoData, ResultOfDownload
from configparser import ConfigParser
import yt_dlp
from yt_dlp import utils
import metadata_mp3
from metadata_mp3 import Mp3Info
import logging

class YouTubeManagerDlTestCase(unittest.TestCase):
    musicPath = "/media/music"
    videoPath = "/media/video"

    empty  = ""

    exceptionMessage = "failed download"
    exceptionErrorExpected = "download failed: "+exceptionMessage

    ytLink      = "https://www.youtube.com/watch?v=yqq3p-brlyc"
    ytMediaHash = "yqq3p-brlyc"
    ytDomain = "https://youtu.be/"

    artist = "artist_test"
    title  = "title_test"
    titleLong = "title_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test test_test_test_test_test_test_test_test_test_test_test_test_test"
    titleLongExpected = "title_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test_test"
    album  = "album_test"
    playlistName = "test_playlist"
    hash = "abcdefgh"
    website = ytDomain + hash

    foundMp3File = musicPath+title+".mp3"

    ytMp3ArchiveFilename = "songsArchive.txt"

    ytPlaylistInfoResponse2 = {"title": "testPlaylist","entries":[{"playlist_name":"testPlaylist", "playlist_index":"1", "url":"https://www.youtube.com/watch?v=1111", "title":"firstTitle"},
                                                                     {"playlist_name":"testPlaylist", "playlist_index":"2", "url":"https://www.youtube.com/watch?v=2222", "title":"secondTitle"}]}
    ytMediaInfoResponse = {"original_url":ytLink, "title":"firstTitle", "title":"testTitle", "artist":"testArtist", "album":"testAlbum"}
    ytMp3DownloadResponse ={"title":title, "artist":artist, "album":album, "id":hash}
    ytMp3LongTitleDownloadResponse ={"title":titleLong, "artist":artist, "album":album, "id":hash}
    ytMp3LongTitleDownloadResponseExpected ={"title":titleLongExpected, "artist":artist, "album":album, "id":hash}

    ytMp3DownloadWithoutArtistResponse = {"title":title, "artist":empty, "album":album, "id":hash}
    ytEmptyPlaylist = {"title": playlistName, "entries":[{}, None]}

    numberOfSongs = 4
    playlistIndex1 = 1
    firstTitle     = "first_title"
    firstArtist    = "first_artist"
    firstAlbum     = "first_album"
    firstAlbumArtist = "first_album_artist"
    firstUrl = "https://www.youtube.com/watch?v=1111"
    firstHash = "1111"
    firstWebsite = ytDomain+firstHash

    playlistIndex2 = 2
    secondTitle    = "second_title"
    secondArtist   = "second_artist"
    secondAlbum    = "second_album"
    secondAlbumArtist = "second_album_artist"
    secondUrl = "https://www.youtube.com/watch?v=2222"
    secondHash = "2222"
    secondWebsite = ytDomain+secondHash

    playlistIndex3 = 3
    thirdTitle    = "third_title"
    thirdArtist   = "third_artist"
    thirdAlbum    = "third_album"
    thirdAlbumArtist = "third_album_artist"
    thirdUrl = "https://www.youtube.com/watch?v=3333"
    thirdHash = "3333"
    thirdWebsite = ytDomain+thirdHash

    playlistIndex4 = 4
    fourthTitle    = "fourth_title"
    fourthArtist   = "fourth_artist"
    fourthAlbum    = "fourth_album"
    fourthAlbumArtist = "third_album_artist"
    fourthUrl = "https://www.youtube.com/watch?v=4444"
    fourthHash = "4444"
    fourthWebsite = ytDomain+fourthHash

    ytDownloadMp3Response1 = {"title":firstTitle, "artist":firstArtist, "album":firstAlbum, "id":firstHash}
    ytDownloadMp3Response2 = {"title":secondTitle, "artist":secondArtist, "album":secondAlbum, "id":secondHash}
    ytDownloadMp3Response3 = {"title":thirdTitle, "artist":thirdArtist, "album":thirdAlbum, "id":thirdHash}
    ytDownloadMp3Response4 = {"title":fourthTitle, "artist":fourthArtist, "album":fourthAlbum, "id":fourthHash}

    ytPlaylistInfoResponse4 = {"title": playlistName,"entries":[{"playlist_name":playlistName, "playlist_index":playlistIndex1, "url":firstUrl, "title":firstTitle},
                                                                {"playlist_name":playlistName, "playlist_index":playlistIndex2, "url":secondUrl, "title":secondTitle},
                                                                {"playlist_name":playlistName, "playlist_index":playlistIndex3, "url":thirdUrl, "title":thirdTitle},
                                                                {"playlist_name":playlistName, "playlist_index":playlistIndex4, "url":fourthUrl, "title":fourthTitle}
                                                                ]}

    ytPlaylistInfoResponse3 = {"title": playlistName,"entries":[{"playlist_name":playlistName, "playlist_index":playlistIndex2, "url":secondUrl, "title":secondTitle},
                                                                {"playlist_name":playlistName, "playlist_index":playlistIndex3, "url":thirdUrl, "title":thirdTitle},
                                                                {"playlist_name":playlistName, "playlist_index":playlistIndex4, "url":fourthUrl, "title":fourthTitle}
                                                                ]}
    ytMediaFromPLaylist1 = MediaFromPlaylist(playlistIndex1, firstUrl, firstTitle)
    ytMediaFromPLaylist2 = MediaFromPlaylist(playlistIndex2, secondUrl, secondTitle)
    ytMediaFromPLaylist3 = MediaFromPlaylist(playlistIndex3, thirdUrl, thirdTitle)
    ytMediaFromPLaylist4 = MediaFromPlaylist(playlistIndex4, fourthUrl, fourthTitle)

    ytDownloadMp3PlaylistResponse = {"entries":[
            {'playlist_index': playlistIndex1,"title":firstTitle,  "artist":firstArtist, "album":firstAlbum, "id":firstHash},
            {'playlist_index': playlistIndex2,"title":secondTitle, "album":secondAlbum, "id":secondHash},
            {'playlist_index': playlistIndex3,"title":thirdTitle,  "artist":thirdArtist, "album":thirdAlbum, "id":thirdHash},
            {'playlist_index': playlistIndex4,"title":fourthTitle, "artist":fourthArtist, "album":fourthAlbum, "id":fourthHash}]}

    extMp4 = "mp4"
    resolution360p = "360p"
    resolution720p = "720p"
    resolution4k   = "4k"
    ytDownloadVideoResponse={"title":title, "artist":artist, "ext":extMp4}

    actualDate = "2020-05-05"
    numberOfArchiveSongs = 5

    mp3InfoTrack1 = Mp3Info(str(firstArtist + " - " + firstTitle+".mp3"), firstTitle, firstArtist, firstAlbum, firstAlbumArtist, str(playlistIndex1), firstWebsite, actualDate)
    mp3InfoTrack2 = Mp3Info(str(secondArtist + " - " + secondTitle+".mp3"), secondTitle, secondArtist, secondAlbum, secondAlbumArtist, str(playlistIndex2), secondWebsite, actualDate)
    mp3InfoTrack3 = Mp3Info(str(thirdArtist + " - " + thirdTitle+".mp3"), thirdTitle, thirdArtist, thirdAlbum, thirdAlbumArtist, str(playlistIndex3), thirdWebsite, actualDate)
    mp3InfoTrack4 = Mp3Info(str(fourthArtist + " - " + fourthTitle+".mp3"), fourthTitle, fourthArtist, fourthAlbum, fourthAlbumArtist, str(playlistIndex4), fourthWebsite, actualDate)
    listOfMp3Info4 = [mp3InfoTrack1, mp3InfoTrack2, mp3InfoTrack3, mp3InfoTrack4]

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.ytManager = YoutubeManager(videoPath=self.videoPath, musicPath=self.musicPath, mp3ArchiveFilename=self.ytMp3ArchiveFilename)
        self.ytManager.createDirIfNotExist = mock.MagicMock()
        self.ytManager.openFile = mock.MagicMock()
        self.ytManager.lookingForFile = mock.MagicMock()
        self.ytManager._isMusicClipArchived = mock.MagicMock()
        self.ytManager._isMusicClipArchived.configure_mock(return_value=False)
        self.ytManager._getNumberOfDownloadedSongs = mock.MagicMock()
        self.ytManager._getActualDate = mock.MagicMock()
        self.ytManager._getActualDate.configure_mock(return_value=self.actualDate)
        self.ytManager._getNumberOfDownloadedSongs.configure_mock(return_value=self.numberOfArchiveSongs)
        self.ytManager._getSongsOfDir = mock.MagicMock()

    def checkPlaylist(self, playlist:PlaylistInfo, ytResponse):
        playlistName = ytResponse['title']
        expectedList = ytResponse['entries']

        self.assertEqual(playlist.playlistName, playlistName)
        self.assertEqual(len(playlist.listOfMedia), len(expectedList))

        list = playlist.listOfMedia

        for indexOfList in range(len(expectedList)):
            media:MediaFromPlaylist
            media = list[indexOfList]
            self.assertEqual(playlistName, expectedList[indexOfList]["playlist_name"])
            self.assertEqual(media.playlistIndex, int(expectedList[indexOfList]["playlist_index"]))
            self.assertEqual(media.title, expectedList[indexOfList]["title"])
            self.assertEqual(media.url, expectedList[indexOfList]["url"])

    def checkMediaInfo(self, mediaInfo:MediaInfo, ytResponse):
        self.assertEqual(mediaInfo.url, ytResponse["original_url"])
        self.assertEqual(mediaInfo.title, ytResponse["title"])
        self.assertEqual(mediaInfo.artist, ytResponse["artist"])
        self.assertEqual(mediaInfo.album, ytResponse["album"])

    def checkAudioData(self, audioData:AudioData, ytResponse):
        self.assertEqual(audioData.title, ytResponse["title"])
        if(len(ytResponse["artist"])>0):
            self.assertEqual(audioData.artist, ytResponse["artist"])
            fileName = self.musicPath+audioData.artist + " - " + audioData.title + ".mp3"
        else:
            self.assertEqual(audioData.artist, self.empty)
            self.assertEqual(ytResponse["artist"], "")
            fileName = self.musicPath+audioData.title + ".mp3"

        if(len(ytResponse["album"])>0):
            self.assertEqual(audioData.album, ytResponse["album"])
        else:
            self.assertEqual(audioData.album, None)
            self.assertEqual(ytResponse["album"], self.empty)

    def assertMp3Info(self, actual:Mp3Info, expected:Mp3Info):
        self.assertEqual(actual.fileName, expected.fileName)
        self.assertEqual(actual.title, expected.title)
        self.assertEqual(actual.artist, expected.artist)
        self.assertEqual(actual.albumArtist, expected.albumArtist)
        self.assertEqual(actual.album, expected.album)
        self.assertEqual(actual.trackNumber, expected.trackNumber)
        self.assertEqual(actual.website, expected.website)
        self.assertEqual(actual.date, expected.date)

    def assertMediaFromPlaylist(self, actual:MediaFromPlaylist, expected:MediaFromPlaylist):
        self.assertEqual(actual.playlistIndex, expected.playlistIndex)
        self.assertEqual(actual.title, expected.title)
        self.assertEqual(actual.url , expected.url)

    def assertMediaFromPlaylistAndMp3Info(self, mediaFromPlaylist:MediaFromPlaylist, mp3Info:Mp3Info):
        self.assertEqual(mediaFromPlaylist.title, mp3Info.title)
        hashMp3Info = mp3Info.website.split("/")[-1]
        hashMediaFromPlaylist = mediaFromPlaylist.url.split("v=")[-1]
        self.assertEqual(hashMp3Info, hashMediaFromPlaylist)

    def checkVideoData(self, data:VideoData, ytResponse, videoResolution):
        self.assertEqual(data.title, ytResponse["title"])
        self.assertEqual(data.path, self.videoPath+"/"+ytResponse["title"]+"_"+videoResolution+"."+ytResponse["ext"])

    def test_getMediaHash1(self):
        hash = self.ytManager.getMediaHashFromLink("https://www.youtube.com/watch?v=Lr4x3sCH7l0&list=PL6uhlddQJkfh4YsbxgPE70a6KeFOCDgG")
        self.assertEqual(hash, "Lr4x3sCH7l0")

    def test_getMediaHash2(self):
        hash = self.ytManager.getMediaHashFromLink("https://www.youtube.com/watch?v=Lr4x3sCH7l0")
        self.assertEqual(hash, "Lr4x3sCH7l0")

    def test_getMediaHash3(self):
        hash = self.ytManager.getMediaHashFromLink("https://www.youtube.com/Lr4x3sCH7l0")
        self.assertIsNone(hash)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getPlaylistInfo(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=self.ytPlaylistInfoResponse2)

        result = self.ytManager.getPlaylistInfo(self.ytLink)

        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertTrue(result.IsSuccess())
        self.checkPlaylist(result.data(), self.ytPlaylistInfoResponse2)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getPlaylistInfoEmptyResult(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=None)

        result = self.ytManager.getPlaylistInfo(self.ytLink)

        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getPlaylistInfoEmptyEntries(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=self.ytEmptyPlaylist)

        result = self.ytManager.getPlaylistInfo(self.ytLink)

        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_getPlaylistInfoException(self, mock_extractInfo):
        result = self.ytManager.getPlaylistInfo(self.ytLink)

        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), self.exceptionErrorExpected)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getMediaInfo(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=self.ytMediaInfoResponse)

        result = self.ytManager.getMediaInfo(self.ytLink)
        mock_extractInfo.assert_called_once_with(self.ytLink, download=False)
        self.assertTrue(result.IsSuccess())
        self.checkMediaInfo(result.data(), self.ytMediaInfoResponse)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_getMediaInfoEmptyResult(self, mock_extractInfo):
        mock_extractInfo.configure_mock(return_value=None)

        result = self.ytManager.getMediaInfo(self.ytLink)

        mock_extractInfo.assert_has_calls([mock.call(self.ytLink, download=False)])
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_getMediaInfoException(self, mock_extractInfo):
        result = self.ytManager.getMediaInfo(self.ytLink)

        mock_extractInfo.assert_has_calls([mock.call(self.ytLink, download=False)])
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), "failed download")

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToSong")
    def test_downloadMP3(self, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadResponse)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        mock_metadata.assert_called_with(self.musicPath, self.album, self.artist, self.title, self.website, self.actualDate)
        self.assertTrue(result.IsSuccess())
        self.checkAudioData(result.data(), self.ytMp3DownloadResponse)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToSong", return_value=None)
    def test_downloadMP3_failedWithModyfiMetadata(self, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadResponse)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        mock_metadata.assert_called_with(self.musicPath, self.album, self.artist, self.title, self.website, self.actualDate)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToSong")
    def test_downloadMP3_without_artist(self, mock_metadata, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadWithoutArtistResponse)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        mock_metadata.assert_called_with(self.musicPath, self.album, self.empty, self.title, self.website, self.actualDate)
        self.assertTrue(result.IsSuccess())
        self.checkAudioData(result.data(), self.ytMp3DownloadWithoutArtistResponse)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_emptyReturn(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=None)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_downloadMP3Exception(self, mock_extract_info):
        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), self.exceptionErrorExpected)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_onlyMetadata(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadResponse)
        self.ytManager._isMusicClipArchived.configure_mock(return_value=True)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.ytManager.lookingForFile.assert_called_with(self.musicPath, self.title, self.artist)
        self.assertTrue(result.IsSuccess())
        data = result.data()
        self.checkAudioData(data, self.ytMp3DownloadResponse)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_downloadMP3_onlyMetadata_exception(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadResponse)
        self.ytManager._isMusicClipArchived.configure_mock(return_value=True)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), self.exceptionErrorExpected)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_downloadMP3_onlyMetadata_NoneResult(self, mock_extract_info):
        self.ytManager._isMusicClipArchived.configure_mock(return_value=True)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_onlyMetadata_FileNotFound(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3DownloadResponse)
        self.ytManager.lookingForFile.configure_mock(return_value=None)
        self.ytManager._isMusicClipArchived.configure_mock(return_value=True)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.ytManager.lookingForFile.assert_called_with(self.musicPath,self.title, self.artist)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3_onlyMetadata_VeryLongTitle(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytMp3LongTitleDownloadResponse)
        self.ytManager._isMusicClipArchived.configure_mock(return_value=True)

        result = self.ytManager.download_mp3(self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.ytManager.lookingForFile.assert_called_with(self.musicPath, self.titleLongExpected, self.artist)
        self.assertTrue(result.IsSuccess())
        data = result.data()
        self.checkAudioData(data, self.ytMp3LongTitleDownloadResponseExpected)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_checkPlaylistStatus(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytPlaylistInfoResponse4)
        self.ytManager._getSongsOfDir.configure_mock(return_value=self.listOfMp3Info4)

        localFilesMissed, ytSongsMissed = self.ytManager.checkPlaylistStatus(self.musicPath+"/"+self.playlistName, self.playlistName, self.ytLink)
        self.assertEqual(len(localFilesMissed), 0)
        self.assertEqual(len(ytSongsMissed), 0)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_checkPlaylistStatus_missedLocally(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytPlaylistInfoResponse4)
        self.ytManager._getSongsOfDir.configure_mock(return_value=[self.mp3InfoTrack2, self.mp3InfoTrack3, self.mp3InfoTrack4])

        localFilesMissed, ytSongsMissed = self.ytManager.checkPlaylistStatus(self.musicPath+"/"+self.playlistName, self.playlistName, self.ytLink)
        self.assertEqual(len(localFilesMissed), 0)
        self.assertEqual(len(ytSongsMissed), 1)

        self.assertMediaFromPlaylistAndMp3Info(ytSongsMissed[0], self.mp3InfoTrack1)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_checkPlaylistStatus_missedYt(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytPlaylistInfoResponse3)
        self.ytManager._getSongsOfDir.configure_mock(return_value=[self.mp3InfoTrack1, self.mp3InfoTrack2, self.mp3InfoTrack3, self.mp3InfoTrack4])

        localFilesMissed, ytSongsMissed = self.ytManager.checkPlaylistStatus(self.musicPath+"/"+self.playlistName, self.playlistName, self.ytLink)
        self.assertEqual(len(localFilesMissed), 1)
        self.assertEqual(len(ytSongsMissed), 0)

        self.assertMediaFromPlaylistAndMp3Info(self.ytMediaFromPLaylist1, localFilesMissed[0])

    @mock.patch.object(metadata_mp3.MetadataManager, "setMetadataMp3Info")
    def test_updateTrackNumber(self, mock_setMetadataMp3Info):
        self.ytManager._getSongsOfDir.configure_mock(return_value=[self.mp3InfoTrack1, self.mp3InfoTrack2])

        self.ytManager.updateTrackNumber(str(self.musicPath+"/"+self.playlistName),self.ytLink,True)

        mock_setMetadataMp3Info.assert_has_calls([mock.call(str(self.musicPath+"/"+self.playlistName+"/"+self.mp3InfoTrack1.fileName),self.mp3InfoTrack1),
                                                  mock.call(str(self.musicPath+"/"+self.playlistName+"/"+self.mp3InfoTrack2.fileName),self.mp3InfoTrack2)])

    @mock.patch.object(metadata_mp3.MetadataManager, "setMetadataMp3Info")
    def test_updateTrackNumber_reverse(self, mock_setMetadataMp3Info):
        self.ytManager._getSongsOfDir.configure_mock(return_value=[self.mp3InfoTrack2, self.mp3InfoTrack1])

        self.ytManager.updateTrackNumber(str(self.musicPath+"/"+self.playlistName),self.ytLink,True)

        mock_setMetadataMp3Info.assert_has_calls([mock.call(str(self.musicPath+"/"+self.playlistName+"/"+self.mp3InfoTrack1.fileName),self.mp3InfoTrack1),
                                                  mock.call(str(self.musicPath+"/"+self.playlistName+"/"+self.mp3InfoTrack2.fileName),self.mp3InfoTrack2)])

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToPlaylist")
    def test_downloadMP3Playlist(self, mock_metadata:mock.MagicMock, mock_extract_info:mock.MagicMock):
        mock_extract_info.configure_mock(side_effect=[self.ytPlaylistInfoResponse4, self.ytDownloadMp3Response1,
                                                      self.ytDownloadMp3Response2, self.ytDownloadMp3Response3, self.ytDownloadMp3Response4])


        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)


        self.assertEqual(self.ytManager.createDirIfNotExist.call_count, 5)
        self.ytManager.createDirIfNotExist.assert_called_with(self.musicPath+"/"+self.playlistName)
        self.assertEqual(mock_extract_info.call_count, 5)
        mock_extract_info.assert_has_calls([mock.call(self.ytLink, download=False),
                                            mock.call(self.firstUrl),
                                            mock.call(self.secondUrl),
                                            mock.call(self.thirdUrl),
                                            mock.call(self.fourthUrl),
                                            ])

        self.assertEqual(mock_metadata.call_count, self.numberOfSongs)
        mock_metadata.assert_has_calls([mock.call(self.musicPath, str(self.numberOfArchiveSongs+1), self.playlistName, self.firstArtist, self.firstAlbum, self.firstTitle, self.firstWebsite, self.actualDate),
                                        mock.call(self.musicPath, str(self.numberOfArchiveSongs+2), self.playlistName, self.secondArtist, self.secondAlbum, self.secondTitle, self.secondWebsite, self.actualDate),
                                        mock.call(self.musicPath, str(self.numberOfArchiveSongs+3), self.playlistName, self.thirdArtist, self.thirdAlbum, self.thirdTitle, self.thirdWebsite, self.actualDate),
                                        mock.call(self.musicPath, str(self.numberOfArchiveSongs+4), self.playlistName, self.fourthArtist, self.fourthAlbum, self.fourthTitle, self.fourthWebsite, self.actualDate)])

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), self.numberOfSongs)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToPlaylist")
    def test_downloadMP3Playlist_OneNewSongFromPlaylist(self, mock_metadata:mock.MagicMock, mock_extract_info:mock.MagicMock):

        self.ytManager._isMusicClipArchived = mock.MagicMock()
        self.ytManager._isMusicClipArchived.configure_mock(side_effect=[True, True, True, False])
        mock_extract_info.configure_mock(side_effect=[self.ytPlaylistInfoResponse4, self.ytDownloadMp3Response4])

        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)


        self.assertEqual(self.ytManager.createDirIfNotExist.call_count, 2)
        self.ytManager.createDirIfNotExist.assert_called_with(self.musicPath+"/"+self.playlistName)
        self.assertEqual(mock_extract_info.call_count, 2)
        mock_extract_info.assert_has_calls([mock.call(self.ytLink, download=False),
                                            mock.call(self.fourthUrl)
                                            ])

        self.assertEqual(mock_metadata.call_count, 1)
        mock_metadata.assert_called_once_with(self.musicPath, str(self.numberOfArchiveSongs+1), self.playlistName, self.fourthArtist, self.fourthAlbum, self.fourthTitle, self.fourthWebsite, self.actualDate)

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), 1)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToPlaylist")
    def test_downloadMP3Playlist_oneSongFailed(self, mock_metadata:mock.MagicMock, mock_extract_info:mock.MagicMock):
        errorMessage = "Failed to download from Youtube"
        mock_extract_info.configure_mock(side_effect=[self.ytPlaylistInfoResponse4, self.ytDownloadMp3Response1,
                                                      self.ytDownloadMp3Response2, utils.ExtractorError(errorMessage, expected=True), self.ytDownloadMp3Response4])

        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)


        self.assertEqual(self.ytManager.createDirIfNotExist.call_count, 5)
        self.ytManager.createDirIfNotExist.assert_called_with(self.musicPath+"/"+self.playlistName)
        self.assertEqual(mock_extract_info.call_count, 5)
        mock_extract_info.assert_has_calls([mock.call(self.ytLink, download=False),
                                            mock.call(self.firstUrl),
                                            mock.call(self.secondUrl),
                                            mock.call(self.thirdUrl),
                                            mock.call(self.fourthUrl),
                                            ])

        self.assertEqual(mock_metadata.call_count, self.numberOfSongs-1)
        mock_metadata.assert_has_calls([mock.call(self.musicPath, str(self.numberOfArchiveSongs+1), self.playlistName, self.firstArtist, self.firstAlbum, self.firstTitle, self.firstWebsite, self.actualDate),
                                        mock.call(self.musicPath, str(self.numberOfArchiveSongs+2), self.playlistName, self.secondArtist, self.secondAlbum, self.secondTitle, self.secondWebsite, self.actualDate),
                                        mock.call(self.musicPath, str(self.numberOfArchiveSongs+3), self.playlistName, self.fourthArtist,  self.fourthAlbum, self.fourthTitle, self.fourthWebsite, self.actualDate)])

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), self.numberOfSongs-1)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3Playlist_getInfoFailed(self, mock_extract_info:mock.MagicMock):
        errorMessage = "Failed to download from Youtube"
        mock_extract_info.configure_mock(side_effect=utils.ExtractorError(errorMessage, expected=True))

        result = self.ytManager.downloadPlaylistMp3(self.musicPath, self.playlistName, self.ytLink)

        self.ytManager.createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        mock_extract_info.assert_called_once_with(self.ytLink, download=False)
        self.assertTrue(result.IsFailed())
        self.assertEqual(result.error(), "download failed: "+errorMessage)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    @mock.patch.object(metadata_mp3.MetadataManager, "renameAndAddMetadataToPlaylist")
    def test_downloadMP3PlaylistFast(self, mock_metadata:mock.MagicMock, mock_extract_info:mock.MagicMock):
        mock_extract_info.configure_mock(return_value=self.ytDownloadMp3PlaylistResponse)

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        self.ytManager.createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        mock_extract_info.assert_called_once_with(self.ytLink)
        self.assertEqual(mock_metadata.call_count, self.numberOfSongs)

        mock_metadata.assert_has_calls([mock.call(self.musicPath, self.playlistIndex1, self.playlistName, self.firstArtist,  self.firstTitle,  self.firstWebsite, self.actualDate),
                                        mock.call(self.musicPath, self.playlistIndex2, self.playlistName, self.empty,        self.secondTitle, self.secondWebsite, self.actualDate),
                                        mock.call(self.musicPath, self.playlistIndex3, self.playlistName, self.thirdArtist,  self.thirdTitle,  self.thirdWebsite, self.actualDate),
                                        mock.call(self.musicPath, self.playlistIndex4, self.playlistName, self.fourthArtist, self.fourthTitle, self.fourthWebsite, self.actualDate)])

        self.assertTrue(result.IsSuccess())
        self.assertEqual(result.data(), self.numberOfSongs)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistFastEmptyResult(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=None)

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager.createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistFastWrongResult(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"fakeData":[]})

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager.createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_downloadMP3PlaylistFastEmptyEntries(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value={"entries":[{},None]})

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager.createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_downloadMP3PlaylistFastException(self, mock_extract_info):

        result = self.ytManager.downloadPlaylistMp3Fast(self.musicPath, self.playlistName, self.ytLink)

        mock_extract_info.assert_called_once_with(self.ytLink)
        self.ytManager.createDirIfNotExist.assert_called_once_with(self.musicPath+"/"+self.playlistName)
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), self.exceptionErrorExpected)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_download360p(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytDownloadVideoResponse)

        result = self.ytManager.download_360p(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertTrue(result.IsSuccess())
        self.checkVideoData(result.data(), self.ytDownloadVideoResponse, self.resolution360p)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_download360pFailed(self, mock_extract_info):

        result = self.ytManager.download_360p(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_download720p(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytDownloadVideoResponse)

        result = self.ytManager.download_720p(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertTrue(result.IsSuccess())
        self.checkVideoData(result.data(), self.ytDownloadVideoResponse, self.resolution720p)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_download720pFailed(self, mock_extract_info):

        result = self.ytManager.download_720p(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info")
    def test_download4k(self, mock_extract_info):
        mock_extract_info.configure_mock(return_value=self.ytDownloadVideoResponse)

        result = self.ytManager.download_4k(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertTrue(result.IsSuccess())
        self.checkVideoData(result.data(), self.ytDownloadVideoResponse, self.resolution4k)

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None)
    def test_download4kFailed(self, mock_extract_info):

        result = self.ytManager.download_4k(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertFalse(result.IsSuccess())

    @mock.patch.object(yt_dlp.YoutubeDL, "extract_info", side_effect=utils.ExtractorError(exceptionMessage, expected=True))
    def test_download4kFailedRaise(self, mock_extract_info):

        result = self.ytManager.download_4k(self.ytLink)

        mock_extract_info.assert_called_with(self.ytLink)
        self.assertFalse(result.IsSuccess())
        self.assertEqual(result.error(), self.exceptionErrorExpected)

class CustomConfigParser(ConfigParser):
    path = "/tmp/muzyka/Youtube list"
    playlist1Name = "relaks"
    playlist1Link = "http://youtube.com/relaks"

    playlist2Name = "chillout"
    playlist2Link = "http://youtube.com/chillout"

    numberOfPlaylists = 2

    def read(self, filename):
        self.read_string("[GLOBAL]\n"
                         "path = "+ self.path + "\n"+
                         "["+self.playlist1Name+"]\n"+
                         "name = "+self.playlist1Name+"\n"+
                         "link = "+self.playlist1Link+"\n"
                         "["+self.playlist2Name+"]\n"+
                         "name = "+self.playlist2Name+"\n"+
                         "link = "+self.playlist2Link+"\n")

    def setMockForRemoveSection(self, mock):
        self.remove_section = mock

class CustomConfigParserEmptyPath(ConfigParser):
    def read(self, filename):
        self.read_string("[relaks]\nname = relaks\nlink = http://youtube.com/relaks\n[chillout]\nname = chillout\nlink = http://youtube.com/chillout\n")

class YouTubeManagerConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.ytConfig = YoutubeConfig()

    def tearDown(self):
        pass

    def test_getPath(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        path = self.ytConfig.getPath()
        self.assertEqual(path, CustomConfigParser.path)

    @mock.patch.object(YoutubeConfig, "save")
    @mock.patch('configparser.ConfigParser.__setitem__')
    @mock.patch('configparser.ConfigParser.__getitem__')
    def test_setPath(self, mock_getItem, mock_setItem, mock_save):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        newPath = "/tmp/"

        self.ytConfig.setPath(newPath)

        mock_getItem.assert_has_calls([mock.call("GLOBAL"),
                                       mock.call().__setitem__('path', newPath)])
        self.assertEqual(mock_save.call_count, 1)

    @mock.patch.object(YoutubeConfig, "save")
    @mock.patch('configparser.ConfigParser.__setitem__')
    @mock.patch('configparser.ConfigParser.__getitem__')
    def test_setNewPath(self, mock_getItem, mock_setItem, mock_save):
        self.ytConfig.initialize("neverMind", CustomConfigParserEmptyPath())
        newPath = "/tmp/"

        self.ytConfig.setPath(newPath)

        mock_getItem.assert_has_calls([mock.call("GLOBAL"),
                                       mock.call().__setitem__('path', newPath)])
        self.assertEqual(mock_save.call_count, 1)

    def test_getPathFailed(self):
        self.ytConfig.initialize("neverMind", CustomConfigParserEmptyPath())
        path = self.ytConfig.getPath()
        self.assertEqual(path, None)

    def test_getPlaylists(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        playlists = self.ytConfig.getPlaylists()
        self.assertEqual(len(playlists), 2)
        self.assertEqual(playlists[0].name, CustomConfigParser.playlist1Name)
        self.assertEqual(playlists[0].link, CustomConfigParser.playlist1Link)

        self.assertEqual(playlists[1].name, CustomConfigParser.playlist2Name)
        self.assertEqual(playlists[1].link, CustomConfigParser.playlist2Link)

    def test_getPlaylistsName(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        playlists = self.ytConfig.getPlaylistsName()
        self.assertEqual(len(playlists), 2)
        self.assertEqual(playlists[0], CustomConfigParser.playlist1Name)
        self.assertEqual(playlists[1], CustomConfigParser.playlist2Name)

    def test_getUrlOfPaylist(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        url = self.ytConfig.getUrlOfPlaylist(CustomConfigParser.playlist1Name)
        self.assertEqual(url, CustomConfigParser.playlist1Link)

    def test_getUrlOfPlaylistWrongName(self):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        url = self.ytConfig.getUrlOfPlaylist("WrongPlaylistName")
        self.assertEqual(url, None)

    @mock.patch.object(YoutubeConfig, "save")
    @mock.patch('configparser.ConfigParser.__setitem__')
    @mock.patch('configparser.ConfigParser.__getitem__')
    @mock.patch('configparser.ConfigParser.read')
    def test_addPlaylist(self, mock_read, mock_getItem, mock_setItem, mock_save):
        newPlaylist = {"name":"disco", "link":"https://yt.com/disco"}
        self.ytConfig.initialize("neverMind")
        self.assertTrue(self.ytConfig.addPlaylist(newPlaylist))
        keys = list(newPlaylist.keys())
        values = list(newPlaylist.values())

        mock_getItem.assert_has_calls([
            mock.call(values[0]), mock.call().__setitem__(keys[0], values[0]),
            mock.call(values[0]), mock.call().__setitem__(keys[1], values[1])])
        self.assertEqual(mock_getItem.call_count, 2)

        mock_setItem.assert_has_calls([mock.call("disco",{})])
        self.assertEqual(mock_setItem.call_count, 1)

        self.assertEqual(mock_save.call_count, 1)
        self.assertEqual(mock_read.call_count, 1)

    @mock.patch.object(YoutubeConfig, "save")
    @mock.patch('configparser.ConfigParser.__setitem__')
    @mock.patch('configparser.ConfigParser.__getitem__')
    @mock.patch('configparser.ConfigParser.read')
    def test_addPlaylistWrongKeys(self, mock_read, mock_getItem, mock_setItem, mock_save):
        self.ytConfig.initialize("neverMind")
        newPlaylist = {"name1":"disco", "link":"https://yt.com/disco"}
        self.assertFalse(self.ytConfig.addPlaylist(newPlaylist))

        newPlaylist = {"name":"disco", "link2":"https://yt.com/disco"}
        self.assertFalse(self.ytConfig.addPlaylist(newPlaylist))

        newPlaylist = {"name3":"disco", "link3":"https://yt.com/disco"}
        self.assertFalse(self.ytConfig.addPlaylist(newPlaylist))

        self.assertEqual(mock_getItem.call_count, 0)
        self.assertEqual(mock_setItem.call_count, 0)
        self.assertEqual(mock_save.call_count, 0)
        self.assertEqual(mock_read.call_count, 0)

    @mock.patch('configparser.ConfigParser.remove_section')
    @mock.patch.object(YoutubeConfig, "save")
    def test_removePlaylist(self, mock_save, mock_removeSection):
        self.ytConfig.initialize("neverMind", CustomConfigParser())
        self.assertTrue(self.ytConfig.removePlaylist(CustomConfigParser.playlist1Name))
        self.assertEqual(mock_save.call_count, 1)
        self.assertEqual(mock_removeSection.call_count, 1)
        mock_removeSection.assert_called_once_with(CustomConfigParser.playlist1Name)

    @mock.patch.object(YoutubeConfig, "save")
    def test_removePlaylist2(self, mock_save):
        configParser = CustomConfigParser()
        removeSectionMock = mock.MagicMock()
        configParser.setMockForRemoveSection(removeSectionMock)

        self.ytConfig.initialize("neverMind", configParser)
        self.assertTrue(self.ytConfig.removePlaylist(CustomConfigParser.playlist1Name))
        self.assertEqual(mock_save.call_count, 1)
        removeSectionMock.assert_called_once_with(CustomConfigParser.playlist1Name)

    @mock.patch.object(YoutubeConfig, "save")
    def test_removePlaylistWrongName(self, mock_save):
        configParser = CustomConfigParser()
        removeSectionMock = mock.MagicMock()
        configParser.setMockForRemoveSection(removeSectionMock)

        self.ytConfig.initialize("neverMind", configParser)
        self.assertFalse(self.ytConfig.removePlaylist("wrongName"))
        self.assertEqual(mock_save.call_count, 0)
        self.assertEqual(removeSectionMock.call_count, 0)

class MediaServerDownloaderTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.downloader = MediaServerDownloader("test.ini")
        self.downloader.ytConfig.initialize("test.ini", CustomConfigParser())
        self.downloader.downloadPlaylistMp3 = MagicMock()
        self.downloader.checkPlaylistStatus = MagicMock()
        self.downloader.updateTrackNumber = MagicMock()

    def test_setMusicPathSuccess(self):
        oldMusicPath = self.downloader.MUSIC_PATH
        newMusicPath = "/tmp"

        self.assertTrue(self.downloader.setMusicPath(newMusicPath))

        self.assertEqual(self.downloader.MUSIC_PATH, newMusicPath)
        self.assertNotEqual(self.downloader.MUSIC_PATH, oldMusicPath)

    def test_setMusicPathFailed(self):
        oldMusicPath = self.downloader.MUSIC_PATH
        newMusicPath = "/wrongPath"

        self.assertIsNone(self.downloader.setMusicPath(newMusicPath))

        self.assertNotEqual(self.downloader.MUSIC_PATH, newMusicPath)
        self.assertEqual(self.downloader.MUSIC_PATH, oldMusicPath)

    def test_downloadPlaylists(self):
        self.downloader.setMusicPath = MagicMock()
        self.downloader.setMusicPath.configure_mock(return_value="/music/path/")
        listOfPlaylistResult = [4, 15]
        lisOfResults = []
        expectedNumberOfDownloadedSongs = 0
        for x in range(CustomConfigParser.numberOfPlaylists):
            numberOfDonwloadedSongs = listOfPlaylistResult[x]
            expectedNumberOfDownloadedSongs += numberOfDonwloadedSongs
            lisOfResults.append(ResultOfDownload(numberOfDonwloadedSongs))
        self.downloader.downloadPlaylistMp3.configure_mock(side_effect=lisOfResults)

        result = self.downloader.download_playlists()

        self.assertEqual(result, expectedNumberOfDownloadedSongs)
        self.downloader.setMusicPath.assert_has_calls([mock.call(CustomConfigParser.path)])
        self.downloader.downloadPlaylistMp3.assert_has_calls(
            [mock.call(CustomConfigParser.path, CustomConfigParser.playlist1Name, CustomConfigParser.playlist1Link),
             mock.call(CustomConfigParser.path, CustomConfigParser.playlist2Name, CustomConfigParser.playlist2Link)])

        self.downloader.checkPlaylistStatus.assert_has_calls(
            [mock.call(CustomConfigParser.path, CustomConfigParser.playlist1Name, CustomConfigParser.playlist1Link),
             mock.call(CustomConfigParser.path, CustomConfigParser.playlist2Name, CustomConfigParser.playlist2Link)])

    def test_downloadPlaylistsOnePlaylistFailed(self):
        self.downloader.setMusicPath = MagicMock()
        self.downloader.setMusicPath.configure_mock(return_value="/music/path/")
        lisOfResults = []
        expectedNumberOfDownloadedSongs = 4
        lisOfResults.append(ResultOfDownload(4))
        lisOfResults.append(ResultOfDownload("error"))
        self.downloader.downloadPlaylistMp3.configure_mock(side_effect=lisOfResults)

        result = self.downloader.download_playlists()

        self.assertEqual(result, expectedNumberOfDownloadedSongs)
        self.downloader.setMusicPath.assert_has_calls([mock.call(CustomConfigParser.path)])
        self.downloader.downloadPlaylistMp3.assert_has_calls(
            [mock.call(CustomConfigParser.path, CustomConfigParser.playlist1Name, CustomConfigParser.playlist1Link),
             mock.call(CustomConfigParser.path, CustomConfigParser.playlist2Name, CustomConfigParser.playlist2Link)])

        self.downloader.checkPlaylistStatus.assert_has_calls(
            [mock.call(CustomConfigParser.path, CustomConfigParser.playlist1Name, CustomConfigParser.playlist1Link),
             mock.call(CustomConfigParser.path, CustomConfigParser.playlist2Name, CustomConfigParser.playlist2Link)])

    def test_downloadPlaylistsFailedWrongPath(self):
        self.downloader.setMusicPath = MagicMock()
        self.downloader.setMusicPath.configure_mock(return_value=None)

        result = self.downloader.download_playlists()

        self.assertIsNone(result)
        self.downloader.setMusicPath.assert_has_calls([mock.call(CustomConfigParser.path)])
        self.downloader.downloadPlaylistMp3.assert_not_called()

    def test_checkPlaylistsSync(self):
        self.downloader.setMusicPath = MagicMock()
        self.downloader.setMusicPath.configure_mock(return_value="/music/path")

        self.downloader.checkPlaylistsSync()

        self.downloader.checkPlaylistStatus.assert_has_calls(
            [mock.call(CustomConfigParser.path, CustomConfigParser.playlist1Name, CustomConfigParser.playlist1Link),
             mock.call(CustomConfigParser.path, CustomConfigParser.playlist2Name, CustomConfigParser.playlist2Link)])

    def test_updateTrackNumberAllPlaylists(self):
        self.downloader.setMusicPath = MagicMock()
        self.downloader.setMusicPath.configure_mock(return_value="/music/path")

        self.downloader.updateTrackNumberAllPlaylists()

        self.downloader.updateTrackNumber.assert_has_calls(
            [mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist1Name), CustomConfigParser.playlist1Link, False),
             mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist2Name), CustomConfigParser.playlist2Link, False)])

    def test_updateTrackNumberAllPlaylists_isSave(self):
        self.downloader.setMusicPath = MagicMock()
        self.downloader.setMusicPath.configure_mock(return_value="/music/path")

        self.downloader.updateTrackNumberAllPlaylists(isSave=True)

        self.downloader.updateTrackNumber.assert_has_calls(
            [mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist1Name), CustomConfigParser.playlist1Link, True),
             mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist2Name), CustomConfigParser.playlist2Link, True)])

    def test_updateTrackNumberAllPlaylists_singleNumberOne(self):
        self.downloader.setMusicPath = MagicMock()
        self.downloader.setMusicPath.configure_mock(return_value="/music/path")

        self.downloader.updateTrackNumberAllPlaylists(0,isSave=True)

        self.downloader.updateTrackNumber.assert_has_calls(
            [mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist1Name), CustomConfigParser.playlist1Link, True)])

    def test_updateTrackNumberAllPlaylists_singleNumberTwo(self):
        self.downloader.setMusicPath = MagicMock()
        self.downloader.setMusicPath.configure_mock(return_value="/music/path")

        self.downloader.updateTrackNumberAllPlaylists(1)

        self.downloader.updateTrackNumber.assert_has_calls(
            [mock.call(str(CustomConfigParser.path + "/" + CustomConfigParser.playlist2Name), CustomConfigParser.playlist2Link, False)])

class ResultOfDownloadTestCase(unittest.TestCase):
    def test_resultSuccess(self):
        data = ["data"]

        result = ResultOfDownload(data)

        self.assertTrue(result.IsSuccess())
        self.assertFalse(result.IsFailed())
        self.assertIsNone(result.error())
        self.assertListEqual(data, result.data())

    def test_resultFailed(self):
        error = "error"

        result = ResultOfDownload(error)

        self.assertFalse(result.IsSuccess())
        self.assertTrue(result.IsFailed())
        self.assertIsNone(result.data())
        self.assertEqual(result.error(), error)

if __name__ == "__main__":
    unittest.main()
