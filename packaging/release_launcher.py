#!/usr/bin/env python3
"""Packaged release launcher for the desktop builds.

The source application remains directly runnable as youtube_downloader.py. This
launcher adds packaging-specific checks without making the source workflow
pretend that bundled dependencies are normal site-packages.
"""

from __future__ import annotations

import importlib.util
import sys
from importlib.metadata import PackageNotFoundError, version

import youtube_downloader as app


RELEASE_VERSION = "0.2.4"
WPC_DISTRIBUTION = "yt-dlp-getpot-wpc"


def wpc_metadata_available() -> bool:
    try:
        version(WPC_DISTRIBUTION)
        return True
    except PackageNotFoundError:
        return False
    except Exception:
        return False


def wpc_module_available() -> bool:
    try:
        return importlib.util.find_spec(app.WPC_MODULE) is not None
    except (ImportError, ModuleNotFoundError, AttributeError):
        return False


def wpc_available(_self=None) -> bool:
    """Packaged builds accept copied distribution metadata or module discovery."""
    return wpc_metadata_available() or wpc_module_available()


def self_test() -> int:
    checks = {
        "yt_dlp": app.yt_dlp is not None,
        "psutil": app.psutil is not None,
        "wpc_metadata": wpc_metadata_available(),
        "wpc_module": wpc_module_available(),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("SELF-TEST FAILED:", ", ".join(failed))
        return 1
    print("SELF-TEST OK:", ", ".join(checks))
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()

    app.APP_VERSION = RELEASE_VERSION
    app.MP3DownloaderApp._wpc_available = wpc_available
    app.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
