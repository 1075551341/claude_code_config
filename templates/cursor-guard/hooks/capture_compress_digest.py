#!/usr/bin/env python3
"""afterAgentResponse: 「提取上下文」流程中把 Agent 摘要写入 session-digest.md。"""
from __future__ import annotations

import sys

import _path  # noqa: F401

from hook_io import ensure_hook_output, ensure_lib_path, read_stdin, setup_stdio

ensure_lib_path()
setup_stdio()

from session_handoff import (
    clear_compress_pending,
    extract_session_id,
    load_compress_pending,
    save_session_digest,
)


def main() -> None:
    try:
        data = read_stdin()
        pending = load_compress_pending()
        if not pending:
            return
        text = data.get("text") or ""
        if not isinstance(text, str) or len(text.strip()) < 40:
            return
        session_id = extract_session_id(data) or pending.get("session_id", "")
        save_session_digest(text.strip(), session_id)
        clear_compress_pending()
    except Exception as e:
        print(f"capture_compress_digest: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
