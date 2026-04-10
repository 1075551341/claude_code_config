#!/usr/bin/env python3
"""
PreCompact Hook: Pre-Compact State
在上下文压缩前保存状态

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


def main():
    try:
        # 读取 stdin
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        # 保存当前会话状态
        state_dir = os.path.expanduser("~/.claude/state")
        os.makedirs(state_dir, exist_ok=True)
        
        state_file = os.path.join(state_dir, "pre-compact-state.json")
        
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "cwd": os.getcwd(),
            "event": "pre_compact",
            "note": "State saved before context compaction"
        }
        
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
