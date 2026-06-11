#!/usr/bin/env python3
"""
PreToolUse Hook: Tmux Reminder (ECC pre:bash:tmux-reminder)
长时间运行命令在非 tmux 环境提醒，不阻断执行。
"""
import json
import os
import re
import sys
import io

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception as e:
    print(f"pre-tmux-reminder: stdout setup failed: {e}", file=sys.stderr)

LONG_RUNNING_PATTERNS = [
    r"npm\s+run\s+(dev|start|build|test)",
    r"yarn\s+(dev|start|build|test)",
    r"pnpm\s+(dev|start|build|test)",
    r"bun\s+run\s+(dev|start|build|test)",
    r"pytest\s+",
    r"python\s+-m\s+pytest",
    r"cargo\s+(build|test|run)",
    r"go\s+test\s+.*-v",
    r"gradle\s+test",
    r"mvn\s+(test|package|install)",
    r"docker\s+(build|compose\s+up)",
]


def is_in_tmux() -> bool:
    return bool(os.environ.get("TMUX"))


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        print(f"pre-tmux-reminder: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "").strip()
    is_long = any(re.search(p, command, re.IGNORECASE) for p in LONG_RUNNING_PATTERNS)
    if not is_long or is_in_tmux():
        sys.exit(0)

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                "💡 Tmux Reminder: 长时间命令建议用 tmux\n"
                "  • 终端关闭不中断  • 可重连看日志\n"
                "快速启动: `tmux new -s work`"
            ),
        }
    }
    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    sys.exit(0)


if __name__ == "__main__":
    main()
