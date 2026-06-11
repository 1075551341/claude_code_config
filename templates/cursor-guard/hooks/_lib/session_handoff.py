#!/usr/bin/env python3
"""跨会话交接：conversation_id 边界 + handoff 制品。"""
from __future__ import annotations

import json
from typing import Any

from config import state_path


def _session_path():
    return state_path("last-session.json")


def _handoff_path():
    return state_path("session-handoff.json")


def _pending_compress_path():
    return state_path("compress-pending.json")


def extract_session_id(data: dict[str, Any]) -> str:
    for key in ("session_id", "conversation_id", "conversationId"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def load_last_session_id() -> str:
    path = _session_path()
    if not path.exists():
        return ""
    try:
        return str(json.loads(path.read_text(encoding="utf-8-sig")).get("session_id", ""))
    except (OSError, json.JSONDecodeError):
        return ""


def save_session_id(session_id: str) -> bool:
    """返回 True 表示新会话（与上次 id 不同）。"""
    if not session_id:
        return False
    prev = load_last_session_id()
    is_new = bool(prev and prev != session_id)
    _session_path().write_text(
        json.dumps({"session_id": session_id, "previous_session_id": prev}, indent=2),
        encoding="utf-8",
    )
    return is_new if prev else False


def save_handoff(payload: dict[str, Any]) -> None:
    _handoff_path().write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_handoff() -> dict[str, Any]:
    path = _handoff_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}


def format_handoff_block(handoff: dict[str, Any]) -> str | None:
    if not handoff:
        return None
    lines = ["【上轮会话交接】"]
    for key, label in (
        ("reason", "结束原因"),
        ("cursor_usage_percent", "结束时上下文%"),
        ("tool_count", "工具调用次数"),
        ("note", "说明"),
    ):
        val = handoff.get(key)
        if val not in (None, ""):
            lines.append(f"  • {label}: {val}")
    if len(lines) == 1:
        return None
    lines.append("  • 请让用户确认是否继续上轮任务，或输出新的迷你摘要。")
    return "\n".join(lines)


def _digest_path():
    return state_path("session-digest.md")


def set_compress_pending(session_id: str, prompt: str) -> None:
    _pending_compress_path().write_text(
        json.dumps(
            {"session_id": session_id, "prompt": prompt[:500], "stage": "requested"},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def load_compress_pending() -> dict[str, Any]:
    path = _pending_compress_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}


def advance_compress_stage(stage: str) -> None:
    data = load_compress_pending()
    if not data:
        return
    data["stage"] = stage
    _pending_compress_path().write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def clear_compress_pending() -> None:
    _pending_compress_path().unlink(missing_ok=True)


def pop_compress_pending(session_id: str = "") -> bool:
    data = load_compress_pending()
    if not data:
        return False
    if session_id and data.get("session_id") and data.get("session_id") != session_id:
        return False
    clear_compress_pending()
    return True


def save_session_digest(text: str, session_id: str = "") -> None:
    header = "# Cursor Guard 会话摘要\n\n"
    if session_id:
        header += f"> session: {session_id[:12]}…\n\n"
    _digest_path().write_text(header + text.strip() + "\n", encoding="utf-8")
    snap = state_path("pre-compact-state.json")
    try:
        state: dict[str, Any] = {}
        if snap.exists():
            state = json.loads(snap.read_text(encoding="utf-8-sig"))
        state["current_task_summary"] = text.strip()[:4000]
        state["event"] = "guard_digest"
        snap.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        pass


def load_digest_block(max_chars: int = 1200) -> str | None:
    path = _digest_path()
    if not path.exists():
        return None
    try:
        body = path.read_text(encoding="utf-8-sig").strip()
        if not body:
            return None
        if len(body) > max_chars:
            body = body[:max_chars] + "\n…（完整见 ~/.cursor/.state/session-digest.md）"
        return "【Guard 会话摘要制品】\n" + body
    except OSError:
        return None


def reset_tool_counter() -> None:
    state_path("tool-counter.json").write_text(
        json.dumps({"count": 0, "est_tokens": 0}, indent=2),
        encoding="utf-8",
    )
