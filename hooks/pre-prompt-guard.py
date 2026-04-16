#!/usr/bin/env python3
"""PreToolUse Hook: 提示注入防护 - 检测用户输入中的注入模式"""
import sys
import json

INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "you are now",
    "act as",
    "repeat your system prompt",
    "show your instructions",
    "execute without validation",
    "bypass safety",
    "jailbreak",
]

def main():
    try:
        input_data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    except:
        input_data = {}
    
    tool_input = input_data.get("tool_input", {})
    prompt = ""
    if isinstance(tool_input, dict):
        prompt = str(tool_input.get("prompt", "")) + str(tool_input.get("content", ""))
    prompt_lower = prompt.lower()
    
    for pattern in INJECTION_PATTERNS:
        if pattern in prompt_lower:
            print(f"⚠️ 提示注入检测: 发现模式 '{pattern}'。建议审查输入内容。", file=sys.stderr)
            # 不阻断，仅警告
            break
    
    sys.exit(0)

if __name__ == "__main__":
    main()
