"""Pure ASCII art conversion engine — single responsibility: pixel data → AsciiFrame.

Pipeline:
    PIL Image → resize (aspect-ratio + font-ratio) → per-pixel luma →
    gradient char lookup → AsciiFrame → Rich Text (TUI) | ANSI string (CLI)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Generator, NamedTuple

from PIL import Image, ImageSequence
from rich.style import Style
from rich.text import Text

# ── Gradient presets ───────────────────────────────────────────────────────────

GRADIENT_PRESETS: dict[str, str] = {
    # Classic 10-level, most universal
    "standard":  " .:-=+*#%@",
    # Paul Bourke's famous 70-character set (light→dark, auto-inverted by default)
    "dense":     r" .'`^\",:;Il!i><~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    # Unicode block elements — stunning in modern terminals
    "blocks":    " ░▒▓█",
    # Braille-dot density — ultra-fine detail
    "braille":   " ⠁⠃⠇⠿",
    # High-contrast minimal
    "simple":    " .:#@",
    # Pure on/off
    "binary":    " @",
    # Numerals — geeky look
    "numerals":  " 1234567890",
    # Mathematical symbols
    "math":      " +-×÷=≠≈∞∑∏√",
}

GRADIENT_PRESET_NAMES = list(GRADIENT_PRESETS.keys())

# ── Supported media extensions ─────────────────────────────────────────────────
# Images (static) — decoded by Pillow
SUPPORTED_IMAGES: frozenset[str] = frozenset({
    ".jpg", ".jpeg",
    ".png",
    ".bmp", ".dib",
    ".webp",                         # static WebP
    ".tiff", ".tif",
    ".ico",
    ".tga", ".icb", ".vda", ".vst",  # Targa
    ".psd",                          # Photoshop (Pillow partial)
    ".ppm", ".pgm", ".pbm", ".pnm",  # NetPBM family
    ".xpm",
    ".icns",                         # macOS icon
    ".eps",                          # Encapsulated PostScript
    ".avif",                         # AV1 Image Format
    ".hdr",                          # HDR Radiance
    ".exr",                          # OpenEXR (Pillow ≥ 10.1 via optional dep)
    ".sgi", ".rgb", ".rgba",         # SGI
    ".pcx",                          # ZSoft PCX
    ".dcx",                          # Multi-page PCX
    ".fit", ".fits",                 # Astronomical FITS
    ".im",                           # IFUNC IM
    ".msp",                          # Microsoft Paint
    ".xbm",                          # X BitMap
})

# Animated (multi-frame) — decoded frame-by-frame via Pillow
SUPPORTED_ANIMATED: frozenset[str] = frozenset({
    ".gif",
    ".apng",                         # Animated PNG (Pillow ≥ 9.1)
    ".webp",                         # Animated WebP (Pillow ≥ 9.1)
})

# Videos — decoded frame-by-frame via OpenCV
SUPPORTED_VIDEOS: frozenset[str] = frozenset({
    ".mp4", ".m4v",
    ".avi", ".divx",
    ".mov", ".qt",
    ".mkv",
    ".webm",
    ".flv", ".f4v",
    ".wmv", ".asf",
    ".3gp", ".3g2",
    ".ts", ".mts", ".m2ts",
    ".mxf",
    ".ogv", ".ogg",
    ".rm", ".rmvb",
    ".vob",
    ".mpg", ".mpeg", ".m2v",
    ".h264", ".h265",
    ".dv",
})

SUPPORTED_ALL: frozenset[str] = SUPPORTED_IMAGES | SUPPORTED_ANIMATED | SUPPORTED_VIDEOS


# ── Errors ─────────────────────────────────────────────────────────────────────

class UnsupportedMediaError(ValueError):
    """File extension is not in SUPPORTED_ALL."""


class MediaLoadError(OSError):
    """File exists but cannot be decoded."""


# ── Data types ─────────────────────────────────────────────────────────────────

class AsciiPixel(NamedTuple):
    """One terminal character cell with its source RGB colour."""
    char: str
    r: int
    g: int
    b: int


AsciiFrame = list[list[AsciiPixel]]  # [row][col]


class MediaType:
    IMAGE = "image"
    GIF   = "gif"      # any multi-frame PIL source
    VIDEO = "video"


@dataclass
class ConversionConfig:
    target_width: int   = 120
    font_ratio:   float = 0.55   # vertical compression for tall terminal glyphs
    gradient:     str   = GRADIENT_PRESETS["standard"]
    color_mode:   bool  = True
    invert:       bool  = False
    target_fps:   float = 15.0


@dataclass
class MediaInfo:
    """Metadata returned after opening a file."""
    media_type: str
    width: int
    height: int
    n_frames: int
    format_name: str


# ── Media-type detection ───────────────────────────────────────────────────────

def _is_animated_pil(path: Path) -> bool:
    """Return True if Pillow reports more than one frame (WebP, APNG, etc.)."""
    try:
        img = Image.open(path)
        return getattr(img, "n_frames", 1) > 1
    except Exception:
        return False


def detect_media_type(path: Path) -> str:
    """Return a MediaType constant or raise UnsupportedMediaError."""
    suffix = path.suffix.lower()

    # Formats that *might* be animated — inspect the actual file
    if suffix in {".webp", ".png", ".apng"}:
        return MediaType.GIF if _is_animated_pil(path) else MediaType.IMAGE

    if suffix in SUPPORTED_ANIMATED:
        return MediaType.GIF
    if suffix in SUPPORTED_IMAGES:
        return MediaType.IMAGE
    if suffix in SUPPORTED_VIDEOS:
        return MediaType.VIDEO

    raise UnsupportedMediaError(
        f"Unsupported format '{suffix}'.  "
        f"Images: {len(SUPPORTED_IMAGES)}  "
        f"Animated: {len(SUPPORTED_ANIMATED)}  "
        f"Video: {len(SUPPORTED_VIDEOS)} formats supported."
    )


def probe_media(path: Path) -> MediaInfo:
    """Open the file once and return its metadata (size, frames, type)."""
    media_type = detect_media_type(path)
    try:
        img = Image.open(path)
        w, h = img.size
        n = getattr(img, "n_frames", 1)
        fmt = img.format or path.suffix.lstrip(".").upper()
        return MediaInfo(
            media_type=media_type,
            width=w,
            height=h,
            n_frames=n,
            format_name=fmt,
        )
    except Exception:
        return MediaInfo(
            media_type=media_type,
            width=0, height=0, n_frames=1,
            format_name=path.suffix.lstrip(".").upper(),
        )


# ── Core converter ─────────────────────────────────────────────────────────────

class AsciiConverter:
    """Stateless image-to-ASCII transformation pipeline."""

    @staticmethod
    def _resize(img: Image.Image, cfg: ConversionConfig) -> Image.Image:
        w, h = img.size
        new_w = cfg.target_width
        new_h = max(1, int(new_w * (h / w) * cfg.font_ratio))
        return img.resize((new_w, new_h), Image.LANCZOS)

    @staticmethod
    def _luma(r: int, g: int, b: int) -> int:
        """BT.601 luma: Y = 0.299·R + 0.587·G + 0.114·B  (range 0–255)."""
        return int(0.299 * r + 0.587 * g + 0.114 * b)

    @staticmethod
    def _map_char(luma: int, gradient: str, invert: bool) -> str:
        if invert:
            luma = 255 - luma
        idx = int(luma / 255 * (len(gradient) - 1))
        return gradient[max(0, min(idx, len(gradient) - 1))]

    @classmethod
    def image_to_frame(cls, img: Image.Image, cfg: ConversionConfig) -> AsciiFrame:
        """Full pipeline: PIL Image → AsciiFrame."""
        img   = img.convert("RGB")
        small = cls._resize(img, cfg)
        px    = small.load()
        return [
            [
                AsciiPixel(
                    char=cls._map_char(cls._luma(*px[x, y]), cfg.gradient, cfg.invert),
                    r=px[x, y][0],
                    g=px[x, y][1],
                    b=px[x, y][2],
                )
                for x in range(small.width)
            ]
            for y in range(small.height)
        ]

    @staticmethod
    def frame_to_rich_text(frame: AsciiFrame, color_mode: bool) -> Text:
        """Convert an AsciiFrame to a Rich Text renderable (for Textual)."""
        text = Text(no_wrap=True, overflow="fold")
        for row in frame:
            for pixel in row:
                style = (
                    Style(color=f"rgb({pixel.r},{pixel.g},{pixel.b})")
                    if color_mode
                    else Style.null()
                )
                text.append(pixel.char, style=style)
            text.append("\n")
        return text

    @staticmethod
    def frame_to_plain_text(frame: AsciiFrame) -> str:
        """Convert an AsciiFrame to plain text (no colour codes)."""
        return "\n".join("".join(p.char for p in row) for row in frame)

    @staticmethod
    def frame_to_ansi(frame: AsciiFrame, color_mode: bool) -> str:
        """Convert an AsciiFrame to raw ANSI escape-code string (CLI / pipe)."""
        lines: list[str] = []
        for row in frame:
            parts = (
                [f"\033[38;2;{p.r};{p.g};{p.b}m{p.char}\033[0m" for p in row]
                if color_mode
                else [p.char for p in row]
            )
            lines.append("".join(parts))
        return "\n".join(lines)

    @staticmethod
    def gradient_preview(gradient: str, color_mode: bool = True) -> Text:
        """Rich Text showing each gradient character in its matching grey shade."""
        text = Text(no_wrap=True)
        n = max(len(gradient) - 1, 1)
        for i, ch in enumerate(gradient):
            luma  = int(i / n * 255)
            style = Style(color=f"rgb({luma},{luma},{luma})") if color_mode else Style.null()
            text.append(ch, style=style)
        return text


# ── Media loaders ──────────────────────────────────────────────────────────────

class MediaLoader:
    """Loads images, animated frames, and video frames as PIL Images."""

    @staticmethod
    def load_image(path: Path) -> Image.Image:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        try:
            img = Image.open(path)
            img.load()
            return img.convert("RGB")
        except Exception as exc:
            raise MediaLoadError(f"Cannot open '{path}': {exc}") from exc

    @staticmethod
    def iter_animated_frames(
        path: Path,
    ) -> Generator[tuple[Image.Image, float], None, None]:
        """Yield (RGB frame, duration_seconds) for GIF, animated WebP, APNG, etc."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        try:
            src = Image.open(path)
        except Exception as exc:
            raise MediaLoadError(f"Cannot open '{path}': {exc}") from exc

        for frame in ImageSequence.Iterator(src):
            duration_ms: int = frame.info.get("duration", 100)
            yield frame.convert("RGB"), max(duration_ms, 10) / 1000.0

    @staticmethod
    def iter_video_frames(
        path: Path,
        cfg: ConversionConfig,
    ) -> Generator[tuple[Image.Image, float], None, None]:
        """Yield (RGB frame, target_frame_duration_seconds) via OpenCV."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        try:
            import cv2  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "opencv-python required for video: pip install opencv-python"
            ) from exc

        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            raise MediaLoadError(f"OpenCV cannot open '{path}'")

        frame_duration = 1.0 / max(0.1, cfg.target_fps)
        try:
            while True:
                ret, bgr = cap.read()
                if not ret:
                    break
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                yield Image.fromarray(rgb), frame_duration
        finally:
            cap.release()

    # Keep old name as alias for backwards compatibility within the package
    iter_gif_frames = iter_animated_frames
