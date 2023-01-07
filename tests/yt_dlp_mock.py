from unittest import mock

YoutubeDL = mock.Mock()
YoutubeDL().extract_info.return_value = {"title":"test_title", "artist":"test_artist", "album":"test_album", "ext":"mp4"}
