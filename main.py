"""AnsiArt Pro — entry point.

Usage examples
--------------
  python main.py                        # open TUI with file browser
  python main.py photo.jpg              # load a static image
  python main.py animation.gif          # play a GIF at 15 FPS (default)
  python main.py clip.mp4 --fps 24      # play video at 24 FPS
  python main.py clip.mp4 --width 80 --no-color --gradient blocks
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ansiart-pro",
        description="Convert images, GIFs, and videos into TrueColor ASCII art.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Gradient presets:  standard  dense  blocks  simple  binary
You may also pass a raw gradient string, e.g. --gradient " .oO0@"
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
        "--output", "-o",
        metavar="FILE",
        help="Save ASCII art to a text file and exit (no TUI). Requires a file argument.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args   = parser.parse_args()

    # ── lazy imports keep startup fast ─────────────────────────────────────────
    from ansiart.core import GRADIENT_PRESETS, ConversionConfig
    from ansiart.tui.app import AnsiArtApp

    # resolve gradient
    gradient_str = GRADIENT_PRESETS.get(args.gradient, args.gradient)
    if len(gradient_str) < 2:
        parser.error(
            f"Gradient must contain at least 2 characters.  "
            f"Known presets: {', '.join(GRADIENT_PRESETS)}"
        )

    # build config
    config = ConversionConfig(
        target_width=max(20, min(500, args.width)),
        font_ratio=max(0.1, min(2.0, args.font_ratio)),
        gradient=gradient_str,
        color_mode=not args.no_color,
        invert=args.invert,
        target_fps=max(1.0, min(60.0, args.fps)),
    )

    # validate file path when provided
    initial_file: Path | None = None
    if args.file:
        initial_file = Path(args.file).expanduser().resolve()
        if not initial_file.exists():
            print(f"error: file not found — '{initial_file}'", file=sys.stderr)
            sys.exit(1)

    # ── headless export mode ────────────────────────────────────────────────────
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
            else:  # VIDEO
                img, _ = next(iter(MediaLoader.iter_video_frames(initial_file, config)))
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)

        frame = conv.image_to_frame(img, config)
        text  = conv.frame_to_plain_text(frame)

        output_path = Path(args.output).expanduser()
        output_path.write_text(text, encoding="utf-8")
        print(f"Saved → {output_path}")
        return

    # launch TUI
    app = AnsiArtApp(initial_file=initial_file, config=config)
    app.run()


if __name__ == "__main__":
    main()
