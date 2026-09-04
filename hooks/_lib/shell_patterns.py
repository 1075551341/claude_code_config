#!/usr/bin/env python3
"""Shell 危险/警告模式 SSOT（Claude bash-guard + Cursor shell_guard 共用）。"""
from __future__ import annotations

import re

GIT_OPTS = r"(?:(?:-C|-c|--git-dir|--work-tree)(?:\s+|=)\S+(?:\s+|))*"

DANGER_PATTERNS: list[tuple[str, str]] = [
    (r"rm\s+.*-[rRfF]{1,4}\s+/$", "禁止删除根目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/\*", "禁止删除根目录所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+~\s*$", "禁止删除用户主目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+~/?\*", "禁止删除用户主目录所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+[\"']?C:\\\\?\*", "禁止删除 C 盘所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/etc\b", "禁止删除 /etc 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/usr\b", "禁止删除 /usr 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/boot\b", "禁止删除 /boot 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/var\b", "禁止删除 /var 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/home\b", "禁止删除 /home 目录"),
    (r"^format\s+[A-Za-z]:", "禁止格式化磁盘"),
    (r"^mkfs\b", "禁止格式化分区"),
    (r"dd\s+if=.+of=/dev/[sh]d[a-z]", "禁止 dd 写入块设备"),
    (r"dd\s+if=/dev/zero\s+of=", "禁止 dd 零写覆盖"),
    (r"shred\s+.*-[zun].*\s+/dev/", "禁止 shred 覆盖设备"),
    (r"\bgit\s+" + GIT_OPTS + r"commit\b", "禁止 Agent 自动 git commit（R19）；仅用户本条消息显式要求时由用户手动执行"),
    (r"\bgit\s+" + GIT_OPTS + r"push\b(?!.*--dry-run)", "禁止 Agent 自动 git push（R19）— 自动提交远端的主因；需推送请用户手动执行"),
    (r"\bgit\s+" + GIT_OPTS + r"stash\b", "禁止 Agent 执行 git stash（请本地手动处理）"),
    (r"\bgit\s+" + GIT_OPTS + r"checkout\s+(?:-b|-B|--orphan)\b",
     "禁止 Agent 自动新建分支（R19）；仅用户本条消息显式要求时由用户手动执行"),
    (r"\bgit\s+" + GIT_OPTS + r"switch\s+(?:-c|--create)\b",
     "禁止 Agent 自动新建分支（R19）；仅用户本条消息显式要求时由用户手动执行"),
    (r"\bgit\s+" + GIT_OPTS + r"switch\b",
     "禁止 Agent 自动 git switch 改分支（R19）；仅用户本条消息显式要求时由用户手动执行"),
    (r"\bgit\s+" + GIT_OPTS + r"branch\s+[^-]",
     "禁止 Agent 自动 git branch 新建分支（R19）；仅用户本条消息显式要求时由用户手动执行"),
    (r"\bgit\s+" + GIT_OPTS + r"checkout\s+(?![^;\n]*--\s)(?!-p\b|--patch\b)",
     "禁止 Agent 自动切换分支（R19）；恢复文件请用 checkout -- <path>；切分支须用户本条消息显式要求"),
    (r"\bgit\s+" + GIT_OPTS + r"worktree\s+add\b[^;\n]*(?:-b|--branch)\b",
     "禁止 Agent 用 worktree add -b 自动新建分支（R19）；仅用户本条消息显式要求时由用户手动执行"),
    (r"\bgit\s+" + GIT_OPTS + r"branch\s+(?:-[cCmMf]|--copy|--move|--force)\b",
     "禁止 Agent 自动复制/重命名/强制创建分支（R19）"),
    (r"(?:^|[;&|(]\s*)powershell(?:\.exe)?\b(?![^;\n]*mcp)",
     "禁止 Agent 使用 powershell.exe（PS5.1）（R15）；用 pwsh 7.5+。Qoder MCP 启动脚本例外"),
    (r"(?:^|[;&|(]\s*)cmd(?:\.exe)?\b",
     "禁止 Agent 使用 cmd.exe 作主壳（R15）；改用 pwsh 7.5+"),
    (r"\bgit\s+" + GIT_OPTS + r"push\s+(?!.*--dry-run).*--force(?:-with-lease)?\b", "禁止 git push 强制推送"),
    (r"git\s+filter-branch\b", "禁止 filter-branch 重写历史（建议用 git filter-repo）"),
    (r"git\s+rebase\s+.*--root\b", "禁止 rebase --root 重写全部历史"),
    (r"redis-cli\s+.*\bFLUSHALL\b", "禁止清空所有 Redis 数据库"),
    (r"redis-cli\s+.*\bFLUSHDB\b", "禁止清空当前 Redis 数据库"),
    (r"redis-cli\s+.*CONFIG\s+SET\s+requirepass\s+[\"']{2}", "禁止清空 Redis 密码"),
    (r"\bDROP\s+DATABASE\b", "禁止删除数据库（请手动执行）"),
    (r"\bDROP\s+TABLE\b", "禁止删除数据表（请手动执行）"),
    (r"\bTRUNCATE\s+TABLE\b", "禁止清空数据表（请手动执行）"),
    (r":\(\)\{:\|:&\};:", "Fork Bomb 攻击，已拦截"),
    (r"chmod\s+-R\s+777\s+/", "禁止递归 chmod 777 根目录"),
    (r"chown\s+-R\s+\S+\s+/(?!home/\S+/\S+)", "禁止递归修改系统目录所有权"),
    (r"curl\s+[^|]+\|\s*(?:sudo\s+)?(?:ba)?sh\b", "禁止 curl 管道直接执行脚本"),
    (r"wget\s+[^|]+\|\s*(?:sudo\s+)?(?:ba)?sh\b", "禁止 wget 管道直接执行脚本"),
    (r"curl\s+[^|]+\|\s*python[23]?\b", "禁止 curl 管道直接执行 Python 脚本"),
    (r"eval\s+[\"'`]\$\(curl", "禁止 eval 执行 curl 下载内容"),
    (r"eval\s+[\"'`]\$\(wget", "禁止 eval 执行 wget 下载内容"),
]

