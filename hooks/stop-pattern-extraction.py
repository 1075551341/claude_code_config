#!/usr/bin/env python3
"""
Stop Hook: Pattern Extraction
评估会话以提取可学习的模式

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

        # 简单的模式检测
        tool_calls = data.get("tool_calls", [])
        
        patterns = []
        
        # 检测常用工具组合
        tools_used = [call.get("tool_name") for call in tool_calls]
        
        if "Edit" in tools_used and "Bash" in tools_used:
            patterns.append({
                "type": "edit_then_test",
                "description": "编辑后执行测试",
                "confidence": 0.8
            })
        
        if "Read" in tools_used and "Edit" in tools_used:
            patterns.append({
                "type": "read_edit_pattern",
                "description": "读取后编辑模式",
                "confidence": 0.7
            })
        
        if not patterns:
            sys.exit(0)

        # 保存提取的模式
        patterns_dir = os.path.expanduser("~/.claude/patterns")
        os.makedirs(patterns_dir, exist_ok=True)
        
        patterns_file = os.path.join(patterns_dir, f"patterns-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
        
        with open(patterns_file, "w", encoding="utf-8") as f:
            json.dump(patterns, f, indent=2)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
