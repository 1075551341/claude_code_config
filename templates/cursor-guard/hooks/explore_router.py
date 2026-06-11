#!/usr/bin/env python3
"""preToolUse: codegraph 优先探索路由（不阻断）。"""
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

from config import load_guard_config

MESSAGES = {
    "Grep": "结构/引用探索请优先 codegraph_explore 或 codegraph_search，Grep 仅作 fallback。",
    "Read": "大范围读文件前请先用 codegraph_explore / codegraph_context；Read 用于定点深读。",
    "Glob": "目录结构探索请优先 codegraph files/explore，Glob 仅作 fallback。",
}


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        if not cfg["explore"]["codegraph_first"] or not cfg["explore"]["nudge_on_grep_read"]:
            return

        tool_name = extract_tool_name(data)
        msg = MESSAGES.get(tool_name)
        if msg:
            write_json({"agent_message": f"【Cursor Guard · codegraph 优先】\n{msg}"})
    except Exception as e:
        print(f"explore_router: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
