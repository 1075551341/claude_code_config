#!/usr/bin/env python3
"""
PostToolUse Hook: 操作日志
记录所有文件编辑和 Bash 命令到日志文件
日志位置：~/.claude/logs/operations.log

修复记录：
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: BaseException/SystemExit 分离捕获
- FIX: 轮转逻辑加独立 try/except，写入失败不影响主流程
"""
import json
import sys
import os
from datetime import datetime

LOG_DIR  = os.path.join(os.path.expanduser("~"), ".claude", "logs")
LOG_FILE = os.path.join(LOG_DIR, "operations.log")
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB 自动轮转


def rotate_if_needed():
    try:
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
            backup = LOG_FILE.replace(".log", ".bak.log")
            if os.path.exists(backup):
                os.remove(backup)
            os.rename(LOG_FILE, backup)
    except Exception:
        pass


def write_log(log_line: str):
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        rotate_if_needed()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception:
        pass


def main():
    try:
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name  = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        session_id = data.get("session_id", "unknown")[:8]
        ts         = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if tool_name in ("Edit", "Write", "MultiEdit"):
            file_path = tool_input.get("file_path", "unknown")
            write_log(f"[{ts}] [{session_id}] {tool_name:<12} {file_path}")

        elif tool_name == "Bash":
            command = tool_input.get("command", "")[:150]
            write_log(f"[{ts}] [{session_id}] Bash         {command}")

        elif tool_name in ("Read", "Glob", "Grep"):
            target = tool_input.get("file_path") or tool_input.get("pattern", "")
            write_log(f"[{ts}] [{session_id}] {tool_name:<12} {target}")

        elif tool_name == "WebSearch":
            query = tool_input.get("query", "")[:100]
            write_log(f"[{ts}] [{session_id}] WebSearch    {query}")

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
