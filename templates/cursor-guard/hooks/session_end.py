#!/usr/bin/env python3
"""sessionEnd: 会话结束 — 刷新双图 + 写入 handoff 供下一会话加载。"""
from __future__ import annotations

import sys
from datetime import datetime, timezone

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    import_claude_lib,
    read_stdin,
    setup_stdio,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config
from context_estimator import peek_context
from context_usage_store import usage_percent
from session_handoff import extract_session_id, save_handoff


def main() -> None:
    note = "会话已结束；新会话 sessionStart 将注入本交接块（若 Cursor 注入 additional_context 生效）"
    try:
        data = read_stdin()
        session_id = extract_session_id(data)
        count, est_pct, _ = peek_context()
        try:
            cfg = load_guard_config()
            gf = import_claude_lib(cfg["sync"]["claude_home"], "graph_freshness")
            cwd = gf.resolve_cwd(data)
            if cwd:
                gcfg = gf.load_cfg()
                _has, warns, result = gf.refresh_incremental(
                    [cwd],
                    int(gcfg.get("stop_refresh_timeout_sec", 30)),
                    session_id=session_id or "",
                )
                for w in warns:
                    print(f"session_end: {w}", file=sys.stderr)
                ui = str((result or {}).get("ui") or "").strip()
                if ui:
                    note = f"{note} | {ui}"
                if result.get("blocked") or not result.get("ok"):
                    note = f"{note} | 图谱 refresh 失败"
        except Exception as e:
            print(f"session_end: graph refresh failed: {e}", file=sys.stderr)
            note = f"{note} | 图谱 refresh 异常"
        save_handoff(
            {
                "session_id": session_id,
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "reason": data.get("reason", "unknown"),
                "duration_ms": data.get("duration_ms"),
                "cursor_usage_percent": usage_percent(),
                "tool_est_pct": est_pct,
                "tool_count": count,
                "note": note,
            }
        )
    except Exception as e:
        print(f"session_end: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
