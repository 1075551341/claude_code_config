#!/usr/bin/env python3
"""
PreToolUse Hook: 变更影响门（v10.17.0）
**每个文件首次被编辑**时注入 change-impact-analysis 强制指令（v10.7–v10.16 是每会话
只注入一次，之后所有编辑无门 —— 这正是「遗漏关联文件」的成因：影响分析只在第一个
文件上做过一次，后续文件改动没有任何提示要求重新评估影响面）。
按 session_id + 文件路径记忆；永不 deny（决策：注入提醒，不阻断流程）。
MCP 写工具（serena/fs）的路径解析走 `_lib/tool_paths.py`，与验证追踪器同一套。
"""
import json
import sys
import io
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

from tool_paths import extract_edit_paths  # noqa: E402
from issue_state import claude_home  # noqa: E402  仅取 CLAUDE_HOME 解析，便于测试隔离

STATE_DIR = os.path.join(str(claude_home()), ".state")
STATE_FILE = os.path.join(STATE_DIR, "impact-nudge.json")
STALE_SECONDS = 7 * 24 * 3600
MAX_TRACKED_FILES = 200

FALLBACK = (
    "【门控 · 每个文件首次编辑前必做】\n"
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
    tool_input = data.get("tool_input") or {}
    cwd = str(data.get("cwd") or "")
    paths = extract_edit_paths(tool_input, cwd)

    state = load_state()
    entry = state.setdefault(session_id, {"nudged": True, "ts": time.time(), "files": []})
    tracked = entry.setdefault("files", [])

    # 解析不出路径时退回会话级语义，避免完全失去门控
    targets = paths or ["__unknown__"]
    fresh = [p for p in targets if p not in tracked]
    if not fresh:
        sys.exit(0)

    tracked.extend(fresh)
    del tracked[:-MAX_TRACKED_FILES]
    entry["ts"] = time.time()
    save_state(state)

    message = load_gate_message()
    if len(tracked) > len(fresh):
        names = ", ".join(os.path.basename(p) for p in fresh)
        message = (
            f"{message}\n\n"
            f"（本会话新增编辑目标：{names} — 影响面须针对该文件重新评估，"
            "勿沿用上一个文件的分析结论）"
        )

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": message,
        }
    }
    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    sys.exit(0)


if __name__ == "__main__":
    main()
