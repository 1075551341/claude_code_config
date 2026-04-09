#!/usr/bin/env python3
"""
PreToolUse Hook: 安全拦截器
在 Bash 命令执行前拦截危险操作

exit 0 = 允许执行
exit 2 = 阻止执行（stderr 内容会发送给 Claude）

修复记录：
- FIX: 整体 BaseException 捕获，防止 sys.exit() 被误拦截
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: sys.stdout.flush() 确保输出刷新
- FIX: 补充更多危险命令模式（curl/eval、生产环境 db 操作等）
- FIX: 改进敏感文件写入检测范围
"""
import json
import sys
import io
import re
import os

# ── stdout 安全包装 ───────────────────────────────────────────────────────────
try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# ── 危险命令模式（阻止，exit 2）──────────────────────────────────────────────
DANGER_PATTERNS = [
    # 递归删除系统/用户目录
    (r"rm\s+.*-[rRfF]{1,4}\s+/$",                  "禁止删除根目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/\*",                 "禁止删除根目录所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+~\s*$",               "禁止删除用户主目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+~/?\*",               "禁止删除用户主目录所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+[\"']?C:\\\\?\*",     "禁止删除 C 盘所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/etc\b",              "禁止删除 /etc 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/usr\b",              "禁止删除 /usr 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/boot\b",             "禁止删除 /boot 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/var\b",              "禁止删除 /var 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/home\b",             "禁止删除 /home 目录"),
    # 磁盘格式化
    (r"^format\s+[A-Za-z]:",                         "禁止格式化磁盘"),
    (r"^mkfs\b",                                      "禁止格式化分区"),
    (r"dd\s+if=.+of=/dev/[sh]d[a-z]",              "禁止 dd 写入块设备"),
    (r"dd\s+if=/dev/zero\s+of=",                    "禁止 dd 零写覆盖"),
    (r"shred\s+.*-[zun].*\s+/dev/",                "禁止 shred 覆盖设备"),
    # Git 强制推送保护
    (r"git\s+push\s+(?!.*--dry-run).*--force(?:-with-lease)?\s*$",  "禁止无目标强制推送"),
    (r"git\s+push\s+(?!.*--dry-run).*-f\s+\S*origin\s+(main|master|release|prod)\b",
     "禁止强制推送到保护分支"),
    (r"git\s+push\s+(?!.*--dry-run).*--force\s+\S*origin\s+(main|master|release|prod)\b",
     "禁止强制推送到保护分支"),
    # Git 历史重写
    (r"git\s+filter-branch\b",                      "禁止 filter-branch 重写历史（建议用 git filter-repo）"),
    (r"git\s+rebase\s+.*--root\b",                  "禁止 rebase --root 重写全部历史"),
    # Redis 危险操作
    (r"redis-cli\s+.*\bFLUSHALL\b",                "禁止清空所有 Redis 数据库"),
    (r"redis-cli\s+.*\bFLUSHDB\b",                 "禁止清空当前 Redis 数据库"),
    (r"redis-cli\s+.*CONFIG\s+SET\s+requirepass\s+[\"']{2}",
     "禁止清空 Redis 密码"),
    # 数据库危险 DDL
    (r"\bDROP\s+DATABASE\b",                        "禁止删除数据库（请手动执行）"),
    (r"\bDROP\s+TABLE\b",                           "禁止删除数据表（请手动执行）"),
    (r"\bTRUNCATE\s+TABLE\b",                       "禁止清空数据表（请手动执行）"),
    # 系统级危险命令
    (r":\(\)\{:\|:&\};:",                           "Fork Bomb 攻击，已拦截"),
    (r"chmod\s+-R\s+777\s+/",                       "禁止递归 chmod 777 根目录"),
    (r"chown\s+-R\s+\S+\s+/(?!home/\S+/\S+)",     "禁止递归修改系统目录所有权"),
    # 脚本直接管道执行
    (r"curl\s+[^|]+\|\s*(?:sudo\s+)?(?:ba)?sh\b",  "禁止 curl 管道直接执行脚本"),
    (r"wget\s+[^|]+\|\s*(?:sudo\s+)?(?:ba)?sh\b",  "禁止 wget 管道直接执行脚本"),
    (r"curl\s+[^|]+\|\s*python[23]?\b",            "禁止 curl 管道直接执行 Python 脚本"),
    # eval 执行下载内容
    (r"eval\s+[\"'`]\$\(curl",                      "禁止 eval 执行 curl 下载内容"),
    (r"eval\s+[\"'`]\$\(wget",                      "禁止 eval 执行 wget 下载内容"),
]

