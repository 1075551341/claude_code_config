#!/usr/bin/env python3
"""
UserPromptSubmit Hook: 粘贴密钥扫描
source: dwarvesf/claude-guardrails
strict profile only — 见 hooks/README.md
"""
import json
import re
import sys

SECRET_PATTERNS = [
    (r"sk-ant-[A-Za-z0-9_\-]{20,}", "Anthropic API Key"),
    (r"sk-[A-Za-z0-9]{20,}", "API Key"),
    (r"gh[pousr]_[A-Za-z0-9]{36,}", "GitHub Token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"-----BEGIN\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE KEY-----", "Private Key"),
]


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        sys.exit(0)

    prompt = str(payload.get("prompt", "") or payload.get("user_prompt", ""))
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, prompt):
            print(
                f"Blocked: detected {label} in user prompt. Remove secrets before submitting.",
                file=sys.stderr,
            )
            sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
