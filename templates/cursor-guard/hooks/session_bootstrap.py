#!/usr/bin/env python3
"""sessionStart: Guard 状态 + 新会话检测 + handoff + 压缩快照。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import _path  # noqa: F401

from hook_io import ensure_hook_output, ensure_lib_path, read_stdin, setup_stdio, write_json

ensure_lib_path()
setup_stdio()

from config import load_guard_config, state_path
from context_usage_store import usage_percent
from impact_sync import rules_out_of_sync
from session_handoff import (
    format_handoff_block,
    load_digest_block,
    load_handoff,
    reset_tool_counter,
    save_session_id,
)
from session_handoff import extract_session_id as handoff_session_id


def load_checkpoint() -> str | None:
    for path in (
        state_path("pre-compact-state.json"),
        Path.home() / ".cursor" / ".state" / "pre-compact-state.json",
    ):
        try:
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            parts = []
            if data.get("context_usage_percent") is not None:
                parts.append(f"压缩时上下文: {data['context_usage_percent']}%")
            if data.get("current_task_summary"):
                parts.append(f"任务: {data['current_task_summary']}")
            if data.get("last_verified_checkpoint"):
                parts.append(f"检查点: {data['last_verified_checkpoint']}")
            if data.get("pending_decisions"):
                parts.append(f"待定: {data['pending_decisions']}")
            if parts:
                return "上次压缩快照:\n" + "\n".join(f"  • {p}" for p in parts)
        except (OSError, json.JSONDecodeError) as e:
            print(f"session_bootstrap: checkpoint read failed: {e}", file=sys.stderr)
    return None


def main() -> None:
    try:
        data = read_stdin()
        session_id = handoff_session_id(data)
        is_new_session = save_session_id(session_id) if session_id else False
        if is_new_session:
            reset_tool_counter()

        cfg = load_guard_config()
        comp = cfg["compression"]
        parts: list[str] = [
            "【Cursor Guard 状态】",
            f"- 自动同步: {'开' if cfg['sync']['auto_on_edit'] else '关'}",
            f"- 自动压缩阈值: {comp['warn_pct']:.0f}% / {comp['force_pct']:.0f}%",
            f"- codegraph 优先: {'开' if cfg['explore']['codegraph_first'] else '关'}",
            f"- Shell 守卫: {'开' if cfg['shell']['enabled'] else '关'}",
        ]

        if session_id:
            parts.append(f"- 会话 ID: {session_id[:8]}…")
        if is_new_session:
            parts.append("- 新会话: 是（已重置工具计数）")

        stale, stale_msg = rules_out_of_sync(cfg["sync"]["claude_home"])
        parts.append(f"- rules: {stale_msg}")

        cursor_pct = usage_percent()
        if cursor_pct is not None:
            parts.append(f"- Cursor 上下文（preCompact 记录）: {cursor_pct:.0f}%")

        if is_new_session:
            handoff = load_handoff()
            block = format_handoff_block(handoff)
            if block:
                parts.append(block)

        digest = load_digest_block()
        if digest:
            parts.append(digest)

        checkpoint = load_checkpoint()
        if checkpoint:
            parts.append(checkpoint)
        else:
            parts.append(
                "- 上次压缩快照: 无（在 Agent 输入框发送 /summarize 触发 Cursor 原生压缩；"
                "非 Claude /compact）"
            )

        write_json({"additional_context": "\n".join(parts)})
    except Exception as e:
        print(f"session_bootstrap: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
