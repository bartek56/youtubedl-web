#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from PlaylistsManager import PlaylistsManager

def main():
    path = os.path.abspath(os.getcwd())
    manager = PlaylistsManager(path)

    manager.createTopOfMusic(100)
    manager = PlaylistsManager(path)
    manager.removeCovers()
    manager.createPlaylists()
    manager.createPlaylist(".", "all")

    folders=["imprezka","positive chill","relaks","stare ale jare","techno"]
    manager.createGroupOfPlaylists("trening", folders)
    manager.createGroupOfPlaylists("trening", folders, 40)

    folders=["chillout","positive chill","relaks","spokojne-sad"]
    manager.createGroupOfPlaylists("praca", folders)

    folders=["Bachata","Kizomba"]
    manager.createGroupOfPlaylists("taniec", folders)


    manager.createTopOfMusic(30)
    manager.createTopOfMusic(50)
    manager.createTopOfMusic(100)
    manager.checkDuplicates()
    totalSize = manager.getTotalSize()
    print(f"Total size: {totalSize}Mb")
    if totalSize > 1400:
        print("Warning, total size is greater than 1200Mb")
        return

    manager = PlaylistsManager("/home/bartosz/Music/MediaServer/Youtube list")
    manager.createPlaylistsAsGarmin("/home/bartosz/Music/Garmin5_music_128")

if __name__ == '__main__':
    main()

    #sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])

    #sys.exit(main())

