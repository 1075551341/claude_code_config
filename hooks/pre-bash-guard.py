#!/usr/bin/env python3
"""
PreToolUse Hook: 安全拦截器
在 Bash 命令执行前拦截危险操作
exit 0 = 允许执行
exit 2 = 阻止执行（stderr 内容会发送给 Claude）
"""
import json
import sys
import re

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name != "Bash":
        sys.exit(0)

    command = tool_input.get("command", "").strip()

    # ── 危险命令模式（阻止）────────────────────────────────
    DANGER_PATTERNS = [
        # 递归删除根目录或系统目录
        (r"rm\s+-rf\s+/$",              "禁止删除根目录"),
        (r"rm\s+-rf\s+/\*",             "禁止删除根目录所有文件"),
        (r"rm\s+-rf\s+~\s*$",           "禁止删除用户主目录"),
        (r"rm\s+-rf\s+C:\\\\?\*",       "禁止删除 C 盘所有文件"),
        # 格式化/磁盘操作
        (r"^format\s+[A-Za-z]:",        "禁止格式化磁盘"),
        (r"^mkfs",                       "禁止格式化分区"),
        (r"dd\s+if=.+of=/dev/",         "禁止 dd 写入设备"),
        # 强制推送到主分支
        (r"git push.+--force\s*$",      "禁止强制推送（未指定分支）"),
        (r"git push.+-f\s+origin\s+(main|master)", "禁止强制推送到主分支"),
        # Redis 清空数据库
        (r"redis-cli\s+FLUSHALL",       "禁止清空所有 Redis 数据库"),
        (r"redis-cli\s+FLUSHDB",        "禁止清空当前 Redis 数据库"),
        # 删除生产数据库
        (r"DROP\s+DATABASE",            "禁止删除数据库（需手动执行）"),
        (r"DROP\s+TABLE\s+\w+\s*;",     "禁止删除数据表（需手动执行）"),
    ]

    for pattern, reason in DANGER_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(f"[安全拦截] {reason}\n命令: {command}", file=sys.stderr)
            sys.exit(2)

    # ── 敏感文件保护（写操作）────────────────────────────────
    SENSITIVE_WRITE_PATTERNS = [
        r"\.env\.production",
        r"\.env\.prod",
        r"id_rsa$",
        r"id_ed25519$",
        r"\.pem$",
        r"\.key$",
    ]

    # 检查是否试图覆盖敏感文件
    if any(kw in command for kw in [">", "tee", "write"]):
        for pat in SENSITIVE_WRITE_PATTERNS:
            if re.search(pat, command, re.IGNORECASE):
                print(f"[安全拦截] 禁止覆盖敏感文件\n命令: {command}", file=sys.stderr)
                sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
