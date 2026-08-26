#!/usr/bin/env python3
"""
PreToolUse Hook: 编辑前编码快照（v11.4.2）。

encoding_guard 双阶段之一：在 Edit/Write/MultiEdit 及 MCP 写工具执行前，
把目标文件的 BOM/EOL/大小签名写入 `~/.claude/.state/encoding-snapshots.json`。
Post 侧（post-encoding-check.py）比对差异检出乱码/EOL 翻转。
永不阻断，静默快照；核心逻辑 → `_lib/encoding_guard.py`。
"""
import json
import sys
import io
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

from encoding_guard import _wrap_stdout, take_snapshot  # noqa: E402
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
        print(f"pre-encoding-snapshot: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = str(data.get("tool_name") or "")
    tool_input = data.get("tool_input") or {}
    cwd = str(data.get("cwd") or "")

    if not is_edit_tool(tool_name):
        sys.exit(0)

    try:
        take_snapshot(tool_name, tool_input, cwd)
    except Exception as e:  # noqa: BLE001 - 快照失败不阻断编辑
        print(f"pre-encoding-snapshot: snapshot failed: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
