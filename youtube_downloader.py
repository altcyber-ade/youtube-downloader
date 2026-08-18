#!/usr/bin/env python3
"""Cross-platform yt-dlp MP3 downloader GUI."""

from __future__ import annotations

import platform
import queue
import shutil
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

# Import explicitly so PyInstaller can see the provider plugin.
try:
    import yt_dlp_plugins.extractor.getpot_wpc as _wpc_plugin  # noqa: F401
except Exception:
    _wpc_plugin = None

APP_VERSION = "0.2.0"


class DownloadCancelled(Exception):
    pass


class YTDLPLogger:
    IMPORTANT_PREFIXES = (
        "[youtube]",
        "[debug] [youtube]",
        "[debug] JS runtimes",
        "[debug] Plugin directories",
        "[debug] Extractor Plugins",
    )

    def __init__(self, events: queue.Queue[tuple[str, Any]], verbose: bool) -> None:
        self.events = events
        self.verbose = verbose

    def debug(self, message: str) -> None:
        if self.verbose or message.startswith(self.IMPORTANT_PREFIXES):
            self.events.put(("log", message))
        elif not message.startswith("[debug]"):
            self.events.put(("log", message))

    def warning(self, message: str) -> None:
        self.events.put(("log", f"Warning: {message}"))

    def error(self, message: str) -> None:
        self.events.put(("log", f"Error: {message}"))


