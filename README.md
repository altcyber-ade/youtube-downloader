# yt-dlp MP3 Downloader GUI

A small cross-platform Python/Tkinter GUI around **yt-dlp** for extracting audio to MP3.

The app provides a URL field, destination picker, MP3 quality selection, playlist support,
metadata/thumbnail options, browser-cookie selection, progress reporting and cancellation.

> Use this software only for media you own or are authorised to download. You are responsible
> for complying with the terms of the services you use and with applicable copyright law.

## Requirements

- Python 3.10 or newer
- `yt-dlp`
- FFmpeg available on your `PATH`
- Tkinter

yt-dlp recommends FFmpeg/ffprobe for post-processing, which this application requires for MP3 output.

## Quick start

### macOS

```bash
git clone https://github.com/altcyber-ade/youtube-downloader.git
cd youtube-downloader

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt

brew install ffmpeg
python yt_dlp_mp3_gui.py
```

If Python was installed from python.org on macOS and HTTPS certificate verification fails,
run the `Install Certificates.command` included in `/Applications/Python 3.x/`.

### Windows

```powershell
git clone https://github.com/altcyber-ade/youtube-downloader.git
cd youtube-downloader

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt

python yt_dlp_mp3_gui.py
```

FFmpeg must be installed separately and its `bin` directory must be on `PATH`.
See [BUILD_WINDOWS.md](BUILD_WINDOWS.md).

## Features

- Extract best available audio and convert it to MP3
- Select 128, 160, 192, 256 or 320 kbps target quality
- Download a single item or an entire playlist
- Choose an output folder
- Custom yt-dlp filename template
- Embed metadata and thumbnails
- Browser-cookie support for Safari, Chrome, Firefox and Brave
- Restrict filenames
- Overwrite existing files
- Keep original downloaded media
- Optional playlist-named subfolders
- Progress, speed and ETA display
- Cancel an active download

## Desktop builds

- macOS: [BUILD_MACOS.md](BUILD_MACOS.md)
- Windows: [BUILD_WINDOWS.md](BUILD_WINDOWS.md)

Build the Windows `.exe` on Windows and the macOS `.app` on macOS.

## Updating yt-dlp

```bash
python -m pip install -U "yt-dlp[default]"
```

## License

No license has been selected yet. Add a `LICENSE` file before encouraging third-party
redistribution or contributions.