DENY_PATTERNS = DANGER_PATTERNS

WARN_PATTERNS: list[tuple[str, str]] = [
    (r"sudo\s+rm\s+.*-[rRfF]", "sudo rm -rf 需谨慎，请确认目标路径"),
    (r"git\s+reset\s+--hard\b", "git reset --hard 会丢弃工作区修改，请确认"),
    (r"git\s+clean\s+.*-f", "git clean -f 会永久删除未跟踪文件"),
    (r"npm\s+run\s+(?:clean|purge|reset|nuke)\b", "清理脚本可能删除构建产物，请确认"),
    (r"pkill\s+-9\b", "SIGKILL 强制终止进程，请确认目标"),
    (r"\bdropdb\b", "dropdb 将永久删除整个数据库，请确认"),
    (r"mongo.*--eval.*db\.dropDatabase", "dropDatabase 将清除整个数据库"),
    (r"git\s+stash\s+(?:drop|clear)\b", "stash drop/clear 将永久删除暂存内容"),
    (r"docker\s+(?:system|volume|image)\s+prune\b", "docker prune 将删除未使用的资源，请确认"),
]

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

ENCODING_MISUSE_PATTERNS = [
    (r"\b(?:Set-Content|Add-Content|Out-File)\b",
     "shell 写文件易致编码乱码（PS5.1 默认 ANSI）— 改用 Edit/Write 工具写入内容"),
    (r"\becho\b[^|;&]*>{1,2}\s*\S",
     "echo 重定向写文件易致编码/EOL 异常 — 改用 Edit/Write 工具写入内容"),
    (r"\btee\s+(?:-{1,2}\w+\s+)*(?!-)\S+",
     "tee 写文件易致编码异常 — 改用 Edit/Write 工具写入内容"),
    (r"<<\s*['\"]?\w+['\"]?\s*>?>",
     "heredoc 重定向写文件易致转义/编码异常 — 改用 Edit/Write 工具写入内容"),
    (r"\bsed\s[^|;&]*\s-i(?:\.|\b)",
     "sed -i 可能破坏 CRLF/BOM — 文件内容修改改用 Edit 工具"),
]

_GIT_STASH_RE = re.compile(r"\bgit\s+" + GIT_OPTS + r"stash\b", re.IGNORECASE)
_GIT_COMMIT_RE = re.compile(r"\bgit\s+" + GIT_OPTS + r"commit\b", re.IGNORECASE)
NETWORK_ASK_PATTERN = re.compile(r"\b(curl|wget|nc)\s", re.IGNORECASE)


def match_git_stash(command: str) -> bool:
    return bool(_GIT_STASH_RE.search(command))


def match_git_commit(command: str) -> bool:
    return bool(_GIT_COMMIT_RE.search(command))


def match_deny(command: str) -> str | None:
    for pattern, reason in DANGER_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE | re.MULTILINE):
            return reason
    return None


def match_warn(command: str) -> str | None:
    for pattern, reason in WARN_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE | re.MULTILINE):
            return reason
    return None


def is_network_command(command: str) -> bool:
    return bool(NETWORK_ASK_PATTERN.search(command))
