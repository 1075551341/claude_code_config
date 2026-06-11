#!/usr/bin/env python3
"""
PostToolUse Hook: 文件变更后触发 codegraph 增量同步
触发: Write|Edit|MultiEdit
条件: 变更含 .ts/.tsx/.js/.jsx/.py/.go/.rs 或累计变更≥1
"""
import json
import os
import subprocess
import sys
from pathlib import Path

CODE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java", ".rb"}
STATE_FILE = Path.home() / ".claude" / ".state" / "codegraph_sync_state.json"
MIN_CHANGES = int(os.environ.get("CODEGRAPH_SYNC_MIN_CHANGES", "1"))


def load_state():
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"post-codegraph-sync: state read failed: {e}", file=sys.stderr)
    return {"change_count": 0, "last_sync": None}


def save_state(state: dict):
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"post-codegraph-sync: state write failed: {e}", file=sys.stderr)


def should_sync(tool_input: dict, state: dict) -> bool:
    file_path = tool_input.get("file_path") or tool_input.get("path") or ""
    if file_path and Path(file_path).suffix.lower() in CODE_EXTENSIONS:
        return True
    return state.get("change_count", 0) >= MIN_CHANGES


def run_codegraph_sync(cwd: str):
    commands = [
        ["codegraph", "sync", "--incremental"],
        ["npx", "-y", "@colbymchenry/codegraph", "sync", "--incremental"],
    ]
    last_err = None
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                return True, " ".join(cmd)
            last_err = result.stderr or result.stdout or f"exit {result.returncode}"
        except FileNotFoundError:
            last_err = f"command not found: {cmd[0]}"
        except subprocess.TimeoutExpired:
            last_err = "codegraph sync timeout (120s)"
        except Exception as e:
            last_err = str(e)
    return False, last_err


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        print(f"post-codegraph-sync: stdin failed: {e}", file=sys.stderr)
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    state = load_state()
    state["change_count"] = state.get("change_count", 0) + 1

    if not should_sync(tool_input, state):
        save_state(state)
        sys.exit(0)

    cwd = os.getcwd()
    ok, detail = run_codegraph_sync(cwd)

    if ok:
        state["change_count"] = 0
        state["last_sync"] = detail
    else:
        print(f"post-codegraph-sync: sync skipped — {detail}", file=sys.stderr)
        state["last_sync_error"] = detail

    save_state(state)
    sys.exit(0)


if __name__ == "__main__":
    main()
