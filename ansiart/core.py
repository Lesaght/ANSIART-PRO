from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Generator, NamedTuple

try:
    from PIL import Image, ImageEnhance, ImageSequence
    import numpy as np
except ImportError as _e:
    raise ImportError(
        "Missing dependency: Pillow or numpy not found.\n"
        "  Launch via:  ./run.sh\n"
        "  Or install:  venv/bin/pip install pillow numpy"
    ) from _e
from rich.style import Style
from rich.text import Text


GRADIENT_PRESETS: dict[str, str] = {
    "standard":  " .:-=+*#%@",
    "dense":     r" .'`^\",:;Il!i><~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "blocks":    " ░▒▓█",
    "braille":   " ⠁⠃⠇⠿",
    "simple":    " .:#@",
    "binary":    " @",
    "numerals":  " 1234567890",
    "math":      " +-×÷=≠≈∞∑∏√",
}

GRADIENT_PRESET_NAMES = list(GRADIENT_PRESETS.keys())


SUPPORTED_IMAGES: frozenset[str] = frozenset({
    ".jpg", ".jpeg", ".png", ".bmp", ".dib", ".webp", ".tiff", ".tif",
    ".ico", ".tga", ".icb", ".vda", ".vst", ".psd", ".ppm", ".pgm",
    ".pbm", ".pnm", ".xpm", ".icns", ".eps", ".avif", ".hdr", ".exr",
    ".sgi", ".rgb", ".rgba", ".pcx", ".dcx", ".fit", ".fits", ".im",
    ".msp", ".xbm",
})

SUPPORTED_ANIMATED: frozenset[str] = frozenset({
    ".gif", ".apng", ".webp",
})

SUPPORTED_VIDEOS: frozenset[str] = frozenset({
    ".mp4", ".m4v", ".avi", ".divx", ".mov", ".qt", ".mkv", ".webm",
    ".flv", ".f4v", ".wmv", ".asf", ".3gp", ".3g2", ".ts", ".mts",
    ".m2ts", ".mxf", ".ogv", ".ogg", ".rm", ".rmvb", ".vob",
    ".mpg", ".mpeg", ".m2v", ".h264", ".h265", ".dv",
})

SUPPORTED_ALL: frozenset[str] = SUPPORTED_IMAGES | SUPPORTED_ANIMATED | SUPPORTED_VIDEOS


class UnsupportedMediaError(ValueError):
    pass


class MediaLoadError(OSError):
    pass


class AsciiPixel(NamedTuple):
    char: str
    r: int
    g: int
    b: int


AsciiFrame = list[list[AsciiPixel]]


class MediaType:
    IMAGE  = "image"
    GIF    = "gif"
    VIDEO  = "video"
    WEBCAM = "webcam"


@dataclass
class ConversionConfig:
    target_width: int   = 120
    font_ratio:   float = 0.55
    gradient:     str   = GRADIENT_PRESETS["standard"]
    color_mode:   bool  = True
    invert:       bool  = False
    target_fps:   float = 15.0
    brightness:   float = 1.0
    contrast:     float = 1.0
    dither:       bool  = False
    loop:         bool  = True


@dataclass
class MediaInfo:
    media_type: str
    width: int
    height: int
    n_frames: int
    format_name: str


def _is_animated_pil(path: Path) -> bool:
    try:
        img = Image.open(path)
        return getattr(img, "n_frames", 1) > 1
    except Exception:
        return False


def detect_media_type(path: Path) -> str:
    suffix = path.suffix.lower()
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
    media_type = detect_media_type(path)
    try:
        img = Image.open(path)
        w, h = img.size
        n = getattr(img, "n_frames", 1)
        fmt = img.format or path.suffix.lstrip(".").upper()
        return MediaInfo(media_type=media_type, width=w, height=h, n_frames=n, format_name=fmt)
    except Exception:
        return MediaInfo(media_type=media_type, width=0, height=0, n_frames=1,
                         format_name=path.suffix.lstrip(".").upper())


