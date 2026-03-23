#!/usr/bin/env python3
"""
PostToolUse Hook: 操作日志
记录所有文件编辑和 Bash 命令到日志文件
日志位置：C:/Users/DELL/.claude/logs/operations.log
"""
import json
import sys
import os
from datetime import datetime

LOG_DIR  = os.path.join(os.path.expanduser("~"), ".claude", "logs")
LOG_FILE = os.path.join(LOG_DIR, "operations.log")
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB 自动轮转

def rotate_if_needed():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        backup = LOG_FILE.replace(".log", ".bak.log")
        if os.path.exists(backup):
            os.remove(backup)
        os.rename(LOG_FILE, backup)

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name  = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", "unknown")[:8]
    ts         = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 构建日志行
    if tool_name in ("Edit", "Write", "MultiEdit"):
        file_path = tool_input.get("file_path", "unknown")
        log_line  = f"[{ts}] [{session_id}] {tool_name:10s} {file_path}"

    elif tool_name == "Bash":
        command  = tool_input.get("command", "")[:120]
        log_line = f"[{ts}] [{session_id}] Bash       {command}"

    elif tool_name in ("Read", "Glob", "Grep"):
        target   = tool_input.get("file_path") or tool_input.get("pattern", "")
        log_line = f"[{ts}] [{session_id}] {tool_name:10s} {target}"

    else:
        sys.exit(0)

    # 写入日志
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        rotate_if_needed()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception:
        pass

    sys.exit(0)

if __name__ == "__main__":
    main()