class MP3DownloaderApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"yt-dlp MP3 Downloader {APP_VERSION}")
        self.geometry("820x800")
        self.minsize(720, 680)

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
        self.youtube_compat_var = tk.BooleanVar(value=True)
        self.force_ipv4_var = tk.BooleanVar(value=False)
        self.verbose_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0.0)

        self._build_ui()
        self.after(100, self._process_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=16)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(5, weight=1)

        ttk.Label(outer, text=f"yt-dlp MP3 Downloader {APP_VERSION}", font=("Helvetica Neue", 20, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 14))

        source = ttk.LabelFrame(outer, text="Source", padding=12)
        source.grid(row=1, column=0, sticky="ew")
        source.columnconfigure(0, weight=1)
        ttk.Label(source, text="Video or playlist URL").grid(row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(source, textvariable=self.url_var)
        self.url_entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        destination = ttk.LabelFrame(outer, text="Destination", padding=12)
        destination.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        destination.columnconfigure(0, weight=1)
        ttk.Label(destination, text="Save files in").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Entry(destination, textvariable=self.output_var).grid(row=1, column=0, sticky="ew", pady=(4, 0))
        ttk.Button(destination, text="Choose…", command=self._choose_folder).grid(row=1, column=1, padx=(8, 0), pady=(4, 0))
        ttk.Label(destination, text="Filename template").grid(row=2, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Entry(destination, textvariable=self.template_var).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        settings = ttk.LabelFrame(outer, text="Download settings", padding=12)
        settings.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        for col in range(4):
            settings.columnconfigure(col, weight=1)

        ttk.Label(settings, text="MP3 quality").grid(row=0, column=0, sticky="w")
        ttk.Combobox(settings, textvariable=self.quality_var, values=("320", "256", "192", "160", "128"), state="readonly", width=9).grid(row=1, column=0, sticky="w", pady=(4, 8))
        ttk.Label(settings, text="kbps").grid(row=1, column=1, sticky="w")
        ttk.Label(settings, text="Browser cookies").grid(row=0, column=2, sticky="w")
        ttk.Combobox(settings, textvariable=self.cookies_var, values=("None", "Safari", "Chrome", "Firefox", "Brave"), state="readonly", width=12).grid(row=1, column=2, columnspan=2, sticky="w", pady=(4, 8))

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
            ttk.Checkbutton(settings, text=label, variable=variable).grid(row=2 + i // 2, column=(i % 2) * 2, columnspan=2, sticky="w", pady=3)

        compatibility = ttk.LabelFrame(outer, text="YouTube compatibility", padding=12)
        compatibility.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        ttk.Checkbutton(compatibility, text="Use mweb + automatic PO-token provider (recommended)", variable=self.youtube_compat_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(compatibility, text="Force IPv4", variable=self.force_ipv4_var).grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Checkbutton(compatibility, text="Verbose yt-dlp diagnostics", variable=self.verbose_var).grid(row=2, column=0, sticky="w", pady=(4, 0))
        ttk.Label(compatibility, text="PO-token mode uses Chrome/Chromium briefly when YouTube requests a token.").grid(row=3, column=0, sticky="w", pady=(6, 0))

        progress_box = ttk.LabelFrame(outer, text="Progress", padding=12)
        progress_box.grid(row=5, column=0, sticky="nsew", pady=(12, 0))
        progress_box.columnconfigure(0, weight=1)
        progress_box.rowconfigure(2, weight=1)
        self.progress = ttk.Progressbar(progress_box, variable=self.progress_var, maximum=100, mode="determinate")
        self.progress.grid(row=0, column=0, sticky="ew")
        ttk.Label(progress_box, textvariable=self.status_var).grid(row=1, column=0, sticky="w", pady=(6, 8))
        log_font = "Menlo" if platform.system() == "Darwin" else "TkFixedFont"
        self.log = tk.Text(progress_box, height=11, wrap="word", state="disabled", font=(log_font, 10))
        self.log.grid(row=2, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(progress_box, orient="vertical", command=self.log.yview)
        scrollbar.grid(row=2, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(outer)
        actions.grid(row=6, column=0, sticky="ew", pady=(12, 0))
        actions.columnconfigure(0, weight=1)
        self.download_button = ttk.Button(actions, text="Download MP3", command=self._start_download)
        self.download_button.grid(row=0, column=1)
        self.cancel_button = ttk.Button(actions, text="Cancel", command=self._cancel_download, state="disabled")
        self.cancel_button.grid(row=0, column=2, padx=(8, 0))
        self.url_entry.focus_set()

    def _choose_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_var.get() or str(Path.home()))
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

    def _chrome_available(self) -> bool:
        paths: list[str] = []
        if platform.system() == "Darwin":
            paths += [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
            ]
        elif platform.system() == "Windows":
            paths += [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
        return any(Path(p).exists() for p in paths) or bool(shutil.which("google-chrome") or shutil.which("chromium"))

    def _validate_environment(self) -> bool:
        if yt_dlp is None:
            messagebox.showerror("yt-dlp is missing", "Install dependencies with:\n\npython -m pip install -U -r requirements.txt")
            return False
        if shutil.which("ffmpeg") is None:
            if platform.system() == "Darwin":
                hint = "Install FFmpeg with Homebrew:\n\nbrew install ffmpeg"
            elif platform.system() == "Windows":
                hint = "Install FFmpeg and add its bin folder to PATH.\n\nSee BUILD_WINDOWS.md."
            else:
                hint = "Install FFmpeg and make sure ffmpeg is on PATH."
            messagebox.showerror("FFmpeg is missing", hint)
            return False
        if self.youtube_compat_var.get():
            if _wpc_plugin is None:
                messagebox.showerror("PO-token provider is missing", "Install/update dependencies:\n\npython -m pip install -U -r requirements.txt")
                return False
            if not self._chrome_available() and not messagebox.askyesno("Chrome/Chromium not detected", "The PO-token provider requires Chrome or Chromium. Continue anyway?"):
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
            messagebox.showwarning("Filename template required", "Enter a filename template.")
            return

        self.cancel_event.clear()
        self.progress_var.set(0)
        self.status_var.set("Starting…")
        version = getattr(getattr(yt_dlp, "version", None), "__version__", "unknown")
        self._append_log(f"yt-dlp MP3 Downloader {APP_VERSION}")
        self._append_log(f"yt-dlp version: {version}")
        self._append_log(f"Destination: {output}")
        if self.youtube_compat_var.get():
            self._append_log("YouTube compatibility: mweb + WebPoClient PO-token provider")
        if self.force_ipv4_var.get():
            self._append_log("Network: forcing IPv4")
        self._set_running(True)
        options = self._build_options(output, template)
        self.worker = threading.Thread(target=self._download_worker, args=(url, options), daemon=True)
        self.worker.start()

    def _build_options(self, output: Path, template: str) -> dict[str, Any]:
        output_template = str(output / "%(playlist_title|Playlist)s" / template) if self.subfolder_var.get() and self.playlist_var.get() else str(output / template)
        postprocessors: list[dict[str, Any]] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": self.quality_var.get()}]
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
            "logger": YTDLPLogger(self.events, self.verbose_var.get()),
            "quiet": not self.verbose_var.get(),
            "verbose": self.verbose_var.get(),
            "no_warnings": False,
        }
        if self.youtube_compat_var.get():
            options["extractor_args"] = {"youtube": {"player_client": ["mweb"]}}
        if self.force_ipv4_var.get():
            options["source_address"] = "0.0.0.0"
        browser = self.cookies_var.get().lower()
        if browser != "none":
            options["cookiesfrombrowser"] = (browser,)
        return options

    def _progress_hook(self, data: dict[str, Any]) -> None:
        if self.cancel_event.is_set():
            raise DownloadCancelled()
        status = data.get("status")
        if status == "downloading":
            downloaded = data.get("downloaded_bytes", 0)
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            filename = Path(data.get("filename", "")).name
            if total:
                self.events.put(("progress", max(0.0, min(100.0, downloaded * 100.0 / total))))
            else:
                self.events.put(("pulse", None))
            speed = data.get("_speed_str", "").strip()
            eta = data.get("_eta_str", "").strip()
            detail = " • ".join(x for x in (speed, f"ETA {eta}" if eta else "") if x)
            self.events.put(("status", f"Downloading {filename}" + (f" — {detail}" if detail else "")))
        elif status == "finished":
            self.events.put(("progress", 100.0))
            self.events.put(("status", "Download complete; converting to MP3…"))

    def _postprocessor_hook(self, data: dict[str, Any]) -> None:
        if self.cancel_event.is_set():
            raise DownloadCancelled()
        name = data.get("postprocessor", "Post-processing")
        if data.get("status") == "started":
            self.events.put(("status", f"{name}…"))
        elif data.get("status") == "finished":
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
            self.events.put(("cancelled", None) if self.cancel_event.is_set() else ("error", str(exc)))

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
                    self.progress.stop(); self.progress.configure(mode="determinate"); self.progress_var.set(float(payload))
                elif event == "pulse":
                    if str(self.progress.cget("mode")) != "indeterminate":
                        self.progress.configure(mode="indeterminate"); self.progress.start(12)
                elif event == "status":
                    self.status_var.set(str(payload))
                elif event == "log":
                    self._append_log(str(payload))
                elif event == "complete":
                    self.progress.stop(); self.progress.configure(mode="determinate"); self.progress_var.set(100)
                    self.status_var.set("Finished"); self._append_log("All requested downloads finished."); self._set_running(False)
                    messagebox.showinfo("Finished", "The MP3 download is complete.")
                elif event == "cancelled":
                    self.progress.stop(); self.progress.configure(mode="determinate"); self.status_var.set("Cancelled"); self._append_log("Download cancelled."); self._set_running(False)
                elif event == "error":
                    self.progress.stop(); self.progress.configure(mode="determinate"); self.status_var.set("Failed"); self._append_log(f"Failed: {payload}"); self._set_running(False)
                    messagebox.showerror("Download failed", str(payload))
        except queue.Empty:
            pass
        self.after(100, self._process_events)

    def _on_close(self) -> None:
        if self.worker and self.worker.is_alive():
            if not messagebox.askyesno("Quit?", "A download is active. Cancel it and close the app?"):
                return
            self.cancel_event.set()
        self.destroy()


def main() -> None:
    MP3DownloaderApp().mainloop()


if __name__ == "__main__":
    main()
