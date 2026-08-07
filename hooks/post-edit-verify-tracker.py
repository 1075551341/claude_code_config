#!/usr/bin/env python3
"""
PostToolUse Hook: 完成验证追踪器（v10.14.0）
按 session_id 记录本会话编辑文件/验证命令/审查委派，供 stop-verification-gate 硬门核查。
状态 ~/.claude/.state/verification-gate.json（7 天自动清理）；永不阻断（exit 0）。
"""
import json
import sys
import io
import os
import re
import time

STATE_DIR = os.path.expanduser("~/.claude/.state")
STATE_FILE = os.path.join(STATE_DIR, "verification-gate.json")
CONFIG_FILE = os.path.expanduser("~/.claude/config/quality_gates.json")
STALE_SECONDS = 7 * 24 * 3600

DEFAULT_VERIFY_PATTERNS = [
    "pytest", "vitest", "jest", "npm test", "pnpm test", "yarn test",
    "npm run test", "npm run lint", "npm run build", "pnpm lint", "pnpm build",
    "tsc", "mypy", "ruff", "eslint", "clippy", "cargo test", "cargo check",
    "go test", "go vet",
]
DEFAULT_REVIEWER_AGENTS = ["eng-reviewer", "qa", "code-reviewer"]

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def load_config() -> dict:
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f).get("verification_gate", {})
            return {
                "verify_command_patterns": cfg.get("verify_command_patterns", DEFAULT_VERIFY_PATTERNS),
                "reviewer_agents": cfg.get("reviewer_agents", DEFAULT_REVIEWER_AGENTS),
            }
    except (OSError, json.JSONDecodeError) as e:
        print(f"post-edit-verify-tracker: config read failed: {e}", file=sys.stderr)
    return {
        "verify_command_patterns": DEFAULT_VERIFY_PATTERNS,
        "reviewer_agents": DEFAULT_REVIEWER_AGENTS,
    }


def load_state() -> dict:
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"post-edit-verify-tracker: state read failed: {e}", file=sys.stderr)
    return {}


def save_state(state: dict) -> None:
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        now = time.time()
        state = {k: v for k, v in state.items() if now - v.get("ts", 0) < STALE_SECONDS}
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)
    except OSError as e:
        print(f"post-edit-verify-tracker: state write failed: {e}", file=sys.stderr)


def is_verify_command(command: str, patterns: list) -> bool:
    cmd = command.lower()
    for pat in patterns:
        if re.search(r"(?<![\w-])" + re.escape(pat.lower()) + r"(?![\w-])", cmd):
            return True
    return False


def main():
    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"post-edit-verify-tracker: stdout wrap failed: {e}", file=sys.stderr)

    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        print(f"post-edit-verify-tracker: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    session_id = str(data.get("session_id") or data.get("conversation_id") or "unknown")
    tool_name = str(data.get("tool_name") or "")
    tool_input = data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}
    cwd = str(data.get("cwd") or "")

    cfg = load_config()
    now = time.time()
    state = load_state()
    entry = state.setdefault(session_id, {
        "ts": now, "cwd": cwd, "edited_files": [], "verify_commands": [], "reviews": [], "blocks": 0,
    })
    entry["ts"] = now
    if cwd:
        entry["cwd"] = cwd

    changed = False
    if tool_name in EDIT_TOOLS:
        path = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
        if path:
            entry["edited_files"].append({"path": path, "ts": now})
            changed = True
    elif tool_name == "Bash":
        command = str(tool_input.get("command") or "")
        if command and is_verify_command(command, cfg["verify_command_patterns"]):
            entry["verify_commands"].append({"command": command[:300], "ts": now})
            changed = True
    elif tool_name == "Task":
        agent = str(tool_input.get("subagent_type") or tool_input.get("description") or "").lower()
        for reviewer in cfg["reviewer_agents"]:
            if reviewer.lower() in agent:
                entry["reviews"].append({"agent": reviewer, "ts": now})
                changed = True
                break

    if changed:
        save_state(state)
    sys.exit(0)


if __name__ == "__main__":
    main()
