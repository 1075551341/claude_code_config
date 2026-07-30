#!/usr/bin/env python3
"""
PostToolUse Hook: Governance Capture
捕获治理事件，如密钥泄露、策略违规等

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

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        # 检查是否有 governance 相关的输出
        tool_result = data.get("tool_result", {})
        output = tool_result.get("stdout", "") + tool_result.get("stderr", "")

        # 检测治理事件关键词
        governance_keywords = [
            "secret", "token", "password", "api key", 
            "credential", "auth", "private key",
            "security", "vulnerability", "risk"
        ]

        detected = False
        for keyword in governance_keywords:
            if keyword.lower() in output.lower():
                detected = True
                break

        if not detected:
            sys.exit(0)

        # 记录治理事件
        log_dir = os.path.expanduser("~/.claude/logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "governance-log.json")
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool_name,
            "input": str(tool_input)[:500],  # 限制长度
            "event_type": "governance_alert",
            "severity": "medium"
        }

        try:
            # 读取现有日志
            existing_events = []
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    import json as json_lib
                    try:
                        existing_events = json_lib.load(f)
                    except:
                        existing_events = []
            
            existing_events.append(event)
            
            # 保持最近 100 条记录
            if len(existing_events) > 100:
                existing_events = existing_events[-100:]
            
            with open(log_file, "w", encoding="utf-8") as f:
                import json as json_lib
                json_lib.dump(existing_events, f, indent=2)
        except Exception:
            pass

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
