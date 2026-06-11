#!/usr/bin/env python3
"""持久化 Cursor preCompact 提供的真实上下文计量。"""
from __future__ import annotations

import json
from typing import Any

from config import state_path


def _path():
    return state_path("cursor-context.json")


def save_from_hook_payload(data: dict[str, Any]) -> None:
    pct = data.get("context_usage_percent")
    tokens = data.get("context_tokens")
    window = data.get("context_window_size")
    if pct is None and tokens is None:
        return
    record = {
        "context_usage_percent": float(pct) if pct is not None else None,
        "context_tokens": int(tokens) if tokens is not None else None,
        "context_window_size": int(window) if window is not None else None,
        "trigger": data.get("trigger"),
        "message_count": data.get("message_count"),
        "source": data.get("hook_event_name", "preCompact"),
    }
    _path().write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")


def load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}


def usage_percent() -> float | None:
    rec = load()
    pct = rec.get("context_usage_percent")
    if pct is not None:
        return float(pct)
    tokens = rec.get("context_tokens")
    window = rec.get("context_window_size")
    if tokens is not None and window:
        return min(100.0, (int(tokens) / int(window)) * 100)
    return None
