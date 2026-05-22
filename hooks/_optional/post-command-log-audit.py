#!/usr/bin/env python3
"""
PostToolUse Hook: Bash 命令日志审计
记录所有 Bash 命令到 ~/.claude/bash-commands.log
"""
import json
import sys
import io
import os
from datetime import datetime

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

LOG_FILE = os.path.join(os.path.expanduser("~"), ".claude", "bash-commands.log")


def log_command(command: str, session_id: str):
    """记录命令到日志文件"""
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [Session:{session_id[:8]}] {command}\n"
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception:
        pass


def main():
    try:
        # 读取 stdin
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        # 仅处理 Bash 工具
        if tool_name != "Bash":
            sys.exit(0)

        command = tool_input.get("command", "").strip()
        if not command:
            sys.exit(0)

        session_id = data.get("session_id", "unknown")
        
        # 记录命令
        log_command(command, session_id)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
