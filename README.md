# yt-dlp MP3 Downloader GUI

A cross-platform Python/Tkinter GUI around **yt-dlp** for extracting audio to MP3.

The app provides a URL field, destination picker, MP3 quality selection, playlist support,
metadata/thumbnail options, browser-cookie selection, progress reporting and cancellation.

> Use this software only for media you own or are authorised to download. You are responsible
> for complying with the terms of the services you use and with applicable copyright law.

## YouTube compatibility (v0.2)

YouTube increasingly requires Proof-of-Origin (PO) tokens for media requests. Version 0.2 adds:

- the `mweb` YouTube client
- automatic PO-token generation through `yt-dlp-getpot-wpc`
- an optional IPv4 fallback
- improved yt-dlp/YouTube diagnostics in the GUI

The PO-token provider automatically launches Chrome/Chromium briefly when yt-dlp requests a token.
Do not close that browser while the token is being generated.

## Requirements

- Python 3.10 or newer
- `yt-dlp[default]`
- `yt-dlp-getpot-wpc`
- Google Chrome or Chromium for automatic PO-token generation
- FFmpeg available on your `PATH`
- Tkinter

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
python youtube_downloader.py
```

Install Chrome or Chromium if you do not already have one. If Python was installed from
python.org on macOS and HTTPS certificate verification fails, run the
`Install Certificates.command` included in `/Applications/Python 3.x/`.

### Windows

```powershell
git clone https://github.com/altcyber-ade/youtube-downloader.git
cd youtube-downloader

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt

python youtube_downloader.py
```

FFmpeg must be installed separately and its `bin` directory must be on `PATH`. Chrome or
Chromium is also required for the automatic PO-token provider. See
[BUILD_WINDOWS.md](BUILD_WINDOWS.md).

## Features

- Extract best available audio and convert it to MP3
- Select 128, 160, 192, 256 or 320 kbps target quality
- Download a single item or an entire playlist
- Choose an output folder
- Custom yt-dlp filename template
- Embed metadata and thumbnails
- Browser-cookie support for Safari, Chrome, Firefox and Brave
- Recommended `mweb` + automatic PO-token mode
- Optional Force IPv4 fallback
- Optional verbose yt-dlp diagnostics
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

## Updating yt-dlp and the PO-token provider

```bash
python -m pip install -U -r requirements.txt
```

YouTube changes frequently, so updating the dependencies is a useful first troubleshooting step.

## Legacy v0.1 source

`yt_dlp_mp3_gui.py` is retained for the v0.1 history. The current application entry point is
`youtube_downloader.py`.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
