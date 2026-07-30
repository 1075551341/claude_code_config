#!/usr/bin/env python3
"""
PreToolUse Hook: Capture Tool Use Observations for Continuous Learning
捕获工具使用数据用于持续学习

exit 0 = 允许执行
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

# 观察数据存储路径
OBSERVATIONS_DIR = os.path.expanduser("~/.claude/observations")
ENABLE_OBSERVATION = os.environ.get("ECC_ENABLE_OBSERVATION", "1") == "1"


def save_observation(tool_name, tool_input):
    """保存工具观察数据"""
    if not ENABLE_OBSERVATION:
        return
    
    try:
        os.makedirs(OBSERVATIONS_DIR, exist_ok=True)
        
        observation_file = os.path.join(OBSERVATIONS_DIR, f"observations-{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl")
        
        observation = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool_name": tool_name,
            "tool_input": tool_input,
            "cwd": os.getcwd()
        }
        
        with open(observation_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(observation, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        
        # 保存观察数据
        if tool_name:
            save_observation(tool_name, tool_input)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
