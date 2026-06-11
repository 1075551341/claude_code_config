#!/usr/bin/env python3
"""提交前密钥/令牌轻量检测。"""
from __future__ import annotations

import re

SECRET_PATTERNS: list[tuple[str, str]] = [
    (r"\bsk-[a-zA-Z0-9]{20,}\b", "疑似 API key (sk-)"),
    (r"\bAKIA[0-9A-Z]{16}\b", "疑似 AWS Access Key"),
    (r"-----BEGIN (?:RSA )?PRIVATE KEY-----", "疑似私钥"),
    (r"\bghp_[a-zA-Z0-9]{36,}\b", "疑似 GitHub token"),
    (r"\bxox[baprs]-[a-zA-Z0-9-]{10,}\b", "疑似 Slack token"),
    (r"\bAIza[0-9A-Za-z_-]{35}\b", "疑似 Google API key"),
]


def find_secrets(text: str) -> list[str]:
    if not text:
        return []
    found: list[str] = []
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, text):
            found.append(label)
    return found
