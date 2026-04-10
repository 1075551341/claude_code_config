#!/usr/bin/env python3
"""
PreToolUse Hook: Block Git Hook Bypass Flag
阻止 git --no-verify 标志，确保 pre-commit、commit-msg、pre-push hooks 不被跳过

exit 0 = 允许执行
exit 2 = 阻止执行
"""
import json
import sys
import io

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        
        # 只检查 Bash 工具
        if tool_name != "Bash":
            sys.exit(0)
        
        command = tool_input.get("command", "")
        
        # 检测 --no-verify 标志
        if "--no-verify" in command and "git" in command:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": "⛔ 阻止：git --no-verify 会跳过 pre-commit、commit-msg、pre-push hooks\n\n请移除 --no-verify 标志，让 hooks 正常执行以确保代码质量。"
                }
            }
            sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
            sys.stdout.flush()
            sys.exit(2)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
