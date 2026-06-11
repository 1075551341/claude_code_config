#!/usr/bin/env python3
"""Cursor hook stdin/stdout 工具。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_emitted = False


def setup_stdio() -> None:
    try:
        if hasattr(sys.stdout, "buffer"):
            import io

            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
    except Exception as e:
        print(f"cursor-guard: stdout setup failed: {e}", file=sys.stderr)


def ensure_lib_path() -> None:
    lib = Path(__file__).resolve().parent
    if str(lib) not in sys.path:
        sys.path.insert(0, str(lib))


def read_stdin() -> dict:
    """读取 Cursor 传入的单行 JSON；用 readline 避免 stdin 未关闭时 read() 阻塞至超时。"""
    try:
        if sys.stdin is None or sys.stdin.closed:
            return {}
        if sys.stdin.isatty():
            return {}
        raw = sys.stdin.readline()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except (json.JSONDecodeError, OSError, ValueError):
        return {}


def write_json(obj: dict) -> None:
    global _emitted
    _emitted = True
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def ensure_hook_output() -> None:
    """Cursor 要求 hook stdout 必须为合法 JSON；无动作时输出 {}。"""
    global _emitted
    if not _emitted:
        write_json({})


def extract_file_path(data: dict) -> str:
    for key in ("file_path", "path"):
        val = data.get(key)
        if isinstance(val, str) and val:
            return val
    tool_input = data.get("tool_input") or data.get("input") or {}
    if isinstance(tool_input, dict):
        for key in ("file_path", "path", "target_file"):
            val = tool_input.get(key)
            if isinstance(val, str) and val:
                return val
    return ""


def extract_tool_name(data: dict) -> str:
    for key in ("tool_name", "tool", "name"):
        val = data.get(key)
        if isinstance(val, str) and val:
            return val
    return ""


def extract_prompt(data: dict) -> str:
    for key in ("prompt", "text", "message", "content"):
        val = data.get(key)
        if isinstance(val, str):
            return val
    return ""
