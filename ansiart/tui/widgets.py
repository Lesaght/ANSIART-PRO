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

from ansiart import i18n
from ansiart.core import (
    GRADIENT_PRESET_NAMES,
    GRADIENT_PRESETS,
    ConversionConfig,
    AsciiConverter,
)


_CYAN   = "#00d4ff"
_PURPLE = "#9d4eff"
_GREEN  = "#00e676"
_AMBER  = "#ffab40"
_RED    = "#ff5252"
_TEXT   = "#c8c8e8"
_MUTED  = "#6868a0"
_SECHDR = "#1c1c38"


def _build_placeholder() -> Text:
    t = Text(no_wrap=True)
    cyan  = Style(color=_CYAN,  bold=True)
    muted = Style(color=_MUTED)
    dim   = Style(color=_MUTED, dim=True)
    key   = Style(color=_CYAN,  bold=True)

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
    t.append("P R O   v 1 . 1 . 1", Style(color=_AMBER, bold=True))
    t.append("                   ║\n", cyan)
    t.append("  ║                                              ║\n", cyan)
    t.append("  ╚══════════════════════════════════════════════╝\n", cyan)
    t.append("\n")
    t.append(i18n.t("ph_press"), muted)
    t.append("O", key)
    t.append(i18n.t("ph_open_key"), muted)
    t.append(i18n.t("ph_press"), muted)
    t.append("C", key)
    t.append(i18n.t("ph_webcam_key"), muted)
    t.append(i18n.t("ph_press"), muted)
    t.append("F1", key)
    t.append(i18n.t("ph_help_key"), muted)
    t.append(i18n.t("ph_formats"), dim)
    t.append(i18n.t("ph_images"), Style(color=_GREEN))
    t.append("  ·  ", dim)
    t.append("GIF / Animated WebP / APNG", Style(color=_AMBER))
    t.append("  ·  ", dim)
    t.append(i18n.t("ph_video"), Style(color=_RED))
    t.append(i18n.t("ph_line1"), dim)
    t.append(i18n.t("ph_line2"), dim)
    return t


class ArtViewer(Widget):

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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._showing_placeholder = True
        self._file_info: Optional[tuple] = None

    def compose(self) -> ComposeResult:
        yield Static(_build_placeholder(), id="art-content")

    def on_mount(self) -> None:
        self.border_title    = i18n.t("canvas_title")
        self.border_subtitle = i18n.t("canvas_no_file")

    def update_frame(self, content: Text) -> None:
        self.query_one("#art-content", Static).update(content)

    def set_file_info(self, name: str, w: int, h: int, fmt: str, n: int) -> None:
        self._showing_placeholder = False
        self._file_info = (name, w, h, fmt, n)
        self.border_title = f"  {name}  "
        dims   = f"{w}×{h}" if w else ""
        frames = ("  " + i18n.t("n_frames").format(n=n)) if n > 1 else ""
        self.border_subtitle = f"  {dims}  {fmt}{frames}  "

    def show_placeholder(self) -> None:
        self._showing_placeholder = True
        self._file_info = None
        self.query_one("#art-content", Static).update(_build_placeholder())
        self.border_title    = i18n.t("canvas_title")
        self.border_subtitle = i18n.t("canvas_no_file")

    def refresh_lang(self) -> None:
        if self._showing_placeholder:
            self.show_placeholder()
        elif self._file_info:
            self.set_file_info(*self._file_info)


