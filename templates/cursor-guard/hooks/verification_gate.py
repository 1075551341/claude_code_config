#!/usr/bin/env python3
"""beforeSubmitPrompt: 完成验证门已关闭（v11.4.10）。

Cursor 完成门不再注入 additional_context（与 Stop followup 同文案，会进会话）。
完成验证改由规则驱动：修改→验证→独立审查。本 hook 只排空 stdin，永不注入。
"""
from __future__ import annotations

import sys

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    read_stdin,
    setup_stdio,
)

ensure_lib_path()
setup_stdio()


def main() -> None:
    try:
        read_stdin()
        print(
            "verification_gate: Cursor 完成门注入已关闭（v11.4.10，规则驱动双审）",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"verification_gate: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
