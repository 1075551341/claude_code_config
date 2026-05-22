#!/usr/bin/env python3
"""
PreToolUse Hook: Token 预算预警
在执行昂贵操作前检查 Token 使用情况，发出预算警告

exit 0 = 允许执行
exit 2 = 阻止执行（stderr 内容会发送给 Claude）
"""
import json
import sys
import io

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# Token 预算配置（可通过环境变量覆盖）
import os
TOKEN_WARNING_THRESHOLD = int(os.environ.get("CLAUDE_TOKEN_WARNING", 50000))
TOKEN_CRITICAL_THRESHOLD = int(os.environ.get("CLAUDE_TOKEN_CRITICAL", 100000))

# 高 Token 消耗工具
HIGH_TOKEN_TOOLS = {
    "Agent": 50000,
    "Task": 30000,
    "WebFetch": 10000,
    "WebSearch": 15000,
}


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        # 获取当前 Token 使用情况（从上下文）
        # 注意：这需要 Claude Code 传递当前 token 使用信息
        current_tokens = 0
        if "context" in data:
            # 尝试从上下文估算 token
            context_str = json.dumps(data.get("context", {}))
            current_tokens = len(context_str) // 4  # 粗略估算

        # 检查是否为高消耗工具
        estimated_cost = HIGH_TOKEN_TOOLS.get(tool_name, 5000)

        # 构建警告消息
        warnings = []

        if current_tokens > TOKEN_CRITICAL_THRESHOLD:
            warnings.append(f"⚠️ Token 使用已超临界值 ({current_tokens:,} > {TOKEN_CRITICAL_THRESHOLD:,})")
            warnings.append("建议：压缩上下文或开启新会话")

        elif current_tokens > TOKEN_WARNING_THRESHOLD:
            warnings.append(f"⚠️ Token 使用接近警告阈值 ({current_tokens:,} / {TOKEN_WARNING_THRESHOLD:,})")

        # 检查是否有更经济的替代方案
        if tool_name == "Agent" and current_tokens > TOKEN_WARNING_THRESHOLD:
            alternative = "考虑直接执行而非启动子 Agent，可节省约 50% Token"
            warnings.append(alternative)

        if warnings:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": "Token 预算提醒（操作已允许执行）：\n" + "\n".join(warnings),
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