class SettingsPanel(Widget):

    class ConfigChanged(Message):
        def __init__(self, config: ConversionConfig) -> None:
            super().__init__()
            self.config = config

    class OpenFileRequested(Message):
        pass

    class LangChanged(Message):
        def __init__(self, lang: str) -> None:
            super().__init__()
            self.lang = lang

    display_fps:     reactive[float] = reactive(0.0)
    display_playing: reactive[bool]  = reactive(False)
    display_frame:   reactive[int]   = reactive(0)

    DEFAULT_CSS = """
    SettingsPanel {
        layout: vertical;
        padding: 0;
        overflow-y: auto;
        scrollbar-size: 1 1;
    }
    SettingsPanel .lang-row {
        height: 3;
        padding: 0 1;
        align: center middle;
        margin: 1 0 1 0;
    }
    SettingsPanel #lang-ru-btn,
    SettingsPanel #lang-en-btn {
        width: 1fr;
        min-width: 0;
        margin: 0;
        background: #1c1c38;
        color: #6868a0;
        border: none;
        text-style: bold;
    }
    SettingsPanel #lang-ru-btn {
        margin-right: 1;
    }
    SettingsPanel #lang-ru-btn.-active,
    SettingsPanel #lang-en-btn.-active {
        background: #9d4eff;
        color: #ffffff;
    }
    SettingsPanel .sec {
        background: #1c1c38;
        color: #00d4ff;
        text-style: bold;
        padding: 0 2;
        width: 100%;
        height: 1;
        margin-top: 1;
    }
    SettingsPanel .sw-row {
        height: 3;
        padding: 0 2;
        align: left middle;
    }
    SettingsPanel .sw-row Label {
        width: 1fr;
        color: #6868a0;
        content-align: left middle;
    }
    SettingsPanel .sw-row Switch {
        width: auto;
    }
    SettingsPanel .ctrl-label {
        color: #6868a0;
        padding: 0 2;
        margin-top: 1;
        height: 1;
    }
    SettingsPanel Input {
        margin: 0 1;
        border: tall #2a2a50;
        background: #0b0b14;
        color: #c8c8e8;
    }
    SettingsPanel Input:focus {
        border: tall #9d4eff;
    }
    SettingsPanel Select {
        margin: 0 1;
    }
    SettingsPanel #status-label {
        height: 1;
        padding: 0 2;
        margin-bottom: 1;
    }
    SettingsPanel #fps-label {
        color: #6868a0;
        text-style: bold;
        padding: 0 2;
        height: 1;
    }
    SettingsPanel #frame-label {
        color: #6868a0;
        padding: 0 2;
        height: 1;
    }
    SettingsPanel #speed-label {
        color: #6868a0;
        padding: 0 2;
        height: 1;
    }
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

    def on_mount(self) -> None:
        self.border_title = i18n.t("settings_border")
        self._update_lang_buttons()

    def compose(self) -> ComposeResult:
        with Horizontal(classes="lang-row"):
            yield Button("RU", id="lang-ru-btn")
            yield Button("EN", id="lang-en-btn")

        yield Label(i18n.t("sec_display"), classes="sec", id="sec-display")

        with Horizontal(classes="sw-row"):
            yield Label(i18n.t("lbl_truecolor"), id="lbl-truecolor")
            yield Switch(value=self._config.color_mode, id="color-switch")

        with Horizontal(classes="sw-row"):
            yield Label(i18n.t("lbl_invert"), id="lbl-invert")
            yield Switch(value=self._config.invert, id="invert-switch")

        with Horizontal(classes="sw-row"):
            yield Label(i18n.t("lbl_dither"), id="lbl-dither")
            yield Switch(value=self._config.dither, id="dither-switch")

        yield Label(i18n.t("sec_output"), classes="sec", id="sec-output")

        yield Label(i18n.t("lbl_width"), classes="ctrl-label", id="lbl-width-ctrl")
        yield Input(value=str(self._config.target_width), id="width-input")

        yield Label(i18n.t("lbl_gradient"), classes="ctrl-label", id="lbl-gradient-ctrl")
        opts = [(n.capitalize(), n) for n in GRADIENT_PRESET_NAMES]
        yield Select(options=opts, value="standard", id="gradient-select")
        yield Static(
            AsciiConverter.gradient_preview(self._config.gradient, self._config.color_mode),
            id="gradient-preview",
        )

        yield Label(i18n.t("lbl_custom_grad"), classes="ctrl-label", id="lbl-custom-grad-ctrl")
        yield Input(
            placeholder=i18n.t("ph_gradient"),
            id="custom-gradient-input",
        )

        yield Label(i18n.t("lbl_fps"), classes="ctrl-label", id="lbl-fps-ctrl")
        yield Input(value=f"{self._config.target_fps:.1f}", id="fps-input")

        yield Label(i18n.t("sec_adjust"), classes="sec", id="sec-adjust")

        yield Label(i18n.t("lbl_brightness"), classes="ctrl-label", id="lbl-brightness-ctrl")
        yield Input(value=f"{self._config.brightness:.2f}", id="brightness-input")

        yield Label(i18n.t("lbl_contrast"), classes="ctrl-label", id="lbl-contrast-ctrl")
        yield Input(value=f"{self._config.contrast:.2f}", id="contrast-input")

        yield Label(i18n.t("sec_animation"), classes="sec", id="sec-animation")

        with Horizontal(classes="sw-row"):
            yield Label(i18n.t("lbl_loop"), id="lbl-loop")
            yield Switch(value=self._config.loop, id="loop-switch")

        yield Label(i18n.t("sec_playback"), classes="sec", id="sec-playback")
        yield Label(i18n.t("status_stopped"),    id="status-label")
        yield Label(i18n.t("lbl_fps_none"),      id="fps-label")
        yield Label(i18n.t("lbl_frame_none"),    id="frame-label")
        yield Label(i18n.t("lbl_speed_default"), id="speed-label")

        yield Label(i18n.t("sec_fileinfo"), classes="sec", id="sec-fileinfo")
        yield Label(i18n.t("lbl_no_file"),  id="file-name")
        yield Label("",                     id="file-meta")

        yield Rule()
        yield Button(i18n.t("btn_open_file"), id="open-file-btn")

    def watch_display_fps(self, fps: float) -> None:
        try:
            self.query_one("#fps-label", Label).update(
                i18n.t("fmt_fps").format(fps) if fps > 0 else i18n.t("lbl_fps_none")
            )
        except Exception:
            pass

    def watch_display_playing(self, playing: bool) -> None:
        try:
            lbl = self.query_one("#status-label", Label)
            if playing:
                lbl.styles.color = _GREEN
                lbl.update(i18n.t("status_playing"))
            else:
                lbl.styles.color = _AMBER
                lbl.update(i18n.t("status_paused"))
        except Exception:
            pass

    def watch_display_frame(self, n: int) -> None:
        try:
            self.query_one("#frame-label", Label).update(
                i18n.t("fmt_frame").format(n) if n > 0 else i18n.t("lbl_frame_none")
            )
        except Exception:
            pass

    def set_fps(self, fps: float) -> None:
        self.display_fps = fps

    def set_playing(self, playing: bool) -> None:
        self.display_playing = playing

    def set_frame(self, n: int) -> None:
        self.display_frame = n

    def set_speed(self, speed: float) -> None:
        try:
            self.query_one("#speed-label", Label).update(i18n.t("fmt_speed").format(speed))
        except Exception:
            pass

    def set_file_info(self, path: Optional[Path], w: int = 0, h: int = 0,
                      fmt: str = "", n_frames: int = 1) -> None:
        try:
            name_lbl = self.query_one("#file-name", Label)
            meta_lbl = self.query_one("#file-meta", Label)
            if path is None:
                name_lbl.update(i18n.t("lbl_no_file"))
                meta_lbl.update("")
            else:
                name_lbl.update(path.name)
                dims   = f"{w}×{h}" if w else ""
                frames = ("  ·  " + i18n.t("n_frames").format(n=n_frames)) if n_frames > 1 else ""
                meta_lbl.update(f"{dims}  {fmt}{frames}")
        except Exception:
            pass

    def _update_lang_buttons(self) -> None:
        try:
            ru = self.query_one("#lang-ru-btn", Button)
            en = self.query_one("#lang-en-btn", Button)
            if i18n.LANG == "ru":
                ru.add_class("-active")
                en.remove_class("-active")
            else:
                en.add_class("-active")
                ru.remove_class("-active")
        except Exception:
            pass

    def refresh_lang(self) -> None:
        self.border_title = i18n.t("settings_border")
        try:
            self.query_one("#sec-display",   Label).update(i18n.t("sec_display"))
            self.query_one("#sec-output",    Label).update(i18n.t("sec_output"))
            self.query_one("#sec-adjust",    Label).update(i18n.t("sec_adjust"))
            self.query_one("#sec-animation", Label).update(i18n.t("sec_animation"))
            self.query_one("#sec-playback",  Label).update(i18n.t("sec_playback"))
            self.query_one("#sec-fileinfo",  Label).update(i18n.t("sec_fileinfo"))

            self.query_one("#lbl-truecolor", Label).update(i18n.t("lbl_truecolor"))
            self.query_one("#lbl-invert",    Label).update(i18n.t("lbl_invert"))
            self.query_one("#lbl-dither",    Label).update(i18n.t("lbl_dither"))
            self.query_one("#lbl-loop",      Label).update(i18n.t("lbl_loop"))

            self.query_one("#lbl-width-ctrl",       Label).update(i18n.t("lbl_width"))
            self.query_one("#lbl-gradient-ctrl",    Label).update(i18n.t("lbl_gradient"))
            self.query_one("#lbl-custom-grad-ctrl", Label).update(i18n.t("lbl_custom_grad"))
            self.query_one("#lbl-fps-ctrl",         Label).update(i18n.t("lbl_fps"))
            self.query_one("#lbl-brightness-ctrl",  Label).update(i18n.t("lbl_brightness"))
            self.query_one("#lbl-contrast-ctrl",    Label).update(i18n.t("lbl_contrast"))

            self.query_one("#open-file-btn", Button).label = i18n.t("btn_open_file")

            self.query_one("#status-label", Label).update(i18n.t("status_stopped"))
            self.query_one("#fps-label",    Label).update(i18n.t("lbl_fps_none"))
            self.query_one("#frame-label",  Label).update(i18n.t("lbl_frame_none"))
            self.query_one("#speed-label",  Label).update(i18n.t("lbl_speed_default"))

            self.query_one("#custom-gradient-input", Input).placeholder = i18n.t("ph_gradient")
        except Exception:
            pass
        self._update_lang_buttons()

    def _refresh_gradient_preview(self) -> None:
        try:
            self.query_one("#gradient-preview", Static).update(
                AsciiConverter.gradient_preview(
                    self._config.gradient, self._config.color_mode
                )
            )
        except Exception:
            pass

    def on_switch_changed(self, event: Switch.Changed) -> None:
        event.stop()
        if event.switch.id == "color-switch":
            self._config = replace(self._config, color_mode=event.value)
            self._refresh_gradient_preview()
        elif event.switch.id == "invert-switch":
            self._config = replace(self._config, invert=event.value)
        elif event.switch.id == "dither-switch":
            self._config = replace(self._config, dither=event.value)
        elif event.switch.id == "loop-switch":
            self._config = replace(self._config, loop=event.value)
        else:
            return
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
        elif event.input.id == "brightness-input":
            try:
                v = max(0.1, min(3.0, float(event.value)))
                self._config = replace(self._config, brightness=v)
                event.input.value = f"{v:.2f}"
            except ValueError:
                event.input.value = f"{self._config.brightness:.2f}"
                return
        elif event.input.id == "contrast-input":
            try:
                v = max(0.1, min(3.0, float(event.value)))
                self._config = replace(self._config, contrast=v)
                event.input.value = f"{v:.2f}"
            except ValueError:
                event.input.value = f"{self._config.contrast:.2f}"
                return
        elif event.input.id == "custom-gradient-input":
            g = event.value.strip()
            if len(g) >= 2:
                self._config = replace(self._config, gradient=g)
                self._refresh_gradient_preview()
            else:
                self.app.notify(i18n.t("notify_grad_short"), severity="warning")
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
            try:
                self.query_one("#custom-gradient-input", Input).value = ""
            except Exception:
                pass
            self.post_message(self.ConfigChanged(self._config))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "open-file-btn":
            self.post_message(self.OpenFileRequested())
        elif event.button.id == "lang-ru-btn":
            i18n.set_lang("ru")
            self.post_message(self.LangChanged("ru"))
        elif event.button.id == "lang-en-btn":
            i18n.set_lang("en")
            self.post_message(self.LangChanged("en"))
