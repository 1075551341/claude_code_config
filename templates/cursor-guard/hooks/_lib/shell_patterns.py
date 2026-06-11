#!/usr/bin/env python3
"""精简 Shell 危险模式（Cursor beforeShellExecution，独立于 Claude hooks）。"""
from __future__ import annotations

import re

DENY_PATTERNS: list[tuple[str, str]] = [
    (r"rm\s+.*-[rRfF]{1,4}\s+/$", "禁止删除根目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/\*", "禁止删除根目录所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+~\s*$", "禁止删除用户主目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+~/?\*", "禁止删除用户主目录所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+[\"']?C:\\\\?\*", "禁止删除 C 盘所有文件"),
    (r"^format\s+[A-Za-z]:", "禁止格式化磁盘"),
    (r"^mkfs\b", "禁止格式化分区"),
    (r"git\s+push\s+(?!.*--dry-run).*(?:--force|-f)\s+\S*origin\s+(main|master|release|prod)\b", "禁止强制推送到保护分支"),
    (r"git\s+push\s+(?!.*--dry-run)\S*origin\s+(main|master)\b(?!\s*--force)", "禁止直接推送到 main/master，请走 PR"),
    (r"\bDROP\s+DATABASE\b", "禁止删除数据库"),
    (r"\bDROP\s+TABLE\b", "禁止删除数据表"),
    (r"redis-cli\s+.*\bFLUSHALL\b", "禁止 FLUSHALL"),
    (r"curl\s+[^|]+\|\s*(?:sudo\s+)?(?:ba)?sh\b", "禁止 curl 管道直接执行脚本"),
    (r"wget\s+[^|]+\|\s*(?:sudo\s+)?(?:ba)?sh\b", "禁止 wget 管道直接执行脚本"),
]

WARN_PATTERNS: list[tuple[str, str]] = [
    (r"sudo\s+rm\s+.*-[rRfF]", "sudo rm -rf 请确认目标路径"),
    (r"git\s+reset\s+--hard\b", "git reset --hard 会丢弃工作区修改"),
    (r"git\s+clean\s+.*-f", "git clean 会删除未跟踪文件"),
    (r"docker\s+(?:system|volume|image)\s+prune\b", "docker prune 请确认范围"),
]

NETWORK_ASK_PATTERN = re.compile(r"\b(curl|wget|nc)\s", re.IGNORECASE)


def match_deny(command: str) -> str | None:
    for pattern, reason in DENY_PATTERNS:
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