class AsciiConverter:

    @staticmethod
    def _resize(img: Image.Image, cfg: ConversionConfig) -> Image.Image:
        w, h = img.size
        new_w = cfg.target_width
        new_h = max(1, int(new_w * (h / w) * cfg.font_ratio))
        return img.resize((new_w, new_h), Image.BILINEAR)

    @staticmethod
    def _luma(r: int, g: int, b: int) -> int:
        return int(0.299 * r + 0.587 * g + 0.114 * b)

    @staticmethod
    def _map_char(luma: int, gradient: str, invert: bool) -> str:
        if invert:
            luma = 255 - luma
        idx = int(luma / 255 * (len(gradient) - 1))
        return gradient[max(0, min(idx, len(gradient) - 1))]

    @staticmethod
    def _adjust(img: Image.Image, brightness: float, contrast: float) -> Image.Image:
        if brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(brightness)
        if contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(contrast)
        return img

    @classmethod
    def image_to_frame(cls, img: Image.Image, cfg: ConversionConfig) -> AsciiFrame:
        img   = img.convert("RGB")
        img   = cls._adjust(img, cfg.brightness, cfg.contrast)
        small = cls._resize(img, cfg)
        if cfg.dither:
            return cls._dither_frame(small, cfg)
        arr  = np.asarray(small, dtype=np.uint8)
        luma = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]).astype(np.uint8)
        n    = len(cfg.gradient) - 1
        if cfg.invert:
            luma = 255 - luma
        idx      = (luma.astype(np.uint32) * n // 255).clip(0, n)
        gradient = cfg.gradient
        h, w     = arr.shape[:2]
        return [
            [
                AsciiPixel(
                    char=gradient[int(idx[y, x])],
                    r=int(arr[y, x, 0]), g=int(arr[y, x, 1]), b=int(arr[y, x, 2]),
                )
                for x in range(w)
            ]
            for y in range(h)
        ]

    @classmethod
    def _dither_frame(cls, img: Image.Image, cfg: ConversionConfig) -> AsciiFrame:
        w, h = img.width, img.height
        n    = len(cfg.gradient) - 1
        px   = img.load()

        luma:   list[list[float]] = [[float(cls._luma(*px[x, y])) for x in range(w)] for y in range(h)]
        colors: list[list[tuple]] = [[px[x, y] for x in range(w)] for y in range(h)]

        result: AsciiFrame = []
        for y in range(h):
            row: list[AsciiPixel] = []
            for x in range(w):
                old = max(0.0, min(255.0, luma[y][x]))
                idx = round(old / 255.0 * n)
                idx = max(0, min(idx, n))
                new = idx * 255.0 / n

                ci   = (n - idx) if cfg.invert else idx
                char = cfg.gradient[max(0, min(ci, len(cfg.gradient) - 1))]
                r, g, b = colors[y][x]
                row.append(AsciiPixel(char=char, r=r, g=g, b=b))

                err = old - new
                if x + 1 < w:
                    luma[y][x + 1]     += err * 7 / 16
                if y + 1 < h:
                    if x - 1 >= 0:
                        luma[y + 1][x - 1] += err * 3 / 16
                    luma[y + 1][x]         += err * 5 / 16
                    if x + 1 < w:
                        luma[y + 1][x + 1] += err * 1 / 16
            result.append(row)
        return result

    @staticmethod
    def frame_to_rich_text(frame: AsciiFrame, color_mode: bool) -> Text:
        text = Text(no_wrap=True, overflow="fold")
        if not color_mode:
            for row in frame:
                text.append("".join(p.char for p in row) + "\n")
            return text
        for row in frame:
            i = 0
            while i < len(row):
                p = row[i]
                j = i + 1
                while j < len(row) and row[j].r == p.r and row[j].g == p.g and row[j].b == p.b:
                    j += 1
                text.append(
                    "".join(row[k].char for k in range(i, j)),
                    Style(color=f"rgb({p.r},{p.g},{p.b})"),
                )
                i = j
            text.append("\n")
        return text

    @staticmethod
    def frame_to_plain_text(frame: AsciiFrame) -> str:
        return "\n".join("".join(p.char for p in row) for row in frame)

    @staticmethod
    def frame_to_ansi(frame: AsciiFrame, color_mode: bool) -> str:
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
    def frame_to_html(frame: AsciiFrame, color_mode: bool) -> str:
        def esc(c: str) -> str:
            return c.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        rows: list[str] = []
        for row in frame:
            parts: list[str] = []
            for p in row:
                ch = esc(p.char)
                if color_mode:
                    parts.append(f'<span style="color:rgb({p.r},{p.g},{p.b})">{ch}</span>')
                else:
                    parts.append(ch)
            rows.append("".join(parts))

        body = "\n".join(rows)
        return (
            '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n'
            '<style>\n'
            'body{background:#000;color:#ccc}\n'
            'pre{font-family:"Courier New",Courier,monospace;font-size:12px;'
            'line-height:1.15;white-space:pre}\n'
            '</style>\n</head>\n<body>\n<pre>'
            + body
            + '</pre>\n</body>\n</html>'
        )

    @staticmethod
    def frame_to_svg(frame: AsciiFrame, color_mode: bool) -> str:
        if not frame:
            return '<svg xmlns="http://www.w3.org/2000/svg"/>'

        CW, CH = 7.2, 13.0
        cols   = max(len(r) for r in frame)
        rows_n = len(frame)
        W, H   = cols * CW, rows_n * CH

        def esc(c: str) -> str:
            return (c.replace("&", "&amp;").replace("<", "&lt;")
                     .replace(">", "&gt;").replace('"', "&quot;"))

        parts: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}">',
            '<rect width="100%" height="100%" fill="#000"/>',
            '<g font-family="Courier New,Courier,monospace" font-size="12">',
        ]
        for yi, row in enumerate(frame):
            y = (yi + 1) * CH
            for xi, p in enumerate(row):
                if p.char == " ":
                    continue
                x    = xi * CW
                ch   = esc(p.char)
                fill = f"rgb({p.r},{p.g},{p.b})" if color_mode else "#cccccc"
                parts.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}">{ch}</text>')
        parts.append("</g></svg>")
        return "\n".join(parts)

    @staticmethod
    def gradient_preview(gradient: str, color_mode: bool = True) -> Text:
        text = Text(no_wrap=True)
        n = max(len(gradient) - 1, 1)
        for i, ch in enumerate(gradient):
            luma  = int(i / n * 255)
            style = Style(color=f"rgb({luma},{luma},{luma})") if color_mode else Style.null()
            text.append(ch, style=style)
        return text


class MediaLoader:

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
    def load_animated_frames(path: Path) -> list[tuple[Image.Image, float]]:
        return list(MediaLoader.iter_animated_frames(path))

    @staticmethod
    def iter_video_frames(
        path: Path,
        cfg: ConversionConfig,
    ) -> Generator[tuple[Image.Image, float], None, None]:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        try:
            import cv2
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

    @staticmethod
    def iter_webcam_frames(
        cfg: ConversionConfig,
        camera_index: int = 0,
    ) -> Generator[tuple[Image.Image, float], None, None]:
        try:
            import cv2
        except ImportError as exc:
            raise ImportError(
                "opencv-python required for webcam: pip install opencv-python"
            ) from exc

        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            raise MediaLoadError(f"Cannot open webcam index {camera_index}")

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


    iter_gif_frames = iter_animated_frames
