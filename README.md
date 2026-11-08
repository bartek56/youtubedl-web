
[![CircleCI](https://img.shields.io/circleci/build/github/bartek56/youtubedl-web)](https://app.circleci.com/pipelines/github/bartek56/youtubedl-web)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen)](https://bartek56.github.io/youtubedl-web/)



website to download and manage Youtube list; to set alarm in MediaServer


More about media server in  [MediaServer](https://github.com/bartek56/mediaserver) or [meta-mediaserver](https://github.com/bartek56/meta-mediaserver)

python3 -m venv env
source env/bin/activate
pip3 install -r requirementsEnv.txt
flask --app youtubedlWeb run

After installing the package with `pip install .`, the following commands are available:

```bash
youtubedlWeb
playlists-manager --config /ścieżka/playlists.ini --music-dir /ścieżka/muzyka
playlists-manager --config-help
```

The `--config-help` option displays a detailed description of the INI file
format and a complete example configuration covering all supported options.

In code, the music source and the playlist output location can be separated:

```python
PlaylistsManager(
    musicDir,
    playlistsDir=None,
    windowsSlash=False,
    playlistsConfigFile=None,
)
```

M3U file paths are relative to `musicDir` and include all intermediate
folders. When `playlistsDir` is not provided, the `.m3u` files are written to
`musicDir`. Changing the output directory outside `musicDir` is blocked so the
script does not write playlists outside the directory specified by `--music-dir`.

The definitions for playlist groups, Top playlists, and global settings live in
separate INI files for each target. The following example shows the full set of
supported options:

```ini
[GLOBAL]
musicDir = /ścieżka/muzyka
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

The file is passed separately to `YoutubeManager.py`:

```bash
python3 -m youtubedlWeb.Common.YoutubeManager \
  --config /ścieżka/youtube.ini \
  --playlists-config /ścieżka/playlists.ini
```

The playlist regeneration step is tied to the download result. After a run,
the downloader keeps track of which folders were updated and passes that
information to the playlist generator. Only groups whose folders intersect the
updated set are rebuilt; unrelated groups are skipped. This avoids regenerating
all playlists from scratch after every download.

Multiple playlist configuration files can be supplied in the same run. In that
case, the same set of updated folders is applied to each configuration, and the
playlist generation is repeated for every provided config file:

```bash
python3 -m youtubedlWeb.Common.YoutubeManager \
  --config /ścieżka/youtube.ini \
  --playlists-config /ścieżka/playlists-a.ini \
  --playlists-config /ścieżka/playlists-b.ini
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
`musicDir` can be set in `[GLOBAL]` as a fallback for `--music-dir`. If neither is
provided, the program exits with an error.
`createPlaylistsOfDirs` enables generation of one `.m3u` file per top-level folder in
`musicDir`. This is optional and defaults to `false`.
`playlistsDir` is the output directory for generated `.m3u` files. When omitted,
the generator uses `musicDir` as the destination. Any configured value must remain
inside `musicDir`; otherwise the generator falls back to `musicDir`.
`rootDir` inside `[TOP_PLAYLISTS]` scopes the Top playlists to a selected
subdirectory inside `musicDir`. The default is `.` which means the whole
`musicDir`.
`garminRootDir` can point to a directory with source M3U playlists; when it is
set, the generator also creates Garmin-compatible playlists. A group name in
the form `trening 40 hits` creates a playlist limited to 40 songs.
`--music-dir` is required and specifies the main music directory.
