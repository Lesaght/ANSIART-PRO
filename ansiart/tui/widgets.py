"""Custom Textual widgets: ArtViewer and SettingsPanel — dark neon theme."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Optional

from rich.style import Style
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Rule, Select, Static, Switch

from ansiart.core import (
    GRADIENT_PRESET_NAMES,
    GRADIENT_PRESETS,
    ConversionConfig,
    AsciiConverter,
)

# ── Palette (mirrors app.py CSS) ───────────────────────────────────────────────
_CYAN   = "#00d4ff"
_PURPLE = "#9d4eff"
_GREEN  = "#00e676"
_AMBER  = "#ffab40"
_RED    = "#ff5252"
_TEXT   = "#c8c8e8"
_MUTED  = "#6868a0"
_SECHDR = "#1c1c38"


# ── Welcome placeholder ────────────────────────────────────────────────────────

def _build_placeholder() -> Text:
    t = Text(no_wrap=True)
    cyan  = Style(color=_CYAN,   bold=True)
    muted = Style(color=_MUTED)
    dim   = Style(color=_MUTED,  dim=True)
    key   = Style(color=_CYAN,   bold=True)

    t.append("\n")
    t.append("  ╔══════════════════════════════════════════════╗\n", cyan)
    t.append("  ║                                              ║\n", cyan)
    t.append("  ║   ", cyan)
    t.append("▄▄ ▄  ▄ ▄▄ ▄ ▄ ▄▄ ▄▀▄ ▄▀▄▄", Style(color=_CYAN, bold=True))
    t.append("              ║\n", cyan)
    t.append("  ║   ", cyan)
    t.append("█▀█ █▀▄ ▀▀▄ █ ▀ █ █▀█ █▀█ ▀▀▄", Style(color="#7b8fff", bold=True))
    t.append("            ║\n", cyan)
    t.append("  ║   ", cyan)
    t.append("▀  ▀ ▀ ▀▀▀ ▀   ▀ ▀ ▀ ▀ ▀ ▀▀▀", Style(color=_PURPLE, bold=True))
    t.append("            ║\n", cyan)
    t.append("  ║                                              ║\n", cyan)
    t.append("  ║          ", cyan)
    t.append("P R O   v 1 . 0 . 0", Style(color=_AMBER, bold=True))
    t.append("                   ║\n", cyan)
    t.append("  ║                                              ║\n", cyan)
    t.append("  ╚══════════════════════════════════════════════╝\n", cyan)
    t.append("\n")
    t.append("  Press ", muted); t.append("O", key); t.append(" to open a file\n", muted)
    t.append("  Press ", muted); t.append("F1", key); t.append(" for help\n\n", muted)
    t.append("  Supports: ", dim)
    t.append("Images", Style(color=_GREEN)); t.append("  ·  ", dim)
    t.append("GIF / Animated WebP / APNG", Style(color=_AMBER)); t.append("  ·  ", dim)
    t.append("Video\n", Style(color=_RED))
    t.append("  TrueColor ANSI  ·  Monochrome  ·  8 gradient presets\n", dim)
    return t


# ── ArtViewer ──────────────────────────────────────────────────────────────────

class ArtViewer(Widget):
    """Scrollable canvas that renders AsciiFrame content as Rich Text."""

    BORDER_TITLE    = "  Canvas  "
    BORDER_SUBTITLE = "  No file  "

    DEFAULT_CSS = """
    ArtViewer {
        overflow: auto auto;
        padding: 0;
    }
    ArtViewer Static {
        width: auto;
        height: auto;
        padding: 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(_build_placeholder(), id="art-content")

    def update_frame(self, content: Text) -> None:
        """Replace displayed frame.  Thread-safe via call_from_thread."""
        self.query_one("#art-content", Static).update(content)

    def set_file_info(self, name: str, w: int, h: int, fmt: str, n: int) -> None:
        """Update the border titles with file metadata."""
        self.border_title    = f"  {name}  "
        dims = f"{w}×{h}" if w else ""
        frames = f"  {n} frames" if n > 1 else ""
        self.border_subtitle = f"  {dims}  {fmt}{frames}  "

    def show_placeholder(self) -> None:
        self.query_one("#art-content", Static).update(_build_placeholder())
        self.border_title    = "  Canvas  "
        self.border_subtitle = "  No file  "


# ── SettingsPanel ──────────────────────────────────────────────────────────────

class SettingsPanel(Widget):
    """Dark-neon settings panel with sectioned layout."""

    # ── outbound messages ──────────────────────────────────────────────────────

    class ConfigChanged(Message):
        def __init__(self, config: ConversionConfig) -> None:
            super().__init__()
            self.config = config

    class OpenFileRequested(Message):
        pass

    # ── reactive state ─────────────────────────────────────────────────────────

    display_fps:     reactive[float] = reactive(0.0)
    display_playing: reactive[bool]  = reactive(False)
    display_frame:   reactive[int]   = reactive(0)

    BORDER_TITLE = "  ⚙  Settings  "

    DEFAULT_CSS = """
    SettingsPanel {
        layout: vertical;
        padding: 0;
        overflow-y: auto;
        scrollbar-size: 1 1;
    }

    /* ── section headers ─────────── */
    SettingsPanel .sec {
        background: #1c1c38;
        color: #00d4ff;
        text-style: bold;
        padding: 0 2;
        width: 100%;
        height: 1;
        margin-top: 1;
    }

    /* ── switch rows ─────────────── */
    SettingsPanel .sw-row {
        height: 3;
        padding: 0 2;
        align: left middle;
    }
    SettingsPanel .sw-row Label {
        width: 1fr;
        color: #c8c8e8;
        content-align: left middle;
    }
    SettingsPanel .sw-row Switch {
        width: auto;
    }

    /* ── labelled inputs ─────────── */
    SettingsPanel .ctrl-label {
        color: #6868a0;
        padding: 0 2;
        margin-top: 1;
        height: 1;
    }
    SettingsPanel Input {
        margin: 0 1;
        border: tall #2a2a50;
        background: #0d0d20;
        color: #c8c8e8;
    }
    SettingsPanel Input:focus {
        border: tall #00d4ff;
    }
    SettingsPanel Select {
        margin: 0 1;
    }

    /* ── gradient preview ────────── */
    SettingsPanel #gradient-preview {
        height: 1;
        padding: 0 2;
        margin-bottom: 1;
    }

    /* ── status block ────────────── */
    SettingsPanel #status-label {
        color: #00e676;
        text-style: bold;
        padding: 0 2;
        height: 1;
    }
    SettingsPanel #fps-label {
        color: #9d4eff;
        padding: 0 2;
        height: 1;
    }
    SettingsPanel #frame-label {
        color: #6868a0;
        padding: 0 2;
        height: 1;
    }

    /* ── file info ───────────────── */
    SettingsPanel #file-name {
        color: #c8c8e8;
        text-style: bold;
        padding: 0 2;
        height: 1;
    }
    SettingsPanel #file-meta {
        color: #6868a0;
        padding: 0 2;
        height: 1;
        margin-bottom: 1;
    }

    /* ── open button ─────────────── */
    SettingsPanel Button {
        width: 1fr;
        margin: 1 1 0 1;
        background: #9d4eff;
        color: #ffffff;
        text-style: bold;
        border: none;
    }
    SettingsPanel Button:hover {
        background: #00d4ff;
        color: #000000;
    }
    SettingsPanel Button:focus {
        background: #00d4ff;
        color: #000000;
    }
    """

    def __init__(self, config: ConversionConfig, **kwargs) -> None:
        super().__init__(**kwargs)
        self._config = config

    def compose(self) -> ComposeResult:
        # ── DISPLAY ───────────────────────────────────────────────────────────
        yield Label("◆ DISPLAY", classes="sec")

        with Horizontal(classes="sw-row"):
            yield Label("TrueColor")
            yield Switch(value=self._config.color_mode, id="color-switch")

        with Horizontal(classes="sw-row"):
            yield Label("Invert gradient")
            yield Switch(value=self._config.invert, id="invert-switch")

        # ── OUTPUT ────────────────────────────────────────────────────────────
        yield Label("◆ OUTPUT", classes="sec")

        yield Label("Width (chars)", classes="ctrl-label")
        yield Input(value=str(self._config.target_width), id="width-input")

        yield Label("Gradient preset", classes="ctrl-label")
        opts = [(n.capitalize(), n) for n in GRADIENT_PRESET_NAMES]
        yield Select(options=opts, value="standard", id="gradient-select")
        yield Static(
            AsciiConverter.gradient_preview(self._config.gradient, self._config.color_mode),
            id="gradient-preview",
        )

        yield Label("Target FPS", classes="ctrl-label")
        yield Input(value=f"{self._config.target_fps:.1f}", id="fps-input")

        # ── STATUS ────────────────────────────────────────────────────────────
        yield Label("◆ PLAYBACK", classes="sec")
        yield Label("⏹  Stopped",      id="status-label")
        yield Label("FPS     --",       id="fps-label")
        yield Label("Frame   --",       id="frame-label")

        # ── FILE INFO ─────────────────────────────────────────────────────────
        yield Label("◆ FILE INFO", classes="sec")
        yield Label("No file loaded",   id="file-name")
        yield Label("",                 id="file-meta")

        # ── OPEN ──────────────────────────────────────────────────────────────
        yield Rule()
        yield Button("  Open File  O ", id="open-file-btn")

    # ── reactive watchers ──────────────────────────────────────────────────────

    def watch_display_fps(self, fps: float) -> None:
        try:
            self.query_one("#fps-label", Label).update(
                f"FPS     {fps:.1f}" if fps > 0 else "FPS     --"
            )
        except Exception:
            pass

    def watch_display_playing(self, playing: bool) -> None:
        try:
            lbl = self.query_one("#status-label", Label)
            if playing:
                lbl.styles.color = _GREEN
                lbl.update("▶  Playing")
            else:
                lbl.styles.color = _AMBER
                lbl.update("⏸  Paused")
        except Exception:
            pass

    def watch_display_frame(self, n: int) -> None:
        try:
            self.query_one("#frame-label", Label).update(
                f"Frame   #{n:04d}" if n > 0 else "Frame   --"
            )
        except Exception:
            pass

    # ── public setters (thread-safe via call_from_thread) ─────────────────────

    def set_fps(self, fps: float) -> None:
        self.display_fps = fps

    def set_playing(self, playing: bool) -> None:
        self.display_playing = playing

    def set_frame(self, n: int) -> None:
        self.display_frame = n

    def set_file_info(self, path: Optional[Path], w: int = 0, h: int = 0,
                      fmt: str = "", n_frames: int = 1) -> None:
        try:
            name_lbl = self.query_one("#file-name", Label)
            meta_lbl = self.query_one("#file-meta", Label)
            if path is None:
                name_lbl.update("No file loaded")
                meta_lbl.update("")
            else:
                name_lbl.update(path.name)
                dims   = f"{w}×{h}" if w else ""
                frames = f"  ·  {n_frames} frames" if n_frames > 1 else ""
                meta_lbl.update(f"{dims}  {fmt}{frames}")
        except Exception:
            pass

    def _refresh_gradient_preview(self) -> None:
        try:
            self.query_one("#gradient-preview", Static).update(
                AsciiConverter.gradient_preview(
                    self._config.gradient, self._config.color_mode
                )
            )
        except Exception:
            pass

    # ── Textual event handlers ─────────────────────────────────────────────────

    def on_switch_changed(self, event: Switch.Changed) -> None:
        event.stop()
        if event.switch.id == "color-switch":
            self._config = replace(self._config, color_mode=event.value)
        elif event.switch.id == "invert-switch":
            self._config = replace(self._config, invert=event.value)
        else:
            return
        self._refresh_gradient_preview()
        self.post_message(self.ConfigChanged(self._config))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        if event.input.id == "width-input":
            try:
                w = max(20, min(500, int(event.value)))
                self._config = replace(self._config, target_width=w)
                event.input.value = str(w)
            except ValueError:
                event.input.value = str(self._config.target_width)
                return
        elif event.input.id == "fps-input":
            try:
                fps = max(1.0, min(60.0, float(event.value)))
                self._config = replace(self._config, target_fps=fps)
                event.input.value = f"{fps:.1f}"
            except ValueError:
                event.input.value = f"{self._config.target_fps:.1f}"
                return
        else:
            return
        self.post_message(self.ConfigChanged(self._config))

    def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()
        if event.select.id == "gradient-select" and event.value is not Select.BLANK:
            gradient = GRADIENT_PRESETS.get(str(event.value), GRADIENT_PRESETS["standard"])
            self._config = replace(self._config, gradient=gradient)
            self._refresh_gradient_preview()
            self.post_message(self.ConfigChanged(self._config))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "open-file-btn":
            self.post_message(self.OpenFileRequested())
