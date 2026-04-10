#!/usr/bin/env python3
"""
Stop Hook: Session Summary
在会话结束时持久化会话状态

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

        # 检查是否有 transcript 路径
        transcript_path = data.get("transcript_path")
        if not transcript_path:
            sys.exit(0)

        # 保存会话摘要
        summary_dir = os.path.expanduser("~/.claude/sessions")
        os.makedirs(summary_dir, exist_ok=True)
        
        summary_file = os.path.join(summary_dir, f"summary-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
        
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "cwd": os.getcwd(),
            "transcript_path": transcript_path,
            "tool_calls": data.get("tool_calls", []),
            "event": "session_end"
        }
        
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
