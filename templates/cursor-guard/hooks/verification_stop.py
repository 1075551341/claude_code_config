#!/usr/bin/env python3
"""stop: 完成验证 followup 硬门（v11.3.4）。

Cursor stop 不能 permission deny；未验证编辑或 R20 不合格时用 followup_message 续轮。
loop_limit 对齐 quality_gates.json verification_gate.max_blocks。
与 context_stop.py 并存：本 hook 要续轮时 context_stop 应跳过压缩 followup。
"""
from __future__ import annotations

import json
import os
import sys
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

from config import load_guard_config
from gate_messages import load_gate
from session_handoff import extract_session_id as handoff_session_id

DEFAULT_MAX_BLOCKS = 3
DEFAULT_SKIP = ["跳过验证", "不用验证", "skip verify"]


def _state_path(claude_home) -> Path:
    raw = str(claude_home or os.path.expanduser("~/.claude"))
    return Path(raw) / ".state" / "verification-gate.json"


def _quality_gate_cfg(claude_home) -> dict:
    path = Path(claude_home) / "config" / "quality_gates.json"
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8")).get("verification_gate", {})
    except (OSError, json.JSONDecodeError) as e:
        print(f"verification_stop: quality_gates read failed: {e}", file=sys.stderr)
    return {}


def _load_entry(path: Path, session_id: str) -> dict:
    try:
        if path.exists():
            state = json.loads(path.read_text(encoding="utf-8"))
            return state.get(session_id) or {}
    except (OSError, json.JSONDecodeError) as e:
        print(f"verification_stop: state read failed: {e}", file=sys.stderr)
    return {}


def main() -> None:
    try:
        data = read_stdin()
        if str(data.get("status") or "").lower() in {"aborted", "error"}:
            return
        cfg = load_guard_config()
        vcfg = cfg.get("verification", {})
        if not vcfg.get("enabled"):
            return
        mode = str(vcfg.get("enforce_mode", "followup")).lower()
        if mode in {"off", "disabled", "none"}:
            return

        claude_home = cfg["sync"]["claude_home"]
        qg = _quality_gate_cfg(claude_home)
        max_blocks = int(qg.get("max_blocks", DEFAULT_MAX_BLOCKS))
        skip_keywords = [k.lower() for k in qg.get("skip_keywords", DEFAULT_SKIP)]
        loop_count = int(data.get("loop_count") or 0)
        if loop_count >= max_blocks:
            print(
                f"verification_stop: loop_count={loop_count} ≥ max_blocks={max_blocks}，放行 DONE_WITH_CONCERNS",
                file=sys.stderr,
            )
            return

        prompt = str(data.get("prompt") or data.get("text") or "").lower()
        if any(k in prompt for k in skip_keywords):
            print("verification_stop: 用户跳过验证，放行", file=sys.stderr)
            return

        session_id = (
            handoff_session_id(data)
            or str(data.get("session_id") or data.get("conversation_id") or "unknown")
        )
        entry = _load_entry(_state_path(claude_home), session_id)

        r20 = None
        try:
            r20 = import_claude_lib(claude_home, "r20_replay")
            should = r20.cursor_should_followup(entry)
        except Exception as e:
            print(f"verification_stop: r20_replay unavailable: {e}", file=sys.stderr)
            should = bool(entry.get("edited_files"))

        if not should:
            return

        reasons = []
        if not entry.get("r20_replay_ok"):
            reasons.append("缺少合格 R20（漏改须含文档或无文档影响，原功能须含证据/测试/冒烟）")
        if r20 is not None and r20.has_unverified_edits(entry):
            reasons.append("最后一次编辑后无测试/lint/构建运行记录")
        elif r20 is None:
            reasons.append("验证证据不完整")

        body = load_gate("verify", claude_home)
        extra = (
            "\n\n必须补齐后才能结束本轮：\n"
            + "\n".join(f"  • {r}" for r in reasons)
            + "\n项目已建 .code-review-graph/ 时调用 detect_changes_tool。"
            + f"\n（followup {loop_count + 1}/{max_blocks}；确需跳过请用户说「跳过验证」）"
        )
        write_json({"followup_message": body + extra})
    except Exception as e:
        print(f"verification_stop: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
