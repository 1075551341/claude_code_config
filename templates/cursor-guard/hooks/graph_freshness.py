#!/usr/bin/env python3
"""preToolUse: 图谱保鲜硬门（调用 ~/.claude/hooks/_lib/graph_freshness.py）。"""
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
from hook_io import import_claude_lib


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        claude_home = cfg["sync"]["claude_home"]
        tool_name = extract_tool_name(data)
        if tool_name and not data.get("tool_name"):
            data["tool_name"] = tool_name
        try:
            gf = import_claude_lib(claude_home, "graph_freshness")
        except Exception as exc:
            print(f"graph_freshness: lib unavailable: {exc}", file=sys.stderr)
            return
        gcfg = gf.load_cfg()
        if not gcfg.get("enabled", True):
            return
        decision, payload = gf.pretool_decision(data, gcfg.get("pretool_ensure_timeout_sec"))
        if decision == "deny" and payload:
            write_json(payload)
    except Exception as exc:
        print(f"graph_freshness: {exc}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