# ── 警告模式（不阻断，注入上下文提示）──────────────────────────────────────────
WARN_PATTERNS = [
    (r"sudo\s+rm\s+.*-[rRfF]",                     "sudo rm -rf 需谨慎，请确认目标路径"),
    (r"git\s+reset\s+--hard\b",                     "git reset --hard 会丢弃工作区修改，请确认"),
    (r"git\s+clean\s+.*-f",                         "git clean -f 会永久删除未跟踪文件"),
    (r"npm\s+run\s+(?:clean|purge|reset|nuke)\b",   "清理脚本可能删除构建产物，请确认"),
    (r"pkill\s+-9\b",                               "SIGKILL 强制终止进程，请确认目标"),
    (r"\bdropdb\b",                                  "dropdb 将永久删除整个数据库，请确认"),
    (r"mongo.*--eval.*db\.dropDatabase",            "dropDatabase 将清除整个数据库"),
    (r"git\s+stash\s+(?:drop|clear)\b",            "stash drop/clear 将永久删除暂存内容"),
    (r"docker\s+(?:system|volume|image)\s+prune\b", "docker prune 将删除未使用的资源，请确认"),
]

# ── 敏感文件写入保护 ──────────────────────────────────────────────────────────
SENSITIVE_WRITE_PATTERNS = [
    r"\.env\.(?:production|prod|staging|live)\b",
    r"(?:^|[\s/])id_rsa(?:$|[\s.])",
    r"(?:^|[\s/])id_ed25519(?:$|[\s.])",
    r"(?:^|[\s/])id_ecdsa(?:$|[\s.])",
    r"\.pem(?:$|[\s])",
    r"\.key(?:$|[\s])",
    r"\.pfx(?:$|[\s])",
    r"\.p12(?:$|[\s])",
    r"authorized_keys",
    r"(?:^|/)etc/(?:passwd|shadow|sudoers)\b",
]

WRITE_INDICATORS = [">", ">>", "tee ", " write ", "truncate "]


def main():
    try:
        # ── 读取 stdin ────────────────────────────────────────────────────
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name  = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        if tool_name != "Bash":
            sys.exit(0)

        command = tool_input.get("command", "").strip()
        if not command:
            sys.exit(0)

        # ── 危险命令检测 ──────────────────────────────────────────────────
        for pattern, reason in DANGER_PATTERNS:
            try:
                if re.search(pattern, command, re.IGNORECASE | re.MULTILINE):
                    msg = f"[安全拦截] {reason}\n命令: {command[:300]}"
                    sys.stderr.write(msg + "\n")
                    sys.stderr.flush()
                    sys.exit(2)
            except re.error:
                continue

        # ── 敏感文件写入保护 ──────────────────────────────────────────────
        if any(ind in command for ind in WRITE_INDICATORS):
            for pat in SENSITIVE_WRITE_PATTERNS:
                try:
                    if re.search(pat, command, re.IGNORECASE):
                        msg = f"[安全拦截] 禁止覆写敏感文件\n命令: {command[:300]}"
                        sys.stderr.write(msg + "\n")
                        sys.stderr.flush()
                        sys.exit(2)
                except re.error:
                    continue

        # ── 警告（不阻断，注入上下文）────────────────────────────────────
        warns = []
        for pattern, msg in WARN_PATTERNS:
            try:
                if re.search(pattern, command, re.IGNORECASE):
                    warns.append(f"⚠️  {msg}")
            except re.error:
                continue

        if warns:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": "安全警告（命令已允许执行，请确认意图）：\n" + "\n".join(warns),
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
