#!/usr/bin/env python3
"""SubagentStop: 把审查子代理正文写入本轮 reviews[].text（Claude）。

Stop 不得 attach。仅子代理结束时捕获合格 PASS/NEEDS-CHANGES，避免父会话自报。
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

from issue_state import claude_home  # noqa: E402
from r20_replay import attach_review_text, apply_review_verdict, replay_ok, tool_result_text  # noqa: E402

CLAUDE_HOME = str(claude_home())
STATE_DIR = os.path.join(CLAUDE_HOME, ".state")
STATE_FILE = os.path.join(STATE_DIR, "verification-gate.json")
STALE_SECONDS = 7 * 24 * 3600


def load_state() -> dict:
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"r20-capture: state read failed: {exc}", file=sys.stderr)
    return {}


def save_state(state: dict) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    now = time.time()
    trimmed = {
        k: v
        for k, v in state.items()
        if isinstance(v, dict) and now - float(v.get("ts") or 0) < STALE_SECONDS
    }
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(trimmed, fh, ensure_ascii=False, indent=1)


def main() -> None:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        print(f"r20-capture: stdin parse failed: {exc}", file=sys.stderr)
        sys.exit(0)

    session_id = str(data.get("session_id") or data.get("conversation_id") or "")
    if not session_id:
        print("r20-capture: 无 session_id，跳过", file=sys.stderr)
        sys.exit(0)

    text = tool_result_text(data)
    if len(text.strip()) < 8:
        sys.exit(0)

    now = time.time()
    state = load_state()
    entry = state.setdefault(session_id, {"ts": now, "started_ts": now})
    changed = False
    if attach_review_text(entry, text):
        changed = True
    if apply_review_verdict(entry, text):
        changed = True
    if replay_ok(text) and not entry.get("r20_replay_ok"):
        entry["r20_replay_ok"] = True
        changed = True
    if not changed:
        sys.exit(0)
    entry["ts"] = now
    try:
        save_state(state)
    except OSError as exc:
        print(f"r20-capture: state write failed: {exc}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
