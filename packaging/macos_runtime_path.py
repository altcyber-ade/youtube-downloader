"""PyInstaller runtime hook for Finder-launched macOS app bundles.

Apps launched from Finder/LaunchServices do not inherit the user's interactive
shell PATH, so Homebrew binaries such as ffmpeg may not be discoverable even
when they are installed. Prepend the standard Apple Silicon and Intel Homebrew
locations before the main application imports yt-dlp or checks for ffmpeg.
"""

from __future__ import annotations

import os
import platform


if platform.system() == "Darwin":
    current = os.environ.get("PATH", "")
    existing = [item for item in current.split(os.pathsep) if item]
    preferred = [
        "/opt/homebrew/bin",
        "/opt/homebrew/sbin",
        "/usr/local/bin",
        "/usr/local/sbin",
    ]

    path_entries: list[str] = []
    for item in preferred + existing:
        if item not in path_entries:
            path_entries.append(item)

    os.environ["PATH"] = os.pathsep.join(path_entries)
