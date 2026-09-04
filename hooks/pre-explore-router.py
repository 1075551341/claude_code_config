#!/usr/bin/env python3
"""PreToolUse R17 软门：结构探索工具前若本会话未见 codegraph_explore，注入提示。"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

from issue_state import claude_home  # noqa: E402

STATE = os.path.join(str(claude_home()), ".state", "explore-router.json")
STRUCTURE_TOOLS = {
    "Grep",
    "Glob",
    "Read",
    "mcp__grep__searchGitHub",
}
CODEGRAPH_MARKERS = (
    "codegraph_explore",
    "mcp__codegraph__",
    "mcp__user-codegraph__",
)
SKIP_PATH_HINTS = (
    "/skills/",
    "\\skills\\",
    "/rules/",
    "\\rules\\",
    "CLAUDE.md",
    "SKILL.md",
    "/hooks/",
    "\\hooks\\",
)


def _load() -> dict:
    try:
        with open(STATE, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save(data: dict) -> None:
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False)


def _tool_name(data: dict) -> str:
    return str(data.get("tool_name") or data.get("tool") or data.get("name") or "")


def _is_codegraph(name: str) -> bool:
    n = name.lower()
    return any(m.lower() in n for m in CODEGRAPH_MARKERS)


def main() -> None:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        data = {}
    session_id = str(data.get("session_id") or data.get("conversation_id") or "unknown")
    tool = _tool_name(data)
    state = _load()
    entry = state.setdefault(session_id, {"codegraph": False, "ts": 0})
    if _is_codegraph(tool):
        entry["codegraph"] = True
        entry["ts"] = time.time()
        _save(state)
        sys.exit(0)
    if tool not in STRUCTURE_TOOLS:
        sys.exit(0)
    if entry.get("codegraph"):
        sys.exit(0)
    tool_input = data.get("tool_input") or data.get("input") or {}
    path = str(tool_input.get("path") or tool_input.get("file_path") or "")
    if any(h in path.replace("/", "\\") or h in path for h in SKIP_PATH_HINTS):
        sys.exit(0)
    mode = (os.environ.get("CLAUDE_R17_MODE") or "warn").strip().lower()
    msg = (
        "R17：结构/调用链探索须先 codegraph_explore。"
        "本会话尚未记录 codegraph 调用；请先 MCP codegraph_explore，Grep/Read 仅作残留核对。"
    )
    if mode in ("deny", "block"):
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()
        sys.exit(2)
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": msg,
        }
    }
    sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    sys.exit(0)


if __name__ == "__main__":
    main()
