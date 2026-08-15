#!/usr/bin/env python3
"""
Cross-platform yt-dlp MP3 Downloader GUI.

Use only for media you own or are authorised to download.

Python dependency:
    python -m pip install -U "yt-dlp[default]"

FFmpeg must also be installed and available on PATH.
See README.md and the platform build guides.
"""

from __future__ import annotations

import os
import platform
import queue
import shutil
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


class DownloadCancelled(Exception):
    """Raised from a yt-dlp progress hook when the user cancels."""


class YTDLPLogger:
    """Pass useful yt-dlp messages into the GUI without blocking the worker."""

    def __init__(self, events: queue.Queue[tuple[str, Any]]) -> None:
        self.events = events

    def debug(self, message: str) -> None:
        # yt-dlp sends normal informational messages through debug().
        if message.startswith("[debug]"):
            return
        self.events.put(("log", message))

    def warning(self, message: str) -> None:
        self.events.put(("log", f"Warning: {message}"))

    def error(self, message: str) -> None:
        self.events.put(("log", f"Error: {message}"))


class MP3DownloaderApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("yt-dlp MP3 Downloader")
        self.geometry("780x720")
        self.minsize(700, 620)

        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.worker: threading.Thread | None = None
        self.cancel_event = threading.Event()

        self.url_var = tk.StringVar()
        self.output_var = tk.StringVar(value=str(Path.home() / "Music"))
        self.quality_var = tk.StringVar(value="192")
        self.template_var = tk.StringVar(value="%(title)s [%(id)s].%(ext)s")
        self.cookies_var = tk.StringVar(value="None")

        self.playlist_var = tk.BooleanVar(value=False)
        self.metadata_var = tk.BooleanVar(value=True)
        self.thumbnail_var = tk.BooleanVar(value=True)
        self.restrict_var = tk.BooleanVar(value=False)
        self.overwrite_var = tk.BooleanVar(value=False)
        self.keep_video_var = tk.BooleanVar(value=False)
        self.subfolder_var = tk.BooleanVar(value=False)

        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0.0)

        self._build_ui()
        self.after(100, self._process_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=16)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)

        ttk.Label(
            outer,
            text="yt-dlp MP3 Downloader",
            font=("Helvetica Neue", 20, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 14))

        source = ttk.LabelFrame(outer, text="Source", padding=12)
        source.grid(row=1, column=0, sticky="ew")
        source.columnconfigure(0, weight=1)

        ttk.Label(source, text="Video or playlist URL").grid(
            row=0, column=0, sticky="w"
        )
        self.url_entry = ttk.Entry(source, textvariable=self.url_var)
        self.url_entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        destination = ttk.LabelFrame(outer, text="Destination", padding=12)
        destination.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        destination.columnconfigure(0, weight=1)

        ttk.Label(destination, text="Save files in").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Entry(destination, textvariable=self.output_var).grid(
            row=1, column=0, sticky="ew", pady=(4, 0)
        )
        ttk.Button(destination, text="Choose…", command=self._choose_folder).grid(
            row=1, column=1, padx=(8, 0), pady=(4, 0)
        )

        ttk.Label(destination, text="Filename template").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(12, 0)
        )
        ttk.Entry(destination, textvariable=self.template_var).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(4, 0)
        )

        settings = ttk.LabelFrame(outer, text="Download settings", padding=12)
        settings.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        for col in range(4):
            settings.columnconfigure(col, weight=1)

        ttk.Label(settings, text="MP3 quality").grid(row=0, column=0, sticky="w")
        quality = ttk.Combobox(
            settings,
            textvariable=self.quality_var,
            values=("320", "256", "192", "160", "128"),
            state="readonly",
            width=9,
        )
        quality.grid(row=1, column=0, sticky="w", pady=(4, 8))
        ttk.Label(settings, text="kbps").grid(row=1, column=1, sticky="w")

        ttk.Label(settings, text="Browser cookies").grid(
            row=0, column=2, sticky="w"
        )
        cookies = ttk.Combobox(
            settings,
            textvariable=self.cookies_var,
            values=("None", "Safari", "Chrome", "Firefox", "Brave"),
            state="readonly",
            width=12,
        )
        cookies.grid(row=1, column=2, columnspan=2, sticky="w", pady=(4, 8))

        checks = [
            ("Download playlist", self.playlist_var),
            ("Embed metadata", self.metadata_var),
            ("Embed thumbnail", self.thumbnail_var),
            ("Restrict filenames", self.restrict_var),
            ("Overwrite existing files", self.overwrite_var),
            ("Keep original media file", self.keep_video_var),
            ("Playlist-named subfolder", self.subfolder_var),
        ]
        for i, (label, variable) in enumerate(checks):
            row = 2 + i // 2
            column = (i % 2) * 2
            ttk.Checkbutton(settings, text=label, variable=variable).grid(
                row=row, column=column, columnspan=2, sticky="w", pady=3
            )

        progress_box = ttk.LabelFrame(outer, text="Progress", padding=12)
        progress_box.grid(row=4, column=0, sticky="nsew", pady=(12, 0))
        progress_box.columnconfigure(0, weight=1)
        progress_box.rowconfigure(2, weight=1)
        outer.rowconfigure(4, weight=1)

        self.progress = ttk.Progressbar(
            progress_box,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
        )
        self.progress.grid(row=0, column=0, sticky="ew")

        ttk.Label(progress_box, textvariable=self.status_var).grid(
            row=1, column=0, sticky="w", pady=(6, 8)
        )

        self.log = tk.Text(
            progress_box,
            height=10,
            wrap="word",
            state="disabled",
            font=("Menlo", 11),
        )
        self.log.grid(row=2, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            progress_box, orient="vertical", command=self.log.yview
        )
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(outer)
        actions.grid(row=5, column=0, sticky="ew", pady=(12, 0))
        actions.columnconfigure(0, weight=1)

        self.download_button = ttk.Button(
            actions, text="Download MP3", command=self._start_download
        )
        self.download_button.grid(row=0, column=1)

        self.cancel_button = ttk.Button(
            actions, text="Cancel", command=self._cancel_download, state="disabled"
        )
        self.cancel_button.grid(row=0, column=2, padx=(8, 0))

        self.url_entry.focus_set()

    def _choose_folder(self) -> None:
        selected = filedialog.askdirectory(
            initialdir=self.output_var.get() or str(Path.home())
        )
        if selected:
            self.output_var.set(selected)

    def _append_log(self, text: str) -> None:
        text = text.strip()
        if not text:
            return
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_running(self, running: bool) -> None:
        self.download_button.configure(state="disabled" if running else "normal")
        self.cancel_button.configure(state="normal" if running else "disabled")
        self.url_entry.configure(state="disabled" if running else "normal")

    def _validate_environment(self) -> bool:
        if yt_dlp is None:
            messagebox.showerror(
                "yt-dlp is missing",
                "Install it with:\n\npython -m pip install -U \"yt-dlp[default]\"",
            )
            return False

        if shutil.which("ffmpeg") is None:
            system = platform.system()
            if system == "Darwin":
                install_hint = "Install FFmpeg with Homebrew:\n\nbrew install ffmpeg"
            elif system == "Windows":
                install_hint = (
                    "Install FFmpeg and add its bin folder to PATH.\n\n"
                    "See BUILD_WINDOWS.md in the project for detailed instructions."
                )
            else:
                install_hint = (
                    "Install FFmpeg using your system package manager and make sure "
                    "the ffmpeg executable is available on PATH."
                )

            messagebox.showerror("FFmpeg is missing", install_hint)
            return False

        return True

    def _start_download(self) -> None:
        if not self._validate_environment():
            return

        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("URL required", "Paste a video or playlist URL.")
            return

        output = Path(self.output_var.get()).expanduser()
        try:
            output.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Invalid destination", str(exc))
            return

        template = self.template_var.get().strip()
        if not template:
            messagebox.showwarning(
                "Filename template required", "Enter a filename template."
            )
            return

        self.cancel_event.clear()
        self.progress_var.set(0)
        self.status_var.set("Starting…")
        self._append_log(f"Destination: {output}")
        self._set_running(True)

        options = self._build_options(output, template)
        self.worker = threading.Thread(
            target=self._download_worker,
            args=(url, options),
            daemon=True,
        )
        self.worker.start()

    def _build_options(self, output: Path, template: str) -> dict[str, Any]:
        if self.subfolder_var.get() and self.playlist_var.get():
            output_template = str(
                output / "%(playlist_title|Playlist)s" / template
            )
        else:
            output_template = str(output / template)

        postprocessors: list[dict[str, Any]] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": self.quality_var.get(),
            }
        ]

        if self.metadata_var.get():
            postprocessors.append({"key": "FFmpegMetadata"})

        if self.thumbnail_var.get():
            postprocessors.append({"key": "EmbedThumbnail"})

        options: dict[str, Any] = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "noplaylist": not self.playlist_var.get(),
            "ignoreerrors": self.playlist_var.get(),
            "continuedl": True,
            "retries": 10,
            "fragment_retries": 10,
            "overwrites": self.overwrite_var.get(),
            "restrictfilenames": self.restrict_var.get(),
            "writethumbnail": self.thumbnail_var.get(),
            "keepvideo": self.keep_video_var.get(),
            "postprocessors": postprocessors,
            "progress_hooks": [self._progress_hook],
            "postprocessor_hooks": [self._postprocessor_hook],
            "logger": YTDLPLogger(self.events),
            "quiet": True,
            "no_warnings": False,
        }

        browser = self.cookies_var.get().lower()
        if browser != "none":
            options["cookiesfrombrowser"] = (browser,)

        return options

    def _progress_hook(self, data: dict[str, Any]) -> None:
        if self.cancel_event.is_set():
            raise DownloadCancelled("Download cancelled by user.")

        status = data.get("status")
        if status == "downloading":
            downloaded = data.get("downloaded_bytes", 0)
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            filename = Path(data.get("filename", "")).name

            if total:
                percent = max(0.0, min(100.0, downloaded * 100.0 / total))
                self.events.put(("progress", percent))
            else:
                self.events.put(("pulse", None))

            speed = data.get("_speed_str", "").strip()
            eta = data.get("_eta_str", "").strip()
            detail = " • ".join(
                part for part in (speed, f"ETA {eta}" if eta else "") if part
            )
            self.events.put(
                ("status", f"Downloading {filename}" + (f" — {detail}" if detail else ""))
            )

        elif status == "finished":
            self.events.put(("progress", 100.0))
            self.events.put(("status", "Download complete; converting to MP3…"))

        elif status == "error":
            self.events.put(("status", "A download error occurred."))

    def _postprocessor_hook(self, data: dict[str, Any]) -> None:
        if self.cancel_event.is_set():
            raise DownloadCancelled("Download cancelled by user.")

        name = data.get("postprocessor", "Post-processing")
        status = data.get("status")
        if status == "started":
            self.events.put(("status", f"{name}…"))
        elif status == "finished":
            self.events.put(("log", f"Finished: {name}"))

    def _download_worker(self, url: str, options: dict[str, Any]) -> None:
        try:
            assert yt_dlp is not None
            with yt_dlp.YoutubeDL(options) as downloader:
                result = downloader.download([url])

            if self.cancel_event.is_set():
                self.events.put(("cancelled", None))
            elif result == 0:
                self.events.put(("complete", None))
            else:
                self.events.put(("error", "One or more downloads failed."))

        except DownloadCancelled:
            self.events.put(("cancelled", None))
        except Exception as exc:
            if self.cancel_event.is_set():
                self.events.put(("cancelled", None))
            else:
                self.events.put(("error", str(exc)))

    def _cancel_download(self) -> None:
        self.cancel_event.set()
        self.cancel_button.configure(state="disabled")
        self.status_var.set("Cancelling at the next safe point…")
        self._append_log("Cancellation requested.")

    def _process_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()

                if event == "progress":
                    self.progress.stop()
                    self.progress.configure(mode="determinate")
                    self.progress_var.set(float(payload))

                elif event == "pulse":
                    if str(self.progress.cget("mode")) != "indeterminate":
                        self.progress.configure(mode="indeterminate")
                        self.progress.start(12)

                elif event == "status":
                    self.status_var.set(str(payload))

                elif event == "log":
                    self._append_log(str(payload))

                elif event == "complete":
                    self.progress.stop()
                    self.progress.configure(mode="determinate")
                    self.progress_var.set(100)
                    self.status_var.set("Finished")
                    self._append_log("All requested downloads finished.")
                    self._set_running(False)
                    messagebox.showinfo("Finished", "The MP3 download is complete.")

                elif event == "cancelled":
                    self.progress.stop()
                    self.progress.configure(mode="determinate")
                    self.status_var.set("Cancelled")
                    self._append_log("Download cancelled.")
                    self._set_running(False)

                elif event == "error":
                    self.progress.stop()
                    self.progress.configure(mode="determinate")
                    self.status_var.set("Failed")
                    self._append_log(f"Failed: {payload}")
                    self._set_running(False)
                    messagebox.showerror("Download failed", str(payload))

        except queue.Empty:
            pass

        self.after(100, self._process_events)

    def _on_close(self) -> None:
        if self.worker and self.worker.is_alive():
            if not messagebox.askyesno(
                "Quit?",
                "A download is active. Cancel it and close the app?",
            ):
                return
            self.cancel_event.set()
        self.destroy()


def main() -> None:
    app = MP3DownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
