#!/usr/bin/env python3
"""
Stop Hook: Persist Session State
持久化会话状态

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

# 会话状态存储路径
SESSION_STATE_DIR = os.path.expanduser("~/.claude/session-states")


def persist_session_state(data):
    """持久化会话状态"""
    try:
        os.makedirs(SESSION_STATE_DIR, exist_ok=True)
        
        session_id = data.get("transcript_path", "").split("/")[-1].replace(".md", "")
        if not session_id:
            session_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        
        state_file = os.path.join(SESSION_STATE_DIR, f"{session_id}.json")
        
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "cwd": os.getcwd(),
            "transcript_path": data.get("transcript_path", ""),
            "tool_count": len(data.get("tool_calls", [])) if "tool_calls" in data else 0
        }
        
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        
        persist_session_state(data)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
