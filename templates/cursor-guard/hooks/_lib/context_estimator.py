#!/usr/bin/env python3
"""Cursor 工具 token 估算 + 70/90 阈值判定。"""
from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

from config import load_guard_config, state_path

TOOL_COST = {
    "Task": 30000,
    "Shell": 4000,
    "Write": 3000,
    "StrReplace": 2500,
    "Read": 1500,
    "Grep": 2500,
    "Glob": 2000,
    "Delete": 1000,
    "CallMcpTool": 5000,
    "FetchMcpResource": 4000,
}
DEFAULT_COST = 3000
LOOP_THRESHOLD = 3


class ContextLevel(str, Enum):
    NORMAL = "normal"
    WARN = "warn"
    FORCE = "force"


def counter_file() -> Path:
    return state_path("tool-counter.json")


def monitor_file() -> Path:
    return state_path("context_monitor.json")


def load_counter() -> tuple[int, int]:
    path = counter_file()
    try:
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            return int(d.get("count", 0)), int(d.get("est_tokens", 0))
    except (OSError, ValueError, json.JSONDecodeError) as e:
        import sys

        print(f"cursor-guard: counter read failed: {e}", file=sys.stderr, flush=True)
    return 0, 0


def save_counter(count: int, est_tokens: int) -> None:
    counter_file().write_text(
        json.dumps({"count": count, "est_tokens": est_tokens}, indent=2),
        encoding="utf-8",
    )


def update_tool_history(tool_name: str) -> int:
    path = monitor_file()
    monitor: dict = {"tool_history": [], "repeat_tool_warns": 0}
    try:
        if path.exists():
            monitor = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    history: list = monitor.get("tool_history", [])
    history.append(tool_name)
    monitor["tool_history"] = history[-20:]
    if len(history) >= LOOP_THRESHOLD and len(set(history[-LOOP_THRESHOLD:])) == 1:
        monitor["repeat_tool_warns"] = int(monitor.get("repeat_tool_warns", 0)) + 1
    path.write_text(json.dumps(monitor, indent=2), encoding="utf-8")
    return int(monitor.get("repeat_tool_warns", 0))


def _effective_pct(tool_est_pct: float) -> float:
    """取工具估算与 Cursor preCompact 实测的较大值。"""
    try:
        from context_usage_store import usage_percent

        cursor_pct = usage_percent()
        if cursor_pct is not None:
            return max(tool_est_pct, cursor_pct)
    except Exception:
        pass
    return tool_est_pct


def record_tool_use(tool_name: str) -> tuple[int, float, ContextLevel]:
    cfg = load_guard_config()
    comp = cfg["compression"]
    window = comp["window_tokens"]
    warn_pct = comp["warn_pct"]
    force_pct = comp["force_pct"]

    count, est_tokens = load_counter()
    count += 1
    est_tokens += TOOL_COST.get(tool_name, DEFAULT_COST)
    tool_est_pct = min(100.0, (est_tokens / window) * 100) if window else 0.0
    est_pct = _effective_pct(tool_est_pct)
    update_tool_history(tool_name)

    if est_pct >= force_pct:
        level = ContextLevel.FORCE
        if comp.get("reset_on_warn"):
            count, est_tokens = 0, 0
    elif est_pct >= warn_pct:
        level = ContextLevel.WARN
    else:
        level = ContextLevel.NORMAL

    save_counter(count, est_tokens)
    return count, est_pct, level


def peek_context() -> tuple[int, float, ContextLevel]:
    cfg = load_guard_config()
    comp = cfg["compression"]
    count, est_tokens = load_counter()
    window = comp["window_tokens"]
    tool_est_pct = min(100.0, (est_tokens / window) * 100) if window else 0.0
    est_pct = _effective_pct(tool_est_pct)
    if est_pct >= comp["force_pct"]:
        level = ContextLevel.FORCE
    elif est_pct >= comp["warn_pct"]:
        level = ContextLevel.WARN
    else:
        level = ContextLevel.NORMAL
    return count, est_pct, level


def detect_tool_loop() -> bool:
    path = monitor_file()
    try:
        if not path.exists():
            return False
        monitor = json.loads(path.read_text(encoding="utf-8"))
        history = monitor.get("tool_history", [])
        if len(history) < 4:
            return False
        recent = history[-4:]
        if len(set(recent)) == 1:
            return True
        from collections import Counter

        return any(c >= 3 for c in Counter(recent).values())
    except (OSError, json.JSONDecodeError):
        return False
