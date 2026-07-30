#!/usr/bin/env python3
"""preToolUse: 变更影响门（v10.7.0）。
本会话首次 Write/StrReplace 时注入 change-impact-analysis 强制指令。
永不 deny（决策：注入提醒，不阻断流程）。"""
from __future__ import annotations

import json
import sys
import time

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    read_stdin,
    setup_stdio,
    write_json,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config, state_path
from gate_messages import load_gate
from session_handoff import extract_session_id as handoff_session_id

STATE_NAME = "impact_nudge.json"
STALE_SECONDS = 7 * 24 * 3600


def _load_state() -> dict:
    path = state_path(STATE_NAME)
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"impact_nudge: state read failed: {e}", file=sys.stderr)
    return {}


def _save_state(state: dict) -> None:
    path = state_path(STATE_NAME)
    try:
        now = time.time()
        state = {k: v for k, v in state.items() if now - v.get("ts", 0) < STALE_SECONDS}
        path.write_text(json.dumps(state, indent=1), encoding="utf-8")
    except OSError as e:
        print(f"impact_nudge: state write failed: {e}", file=sys.stderr)


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        if not cfg["impact"]["enabled"]:
            return

        session_id = handoff_session_id(data) or "unknown"
        state = _load_state()
        if state.get(session_id, {}).get("nudged"):
            return

        state[session_id] = {"nudged": True, "ts": time.time()}
        _save_state(state)
        write_json(
            {"agent_message": load_gate("impact", cfg["sync"]["claude_home"])}
        )
    except Exception as e:
        print(f"impact_nudge: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
