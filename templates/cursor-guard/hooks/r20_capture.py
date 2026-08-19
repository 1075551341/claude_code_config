#!/usr/bin/env python3
"""afterAgentResponse: 捕获合格 R20 终验标记，供 Cursor stop followup 判定（v11.3.4）。"""
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
    import_claude_lib,
    read_stdin,
    setup_stdio,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config
from session_handoff import extract_session_id as handoff_session_id

STALE_SECONDS = 7 * 24 * 3600


def _state_path(claude_home) -> Path:
    raw = str(claude_home or os.path.expanduser("~/.claude"))
    return Path(raw) / ".state" / "verification-gate.json"


def main() -> None:
    try:
        data = read_stdin()
        text = data.get("text") or ""
        if not isinstance(text, str) or len(text.strip()) < 20:
            return
        cfg = load_guard_config()
        claude_home = cfg["sync"]["claude_home"]
        try:
            r20 = import_claude_lib(claude_home, "r20_replay")
        except Exception as e:
            print(f"r20_capture: r20_replay unavailable: {e}", file=sys.stderr)
            return
        if not r20.replay_ok(text):
            return
        session_id = (
            handoff_session_id(data)
            or str(data.get("session_id") or data.get("conversation_id") or "unknown")
        )
        path = _state_path(claude_home)
        now = time.time()
        state: dict = {}
        try:
            if path.exists():
                state = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"r20_capture: state read failed: {e}", file=sys.stderr)
            state = {}
        entry = state.setdefault(session_id, {"ts": now, "started_ts": now})
        entry["r20_replay_ok"] = True
        entry["ts"] = now
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            state = {k: v for k, v in state.items() if now - v.get("ts", 0) < STALE_SECONDS}
            path.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError as e:
            print(f"r20_capture: state write failed: {e}", file=sys.stderr)
    except Exception as e:
        print(f"r20_capture: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
