from __future__ import annotations

import os
import sys
from pathlib import Path


def _reexec_with_venv() -> None:
    here     = Path(__file__).resolve().parent
    venv_py  = here / "venv" / "bin" / "python3"
    if not venv_py.exists():
        sys.exit(
            f"error: venv not found at {here / 'venv'}\n"
            f"  Run:  python3 -m venv venv && venv/bin/pip install -r requirements.txt"
        )
    os.execv(str(venv_py), [str(venv_py)] + sys.argv)

try:
    from PIL import Image as _pil_check
    del _pil_check
except ImportError:
    _reexec_with_venv()

import argparse


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ansiart-pro",
        description="Convert images, GIFs, and videos into TrueColor ASCII art.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Gradient presets:  standard  dense  blocks  braille  simple  binary
You may also pass a raw gradient string, e.g. --gradient " .oO0@"

Output format is inferred from the --output extension:
  .txt   plain text (default)
  .ansi  ANSI colour codes
  .html  self-contained HTML page
  .svg   Scalable Vector Graphics
        """,
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to an image, GIF, or video file (omit to open the file browser)",
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=120,
        metavar="N",
        help="Target output width in characters (default: 120, range: 20–500)",
    )
    parser.add_argument(
        "--auto-width",
        action="store_true",
        help="Set width to the current terminal column count (overrides --width)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable TrueColor; render in monochrome ASCII",
    )
    parser.add_argument(
        "--gradient", "-g",
        default="standard",
        metavar="PRESET",
        help="Gradient preset name or a custom character string (default: standard)",
    )
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Invert the luminance-to-character mapping",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=15.0,
        metavar="N",
        help="Target playback frame rate for GIF/video (default: 15.0, range: 1–60)",
    )
    parser.add_argument(
        "--font-ratio",
        type=float,
        default=0.55,
        metavar="F",
        help="Vertical compression factor for terminal font aspect ratio (default: 0.55)",
    )
    parser.add_argument(
        "--brightness",
        type=float,
        default=1.0,
        metavar="F",
        help="Brightness multiplier before conversion (default: 1.0, range: 0.1–3.0)",
    )
    parser.add_argument(
        "--contrast",
        type=float,
        default=1.0,
        metavar="F",
        help="Contrast multiplier before conversion (default: 1.0, range: 0.1–3.0)",
    )
    parser.add_argument(
        "--dither",
        action="store_true",
        help="Apply Floyd–Steinberg error-diffusion dithering for smoother gradients",
    )
    parser.add_argument(
        "--no-loop",
        action="store_true",
        help="Play animated media once and stop (default: loop indefinitely)",
    )
    parser.add_argument(
        "--webcam",
        action="store_true",
        help="Stream live video from the default webcam (requires opencv-python)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help=(
            "Save ASCII art to a file and exit (no TUI). "
            "Format is inferred from extension: .txt .ansi .html .svg"
        ),
    )
    return parser


def _detect_output_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".html":
        return "html"
    if suffix == ".svg":
        return "svg"
    if suffix == ".ansi":
        return "ansi"
    return "txt"


def main() -> None:
    parser = _build_parser()
    args   = parser.parse_args()

    from ansiart.core import GRADIENT_PRESETS, ConversionConfig
    from ansiart.tui.app import AnsiArtApp


    gradient_str = GRADIENT_PRESETS.get(args.gradient, args.gradient)
    if len(gradient_str) < 2:
        parser.error(
            f"Gradient must contain at least 2 characters.  "
            f"Known presets: {', '.join(GRADIENT_PRESETS)}"
        )


    if args.auto_width:
        try:
            target_width = os.get_terminal_size().columns
        except OSError:
            target_width = args.width
    else:
        target_width = max(20, min(500, args.width))


    config = ConversionConfig(
        target_width=target_width,
        font_ratio=max(0.1, min(2.0, args.font_ratio)),
        gradient=gradient_str,
        color_mode=not args.no_color,
        invert=args.invert,
        target_fps=max(1.0, min(60.0, args.fps)),
        brightness=max(0.1, min(3.0, args.brightness)),
        contrast=max(0.1, min(3.0, args.contrast)),
        dither=args.dither,
        loop=not args.no_loop,
    )


    if args.webcam:
        app = AnsiArtApp(initial_file=None, config=config, webcam=True)
        app.run()
        return


    initial_file: Path | None = None
    if args.file:
        initial_file = Path(args.file).expanduser().resolve()
        if not initial_file.exists():
            print(f"error: file not found — '{initial_file}'", file=sys.stderr)
            sys.exit(1)


    if args.output:
        if initial_file is None:
            parser.error("--output requires a file argument")

        from ansiart.core import (
            AsciiConverter,
            MediaLoader,
            MediaType,
            UnsupportedMediaError,
            detect_media_type,
        )

        try:
            media_type = detect_media_type(initial_file)
        except UnsupportedMediaError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)

        conv = AsciiConverter()
        try:
            if media_type == MediaType.IMAGE:
                img = MediaLoader.load_image(initial_file)
            elif media_type == MediaType.GIF:
                img, _ = next(iter(MediaLoader.iter_animated_frames(initial_file)))
            else:
                img, _ = next(iter(MediaLoader.iter_video_frames(initial_file, config)))
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)

        frame       = conv.image_to_frame(img, config)
        output_path = Path(args.output).expanduser()
        fmt         = _detect_output_format(output_path)

        if fmt == "html":
            text = conv.frame_to_html(frame, config.color_mode)
        elif fmt == "svg":
            text = conv.frame_to_svg(frame, config.color_mode)
        elif fmt == "ansi":
            text = conv.frame_to_ansi(frame, config.color_mode)
        else:
            text = conv.frame_to_plain_text(frame)

        output_path.write_text(text, encoding="utf-8")
        print(f"Saved [{fmt.upper()}] → {output_path}")
        return


    app = AnsiArtApp(initial_file=initial_file, config=config)
    app.run()


if __name__ == "__main__":
    main()
