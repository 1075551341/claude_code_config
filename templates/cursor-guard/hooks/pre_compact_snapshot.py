#!/usr/bin/env python3
"""preCompact: Cursor 原生压缩前保存状态 + 真实上下文计量。"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import _path  # noqa: F401

from hook_io import ensure_hook_output, ensure_lib_path, read_stdin, setup_stdio, write_json

ensure_lib_path()
setup_stdio()

from config import state_path
from context_usage_store import save_from_hook_payload


def main() -> None:
    try:
        data = read_stdin()
        save_from_hook_payload({**data, "hook_event_name": "preCompact"})

        state = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cwd": os.getcwd(),
            "event": "pre_compact",
            "trigger": data.get("trigger"),
            "context_usage_percent": data.get("context_usage_percent"),
            "context_tokens": data.get("context_tokens"),
            "context_window_size": data.get("context_window_size"),
            "message_count": data.get("message_count"),
            "messages_to_compact": data.get("messages_to_compact"),
            "is_first_compaction": data.get("is_first_compaction"),
            "current_task_summary": data.get("summary")
            or data.get("current_task")
            or "见会话上下文",
            "in_progress_files": data.get("in_progress_files", []),
            "pending_decisions": data.get("pending_decisions", []),
            "last_verified_checkpoint": data.get("last_checkpoint")
            or "cursor-guard auto-save",
        }
        out = state_path("pre-compact-state.json")
        out.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

        pct = data.get("context_usage_percent")
        if pct is not None:
            write_json(
                {
                    "user_message": (
                        f"【Cursor Guard】/summarize 前快照已保存（上下文 {pct}%）。"
                        "新会话 sessionStart 将注入摘要。"
                    )
                }
            )
    except Exception as e:
        print(f"pre_compact_snapshot: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
