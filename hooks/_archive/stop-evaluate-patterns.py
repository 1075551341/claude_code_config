#!/usr/bin/env python3
"""
Stop Hook: Evaluate Session for Extractable Patterns
评估会话以识别可提取的模式用于持续学习

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

# 模式提取存储路径
PATTERNS_DIR = os.path.expanduser("~/.claude/patterns")
ENABLE_PATTERN_EXTRACTION = os.environ.get("ECC_ENABLE_PATTERN_EXTRACTION", "1") == "1"


def extract_patterns(data):
    """提取可识别的模式"""
    if not ENABLE_PATTERN_EXTRACTION:
        return []
    
    patterns = []
    
    # 识别常用工具组合模式
    tool_calls = data.get("tool_calls", [])
    if len(tool_calls) >= 3:
        tool_names = [call.get("tool_name", "") for call in tool_calls]
        
        # 检测常见模式
        if "Edit" in tool_names and "Bash" in tool_names:
            patterns.append({"type": "edit-and-test", "frequency": tool_names.count("Edit")})
        
        if "Read" in tool_names and "Edit" in tool_names:
            patterns.append({"type": "read-edit-cycle", "frequency": tool_names.count("Read")})
    
    return patterns


def save_patterns(patterns):
    """保存提取的模式"""
    try:
        os.makedirs(PATTERNS_DIR, exist_ok=True)
        
        pattern_file = os.path.join(PATTERNS_DIR, f"patterns-{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl")
        
        for pattern in patterns:
            pattern["timestamp"] = datetime.utcnow().isoformat()
            pattern["cwd"] = os.getcwd()
            
            with open(pattern_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(pattern, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        
        patterns = extract_patterns(data)
        save_patterns(patterns)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
