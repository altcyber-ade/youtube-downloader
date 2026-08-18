"""PyInstaller runtime hook for packaged desktop builds.

Finder/LaunchServices and Windows GUI launches do not reliably inherit an
interactive shell PATH. PyInstaller also places bundled helper executables in
its runtime directory. Put those locations on PATH before the application
checks for ffmpeg/ffprobe or starts yt-dlp.
"""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path


current = os.environ.get("PATH", "")
existing = [item for item in current.split(os.pathsep) if item]
preferred: list[str] = []

if getattr(sys, "frozen", False):
    runtime_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    preferred.extend(
        [
            str(runtime_root),
            str(runtime_root / "bin"),
            str(Path(sys.executable).parent),
        ]
    )

if platform.system() == "Darwin":
    preferred.extend(
        [
            "/opt/homebrew/bin",
            "/opt/homebrew/sbin",
            "/usr/local/bin",
            "/usr/local/sbin",
        ]
    )

path_entries: list[str] = []
for item in preferred + existing:
    if item and item not in path_entries:
        path_entries.append(item)

os.environ["PATH"] = os.pathsep.join(path_entries)
