#!/usr/bin/env python3
"""R20 会话终验机械检测（v11.3.4）— 空模板不得过门。

Claude Stop 与 Cursor stop followup 共用，禁止再复制一份正则。
"""
from __future__ import annotations

import re

_REQUIRED = ("遗漏", "错改", "漏改", "原功能")
_EMPTY_SATISFIED = {"", ".", "..", "...", "…", "无", "n/a", "na", "none"}
_PATH_RE = re.compile(
    r"(?:[A-Za-z]:)?[\\/][\w.\\/-]+|\S+\.(?:md|mdc|py|ts|tsx|js|json|ya?ml|toml|txt)\b"
)
_FIELD_RE = re.compile(
    r"(?:^|\n)\s*-?\s*(满足|遗漏|错改|漏改|原功能)\s*[：:]\s*(.*?)(?="
    r"(?:\n\s*-?\s*(?:满足|遗漏|错改|漏改|原功能)\s*[：:])|\n结论|$)",
    re.S,
)


def field_value(text: str, name: str) -> str:
    """取出终验字段正文；找不到返回空串。"""
    for match in _FIELD_RE.finditer(text):
        if match.group(1) == name:
            return match.group(2).strip()
    return ""


def replay_ok(text: str) -> bool:
    """最后一条助手回复是否构成合格 R20（反空模板）。"""
    if not text or not text.strip():
        return False
    if ("会话终验" not in text) and ("R20" not in text):
        return False
    if any(token not in text for token in _REQUIRED):
        return False

    satisfied = field_value(text, "满足")
    if satisfied.strip().lower() in _EMPTY_SATISFIED:
        return False

    missed = field_value(text, "漏改")
    if not missed:
        return False
    if not (
        "文档" in missed
        or "无文档影响" in missed
        or _PATH_RE.search(missed)
    ):
        return False

    original = field_value(text, "原功能")
    if not original:
        return False
    if not any(token in original for token in ("证据", "测试", "冒烟")):
        return False
    return True


def has_unverified_edits(entry: dict) -> bool:
    """本会话有编辑且最后一次编辑后无验证命令。"""
    edited = entry.get("edited_files") or []
    if not edited:
        return False
    last_edit_ts = max((item.get("ts", 0) for item in edited), default=0)
    if last_edit_ts == 0:
        return False
    return not any(
        cmd.get("ts", 0) >= last_edit_ts - 1
        for cmd in (entry.get("verify_commands") or [])
    )


def cursor_should_followup(entry: dict) -> bool:
    """Cursor stop：有编辑且（无验证命令或 R20 未过）。"""
    if not (entry.get("edited_files") or []):
        return False
    if not entry.get("r20_replay_ok"):
        return True
    return has_unverified_edits(entry)
