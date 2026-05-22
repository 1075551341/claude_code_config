#!/usr/bin/env python3
"""
PreToolUse Hook: Tmux Reminder
提醒用户对长时间运行的命令使用 tmux

exit 0 = 允许执行（仅提醒）
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
    """检测是否在 tmux 会话中"""
    return bool(os.environ.get("TMUX"))


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
        
        # 检测长时间运行命令
        is_long_running = any(re.search(p, command, re.IGNORECASE) for p in LONG_RUNNING_PATTERNS)
        
        if not is_long_running:
            sys.exit(0)

        # 如果在 tmux 中，无需提醒
        if is_in_tmux():
            sys.exit(0)

        # 输出提醒（不阻止执行）
        reminder = (
            "💡 Tmux Reminder: 检测到可能长时间运行的命令\n\n"
            "建议使用 tmux 以获得更好的体验：\n"
            "  • 命令在后台持续运行\n"
            "  • 终端关闭后不中断\n"
            "  • 可随时重新连接查看日志\n\n"
            "快速启动: `tmux new -s work`"
        )

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": reminder,
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
