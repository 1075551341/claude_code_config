#!/usr/bin/env python3
"""
PreToolUse Hook: Git Push 提醒
在 git push 前提醒用户审查变更
"""
import json
import sys
import io
import re
import subprocess

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def get_pending_commits() -> str:
    """获取待推送的 commit 数量"""
    try:
        result = subprocess.run(
            ["git", "log", "HEAD..@{u}", "--oneline"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        if result.returncode == 0:
            lines = result.stdout.strip().splitlines()
            if lines:
                return f"\n".join(lines[:5])  # 最多显示 5 条
    except Exception:
        pass
    return ""


def get_diff_summary() -> str:
    """获取变更摘要"""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD..@{u}"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return ""


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

        # 仅处理 git push 命令
        if tool_name != "Bash":
            sys.exit(0)

        command = tool_input.get("command", "").strip()
        if not re.match(r"git\s+push", command, re.IGNORECASE):
            sys.exit(0)

        # 获取待推送内容
        commits = get_pending_commits()
        diff = get_diff_summary()

        if not commits and not diff:
            sys.exit(0)  # 无待推送内容

        # 构建提醒消息
        reminder = "🚀 准备推送代码到远程仓库\n\n"
        
        if commits:
            reminder += "**待推送的提交：**\n```\n" + commits + "\n```\n\n"
        
        if diff:
            reminder += "**变更统计：**\n```\n" + diff + "\n```\n\n"
        
        reminder += "**推送前检查清单：**\n"
        reminder += "- [ ] 代码已通过 Lint 和类型检查\n"
        reminder += "- [ ] 相关测试已通过\n"
        reminder += "- [ ] 已审查代码变更\n"
        reminder += "- [ ] Commit message 清晰准确\n"
        reminder += "- [ ] 敏感信息已移除（无硬编码密钥）\n"
        reminder += "- [ ] 如有必要，已更新文档\n\n"
        reminder += "确认无误后继续推送。"

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
