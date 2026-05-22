#!/usr/bin/env python3
"""
PostToolUse Hook: Build Analysis
在构建命令完成后执行后台分析

exit 0 = 正常结束
"""
import json
import sys
import io
import re
import os
import subprocess

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


BUILD_PATTERNS = [
    r"npm\s+run\s+build",
    r"yarn\s+build",
    r"pnpm\s+build",
    r"bun\s+run\s+build",
    r"cargo\s+build",
    r"gradle\s+build",
    r"mvn\s+package",
]


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

        if tool_name != "Bash":
            sys.exit(0)

        command = tool_input.get("command", "").strip()
        
        # 检测构建命令
        is_build = any(re.search(p, command, re.IGNORECASE) for p in BUILD_PATTERNS)
        
        if not is_build:
            sys.exit(0)

        # 检查构建是否成功
        tool_result = data.get("tool_result", {})
        returncode = tool_result.get("returncode", 0)
        
        if returncode != 0:
            sys.exit(0)  # 构建失败，跳过分析

        # 执行分析（异步，不阻塞）
        try:
            # 检查构建产物大小
            dist_dir = os.path.join(os.getcwd(), "dist")
            if os.path.exists(dist_dir):
                total_size = 0
                for root, dirs, files in os.walk(dist_dir):
                    for file in files:
                        total_size += os.path.getsize(os.path.join(root, file))
                
                size_mb = total_size / (1024 * 1024)
                
                if size_mb > 10:
                    analysis = (
                        f"📊 Build Analysis:\n"
                        f"  • 构建产物大小: {size_mb:.2f} MB\n"
                        f"  • 建议检查是否有未使用的依赖\n"
                        f"  • 考虑使用代码分割优化加载"
                    )
                    
                    result = {
                        "hookSpecificOutput": {
                            "hookEventName": "PostToolUse",
                            "additionalContext": analysis,
                        }
                    }
                    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
                    sys.stdout.flush()
        except Exception:
            pass

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
