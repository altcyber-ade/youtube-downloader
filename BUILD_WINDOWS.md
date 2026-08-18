# Building on Windows

These instructions cover running the Python source and creating a Windows `.exe`.

## 1. Install Python

Install a current CPython release from python.org and verify it in PowerShell:

```powershell
py --version
```

## 2. Install FFmpeg

The downloader requires the FFmpeg and FFprobe executables for MP3 conversion.

Place them in a permanent folder such as:

```text
C:\Tools\ffmpeg\bin
```

Add that folder to Windows `PATH`, open a new PowerShell window, then verify:

```powershell
ffmpeg -version
ffprobe -version
```

## 3. Install Chrome or Chromium

Version 0.2 uses `yt-dlp-getpot-wpc` to generate YouTube PO tokens automatically. The provider
requires Google Chrome or Chromium and may briefly launch the browser while a token is minted.
Do not close that browser while yt-dlp is using it.

## 4. Clone and install dependencies

```powershell
git clone https://github.com/altcyber-ade/youtube-downloader.git
cd youtube-downloader

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -U pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-build.txt
```

If PowerShell blocks activation, Command Prompt can use:

```cmd
.venv\Scripts\activate.bat
```

## 5. Test the source

```powershell
python youtube_downloader.py
```

Confirm a YouTube download works with **Use mweb + automatic PO-token provider** enabled.

## 6. Build a single `.exe`

```powershell
python -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --collect-submodules yt_dlp_plugins `
  --name "yt-dlp-MP3-Downloader" `
  youtube_downloader.py
```

Output:

```text
dist\yt-dlp-MP3-Downloader.exe
```

FFmpeg and Chrome/Chromium are not bundled and must still be installed on the target machine.

## Optional folder build

For easier troubleshooting and quicker startup, omit `--onefile`:

```powershell
python -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --collect-submodules yt_dlp_plugins `
  --name "yt-dlp-MP3-Downloader" `
  youtube_downloader.py
```

## Optional icon

Add this to the PyInstaller command:

```text
--icon app.ico
```

## Before making a release

Update yt-dlp and the PO-token provider, retest, and rebuild:

```powershell
python -m pip install -U -r requirements.txt
```
