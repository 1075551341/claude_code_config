#!/usr/bin/env python3
"""
PostToolUse Hook: PR Logger
在 gh pr create 后记录 PR URL 和审查命令

exit 0 = 正常结束
"""
import json
import sys
import io
import re
import os

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

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        tool_result = data.get("tool_result", {})

        if tool_name != "Bash":
            sys.exit(0)

        command = tool_input.get("command", "").strip()
        
        # 检测 gh pr create 命令
        if not re.search(r"gh\s+pr\s+create", command, re.IGNORECASE):
            sys.exit(0)

        # 从输出中提取 PR URL
        output = tool_result.get("stdout", "") + tool_result.get("stderr", "")
        
        # GitHub CLI 输出格式: https://github.com/owner/repo/pull/123
        pr_match = re.search(r"https://github\.com/[^/]+/[^/]+/pull/\d+", output)
        
        if not pr_match:
            sys.exit(0)

        pr_url = pr_match.group(0)
        pr_number = pr_url.split("/")[-1]

        # 生成审查命令
        review_cmd = f"gh pr view {pr_number} --web"
        
        # 记录到日志文件
        log_dir = os.path.expanduser("~/.claude/logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "pr-log.txt")
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n--- PR Created ---\n")
            f.write(f"URL: {pr_url}\n")
            f.write(f"Number: {pr_number}\n")
            f.write(f"Review Command: {review_cmd}\n")
            f.write(f"Timestamp: {os.popen('date').read().strip()}\n")

        # 输出提醒
        reminder = (
            f"✅ PR Created: {pr_number}\n\n"
            f"PR URL: {pr_url}\n\n"
            f"快速审查: `{review_cmd}`"
        )

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
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
