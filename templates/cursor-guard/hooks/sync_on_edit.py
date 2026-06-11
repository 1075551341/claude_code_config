#!/usr/bin/env python3
"""afterFileEdit / postToolUse: 影响驱动同步 ~/.claude → Cursor。"""
from __future__ import annotations

import sys

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    extract_file_path,
    read_stdin,
    setup_stdio,
    write_json,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config
from impact_sync import SyncScope, resolve_sync_plan
from sync_runner import run_sync_plan


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        file_path = extract_file_path(data)
        if not file_path:
            return

        plan = resolve_sync_plan(file_path, cfg["sync"]["claude_home"])

        if not cfg["sync"]["auto_on_edit"] and plan.scope == SyncScope.NONE:
            if plan.messages:
                write_json(
                    {
                        "additional_context": "【Cursor Guard · 配置同步】\n"
                        + "\n".join(f"  • {m}" for m in plan.messages)
                    }
                )
            return

        if not cfg["sync"]["auto_on_edit"]:
            return

        ok, msg = run_sync_plan(plan)
        lines = list(plan.messages)
        if msg:
            lines.append(msg)

        if lines:
            prefix = "【Cursor Guard · 配置同步】"
            body = prefix + "\n" + "\n".join(f"  • {line}" for line in lines)
            if ok or plan.scope != SyncScope.NONE:
                write_json({"additional_context": body})
            elif "跳过" not in msg:
                print(body, file=sys.stderr)
    except Exception as e:
        print(f"sync_on_edit: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
