
[![CircleCI](https://img.shields.io/circleci/build/github/bartek56/youtubedl-web)](https://app.circleci.com/pipelines/github/bartek56/youtubedl-web)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen)](https://bartek56.github.io/youtubedl-web/)



website to download and manage Youtube list; to set alarm in MediaServer


More about media server in  [MediaServer](https://github.com/bartek56/mediaserver) or [meta-mediaserver](https://github.com/bartek56/meta-mediaserver)

python3 -m venv env
source env/bin/activate
pip3 install -r requirementsEnv.txt
flask --app youtubedlWeb run

Po zainstalowaniu paczki poleceniem `pip install .` dostępne są dwa polecenia:

```bash
youtubedlWeb
playlists-manager --config /ścieżka/playlists.ini --music-dir /ścieżka/muzyka
playlists-manager --config-help
```

Opcja --config-help wyświetla szczegółowy opis formatu pliku INI oraz
kompletny przykład konfiguracji ze wszystkimi obsługiwanymi opcjami.

W kodzie można rozdzielić źródło muzyki i miejsce zapisu playlist:

```python
PlaylistsManager(
    musicDir,
    playlistsDir=None,
    windowsSlash=False,
    playlistsConfigFile=None,
)
```

Ścieżki utworów w M3U są względne względem `musicDir` i zawierają wszystkie
katalogi pośrednie. Gdy `playlistsDir` nie jest podany, pliki `.m3u` trafiają
do `musicDir`.

Definicje grup playlist, playlist Top oraz ustawienia globalne są w osobnym
pliku INI dla każdego targetu. Przykładowe pliki to
`playlists-sandisk.ini.example`, `playlists-mb57.ini.example` oraz
`playlists-garmin.ini.example`:

```ini
[GLOBAL]
removeCovers = false
CrLf = false
checkMissingWebsite = false
removePolishChars = false
checkCovers = false
checkDuplicates = false
checkTotalSize = false
maxTotalSizeMb =
windowsSlash = false
playlistsDir = /ścieżka/do/playlist
createPlaylistsOfDirs = false
garminRootDir =
checkCovers = false
checkDuplicates = false
checkTotalSize = false
windowsSlash = false

[PLAYLIST_GROUPS]
trening = imprezka, techno, relaks
praca = relaks, chillout

[TOP_PLAYLISTS]
rootDir = .
sizes = 20, 100, 200
```

Plik przekazuje się osobno do `YoutubeManager.py`:

```bash
python3 -m youtubedlWeb.Common.YoutubeManager \
  --config /ścieżka/youtube.ini \
  --playlists-config /ścieżka/playlists.ini
```

Standalone generator receives one target-specific file. The options
`--garmin`, `--sandisk` and `--mediaserver` are no longer used:

```bash
python3 -m youtubedlWeb.Common.PlaylistsManager.PlaylistsManager \
  --config /ścieżka/playlists-sandisk.ini \
  --music-dir /ścieżka/muzyka
```

For another target, run the command with its separate INI file. `removeCovers`
and `CrLf` are read directly by the `PlaylistsManager` constructor from
`[GLOBAL]` in the configuration file. If either option is missing, its
default value is `false`. `checkMissingWebsite` controls the diagnostic check
for MP3 files without a `website` tag and also defaults to `false`.
`removePolishChars` controls removal of Polish characters from file and
directory names and also defaults to `false`.
`checkCovers`, `checkDuplicates` and `checkTotalSize` enable the corresponding
diagnostic steps. `maxTotalSizeMb` limits the total size check when it is
enabled.
`createPlaylistsOfDirs` enables generation of one `.m3u` file per top-level folder in
`musicDir`. This is optional and defaults to `false`.
`playlistsDir` is the output directory for generated `.m3u` files. When omitted,
the generator uses `musicDir` as the destination.
`rootDir` inside `[TOP_PLAYLISTS]` scopes the Top playlists to a selected
subdirectory inside `musicDir`. The default is `.` which means the whole
`musicDir`.
`garminRootDir` can point to a directory with source M3U playlists; when it is
set, the generator also creates Garmin-compatible playlists. A group name in
the form `trening 40 hits` creates a playlist limited to 40 songs.
`--music-dir` is required and specifies the main music directory.
