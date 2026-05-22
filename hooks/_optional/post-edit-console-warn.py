#!/usr/bin/env python3
"""
PostToolUse Hook: Console.log 警告
文件编辑后警告 console.log/debugger 语句（exit 0，仅警告）
"""
import json
import sys
import io
import os
import re

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def scan_console_logs(file_path: str) -> list[dict]:
    """扫描文件中的 console.log/debugger"""
    issues = []
    
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return issues

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # 跳过注释行
        if stripped.startswith(("//", "#", "*", "<!--", "/*", "--")):
            continue
        
        # 检测 console.log/warn/error/debug/info
        console_match = re.search(r"console\.(log|warn|error|debug|info)\(", line)
        if console_match:
            issues.append({
                "line": i,
                "type": f"console.{console_match.group(1)}",
                "content": stripped[:80]
            })
        
        # 检测 debugger
        elif "debugger" in line and not stripped.startswith(("//", "#")):
            issues.append({
                "line": i,
                "type": "debugger",
                "content": stripped[:80]
            })

    return issues


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

        # 处理 Edit/Write/MultiEdit
        if tool_name not in ("Edit", "Write", "MultiEdit"):
            sys.exit(0)

        if tool_name == "MultiEdit":
            file_paths = [e.get("file_path", "") for e in tool_input.get("edits", [])]
        else:
            file_paths = [tool_input.get("file_path", "")]

        all_issues = []
        for file_path in file_paths:
            if not file_path or not os.path.exists(file_path):
                continue
            
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in [".js", ".jsx", ".ts", ".tsx"]:
                continue
            
            issues = scan_console_logs(file_path)
            if issues:
                all_issues.append((file_path, issues))

        if not all_issues:
            sys.exit(0)

        # 构建警告消息
        warning = "🔍 检测到 console.log/debugger 语句\n\n"
        
        for file_path, issues in all_issues:
            warning += f"`{os.path.basename(file_path)}`:\n"
            for issue in issues[:3]:  # 每个文件最多显示 3 条
                warning += f"  第 {issue['line']} 行: {issue['type']}\n"
            if len(issues) > 3:
                warning += f"  ... 还有 {len(issues) - 3} 处\n"
            warning += "\n"
        
        warning += "**建议：**\n"
        warning += "- 移除调试用的 console.log\n"
        warning += "- 移除 debugger 语句\n"
        warning += "- 使用适当的日志库（如 pino、winston）替代\n"
        warning += "- 确保在提交前清理所有调试代码"

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": warning,
            }
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
