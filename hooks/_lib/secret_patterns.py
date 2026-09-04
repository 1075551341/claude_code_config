#!/usr/bin/env python3
"""密钥扫描模式 SSOT（Claude post-secret-detector + Cursor prompt_secret_scan 共用）。"""
from __future__ import annotations

import re

SECRET_PATTERNS: list[tuple[str, str, str]] = [
    (r"sk-ant-[A-Za-z0-9_\-]{20,}", "Anthropic API Key", "critical"),
    (r"sk-[A-Za-z0-9]{48}", "OpenAI API Key", "critical"),
    (r"sk-proj-[A-Za-z0-9_\-]{40,}", "OpenAI Project API Key", "critical"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID", "critical"),
    (r"(?i)aws[_\-]?secret[_\-]?(?:access[_\-]?)?key\s*[=:]\s*[\"']([A-Za-z0-9/+=]{40})[\"']",
     "AWS Secret Key", "critical"),
    (r"gh[pousr]_[A-Za-z0-9]{36,}", "GitHub Token", "critical"),
    (r"github_pat_[A-Za-z0-9_]{82}", "GitHub Fine-grained PAT", "critical"),
    (r"sk_live_[A-Za-z0-9]{24,}", "Stripe Live Secret Key", "critical"),
    (r"rk_live_[A-Za-z0-9]{24,}", "Stripe Restricted Key", "critical"),
    (r"AIza[0-9A-Za-z\-_]{35}", "Google/Firebase API Key", "high"),
    (r"(?i)supabase[^=\n]{0,30}[=:]\s*[\"'](eyJ[A-Za-z0-9_\-]{50,})",
     "Supabase Service Role Key", "critical"),
    (r"vercel_[A-Za-z0-9_]{24,}", "Vercel Token", "high"),
    (r"sk_(?:live|test)_[A-Za-z0-9_]{32,}", "Clerk Secret Key", "critical"),
    (r"re_[A-Za-z0-9_]{32,}", "Resend API Key", "high"),
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}", "Slack Token", "high"),
    (r"SK[a-f0-9]{32}", "Twilio API Key SID", "high"),
    (r"SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}", "SendGrid API Key", "critical"),
    (r"(?i)(?:api[_\-]?key|apikey)\s*[=:]\s*[\"']([A-Za-z0-9_\-]{20,})[\"']",
     "API Key 硬编码", "high"),
    (r"(?i)(?:access[_\-]?token|auth[_\-]?token|bearer[_\-]?token)\s*[=:]\s*[\"']([A-Za-z0-9_\-\.]{20,})[\"']",
     "Token 硬编码", "high"),
    (r"(?i)(?:secret[_\-]?key|client[_\-]?secret)\s*[=:]\s*[\"']([A-Za-z0-9_\-\.+/=]{16,})[\"']",
     "Secret Key 硬编码", "high"),
    (r"(?i)(?:password|passwd|pwd)\s*[=:]\s*[\"']([^\"\\']{8,})[\"']",
     "密码硬编码", "medium"),
    (r"(?i)jwt[_\-]?secret\s*[=:]\s*[\"']([^\"\\']{10,})[\"']",
     "JWT Secret 硬编码", "high"),
    (r"-----BEGIN\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE KEY-----",
     "私钥内容", "critical"),
    (r"(?i)(?:mysql|postgresql|postgres|mongodb|redis|mssql|oracle)://[^:@\s]+:([^@\s\"\']{8,})@",
     "数据库连接串含密码", "high"),
    (r"(?i)(?:wx|wechat|wxpay)[_\-]?(?:secret|key|appsecret)\s*[=:]\s*[\"']([A-Za-z0-9]{16,})[\"']",
     "微信密钥硬编码", "high"),
]

SAFE_CONTEXTS = [
    r"\.test\.", r"\.spec\.", r"__test__", r"_test\.py",
    r"\bexample\b", r"\bsample\b", r"\bmock\b", r"\bfixture\b",
    r"\bfake\b", r"\bdummy\b", r"placeholder",
    r"your[_\-]?", r"xxx+", r"yyy+", r"zzz+",
    r"\$\{", r"process\.env\.", r"os\.environ", r"os\.getenv",
    r"import\.meta\.env", r"env\[",
    r"<YOUR_", r"<your_", r"YOUR_API", r"your-api",
    r"\*{4,}", r"<REPLACE>", r"CHANGEME", r"TODO:",
]

SAFE_FILE_PATTERNS = [
    r"\.example$", r"\.sample$", r"\.template$",
    r"example\.", r"sample\.", r"mock\.",
    r"\.test\.", r"\.spec\.", r"_test\.",
    r"\.md$",
]


def is_safe_context(line: str, surrounding: str) -> bool:
    combined = (line + " " + surrounding).lower()
    return any(re.search(p, combined, re.IGNORECASE) for p in SAFE_CONTEXTS)


def find_secrets(text: str) -> list[str]:
    if not text:
        return []
    found: list[str] = []
    for pattern, label, _sev in SECRET_PATTERNS:
        if re.search(pattern, text):
            found.append(label)
    return found
