#!/usr/bin/env python3
"""
PostToolUse Hook: Cost Tracker
记录 bash 工具使用情况用于成本追踪

exit 0 = 正常结束
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

# 成本追踪日志路径
COST_LOG_FILE = os.path.expanduser("~/.claude/cost-tracker.log")
ENABLE_COST_TRACKING = os.environ.get("ECC_ENABLE_COST_TRACKING", "1") == "1"


def log_cost(tool_name, tool_input, tool_output):
    """记录成本数据"""
    if not ENABLE_COST_TRACKING:
        return
    
    try:
        os.makedirs(os.path.dirname(COST_LOG_FILE), exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool_name": tool_name,
            "command": tool_input.get("command", "") if tool_name == "Bash" else "",
            "cwd": os.getcwd(),
            "exit_code": tool_output.get("exit_code", 0) if tool_output else 0
        }
        
        with open(COST_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        tool_output = data.get("tool_output", {})
        
        # 主要追踪 Bash 工具
        if tool_name == "Bash":
            log_cost(tool_name, tool_input, tool_output)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
