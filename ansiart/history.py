from __future__ import annotations

import json
from pathlib import Path

_HISTORY_FILE = Path.home() / ".ansiart_history.json"
_MAX_ENTRIES  = 20


def load() -> list[Path]:
    try:
        data = json.loads(_HISTORY_FILE.read_text(encoding="utf-8"))
        return [Path(p) for p in data if Path(p).exists()][:_MAX_ENTRIES]
    except Exception:
        return []


def push(path: Path) -> None:
    entries = [p for p in load() if p != path]
    entries.insert(0, path)
    try:
        _HISTORY_FILE.write_text(
            json.dumps([str(p) for p in entries[:_MAX_ENTRIES]]),
            encoding="utf-8",
        )
    except Exception:
        pass
