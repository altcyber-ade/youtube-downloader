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

For python.org Python installations, run the supplied certificate installer if needed:

```bash
open "/Applications/Python 3.14/Install Certificates.command"
```

Adjust the version number if necessary.

## Test first

```bash
python yt_dlp_mp3_gui.py
```

## Build the `.app`

```bash
python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "yt-dlp MP3 Downloader" \
  yt_dlp_mp3_gui.py
```

The app bundle will be created under:

```text
dist/yt-dlp MP3 Downloader.app
```

The current build expects FFmpeg to be installed separately and available on `PATH`.
