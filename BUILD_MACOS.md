# Building on macOS

## Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-build.txt
brew install ffmpeg
```

Install Google Chrome or Chromium as well. The v0.2 automatic PO-token provider uses a browser
to mint YouTube PO tokens when required.

For python.org Python installations, run the supplied certificate installer if needed:

```bash
open "/Applications/Python 3.14/Install Certificates.command"
```

Adjust the version number if necessary.

## Test first

```bash
python youtube_downloader.py
```

Confirm a YouTube download works with **Use mweb + automatic PO-token provider** enabled.

## Build the `.app`

```bash
python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --collect-submodules yt_dlp_plugins \
  --name "yt-dlp MP3 Downloader" \
  youtube_downloader.py
```

The app bundle will be created under:

```text
dist/yt-dlp MP3 Downloader.app
```

The current build expects FFmpeg and Chrome/Chromium to be installed separately on the target Mac.

## Before making a release

```bash
python -m pip install -U -r requirements.txt
```

Then retest a YouTube download before packaging.
