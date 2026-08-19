#!/usr/bin/env python3
"""postToolUse: 每个文件首次成功编辑后注入五维迷你验收（v11.3.4）。"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    extract_file_path,
    extract_tool_name,
    import_claude_lib,
    read_stdin,
    setup_stdio,
    write_json,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config
from session_handoff import extract_session_id as handoff_session_id

STALE_SECONDS = 7 * 24 * 3600
FALLBACK_EDIT_TOOLS = {"Write", "StrReplace", "Replace", "Edit", "MultiEdit"}


def _state_path(claude_home: str) -> Path:
    raw = claude_home or os.path.expanduser("~/.claude")
    return Path(raw) / ".state" / "verification-gate.json"


def _load_state(path: Path) -> dict:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"first_edit_verify: state read failed: {e}", file=sys.stderr)
    return {}


def _save_state(path: Path, state: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        now = time.time()
        state = {k: v for k, v in state.items() if now - v.get("ts", 0) < STALE_SECONDS}
        path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError as e:
        print(f"first_edit_verify: state write failed: {e}", file=sys.stderr)


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        if not cfg["verification"]["enabled"]:
            return
        claude_home = cfg["sync"]["claude_home"]
        tool_name = extract_tool_name(data)
        cwd = str(data.get("cwd") or "")
        session_id = (
            handoff_session_id(data)
            or str(data.get("session_id") or data.get("conversation_id") or "unknown")
        )

        tool_paths = None
        try:
            tool_paths = import_claude_lib(claude_home, "tool_paths")
        except Exception as e:
            print(f"first_edit_verify: tool_paths unavailable: {e}", file=sys.stderr)

        is_edit = tool_paths.is_edit_tool(tool_name) if tool_paths else tool_name in FALLBACK_EDIT_TOOLS
        if not is_edit:
            return

        tool_input = data.get("tool_input") or data.get("input") or {}
        paths = tool_paths.extract_edit_paths(tool_input, cwd) if tool_paths else []
        if not paths:
            single = extract_file_path(data)
            paths = [single] if single else []
        if not paths:
            return

        try:
            fev = import_claude_lib(claude_home, "first_edit_verify")
        except Exception as e:
            print(f"first_edit_verify: lib unavailable: {e}", file=sys.stderr)
            return

        path = _state_path(str(claude_home))
        now = time.time()
        state = _load_state(path)
        entry = state.setdefault(
            session_id,
            {
                "ts": now,
                "started_ts": now,
                "cwd": cwd,
                "edited_files": [],
                "verify_commands": [],
                "reviews": [],
                "blocks": 0,
            },
        )
        entry["ts"] = now
        fresh = fev.fresh_edit_paths(entry, paths)
        if not fresh:
            return
        _save_state(path, state)
        message = fev.compose_message(fev.load_first_edit_message(claude_home), fresh)
        write_json({"additional_context": message, "agent_message": message})
    except Exception as e:
        print(f"first_edit_verify: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
