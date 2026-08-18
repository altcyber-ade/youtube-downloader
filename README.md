# yt-dlp MP3 Downloader GUI

[![Build and release desktop apps](https://github.com/altcyber-ade/youtube-downloader/actions/workflows/release-build.yml/badge.svg)](https://github.com/altcyber-ade/youtube-downloader/actions/workflows/release-build.yml)

A cross-platform Python/Tkinter GUI around **yt-dlp** for extracting audio to MP3.

The app provides a URL field, destination picker, MP3 quality selection, playlist support,
metadata/thumbnail options, browser-cookie selection, progress reporting and cancellation.

> Use this software only for media you own or are authorised to download. You are responsible
> for complying with the terms of the services you use and with applicable copyright law.

## Download the latest desktop builds

| Platform | Download | Notes |
|---|---|---|
| macOS | **[Download macOS app](https://github.com/altcyber-ade/youtube-downloader/releases/latest/download/YouTube-Downloader-macOS.zip)** | Unzip and open `YouTube Downloader.app`. FFmpeg/FFprobe are bundled. Chrome or Chromium is still required for automatic PO-token generation. |
| Windows | **[Download Windows EXE](https://github.com/altcyber-ade/youtube-downloader/releases/latest/download/YouTube-Downloader-Windows.exe)** | Portable executable with FFmpeg/FFprobe bundled. Chrome or Chromium is still required for automatic PO-token generation. |

[View all releases](https://github.com/altcyber-ade/youtube-downloader/releases)

The downloads above are generated automatically by GitHub Actions whenever a `v*` release tag is pushed. The workflow builds the app natively on macOS and Windows, smoke-tests the packaged runtime dependencies, and attaches both files to the matching GitHub Release.

## YouTube compatibility (v0.2)

YouTube increasingly requires Proof-of-Origin (PO) tokens for media requests. Version 0.2 adds:

- the `mweb` YouTube client
- automatic PO-token generation through `yt-dlp-getpot-wpc`
- an optional IPv4 fallback
- improved yt-dlp/YouTube diagnostics in the GUI
- automatic cleanup of safely identifiable temporary PO-token Chrome/Chromium processes

The PO-token provider automatically launches Chrome/Chromium briefly when yt-dlp requests a token. The downloader can close the temporary automation browser afterward when it can identify that process safely; it does not intentionally terminate your normal Chrome session.

## Requirements

For the downloadable macOS and Windows builds, FFmpeg and FFprobe are bundled. You only need Chrome or Chromium for the automatic PO-token provider.

When running from source you need:

- Python 3.10 or newer
- `yt-dlp[default]`
- `yt-dlp-getpot-wpc`
- `psutil`
- Google Chrome or Chromium for automatic PO-token generation
- FFmpeg available on your `PATH`
- Tkinter

## Quick start from source

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

When running from source, FFmpeg must be installed separately and its `bin` directory must be on `PATH`. Chrome or Chromium is also required for the automatic PO-token provider. See [BUILD_WINDOWS.md](BUILD_WINDOWS.md).

## Features

- Extract best available audio and convert it to MP3
- Select 128, 160, 192, 256 or 320 kbps target quality
- Download a single item or an entire playlist
- Choose an output folder
- Right-click URL field with Cut / Copy / Paste / Select All
- Custom yt-dlp filename template
- Embed metadata and thumbnails
- Browser-cookie support for Safari, Chrome, Firefox and Brave
- Recommended `mweb` + automatic PO-token mode
- Optional cleanup of temporary PO-token browser processes
- Optional Force IPv4 fallback
- Optional verbose yt-dlp diagnostics
- Restrict filenames
- Overwrite existing files
- Keep original downloaded media
- Optional playlist-named subfolders
- Progress bar, percentage, speed and ETA display
- Cancel an active download

## Automated releases

The workflow in `.github/workflows/release-build.yml` runs automatically for tags matching `v*`.

For example:

```bash
git tag -a v0.2.4 -m "v0.2.4"
git push origin v0.2.4
```

GitHub Actions then:

1. installs and stages FFmpeg/FFprobe on each native runner,
2. builds `YouTube-Downloader-Windows.exe` with the runtime dependencies and FFmpeg tools bundled,
3. builds `YouTube Downloader.app` on macOS with the same bundled runtime dependencies,
4. runs a packaged self-test checking yt-dlp, psutil, the WPC provider, FFmpeg and FFprobe,
5. packages the macOS application as `YouTube-Downloader-macOS.zip`, and
6. creates or updates the GitHub Release and attaches both downloads.

The workflow can also be run manually from the **Actions** tab for an existing release tag. A manual rebuild uses the source snapshot stored in that tag.

## Local desktop builds

- macOS: [BUILD_MACOS.md](BUILD_MACOS.md)
- Windows: [BUILD_WINDOWS.md](BUILD_WINDOWS.md)

## Updating yt-dlp and the PO-token provider

```bash
python -m pip install -U -r requirements.txt
```

YouTube changes frequently, so updating the dependencies is a useful first troubleshooting step when running from source.

## Legacy v0.1 source

`yt_dlp_mp3_gui.py` is retained for the v0.1 history. The current source application entry point is `youtube_downloader.py`; packaged releases use a small packaging launcher so their bundled-dependency checks stay separate from the source workflow.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
