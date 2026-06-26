"""Modal screens — dark neon theme: FileSelectScreen and HelpScreen."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.style import Style
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Input, Label, Static

from ansiart.core import SUPPORTED_ANIMATED, SUPPORTED_IMAGES, SUPPORTED_VIDEOS


# ── FileSelectScreen ───────────────────────────────────────────────────────────

class FileSelectScreen(ModalScreen[Optional[Path]]):
    """Full-featured file browser.  Dismisses with chosen Path or None."""

    BINDINGS = [Binding("escape", "cancel", "Cancel", show=True)]

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

    def __init__(self, start_dir: Optional[Path] = None) -> None:
        super().__init__()
        self._start_dir = start_dir or Path.home()

    def _fmt_bar(self) -> Text:
        t = Text(no_wrap=True, overflow="ellipsis")
        t.append("Images: ", Style(color="#6868a0"))
        t.append(" ".join(sorted(SUPPORTED_IMAGES))[:55] + "…", Style(color="#00e676"))
        t.append("  |  Animated: ", Style(color="#6868a0"))
        t.append(" ".join(sorted(SUPPORTED_ANIMATED)), Style(color="#ffab40"))
        t.append("  |  Video: ", Style(color="#6868a0"))
        t.append(" ".join(sorted(SUPPORTED_VIDEOS))[:50] + "…", Style(color="#ff5252"))
        return t

    def compose(self) -> ComposeResult:
        with Vertical() as v:
            v.border_title = "  Open Media File  "
            yield Static(self._fmt_bar(), classes="formats-bar")
            yield DirectoryTree(str(self._start_dir), id="dir-tree")
            yield Input(
                placeholder="  ↑ click a file above, or paste a path and press Enter…",
                id="path-input",
            )
            with Horizontal(classes="btn-row"):
                yield Button("Cancel", id="cancel-btn")
                yield Button("  Open  ↵ ", id="open-btn")

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
            self.notify("Select a file or paste a path.", severity="warning")
            return
        self.dismiss(Path(raw).expanduser().resolve())


# ── HelpScreen ─────────────────────────────────────────────────────────────────

def _build_help() -> Text:
    t = Text()
    C  = Style(color="#00d4ff", bold=True)
    P  = Style(color="#9d4eff", bold=True)
    G  = Style(color="#00e676")
    A  = Style(color="#ffab40")
    R  = Style(color="#ff5252")
    H  = Style(color="#c8c8e8", bold=True)
    D  = Style(color="#6868a0")

    t.append("  AnsiArt Pro  ", C)
    t.append("v1.0.0  ·  Keyboard Reference\n\n", D)

    t.append("  NAVIGATION\n", H)
    t.append("  O       ", C); t.append("Open file browser\n", D)
    t.append("  Space   ", C); t.append("Toggle Play / Pause  (GIF & video)\n", D)
    t.append("  R       ", C); t.append("Reload current file\n", D)
    t.append("  S       ", C); t.append("Save current frame to  <name>_ascii.txt\n", D)
    t.append("  F1      ", C); t.append("This help screen\n", D)
    t.append("  Q       ", C); t.append("Quit\n\n", D)

    t.append("  SETTINGS PANEL  ", H); t.append("(press Enter to apply inputs)\n", D)
    t.append("  TrueColor   ", P); t.append("RGB colour vs. monochrome ASCII\n", D)
    t.append("  Invert      ", P); t.append("Flip dark ↔ light mapping\n", D)
    t.append("  Width       ", P); t.append("Character columns  (20 – 500)\n", D)
    t.append("  Gradient    ", P); t.append("8 presets — Standard, Dense, Blocks, Braille…\n", D)
    t.append("  Target FPS  ", P); t.append("Playback frame rate  (1 – 60)\n\n", D)

    t.append("  GRADIENT PRESETS\n", H)
    from ansiart.core import GRADIENT_PRESETS
    for name, chars in GRADIENT_PRESETS.items():
        t.append(f"  {name:<12}", P)
        preview = chars[:24] + ("…" if len(chars) > 24 else "")
        t.append(f"{preview}\n", D)
    t.append("\n")

    t.append("  SUPPORTED FORMATS\n", H)
    from ansiart.core import SUPPORTED_IMAGES, SUPPORTED_ANIMATED, SUPPORTED_VIDEOS
    imgs = "  ".join(sorted(SUPPORTED_IMAGES))
    t.append("  Images     ", G)
    t.append(f"{imgs}\n", D)
    t.append("  Animated   ", A)
    t.append(f"{'  '.join(sorted(SUPPORTED_ANIMATED))}  ", D)
    t.append("(GIF · Animated WebP · APNG)\n", D)
    vids = "  ".join(sorted(SUPPORTED_VIDEOS))
    t.append("  Video      ", R)
    t.append(f"{vids}\n", D)
    t.append("  Requires   ", D); t.append("opencv-python", A); t.append(" for video\n\n", D)

    t.append("  EXPORT\n", H)
    t.append("  S key   ", C); t.append("Save current frame as plain text next to the source file\n", D)
    t.append("  CLI     ", C); t.append("python main.py photo.jpg --output art.txt\n\n", D)

    t.append("  TIPS\n", H)
    t.append("  •  Width 60–80 renders fastest on large videos.\n", D)
    t.append("  •  ", D); t.append("Blocks", P); t.append(" + Monochrome = clean high-contrast look.\n", D)
    t.append("  •  ", D); t.append("Dense", P); t.append(" preset shows the most tonal detail.\n", D)
    t.append("  •  Press ", D); t.append("R", C); t.append(" after changing Width/Gradient on a static image.\n", D)
    return t


class HelpScreen(ModalScreen[None]):
    """Keyboard reference and format support modal."""

    BINDINGS = [Binding("escape,f1,q", "close", "Close", show=True)]

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

    def compose(self) -> ComposeResult:
        with Vertical() as v:
            v.border_title = "  Help  F1  "
            yield Static(_build_help(), id="help-text")
            yield Button("  Close  Esc ", id="close-btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()

    def action_close(self) -> None:
        self.dismiss()
