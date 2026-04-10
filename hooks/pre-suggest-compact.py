#!/usr/bin/env python3
"""
PreToolUse Hook: Suggest Manual Compaction
在大约 50 次工具调用后建议手动压缩上下文

exit 0 = 允许执行
"""
import json
import sys
import io
import os

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# 工具调用计数阈值
COMPACT_SUGGEST_THRESHOLD = int(os.environ.get("CLAUDE_COMPACT_THRESHOLD", 50))
COUNTER_FILE = os.path.expanduser("~/.claude/tool-call-counter.json")


def load_counter():
    """加载工具调用计数"""
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"count": 0, "last_reset": None}


def save_counter(counter):
    """保存工具调用计数"""
    try:
        os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)
        with open(COUNTER_FILE, "w", encoding="utf-8") as f:
            json.dump(counter, f, indent=2)
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}

        tool_name = data.get("tool_name", "")
        
        # 跳过非工具调用
        if not tool_name:
            sys.exit(0)

        # 加载计数器
        counter = load_counter()
        counter["count"] += 1
        
        # 检查是否达到阈值
        if counter["count"] >= COMPACT_SUGGEST_THRESHOLD:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": f"💡 提示：已执行 {counter['count']} 次工具调用，建议运行 /compact 压缩上下文以节省 Token"
                }
            }
            sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
            sys.stdout.flush()
            
            # 重置计数器
            counter["count"] = 0
            counter["last_reset"] = json.dumps({"timestamp": __import__("datetime").datetime.utcnow().isoformat()})
        
        # 保存计数器
        save_counter(counter)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
