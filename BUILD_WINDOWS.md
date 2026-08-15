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

## 3. Clone and install dependencies

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

## 4. Test the source

```powershell
python yt_dlp_mp3_gui.py
```

## 5. Build a single `.exe`

```powershell
python -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name "yt-dlp-MP3-Downloader" `
  yt_dlp_mp3_gui.py
```

Output:

```text
dist\yt-dlp-MP3-Downloader.exe
```

FFmpeg is not bundled and must still be installed on the target machine and available on `PATH`.

## Optional folder build

For easier troubleshooting and quicker startup, omit `--onefile`:

```powershell
python -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --name "yt-dlp-MP3-Downloader" `
  yt_dlp_mp3_gui.py
```

## Optional icon

Add this to the PyInstaller command:

```text
--icon app.ico
```

## Before making a release

Update yt-dlp, retest, and rebuild:

```powershell
python -m pip install -U "yt-dlp[default]"
```
