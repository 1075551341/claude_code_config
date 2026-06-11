#!/usr/bin/env python3
"""sessionEnd: 会话结束 — 写入 handoff 供下一会话 sessionStart 加载。"""
from __future__ import annotations

import sys
from datetime import datetime, timezone

import _path  # noqa: F401

from hook_io import ensure_hook_output, ensure_lib_path, read_stdin, setup_stdio

ensure_lib_path()
setup_stdio()

from context_estimator import peek_context
from context_usage_store import usage_percent
from session_handoff import extract_session_id, save_handoff


def main() -> None:
    try:
        data = read_stdin()
        session_id = extract_session_id(data)
        count, est_pct, _ = peek_context()
        save_handoff(
            {
                "session_id": session_id,
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "reason": data.get("reason", "unknown"),
                "duration_ms": data.get("duration_ms"),
                "cursor_usage_percent": usage_percent(),
                "tool_est_pct": est_pct,
                "tool_count": count,
                "note": "会话已结束；新会话 sessionStart 将注入本交接块（若 Cursor 注入 additional_context 生效）",
            }
        )
    except Exception as e:
        print(f"session_end: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
