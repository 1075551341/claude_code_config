#!/usr/bin/env python3
"""
SessionEnd Hook: Session End Lifecycle Marker
会话结束生命周期标记（非阻塞）

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

# 会话结束标记文件
SESSION_END_MARKER = os.path.expanduser("~/.claude/session-end-marker.json")


def mark_session_end():
    """标记会话结束"""
    try:
        marker = {
            "timestamp": datetime.utcnow().isoformat(),
            "cwd": os.getcwd(),
            "event": "session_end"
        }
        
        with open(SESSION_END_MARKER, "w", encoding="utf-8") as f:
            json.dump(marker, f, indent=2)
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        
        mark_session_end()

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
