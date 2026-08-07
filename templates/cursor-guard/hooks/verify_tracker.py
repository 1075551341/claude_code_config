#!/usr/bin/env python3
"""postToolUse: 完成验证追踪器（v10.14.0）— Cursor 侧。
记录本会话编辑文件/验证命令/审查委派到 ~/.claude/.state/verification-gate.json，
供 verification_gate.py 状态触发与 Claude Code 侧 stop-verification-gate.py 硬门核查。
永不阻断；与 Claude 侧 post-edit-verify-tracker.py 共用 JSON schema。"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    extract_file_path,
    extract_tool_name,
    read_stdin,
    setup_stdio,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config

DEFAULT_VERIFY_PATTERNS = [
    "pytest", "vitest", "jest", "npm test", "pnpm test", "yarn test",
    "npm run test", "npm run lint", "npm run build", "pnpm lint", "pnpm build",
    "tsc", "mypy", "ruff", "eslint", "clippy", "cargo test", "cargo check",
    "go test", "go vet",
]
DEFAULT_REVIEWER_AGENTS = ["eng-reviewer", "qa", "code-reviewer"]
EDIT_TOOLS = {"Write", "StrReplace", "Replace", "Edit", "MultiEdit"}
STALE_SECONDS = 7 * 24 * 3600


def _state_path(claude_home: str) -> Path:
    raw = claude_home or os.path.expanduser("~/.claude")
    return Path(raw) / ".state" / "verification-gate.json"


def load_state(path: Path) -> dict:
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"verify_tracker: state read failed: {e}", file=sys.stderr)
    return {}


def save_state(path: Path, state: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        now = time.time()
        state = {k: v for k, v in state.items() if now - v.get("ts", 0) < STALE_SECONDS}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)
    except OSError as e:
        print(f"verify_tracker: state write failed: {e}", file=sys.stderr)


def is_verify_command(command: str, patterns: list) -> bool:
    cmd = command.lower()
    for pat in patterns:
        if re.search(r"(?<![\w-])" + re.escape(pat.lower()) + r"(?![\w-])", cmd):
            return True
    return False


def extract_shell_command(data: dict) -> str:
    """从 Cursor hook 输入提取 shell 命令（hook_io 未提供此函数，内联实现）。"""
    tool_input = data.get("tool_input") or data.get("input") or {}
    if isinstance(tool_input, dict):
        for key in ("command", "cmd", "shell_command"):
            val = tool_input.get(key)
            if isinstance(val, str) and val:
                return val
    return str(data.get("command") or data.get("cmd") or "")


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        claude_home = cfg["sync"]["claude_home"]
        state_path = _state_path(claude_home)

        tool_name = extract_tool_name(data)
        session_id = str(data.get("session_id") or data.get("conversation_id") or "unknown")

        patterns = cfg.get("verification", {}).get("verify_command_patterns", DEFAULT_VERIFY_PATTERNS)
        reviewers = cfg.get("verification", {}).get("reviewer_agents", DEFAULT_REVIEWER_AGENTS)

        now = time.time()
        state = load_state(state_path)
        entry = state.setdefault(session_id, {
            "ts": now, "cwd": "", "edited_files": [], "verify_commands": [], "reviews": [], "blocks": 0,
        })
        entry["ts"] = now

        changed = False
        if tool_name in EDIT_TOOLS:
            path = extract_file_path(data)
            if path:
                entry["edited_files"].append({"path": path, "ts": now})
                changed = True
        elif tool_name in ("Shell", "Bash"):
            command = extract_shell_command(data)
            if command and is_verify_command(command, patterns):
                entry["verify_commands"].append({"command": command[:300], "ts": now})
                changed = True
        elif tool_name == "Task":
            sub = str(data.get("subagent_type") or data.get("description") or "").lower()
            for reviewer in reviewers:
                if reviewer.lower() in sub:
                    entry["reviews"].append({"agent": reviewer, "ts": now})
                    changed = True
                    break

        if changed:
            save_state(state_path, state)
    except Exception as e:
        print(f"verify_tracker: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
