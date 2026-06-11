#!/usr/bin/env python3
"""postToolUse: 文档/INDEX 维护显式提示。"""
from __future__ import annotations

import sys
from pathlib import Path

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
from maintenance_check import hint_for_path


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        file_path = extract_file_path(data)
        if not file_path:
            return

        claude_home = cfg["sync"]["claude_home"]
        try:
            rel = Path(file_path).resolve().relative_to(claude_home.resolve()).as_posix()
        except (ValueError, OSError):
            return

        hints = hint_for_path(rel)
        if hints:
            body = "【Cursor Guard · 文档/配置维护】\n" + "\n".join(
                f"  • {h}" for h in hints
            )
            write_json({"additional_context": body})
    except Exception as e:
        print(f"maintenance_hints: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
