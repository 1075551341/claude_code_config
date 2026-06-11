#!/usr/bin/env python3
"""preToolUse: 70%/90% 上下文预警（agent_message）。"""
from __future__ import annotations

import sys

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    extract_tool_name,
    read_stdin,
    setup_stdio,
    write_json,
)

ensure_lib_path()
setup_stdio()

from context_estimator import ContextLevel, detect_tool_loop, peek_context


def main() -> None:
    try:
        data = read_stdin()
        tool_name = extract_tool_name(data)
        if not tool_name:
            return

        count, est_pct, level = peek_context()
        messages: list[str] = []

        if level == ContextLevel.FORCE:
            messages.append(
                f"上下文≥90%（预估{est_pct:.0f}%，{count}次工具）— "
                "禁止大范围 Read/探索；输出压缩摘要并建议用户开新对话。"
            )
        elif level == ContextLevel.WARN:
            messages.append(
                f"上下文≥70%（预估{est_pct:.0f}%）— 择机精简回复，完成当前步骤后输出状态摘要。"
            )

        if detect_tool_loop():
            messages.append(
                f"Tool loop: 相同工具连续调用≥3次 — 换策略或委派子 Agent（当前: {tool_name}）"
            )

        if messages:
            write_json({"agent_message": "Cursor Guard:\n" + "\n".join(messages)})
    except Exception as e:
        print(f"context_pre_tool: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
