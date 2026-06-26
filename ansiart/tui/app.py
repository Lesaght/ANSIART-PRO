from __future__ import annotations

import time
from collections import deque
from pathlib import Path
from typing import Optional

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header
from textual.worker import get_current_worker

from ansiart import i18n
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
from ansiart.tui.screens import FileSelectScreen, HelpScreen, HistoryScreen, SaveRequested, SaveScreen
from ansiart.tui.widgets import ArtViewer, SettingsPanel


class AnsiArtApp(App[None]):

    TITLE     = "AnsiArt Pro"
    SUB_TITLE = "v1.1.1  ·  TrueColor ASCII Art"

    BINDINGS = [
        Binding("o",     "open_file",       i18n.t("bind_open")),
        Binding("h",     "history",         i18n.t("bind_history")),
        Binding("c",     "toggle_webcam",   i18n.t("bind_webcam")),
        Binding("space", "toggle_playback", i18n.t("bind_play"),       show=True),
        Binding("left",  "prev_frame",      i18n.t("bind_frame_prev"), show=False),
        Binding("right", "next_frame",      i18n.t("bind_frame_next"), show=False),
        Binding("plus,equal", "zoom_in",    i18n.t("bind_zoom_in"),    show=False),
        Binding("minus",      "zoom_out",   i18n.t("bind_zoom_out"),   show=False),
        Binding("right_square_bracket", "speed_up",   i18n.t("bind_speed_up"),   show=False),
        Binding("left_square_bracket",  "speed_down", i18n.t("bind_speed_down"), show=False),
        Binding("r",     "reload",          i18n.t("bind_reload")),
        Binding("s",     "save",            i18n.t("bind_save")),
        Binding("f1",    "help",            i18n.t("bind_help")),
        Binding("q",     "quit",            i18n.t("bind_quit")),
    ]

    CSS = """
    Screen {
        layout: horizontal;
        background: #0b0b14;
    }
    Header {
        background: #111128;
        color: #00d4ff;
        text-style: bold;
        height: 1;
    }
    Header .header--highlight {
        background: #9d4eff;
    }
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
    ScrollBar { background: #111128; }
    ScrollBar > .scrollbar--bar { color: #9d4eff; }
    Select { border: tall #2a2a50; background: #0d0d20; }
    Select:focus { border: tall #9d4eff; }
    SelectOverlay { border: round #9d4eff; }
    SelectOverlay > .option-list--option-highlighted {
        background: #9d4eff;
        color: #ffffff;
    }
    Switch.-on .switch--slider { color: #9d4eff; }
    Switch .switch--slider     { color: #2a2a50; }
    Toast { background: #111128; }
    Rule  { color: #1c1c38; }
    """


    def __init__(
        self,
        initial_file: Optional[Path] = None,
        config: Optional[ConversionConfig] = None,
        webcam: bool = False,
    ) -> None:
        super().__init__()
        self.config: ConversionConfig = config or ConversionConfig()
        self._current_file: Optional[Path] = initial_file
        self._is_playing:   bool = True
        self._frame_count:  int  = 0
        self._last_frame:   Optional[AsciiFrame] = None
        self._speed:        float = 1.0
        self._webcam_active: bool = webcam


        self._gif_pil_frames: list[tuple] = []
        self._gif_idx:        int         = 0


    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ArtViewer(id="art-viewer")
        yield SettingsPanel(self.config, id="settings-panel")
        yield Footer()

    def on_mount(self) -> None:
        self._apply_bindings()
        self.sub_title = i18n.t("sub_title")
        if self._webcam_active:
            self._start_webcam()
        elif self._current_file:
            self._load_and_render(self._current_file)
        else:
            self.query_one(ArtViewer).show_placeholder()

    def _apply_bindings(self) -> None:
        AnsiArtApp.BINDINGS = [
            Binding("o",     "open_file",       i18n.t("bind_open")),
            Binding("h",     "history",         i18n.t("bind_history")),
            Binding("c",     "toggle_webcam",   i18n.t("bind_webcam")),
            Binding("space", "toggle_playback", i18n.t("bind_play"),       show=True),
            Binding("left",  "prev_frame",      i18n.t("bind_frame_prev"), show=False),
            Binding("right", "next_frame",      i18n.t("bind_frame_next"), show=False),
            Binding("plus,equal", "zoom_in",    i18n.t("bind_zoom_in"),    show=False),
            Binding("minus",      "zoom_out",   i18n.t("bind_zoom_out"),   show=False),
            Binding("right_square_bracket", "speed_up",   i18n.t("bind_speed_up"),   show=False),
            Binding("left_square_bracket",  "speed_down", i18n.t("bind_speed_down"), show=False),
            Binding("r",     "reload",          i18n.t("bind_reload")),
            Binding("s",     "save",            i18n.t("bind_save")),
            Binding("f1",    "help",            i18n.t("bind_help")),
            Binding("q",     "quit",            i18n.t("bind_quit")),
        ]
        AnsiArtApp._merged_bindings = AnsiArtApp._merge_bindings()
        self.refresh_bindings()

    def _refresh_lang(self) -> None:
        self.sub_title = i18n.t("sub_title")
        self._apply_bindings()
        self.query_one(ArtViewer).refresh_lang()
        self.query_one(SettingsPanel).refresh_lang()


    def action_open_file(self) -> None:
        start = self._current_file.parent if self._current_file else Path.home()
        self.push_screen(FileSelectScreen(start), callback=self._on_file_selected)

    def action_history(self) -> None:
        self.push_screen(HistoryScreen(), callback=self._on_file_selected)

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_toggle_playback(self) -> None:
        self._is_playing = not self._is_playing
        panel = self.query_one(SettingsPanel)
        panel.set_playing(self._is_playing)
        if self._is_playing and self._current_file:
            self._start_rendering(self._current_file)

    def action_reload(self) -> None:
        if self._webcam_active:
            self._start_webcam()
        elif self._current_file:
            self._is_playing   = True
            self._frame_count  = 0
            self._gif_idx      = 0
            self._load_and_render(self._current_file)
        else:
            self.notify(i18n.t("notify_no_file"), severity="warning")

    def action_save(self) -> None:
        if self._last_frame is None:
            self.notify(i18n.t("notify_no_frame"), severity="warning")
            return
        stem = self._current_file.stem if self._current_file else "output"
        self.push_screen(SaveScreen(default_stem=stem))

    def action_toggle_webcam(self) -> None:
        self._webcam_active = not self._webcam_active
        if self._webcam_active:
            self._start_webcam()
            self.notify(i18n.t("notify_webcam_on"), severity="information")
        else:
            self._is_playing = False
            self.notify(i18n.t("notify_webcam_off"), severity="information")

    def action_zoom_in(self) -> None:
        new_w = min(500, self.config.target_width + 10)
        self._apply_width(new_w)

    def action_zoom_out(self) -> None:
        new_w = max(20, self.config.target_width - 10)
        self._apply_width(new_w)

    def action_speed_up(self) -> None:
        self._speed = min(8.0, round(self._speed + 0.25, 2))
        self._apply_speed()

    def action_speed_down(self) -> None:
        self._speed = max(0.25, round(self._speed - 0.25, 2))
        self._apply_speed()

    def action_next_frame(self) -> None:
        if self._is_playing or not self._gif_pil_frames:
            return
        self._gif_idx = (self._gif_idx + 1) % len(self._gif_pil_frames)
        self._render_gif_frame_at(self._gif_idx)

    def action_prev_frame(self) -> None:
        if self._is_playing or not self._gif_pil_frames:
            return
        self._gif_idx = (self._gif_idx - 1) % len(self._gif_pil_frames)
        self._render_gif_frame_at(self._gif_idx)


    def _apply_width(self, w: int) -> None:
        from dataclasses import replace
        self.config = replace(self.config, target_width=w)
        self.query_one(SettingsPanel).post_message(
            SettingsPanel.ConfigChanged(self.config)
        )
        self.on_settings_panel_config_changed(
            SettingsPanel.ConfigChanged(self.config)
        )

    def _apply_speed(self) -> None:
        self.query_one(SettingsPanel).set_speed(self._speed)
        if self._current_file and self._is_playing:
            self._start_rendering(self._current_file)


    def on_settings_panel_config_changed(self, msg: SettingsPanel.ConfigChanged) -> None:
        self.config = msg.config
        if self._webcam_active:
            self._start_webcam()
        elif self._current_file and self._is_playing:
            self._start_rendering(self._current_file)

    def on_settings_panel_open_file_requested(self, _: SettingsPanel.OpenFileRequested) -> None:
        self.action_open_file()

    def on_settings_panel_lang_changed(self, msg: SettingsPanel.LangChanged) -> None:
        self._refresh_lang()

    def on_save_requested(self, msg: SaveRequested) -> None:
        if self._last_frame is None:
            self.notify(i18n.t("notify_nothing"), severity="warning")
            return
        conv = AsciiConverter()
        try:
            if msg.fmt == "html":
                text = conv.frame_to_html(self._last_frame, self.config.color_mode)
            elif msg.fmt == "svg":
                text = conv.frame_to_svg(self._last_frame, self.config.color_mode)
            elif msg.fmt == "ansi":
                text = conv.frame_to_ansi(self._last_frame, self.config.color_mode)
            else:
                text = conv.frame_to_plain_text(self._last_frame)
            msg.path.parent.mkdir(parents=True, exist_ok=True)
            msg.path.write_text(text, encoding="utf-8")
            self.notify(i18n.t("notify_saved").format(fmt=msg.fmt.upper(), name=msg.path.name), severity="information")
        except Exception as exc:
            self.notify(i18n.t("notify_save_fail").format(err=exc), severity="error")


    def _on_file_selected(self, path: Optional[Path]) -> None:
        if path is None:
            return
        if not path.exists():
            self.notify(i18n.t("notify_not_found").format(path=path), severity="error")
            return
        self._webcam_active = False
        self._current_file  = path
        self._is_playing    = True
        self._frame_count   = 0
        self._gif_idx       = 0
        self._gif_pil_frames = []
        self.query_one(SettingsPanel).set_playing(True)
        self._load_and_render(path)

        from ansiart import history
        history.push(path)

    def _load_and_render(self, path: Path) -> None:
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


    def _ui_frame(self, text) -> None:
        self._frame_count += 1
        self.query_one(ArtViewer).update_frame(text)
        self.query_one(SettingsPanel).set_frame(self._frame_count)

    def _ui_fps(self, fps: float) -> None:
        self.query_one(SettingsPanel).set_fps(fps)


    def _render_gif_frame_at(self, idx: int) -> None:
        img, _ = self._gif_pil_frames[idx]
        conv   = AsciiConverter()
        frame  = conv.image_to_frame(img, self.config)
        rich   = conv.frame_to_rich_text(frame, self.config.color_mode)
        self._last_frame = frame
        self._frame_count += 1
        self.query_one(ArtViewer).update_frame(rich)
        self.query_one(SettingsPanel).set_frame(self._frame_count)


    @work(thread=True, exclusive=True, name="renderer")
    def _start_rendering(self, path: Path) -> None:
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

    @work(thread=True, exclusive=True, name="webcam-renderer")
    def _start_webcam(self) -> None:
        worker    = get_current_worker()
        converter = AsciiConverter()
        self._loop_webcam(converter, worker)


    def _loop_image(self, path: Path, conv: AsciiConverter) -> None:
        img   = MediaLoader.load_image(path)
        frame = conv.image_to_frame(img, self.config)
        rich  = conv.frame_to_rich_text(frame, self.config.color_mode)
        self._last_frame = frame
        self.call_from_thread(self._ui_frame, rich)
        self.call_from_thread(self._ui_fps, 0.0)

    def _loop_animated(self, path: Path, conv: AsciiConverter, worker) -> None:

        try:
            pil_frames = MediaLoader.load_animated_frames(path)
            self._gif_pil_frames = pil_frames
            self._gif_idx        = 0
        except Exception:
            pil_frames = []

        rolling: deque[float] = deque(maxlen=8)
        loop_count = 0

        while not worker.is_cancelled and self._is_playing:
            for i, (img, duration) in enumerate(pil_frames or MediaLoader.iter_animated_frames(path)):
                if worker.is_cancelled or not self._is_playing:
                    return
                self._gif_idx = i
                t0    = time.perf_counter()
                frame = conv.image_to_frame(img, self.config)
                rich  = conv.frame_to_rich_text(frame, self.config.color_mode)
                self._last_frame = frame
                self.call_from_thread(self._ui_frame, rich)
                elapsed = time.perf_counter() - t0
                wait    = max(0.0, (duration / self._speed) - elapsed)
                if wait:
                    time.sleep(wait)
                rolling.append(time.perf_counter() - t0)
                if len(rolling) >= 4:
                    avg = sum(rolling) / len(rolling)
                    self.call_from_thread(self._ui_fps, (1.0 / avg * self._speed) if avg else 0.0)

            loop_count += 1
            if not self.config.loop:
                self.call_from_thread(
                    self.query_one(SettingsPanel).set_playing, False
                )
                break

    def _loop_video(self, path: Path, conv: AsciiConverter, worker) -> None:
        rolling: deque[float] = deque(maxlen=10)
        loop_count = 0

        while not worker.is_cancelled and self._is_playing:
            for img, duration in MediaLoader.iter_video_frames(path, self.config):
                if worker.is_cancelled or not self._is_playing:
                    return
                t0    = time.perf_counter()
                frame = conv.image_to_frame(img, self.config)
                rich  = conv.frame_to_rich_text(frame, self.config.color_mode)
                self._last_frame = frame
                self.call_from_thread(self._ui_frame, rich)
                elapsed = time.perf_counter() - t0
                wait    = max(0.0, (duration / self._speed) - elapsed)
                if wait:
                    time.sleep(wait)
                rolling.append(time.perf_counter() - t0)
                if len(rolling) >= 4:
                    avg = sum(rolling) / len(rolling)
                    self.call_from_thread(self._ui_fps, (1.0 / avg * self._speed) if avg else 0.0)

            loop_count += 1
            if not self.config.loop:
                self.call_from_thread(
                    self.query_one(SettingsPanel).set_playing, False
                )
                break

    def _loop_webcam(self, conv: AsciiConverter, worker) -> None:
        rolling: deque[float] = deque(maxlen=10)
        try:
            for img, duration in MediaLoader.iter_webcam_frames(self.config):
                if worker.is_cancelled or not self._webcam_active:
                    return
                t0    = time.perf_counter()
                frame = conv.image_to_frame(img, self.config)
                rich  = conv.frame_to_rich_text(frame, self.config.color_mode)
                self._last_frame = frame
                self.call_from_thread(self._ui_frame, rich)
                elapsed = time.perf_counter() - t0
                wait    = max(0.0, (duration / self._speed) - elapsed)
                if wait:
                    time.sleep(wait)
                rolling.append(time.perf_counter() - t0)
                if len(rolling) >= 4:
                    avg = sum(rolling) / len(rolling)
                    self.call_from_thread(self._ui_fps, (1.0 / avg * self._speed) if avg else 0.0)
        except (ImportError, MediaLoadError) as exc:
            self.call_from_thread(self.notify, str(exc), severity="error")
            self._webcam_active = False
