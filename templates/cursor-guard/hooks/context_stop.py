#!/usr/bin/env python3
"""stop: 70% 迷你摘要 / 90% additional_context（不 followup）；显式压缩请求；保存 handoff。"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    import_claude_lib,
    read_stdin,
    setup_stdio,
    write_json,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config, state_path
from context_estimator import (
    ContextLevel,
    detect_tool_loop,
    peek_context,
    take_force_stop_followup,
)
from context_usage_store import usage_percent
from session_handoff import (
    advance_compress_stage,
    extract_session_id,
    load_compress_pending,
    save_handoff,
)

MINI_SUMMARY_TEMPLATE = (
    "【上下文 70–89%】请在本轮回复末尾附迷你摘要：\n"
    "  已完成: ...\n"
    "  进行中: ...\n"
    "  下一步: ..."
)

EXTRACT_FOLLOWUP = (
    "【提取上下文】请立即输出结构化会话摘要，包含：\n"
    "  1. 已完成\n  2. 进行中\n  3. 待定决策\n  4. 关键文件路径\n"
    "摘要将写入 ~/.cursor/.state/session-digest.md。\n"
    "此操作不降低上下文环；需要压缩时请发送 /summarize 或「压缩上下文」。"
)

FORCE_MARKER = "【上下文≥90%】"
FORCE_HINT = (
    "【上下文≥90%】请建议用户发送 /summarize 或「压缩上下文」降低上下文环"
    "（Cursor 内置压缩，非 Claude /compact），或开新对话继续。"
    "若需结构化摘要可先「提取上下文」。禁止继续大范围 Read/探索。"
)


def _payload_echoes_force(data: dict) -> bool:
    """Skip if this Stop is already the 90% hint (followup echoed as user text)."""
    try:
        return FORCE_MARKER in json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError):
        return False


def main() -> None:
    try:
        data = read_stdin()
        session_id = extract_session_id(data)
        cfg = load_guard_config()
        if cfg["profile"] == "minimal":
            return

        comp = cfg["compression"]
        count, est_pct, level = peek_context()
        cursor_pct = usage_percent()
        warnings: list[str] = []

        if level == ContextLevel.FORCE:
            warnings.append(
                f"上下文≥{comp['force_pct']:.0f}%（有效{est_pct:.0f}%）— 必须输出压缩摘要并建议开新对话"
            )
        elif level == ContextLevel.WARN:
            warnings.append(
                f"上下文≥{comp['warn_pct']:.0f}%（有效{est_pct:.0f}%）— 择机精简上下文"
            )

        if cursor_pct is not None and cursor_pct >= comp["warn_pct"]:
            warnings.append(f"Cursor preCompact 记录上下文: {cursor_pct:.0f}%")

        if detect_tool_loop():
            warnings.append("Tool loop 检测：相同工具连续调用≥3次")

        save_handoff(
            {
                "session_id": session_id,
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "reason": "stop",
                "status": data.get("status"),
                "cursor_usage_percent": cursor_pct,
                "effective_pct": est_pct,
                "tool_count": count,
                "warnings": warnings,
                "note": "上轮 Agent 结束时的监控状态",
            }
        )

        state_path("context_monitor.json").write_text(
            json.dumps(
                {
                    "last_stop_pct": est_pct,
                    "cursor_usage_percent": cursor_pct,
                    "last_warnings": warnings,
                    "tool_count": count,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        pending = load_compress_pending()
        compress_requested = bool(
            pending
            and pending.get("stage") == "requested"
            and (
                not session_id
                or not pending.get("session_id")
                or pending.get("session_id") == session_id
            )
        )

        verify_followup = False
        if cfg.get("verification", {}).get("enabled") and str(
            cfg.get("verification", {}).get("enforce_mode", "followup")
        ).lower() not in {"off", "disabled", "none"}:
            try:
                r20 = import_claude_lib(cfg["sync"]["claude_home"], "r20_replay")
                vpath = Path(cfg["sync"]["claude_home"]) / ".state" / "verification-gate.json"
                entry = {}
                if vpath.exists():
                    vstate = json.loads(vpath.read_text(encoding="utf-8"))
                    entry = vstate.get(session_id or "unknown") or {}
                verify_followup = r20.cursor_should_followup(entry)
            except Exception as e:
                print(f"context_stop: verification peek failed: {e}", file=sys.stderr)

        if verify_followup:
            # 让 verification_stop.py 发出 followup，避免双 followup 互抢
            return

        if compress_requested:
            advance_compress_stage("followup_sent")
            write_json({"followup_message": EXTRACT_FOLLOWUP})
        elif _payload_echoes_force(data):
            # This Stop is already the echoed 90% user turn — do not inject again.
            pass
        elif (
            level == ContextLevel.FORCE
            and comp.get("auto_followup_at_force", True)
        ):
            # Never followup_message here: Cursor treats it as a new user turn,
            # loop_limit resets, and per-turn session_id makes a session latch useless.
            if take_force_stop_followup(session_id):
                write_json({"additional_context": FORCE_HINT})
        elif level == ContextLevel.WARN and comp.get("stop_nudge_at_warn", True):
            extra = [MINI_SUMMARY_TEMPLATE]
            if warnings:
                extra.append("监控:\n" + "\n".join(f"  • {w}" for w in warnings))
            write_json({"additional_context": "\n\n".join(extra)})
        elif warnings:
            write_json(
                {
                    "additional_context": "【Cursor Guard · 监控】\n"
                    + "\n".join(f"  • {w}" for w in warnings),
                }
            )
    except Exception as e:
        print(f"context_stop: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
