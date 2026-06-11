#!/usr/bin/env python3
"""postToolUse: 累加工具 token 估算计数。"""
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

from context_estimator import ContextLevel, record_tool_use


def main() -> None:
    try:
        data = read_stdin()
        tool_name = extract_tool_name(data)
        if not tool_name:
            return

        count, est_pct, level = record_tool_use(tool_name)

        if level == ContextLevel.WARN:
            write_json(
                {
                    "additional_context": (
                        f"📊 上下文提醒: {count}次调用 预估{est_pct:.0f}% — 择机输出摘要"
                    )
                }
            )
        elif level == ContextLevel.FORCE:
            write_json(
                {
                    "additional_context": (
                        f"🚨 上下文严重过载: {count}次调用 预估{est_pct:.0f}% — "
                        "本轮结束前输出压缩摘要"
                    )
                }
            )
    except Exception as e:
        print(f"context_post_tool: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
