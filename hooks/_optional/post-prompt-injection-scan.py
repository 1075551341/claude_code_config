#!/usr/bin/env python3
"""
PostToolUse Hook: 工具输出注入模式扫描（warn only）
source: lasso-security/claude-hooks
strict profile only — 见 hooks/README.md
"""
import json
import sys

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard your instructions",
    "you are now",
    "system prompt override",
    "jailbreak",
    "<!-- inject",
    "hidden instruction",
]


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        sys.exit(0)

    tool_output = str(payload.get("tool_output", "") or payload.get("result", ""))
    tool_name = str(payload.get("tool_name", ""))
    if tool_name not in {"Read", "WebFetch", "Bash", "Grep"}:
        sys.exit(0)

    lower = tool_output.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lower:
            print(
                f"⚠️ Injection pattern '{pattern}' in {tool_name} output. Treat as untrusted.",
                file=sys.stderr,
            )
            break
    sys.exit(0)


if __name__ == "__main__":
    main()
