#!/usr/bin/env python3
"""
PostToolUse Hook: 编辑后编码校验（v11.4.2）。

encoding_guard 双阶段之二：对本次写操作的目标文件做绝对检查
（非法 UTF-8 / U+FFFD / GBK 特征串 / 游离 BOM / json+py 带 BOM / 严重 mixed EOL）
并与 Pre 侧快照比对（BOM 增删、EOL 风格翻转）。
检出问题经 additionalContext 警告注入（exit 0，永不阻断），
提示 AI 立即回滚而非在损坏内容上继续叠加。核心逻辑 → `_lib/encoding_guard.py`。
"""
import json
import sys
import io
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

from encoding_guard import (  # noqa: E402
    _wrap_stdout,
    check_after_edit,
    emit_warning,
    format_warning,
)
from tool_paths import is_edit_tool  # noqa: E402


def main():
    _wrap_stdout()
    try:
        raw = (
            sys.stdin.buffer.read().decode("utf-8", errors="replace")
            if hasattr(sys.stdin, "buffer")
            else sys.stdin.read()
        )
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        print(f"post-encoding-check: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = str(data.get("tool_name") or "")
    tool_input = data.get("tool_input") or {}
    cwd = str(data.get("cwd") or "")

    if not is_edit_tool(tool_name):
        sys.exit(0)

    try:
        results = check_after_edit(tool_name, tool_input, cwd)
        if results:
            emit_warning(format_warning(results), "PostToolUse")
    except Exception as e:  # noqa: BLE001 - 校验失败不阻断主流程
        print(f"post-encoding-check: check failed: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
