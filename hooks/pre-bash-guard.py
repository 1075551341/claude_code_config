#!/usr/bin/env python3
"""
PreToolUse Hook: 安全拦截器
在 Bash 命令执行前拦截危险操作

exit 0 = 允许执行
exit 2 = 阻止执行（stderr 内容会发送给 Claude）

模式表 SSOT → hooks/_lib/shell_patterns.py（v12 与 Cursor Guard 共用）
"""
# source: shanraisshan/claude-code-best-practice
import json
import sys
import io
import re
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))
from shell_patterns import (  # noqa: E402
    DANGER_PATTERNS,
    ENCODING_MISUSE_PATTERNS,
    SENSITIVE_WRITE_PATTERNS,
    WARN_PATTERNS,
    WRITE_INDICATORS,
)

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception as e:
    print(f"⚠️ {e}", file=sys.stderr)


def _block(msg: str, is_trae: bool = False) -> None:
    """拦截输出：TRAE 用 hookSpecificOutput.permissionDecision=deny（stdout + exit 0），Claude Code 用 stderr + exit 2。"""
    if is_trae:
        # TRAE PreToolUse 协议：permissionDecision=deny 拒绝本次工具调用，原因附加给模型
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": msg,
                "additionalContext": msg,
            }
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.stdout.flush()
        sys.exit(0)
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()
    sys.exit(2)


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

        # 兼容 Claude Code（Bash）与 TraeCode（RunCommand）工具名
        if tool_name not in ("Bash", "RunCommand"):
            sys.exit(0)

        command = tool_input.get("command", "").strip()
        if not command:
            command = tool_input.get("shell_command", "").strip()
        if not command:
            sys.exit(0)

        # ── 危险命令检测 ──────────────────────────────────────────────────
        for pattern, reason in DANGER_PATTERNS:
            try:
                if re.search(pattern, command, re.IGNORECASE | re.MULTILINE):
                    msg = f"[安全拦截] {reason}\n命令: {command[:300]}"
                    _block(msg, is_trae=(tool_name == "RunCommand"))
            except re.error:
                continue

        # ── 敏感文件写入保护 ──────────────────────────────────────────────
        if any(ind in command for ind in WRITE_INDICATORS):
            for pat in SENSITIVE_WRITE_PATTERNS:
                try:
                    if re.search(pat, command, re.IGNORECASE):
                        msg = f"[安全拦截] 禁止覆写敏感文件\n命令: {command[:300]}"
                        _block(msg, is_trae=(tool_name == "RunCommand"))
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

        # ─── Encoding misuse (improper commands causing mojibake) ─────────
        for pattern, msg in ENCODING_MISUSE_PATTERNS:
            try:
                if re.search(pattern, command, re.IGNORECASE):
                    warns.append("[编码] " + msg)
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
    except Exception as e:
        print(f"⚠️ {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
