#!/usr/bin/env python3
"""
PreToolUse Hook: Dev Server Blocker
阻止在 tmux 会话外运行 npm run dev / yarn dev / pnpm dev，确保日志可访问

exit 0 = 允许执行
exit 2 = 阻止执行（stderr 内容会发送给 Claude）
"""
import json
import sys
import io
import os
import subprocess

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def is_in_tmux() -> bool:
    """检测是否在 tmux 会话中"""
    # 检查 TMUX 环境变量
    if os.environ.get("TMUX"):
        return True
    
    # 检查父进程是否为 tmux
    try:
        result = subprocess.run(
            ["ps", "-p", str(os.getppid()), "-o", "comm="],
            capture_output=True,
            text=True,
            timeout=3,
            check=False
        )
        if "tmux" in result.stdout.lower():
            return True
    except Exception:
        pass
    
    return False


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
        
        # 检测 dev server 命令
        dev_patterns = [
            r"npm\s+run\s+dev",
            r"npm\s+dev",
            r"yarn\s+dev",
            r"pnpm\s+dev",
            r"bun\s+run\s+dev",
            r"vite",
            r"next\s+dev",
            r"nuxt\s+dev",
        ]
        
        import re
        is_dev_cmd = any(re.search(p, command, re.IGNORECASE) for p in dev_patterns)
        
        if not is_dev_cmd:
            sys.exit(0)

        # 如果在 tmux 中，允许执行
        if is_in_tmux():
            sys.exit(0)

        # 阻止执行
        error_msg = (
            "🚫 Dev Server Blocker: 检测到开发服务器命令\n\n"
            "请在 tmux 会话中运行此命令，以确保：\n"
            "  • 日志持久化可查看\n"
            "  • 会话断开后服务继续运行\n"
            "  • 可轻松 attach/detach\n\n"
            "**启动 tmux 的方法：**\n"
            "  1. 运行 `tmux new -s dev`\n"
            "  2. 在 tmux 会话中运行 dev server 命令\n"
            "  3. 按 Ctrl+B 然后按 D 分离会话\n"
            "  4. 使用 `tmux attach -t dev` 重新连接\n\n"
            "如需跳过此检查，使用 `--no-verify` 标志（不推荐）。"
        )

        sys.stderr.write(error_msg + "\n")
        sys.stderr.flush()
        sys.exit(2)

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
