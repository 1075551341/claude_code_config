#!/usr/bin/env python3
"""
PreToolUse Hook: 变更影响门（v10.7.0）
本会话首次 Edit/Write/MultiEdit 时注入 change-impact-analysis 强制指令。
按 session_id 状态记忆；永不 deny（决策：注入提醒，不阻断流程）。
"""
import json
import sys
import io
import os
import time

STATE_DIR = os.path.expanduser("~/.claude/.state")
STATE_FILE = os.path.join(STATE_DIR, "impact-nudge.json")
STALE_SECONDS = 7 * 24 * 3600

FALLBACK = (
    "【门控 · 本会话首次编辑前必做】\n"
    "1. codegraph_explore 目标 blast-radius；2. Grep 全项目引用；"
    "3. 配置类改动查 MANIFEST depends_on。范围不明不修改。"
)


def load_gate_message() -> str:
    gate_file = os.path.join(os.path.dirname(__file__), "_lib", "gate_messages.md")
    try:
        with open(gate_file, "r", encoding="utf-8") as f:
            content = f.read()
        section = content.split("## 变更影响门", 1)[1].strip()
        return section if section else FALLBACK
    except (OSError, IndexError) as e:
        print(f"pre-edit-impact-nudge: gate_messages read failed: {e}", file=sys.stderr)
        return FALLBACK


def load_state() -> dict:
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"pre-edit-impact-nudge: state read failed: {e}", file=sys.stderr)
    return {}


def save_state(state: dict) -> None:
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        now = time.time()
        state = {k: v for k, v in state.items() if now - v.get("ts", 0) < STALE_SECONDS}
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)
    except OSError as e:
        print(f"pre-edit-impact-nudge: state write failed: {e}", file=sys.stderr)


def main():
    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"pre-edit-impact-nudge: stdout wrap failed: {e}", file=sys.stderr)

    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        print(f"pre-edit-impact-nudge: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    session_id = str(data.get("session_id") or data.get("conversation_id") or "unknown")
    state = load_state()
    if state.get(session_id, {}).get("nudged"):
        sys.exit(0)

    state[session_id] = {"nudged": True, "ts": time.time()}
    save_state(state)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": load_gate_message(),
        }
    }
    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    sys.exit(0)


if __name__ == "__main__":
    main()
