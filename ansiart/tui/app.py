"""Main Textual Application — dark neon theme, layout, and async rendering loop."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header
from textual.worker import get_current_worker

from ansiart.core import (
    AsciiConverter,
    AsciiFrame,
    ConversionConfig,
    MediaInfo,
    MediaLoadError,
    MediaLoader,
    MediaType,
    UnsupportedMediaError,
    detect_media_type,
    probe_media,
)
from ansiart.tui.screens import FileSelectScreen, HelpScreen
from ansiart.tui.widgets import ArtViewer, SettingsPanel


class AnsiArtApp(App[None]):
    """Root Textual application for AnsiArt Pro."""

    TITLE     = "AnsiArt Pro"
    SUB_TITLE = "v1.0.0  ·  TrueColor ASCII Art Converter"

    BINDINGS = [
        Binding("o",     "open_file",       "Open"),
        Binding("space", "toggle_playback", "Play/Pause", show=True),
        Binding("r",     "reload",          "Reload"),
        Binding("s",     "save",            "Save"),
        Binding("f1",    "help",            "Help"),
        Binding("q",     "quit",            "Quit"),
    ]

    # ── Dark neon CSS ──────────────────────────────────────────────────────────
    CSS = """
    Screen {
        layout: horizontal;
        background: #0b0b14;
    }

    /* ── Header ─────────────────────────────────── */
    Header {
        background: #111128;
        color: #00d4ff;
        text-style: bold;
        height: 1;
    }
    Header .header--highlight {
        background: #9d4eff;
    }

    /* ── Footer ─────────────────────────────────── */
    Footer {
        background: #111128;
        color: #6868a0;
        height: 1;
    }
    Footer > .footer--key {
        background: #1c1c38;
        color: #00d4ff;
        text-style: bold;
    }
    Footer > .footer--description {
        color: #6868a0;
    }
    Footer > .footer--highlight {
        background: #9d4eff;
    }

    /* ── ArtViewer ───────────────────────────────── */
    ArtViewer {
        width: 3fr;
        height: 100%;
        border: round #00d4ff;
        border-title-color: #00d4ff;
        border-title-style: bold;
        border-subtitle-color: #6868a0;
        background: #0b0b14;
        scrollbar-color: #9d4eff;
        scrollbar-background: #111128;
        scrollbar-corner-color: #111128;
    }

    /* ── SettingsPanel ───────────────────────────── */
    SettingsPanel {
        width: 34;
        height: 100%;
        border: round #9d4eff;
        border-title-color: #9d4eff;
        border-title-style: bold;
        background: #0e0e1e;
        scrollbar-color: #9d4eff;
        scrollbar-background: #111128;
    }

    /* ── Scrollbar global ────────────────────────── */
    ScrollBar {
        background: #111128;
    }
    ScrollBar > .scrollbar--bar {
        color: #9d4eff;
    }

    /* ── Select widget ───────────────────────────── */
    Select {
        border: tall #2a2a50;
        background: #0d0d20;
    }
    Select:focus {
        border: tall #9d4eff;
    }
    SelectOverlay {
        border: round #9d4eff;
        background: #111128;
    }
    SelectOverlay > .option-list--option-highlighted {
        background: #1c1c38;
        color: #00d4ff;
    }

    /* ── Switch ──────────────────────────────────── */
    Switch.-on .switch--slider {
        color: #00d4ff;
    }
    Switch .switch--slider {
        color: #2a2a50;
    }

    /* ── Notifications ───────────────────────────── */
    Toast {
        background: #1c1c38;
        border: round #9d4eff;
        color: #c8c8e8;
    }

    /* ── Rule ────────────────────────────────────── */
    Rule {
        color: #2a2a50;
        margin: 0 1;
    }
    """

    # ── Construction ───────────────────────────────────────────────────────────

    def __init__(
        self,
        initial_file: Optional[Path] = None,
        config: Optional[ConversionConfig] = None,
    ) -> None:
        super().__init__()
        self.config: ConversionConfig = config or ConversionConfig()
        self._current_file: Optional[Path] = initial_file
        self._is_playing: bool = True
        self._frame_count: int = 0
        self._last_frame: Optional[AsciiFrame] = None

    # ── Layout ─────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ArtViewer(id="art-viewer")
        yield SettingsPanel(self.config, id="settings-panel")
        yield Footer()

    def on_mount(self) -> None:
        if self._current_file:
            self._load_and_render(self._current_file)
        else:
            self.query_one(ArtViewer).show_placeholder()

    # ── Actions ────────────────────────────────────────────────────────────────

    def action_open_file(self) -> None:
        start = self._current_file.parent if self._current_file else Path.home()
        self.push_screen(FileSelectScreen(start), callback=self._on_file_selected)

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_toggle_playback(self) -> None:
        self._is_playing = not self._is_playing
        panel = self.query_one(SettingsPanel)
        panel.set_playing(self._is_playing)
        if self._is_playing and self._current_file:
            self._start_rendering(self._current_file)

    def action_reload(self) -> None:
        if self._current_file:
            self._is_playing = True
            self._frame_count = 0
            self._load_and_render(self._current_file)
        else:
            self.notify("No file loaded — press  O  to open one.", severity="warning")

    def action_save(self) -> None:
        if self._last_frame is None or self._current_file is None:
            self.notify("No frame to save — load a file first.", severity="warning")
            return
        output = self._current_file.with_stem(self._current_file.stem + "_ascii").with_suffix(".txt")
        try:
            text = AsciiConverter.frame_to_plain_text(self._last_frame)
            output.write_text(text, encoding="utf-8")
            self.notify(f"Saved → {output.name}", severity="information")
        except Exception as exc:
            self.notify(f"Save failed: {exc}", severity="error")

    # ── Message handlers ───────────────────────────────────────────────────────

    def on_settings_panel_config_changed(self, msg: SettingsPanel.ConfigChanged) -> None:
        self.config = msg.config
        if self._current_file and self._is_playing:
            self._start_rendering(self._current_file)

    def on_settings_panel_open_file_requested(self, _: SettingsPanel.OpenFileRequested) -> None:
        self.action_open_file()

    # ── File-selection callback ────────────────────────────────────────────────

    def _on_file_selected(self, path: Optional[Path]) -> None:
        if path is None:
            return
        if not path.exists():
            self.notify(f"File not found:\n{path}", severity="error")
            return
        self._current_file = path
        self._is_playing = True
        self._frame_count = 0
        self.query_one(SettingsPanel).set_playing(True)
        self._load_and_render(path)

    def _load_and_render(self, path: Path) -> None:
        """Probe metadata → update UI labels → start the render worker."""
        try:
            info = probe_media(path)
        except UnsupportedMediaError as exc:
            self.notify(str(exc), severity="error")
            return
        except Exception:
            info = MediaInfo("image", 0, 0, 1, path.suffix.lstrip(".").upper())

        viewer = self.query_one(ArtViewer)
        panel  = self.query_one(SettingsPanel)
        viewer.set_file_info(path.name, info.width, info.height, info.format_name, info.n_frames)
        panel.set_file_info(path, info.width, info.height, info.format_name, info.n_frames)
        self._start_rendering(path)

    # ── Thread-safe UI helpers ─────────────────────────────────────────────────

    def _ui_frame(self, text) -> None:
        self._frame_count += 1
        self.query_one(ArtViewer).update_frame(text)
        self.query_one(SettingsPanel).set_frame(self._frame_count)

    def _ui_fps(self, fps: float) -> None:
        self.query_one(SettingsPanel).set_fps(fps)

    # ── Background rendering worker ────────────────────────────────────────────

    @work(thread=True, exclusive=True, name="renderer")
    def _start_rendering(self, path: Path) -> None:
        """Drives the full media → ASCII → UI pipeline in a background thread.

        exclusive=True automatically cancels any previous renderer when a new
        file or settings change triggers a new render.
        """
        worker    = get_current_worker()
        converter = AsciiConverter()

        try:
            media_type = detect_media_type(path)
        except UnsupportedMediaError as exc:
            self.call_from_thread(self.notify, str(exc), severity="error")
            return

        try:
            if media_type == MediaType.IMAGE:
                self._loop_image(path, converter)
            elif media_type == MediaType.GIF:
                self._loop_animated(path, converter, worker)
            elif media_type == MediaType.VIDEO:
                self._loop_video(path, converter, worker)
        except FileNotFoundError as exc:
            self.call_from_thread(self.notify, str(exc), severity="error")
        except (MediaLoadError, ImportError) as exc:
            self.call_from_thread(self.notify, str(exc), severity="error")
        except Exception as exc:
            self.call_from_thread(self.notify, f"Render error: {exc}", severity="error")

    # ── Render loops (execute inside the worker thread) ────────────────────────

    def _loop_image(self, path: Path, conv: AsciiConverter) -> None:
        img   = MediaLoader.load_image(path)
        frame = conv.image_to_frame(img, self.config)
        rich  = conv.frame_to_rich_text(frame, self.config.color_mode)
        self._last_frame = frame
        self.call_from_thread(self._ui_frame, rich)
        self.call_from_thread(self._ui_fps, 0.0)

    def _loop_animated(self, path: Path, conv: AsciiConverter, worker) -> None:
        """Loop GIF / animated WebP / APNG indefinitely, honouring frame timing."""
        rolling: list[float] = []

        while not worker.is_cancelled and self._is_playing:
            for img, duration in MediaLoader.iter_animated_frames(path):
                if worker.is_cancelled or not self._is_playing:
                    return
                t0    = time.perf_counter()
                frame = conv.image_to_frame(img, self.config)
                rich  = conv.frame_to_rich_text(frame, self.config.color_mode)
                self._last_frame = frame
                self.call_from_thread(self._ui_frame, rich)
                elapsed = time.perf_counter() - t0
                wait    = max(0.0, duration - elapsed)
                if wait:
                    time.sleep(wait)
                rolling.append(time.perf_counter() - t0)
                if len(rolling) >= 6:
                    avg = sum(rolling[-6:]) / 6
                    self.call_from_thread(self._ui_fps, 1.0 / avg if avg else 0.0)

    def _loop_video(self, path: Path, conv: AsciiConverter, worker) -> None:
        """Render video frames at configured target FPS."""
        rolling: list[float] = []

        for img, duration in MediaLoader.iter_video_frames(path, self.config):
            if worker.is_cancelled or not self._is_playing:
                return
            t0    = time.perf_counter()
            frame = conv.image_to_frame(img, self.config)
            rich  = conv.frame_to_rich_text(frame, self.config.color_mode)
            self._last_frame = frame
            self.call_from_thread(self._ui_frame, rich)
            elapsed = time.perf_counter() - t0
            wait    = max(0.0, duration - elapsed)
            if wait:
                time.sleep(wait)
            rolling.append(time.perf_counter() - t0)
            if len(rolling) >= 10:
                avg = sum(rolling[-10:]) / 10
                self.call_from_thread(self._ui_fps, 1.0 / avg if avg else 0.0)
