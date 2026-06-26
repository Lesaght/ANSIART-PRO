from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.style import Style
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Input, Label, Select, Static

from ansiart import i18n
from ansiart.core import SUPPORTED_ANIMATED, SUPPORTED_IMAGES, SUPPORTED_VIDEOS


class SaveRequested(Message):
    def __init__(self, path: Path, fmt: str) -> None:
        super().__init__()
        self.path = path
        self.fmt  = fmt


class FileSelectScreen(ModalScreen[Optional[Path]]):

    DEFAULT_CSS = """
    FileSelectScreen {
        align: center middle;
        background: rgba(0,0,0,0.75);
    }
    FileSelectScreen > Vertical {
        width: 74%;
        height: 84%;
        background: #0e0e1e;
        border: round #00d4ff;
        border-title-color: #00d4ff;
        border-title-style: bold;
        padding: 0 1;
    }
    FileSelectScreen .formats-bar {
        height: 1;
        padding: 0 1;
        margin-bottom: 1;
        color: #6868a0;
    }
    FileSelectScreen DirectoryTree {
        height: 1fr;
        border: round #1c1c38;
        background: #0b0b14;
        margin: 0 0 1 0;
        scrollbar-color: #9d4eff;
        scrollbar-background: #111128;
    }
    FileSelectScreen DirectoryTree:focus {
        border: round #00d4ff;
    }
    FileSelectScreen DirectoryTree > .directory-tree--folder {
        color: #00d4ff;
    }
    FileSelectScreen DirectoryTree > .directory-tree--file {
        color: #c8c8e8;
    }
    FileSelectScreen #path-input {
        background: #0b0b14;
        border: tall #2a2a50;
        color: #c8c8e8;
        margin-bottom: 1;
    }
    FileSelectScreen #path-input:focus {
        border: tall #00d4ff;
    }
    FileSelectScreen .btn-row {
        height: 3;
        align: right middle;
        padding: 0 1;
    }
    FileSelectScreen #open-btn {
        background: #9d4eff;
        color: #ffffff;
        text-style: bold;
        border: none;
        margin-left: 1;
    }
    FileSelectScreen #open-btn:hover {
        background: #00d4ff;
        color: #000000;
    }
    FileSelectScreen #cancel-btn {
        background: #1c1c38;
        color: #6868a0;
        border: none;
        margin-left: 1;
    }
    FileSelectScreen #cancel-btn:hover {
        background: #2a2a50;
        color: #c8c8e8;
    }
    """

    BINDINGS = [Binding("escape", "cancel", "Esc", show=True)]

    def __init__(self, start_dir: Optional[Path] = None) -> None:
        super().__init__()
        self._start_dir = start_dir or Path.home()

    def _fmt_bar(self) -> Text:
        t = Text(no_wrap=True, overflow="ellipsis")
        t.append(i18n.t("fss_images"),   Style(color="#6868a0"))
        t.append(" ".join(sorted(SUPPORTED_IMAGES))[:55] + "…", Style(color="#00e676"))
        t.append(i18n.t("fss_animated"), Style(color="#6868a0"))
        t.append(" ".join(sorted(SUPPORTED_ANIMATED)), Style(color="#ffab40"))
        t.append(i18n.t("fss_video"),    Style(color="#6868a0"))
        t.append(" ".join(sorted(SUPPORTED_VIDEOS))[:50] + "…", Style(color="#ff5252"))
        return t

    def compose(self) -> ComposeResult:
        with Vertical() as v:
            v.border_title = i18n.t("fss_title")
            yield Static(self._fmt_bar(), classes="formats-bar")
            yield DirectoryTree(str(self._start_dir), id="dir-tree")
            yield Input(placeholder=i18n.t("fss_placeholder"), id="path-input")
            with Horizontal(classes="btn-row"):
                yield Button(i18n.t("fss_cancel"), id="cancel-btn")
                yield Button(i18n.t("fss_open"),   id="open-btn")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.query_one("#path-input", Input).value = str(event.path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open-btn":
            self._try_open()
        elif event.button.id == "cancel-btn":
            self.dismiss(None)

    def on_input_submitted(self, _: Input.Submitted) -> None:
        self._try_open()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _try_open(self) -> None:
        raw = self.query_one("#path-input", Input).value.strip()
        if not raw:
            self.notify(i18n.t("fss_select_warn"), severity="warning")
            return
        self.dismiss(Path(raw).expanduser().resolve())


class SaveScreen(ModalScreen[None]):

    DEFAULT_CSS = """
    SaveScreen {
        align: center middle;
        background: rgba(0,0,0,0.80);
    }
    SaveScreen > Vertical {
        width: 60;
        height: auto;
        background: #0e0e1e;
        border: round #9d4eff;
        border-title-color: #9d4eff;
        border-title-style: bold;
        padding: 1 2;
    }
    SaveScreen Label {
        color: #6868a0;
        height: 1;
        margin-top: 1;
    }
    SaveScreen Input {
        border: tall #2a2a50;
        background: #0b0b14;
        color: #c8c8e8;
        margin-bottom: 1;
    }
    SaveScreen Input:focus {
        border: tall #9d4eff;
    }
    SaveScreen Select {
        margin-bottom: 1;
    }
    SaveScreen .btn-row {
        height: 3;
        align: right middle;
        margin-top: 1;
    }
    SaveScreen #save-btn {
        background: #9d4eff;
        color: #ffffff;
        text-style: bold;
        border: none;
        margin-left: 1;
    }
    SaveScreen #save-btn:hover {
        background: #00d4ff;
        color: #000000;
    }
    SaveScreen #cancel-btn {
        background: #1c1c38;
        color: #6868a0;
        border: none;
        margin-left: 1;
    }
    SaveScreen #cancel-btn:hover {
        background: #2a2a50;
        color: #c8c8e8;
    }
    """

    BINDINGS = [Binding("escape", "cancel", "Esc", show=True)]

    def __init__(self, default_stem: str = "output") -> None:
        super().__init__()
        self._default_stem = default_stem

    def _formats(self) -> list[tuple[str, str]]:
        return [
            (i18n.t("ss_fmt_txt"),  "txt"),
            (i18n.t("ss_fmt_ansi"), "ansi"),
            (i18n.t("ss_fmt_html"), "html"),
            (i18n.t("ss_fmt_svg"),  "svg"),
        ]

    def compose(self) -> ComposeResult:
        with Vertical() as v:
            v.border_title = i18n.t("ss_title")
            yield Label(i18n.t("ss_path_lbl"))
            yield Input(value=f"{self._default_stem}_ascii.txt", id="save-path-input")
            yield Label(i18n.t("ss_fmt_lbl"))
            yield Select(options=self._formats(), value="txt", id="format-select")
            with Horizontal(classes="btn-row"):
                yield Button(i18n.t("ss_cancel"), id="cancel-btn")
                yield Button(i18n.t("ss_save"),   id="save-btn")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "format-select" or event.value is Select.BLANK:
            return
        fmt  = str(event.value)
        inp  = self.query_one("#save-path-input", Input)
        path = Path(inp.value.strip()) if inp.value.strip() else Path(f"{self._default_stem}_ascii")
        inp.value = str(path.with_suffix(f".{fmt}"))

    def on_input_submitted(self, _: Input.Submitted) -> None:
        self._do_save()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self._do_save()
        elif event.button.id == "cancel-btn":
            self.dismiss()

    def action_cancel(self) -> None:
        self.dismiss()

    def _do_save(self) -> None:
        raw = self.query_one("#save-path-input", Input).value.strip()
        if not raw:
            self.notify(i18n.t("ss_enter_path"), severity="warning")
            return
        fmt_val = self.query_one("#format-select", Select).value
        fmt     = str(fmt_val) if fmt_val is not Select.BLANK else "txt"
        output  = Path(raw).expanduser()
        self.dismiss()
        self.app.post_message(SaveRequested(output, fmt))


class HistoryScreen(ModalScreen[Optional[Path]]):

    DEFAULT_CSS = """
    HistoryScreen {
        align: center middle;
        background: rgba(0,0,0,0.80);
    }
    HistoryScreen > Vertical {
        width: 70;
        height: auto;
        max-height: 70%;
        background: #0e0e1e;
        border: round #00d4ff;
        border-title-color: #00d4ff;
        border-title-style: bold;
        padding: 1 2;
        overflow-y: auto;
    }
    HistoryScreen .hist-btn {
        width: 100%;
        margin: 0 0 1 0;
        background: #1c1c38;
        color: #c8c8e8;
        border: none;
        text-align: left;
    }
    HistoryScreen .hist-btn:hover {
        background: #2a2a50;
        color: #00d4ff;
    }
    HistoryScreen #cancel-btn {
        width: 100%;
        margin-top: 1;
        background: #0e0e1e;
        color: #6868a0;
        border: tall #2a2a50;
    }
    HistoryScreen #cancel-btn:hover {
        background: #1c1c38;
        color: #c8c8e8;
    }
    HistoryScreen #empty-label {
        color: #6868a0;
        text-align: center;
        margin: 1 0;
    }
    """

    BINDINGS = [Binding("escape", "cancel", "Esc", show=True)]

    def __init__(self) -> None:
        super().__init__()
        from ansiart import history
        self._entries: list[Path] = history.load()

    def compose(self) -> ComposeResult:
        with Vertical() as v:
            v.border_title = i18n.t("hs_title")
            if not self._entries:
                yield Label(i18n.t("hs_empty"), id="empty-label")
            else:
                for idx, path in enumerate(self._entries):
                    yield Button(
                        f"  {path.name}\n  {path.parent}",
                        id=f"hist-{idx}",
                        classes="hist-btn",
                    )
            yield Button(i18n.t("hs_cancel"), id="cancel-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(None)
            return
        if event.button.id and event.button.id.startswith("hist-"):
            idx = int(event.button.id.split("-")[1])
            self.dismiss(self._entries[idx])

    def action_cancel(self) -> None:
        self.dismiss(None)


def _build_help() -> Text:
    t = Text()
    C = Style(color="#00d4ff", bold=True)
    P = Style(color="#9d4eff", bold=True)
    G = Style(color="#00e676")
    A = Style(color="#ffab40")
    R = Style(color="#ff5252")
    H = Style(color="#c8c8e8", bold=True)
    D = Style(color="#6868a0")

    t.append("  AnsiArt Pro  ", C)
    t.append(i18n.t("help_header"), D)

    t.append(i18n.t("h_nav"), H)
    t.append("  O         ", C); t.append(i18n.t("h_o"), D)
    t.append("  H         ", C); t.append(i18n.t("h_h"), D)
    t.append("  C         ", C); t.append(i18n.t("h_c"), D)
    t.append(i18n.t("h_space_key"), C)
    t.append(i18n.t("h_space_desc"), D)
    t.append("  ← →       ", C); t.append(i18n.t("h_arrows_desc"), D)
    t.append("  R         ", C); t.append(i18n.t("h_r"), D)
    t.append("  F1        ", C); t.append(i18n.t("h_f1"), D)
    t.append("  Q         ", C); t.append(i18n.t("h_q"), D)

    t.append(i18n.t("h_zoom"), H)
    t.append("  +  /  -   ", C); t.append(i18n.t("h_plus"), D)
    t.append("  ]  /  [   ", C); t.append(i18n.t("h_bracket"), D)

    t.append(i18n.t("h_export"), H)
    t.append("  S         ", C); t.append(i18n.t("h_s"), D)
    t.append(i18n.t("h_formats_lbl"), P)
    t.append(i18n.t("h_formats_val"), D)

    t.append(i18n.t("h_settings_hdr"), H)
    t.append(i18n.t("h_settings_hint"), D)
    t.append("  TrueColor   ", P); t.append(i18n.t("h_truecolor_desc"), D)
    t.append("  " + i18n.t("lbl_invert").ljust(11), P)
    t.append(i18n.t("h_invert_desc"), D)
    t.append("  " + i18n.t("lbl_dither").ljust(11), P)
    t.append(i18n.t("h_dither_desc"), D)
    t.append("  " + i18n.t("lbl_width").ljust(11), P)
    t.append(i18n.t("h_width_desc"), D)
    t.append("  " + i18n.t("lbl_gradient").ljust(11), P)
    t.append(i18n.t("h_gradient_desc"), D)
    t.append("  FPS        ", P); t.append(i18n.t("h_fps_desc"), D)
    t.append("  " + i18n.t("lbl_brightness")[:11].ljust(11), P)
    t.append(i18n.t("h_brightness_desc"), D)
    t.append("  " + i18n.t("lbl_contrast")[:11].ljust(11), P)
    t.append(i18n.t("h_contrast_desc"), D)
    t.append("  " + i18n.t("lbl_loop").ljust(11), P)
    t.append(i18n.t("h_loop_desc"), D)

    t.append(i18n.t("h_grad_presets"), H)
    from ansiart.core import GRADIENT_PRESETS
    for name, chars in GRADIENT_PRESETS.items():
        t.append(f"  {name:<12}", P)
        preview = chars[:24] + ("…" if len(chars) > 24 else "")
        t.append(f"{preview}\n", D)
    t.append("\n")

    t.append(i18n.t("h_formats_section"), H)
    from ansiart.core import SUPPORTED_IMAGES, SUPPORTED_ANIMATED, SUPPORTED_VIDEOS
    t.append(i18n.t("h_images_lbl"), G)
    t.append("  ".join(sorted(SUPPORTED_IMAGES)) + "\n", D)
    t.append(i18n.t("h_animated_lbl"), A)
    t.append("  ".join(sorted(SUPPORTED_ANIMATED)) + i18n.t("h_animated_desc"), D)
    t.append(i18n.t("h_video_lbl"), R)
    t.append("  ".join(sorted(SUPPORTED_VIDEOS)) + "\n", D)
    t.append(i18n.t("h_webcam_lbl"), C)
    t.append(i18n.t("h_webcam_req"), D)

    t.append(i18n.t("h_cli"), H)
    t.append("  python main.py photo.jpg -o art.txt\n", D)
    t.append("  python main.py photo.jpg -o art.html\n", D)
    t.append("  python main.py photo.jpg -o art.svg\n", D)
    t.append("  python main.py photo.jpg -o art.ansi\n", D)
    t.append("  python main.py photo.jpg --dither --brightness 1.2\n", D)
    t.append("  python main.py --webcam\n\n", D)

    t.append(i18n.t("h_tips"), H)
    t.append(i18n.t("h_tip1"), D)
    t.append("  •  ", D); t.append("Blocks", P); t.append(i18n.t("h_tip2_suffix"), D)
    t.append("  •  ", D); t.append("Dense",  P); t.append(i18n.t("h_tip3_suffix"), D)
    t.append(i18n.t("h_tip4_prefix"), D)
    t.append("R", C)
    t.append(i18n.t("h_tip4_suffix"), D)
    return t


class HelpScreen(ModalScreen[None]):

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
        background: rgba(0,0,0,0.8);
    }
    HelpScreen > Vertical {
        width: 72;
        height: auto;
        max-height: 90%;
        background: #0e0e1e;
        border: round #9d4eff;
        border-title-color: #9d4eff;
        border-title-style: bold;
        padding: 1 1;
        overflow-y: auto;
        scrollbar-color: #9d4eff;
        scrollbar-background: #111128;
    }
    HelpScreen Static {
        width: 100%;
        height: auto;
    }
    HelpScreen #close-btn {
        width: 100%;
        margin-top: 1;
        background: #9d4eff;
        color: #ffffff;
        text-style: bold;
        border: none;
    }
    HelpScreen #close-btn:hover {
        background: #00d4ff;
        color: #000000;
    }
    """

    BINDINGS = [Binding("escape,f1,q", "close", "Esc", show=True)]

    def compose(self) -> ComposeResult:
        with Vertical() as v:
            v.border_title = i18n.t("help_title")
            yield Static(_build_help(), id="help-text")
            yield Button(i18n.t("help_close"), id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_close(self) -> None:
        self.dismiss()
