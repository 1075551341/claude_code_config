#!/usr/bin/env python3
"""afterAgentResponse: 捕获 R20 / 审查结论 / 非简单标记（v11.4.8）。"""
from __future__ import annotations

import json
import re
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
_NON_SIMPLE_RE = re.compile(r"(执行升档\s*=\s*非简单)|((^|\n).{0,40}非简单)")


def _state_path(claude_home) -> Path:
    raw = str(claude_home or (Path.home() / ".claude"))
    return Path(raw) / ".state" / "verification-gate.json"


def main() -> None:
    try:
        data = read_stdin()
        text = data.get("text") or ""
        if not isinstance(text, str) or len(text.strip()) < 8:
            return
        cfg = load_guard_config()
        claude_home = cfg["sync"]["claude_home"]
        try:
            r20 = import_claude_lib(claude_home, "r20_replay")
        except Exception as e:
            print(f"r20_capture: r20_replay unavailable: {e}", file=sys.stderr)
            return
        session_id = handoff_session_id(data)
        if not session_id:
            print("r20_capture: 无 conversation_id/session_id，跳过", file=sys.stderr)
            return
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
        changed = False
        if _NON_SIMPLE_RE.search(text):
            if not entry.get("non_simple"):
                entry["non_simple"] = True
                changed = True
        if r20.apply_review_verdict(entry, text):
            changed = True
        if r20.replay_ok(text):
            if not entry.get("r20_replay_ok"):
                entry["r20_replay_ok"] = True
                changed = True
        if not changed:
            return
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
