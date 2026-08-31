#!/usr/bin/env python3
"""Stop: 图谱增量刷新；仅 verification-gate 全绿时跑 sync.ps1。

Claude Code 已在 stop-verification-gate 内处理；本脚本给 TRAE / Qoder Stop 用。
禁止经 _editor_hook_launcher 调用（launcher 会在编辑器内跳过）。
"""
from __future__ import annotations

import json
import os
import sys
import io

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception as e:
    print(f"⚠️ {e}", file=sys.stderr)

from graph_freshness import (  # noqa: E402
    load_cfg,
    refresh_incremental,
    resolve_cwd,
    run_sync_ps1_if_verified,
    take_ui_slot,
)
from r20_replay import has_unverified_edits  # noqa: E402


def _load_entry(session_id: str) -> dict:
    path = os.path.join(os.path.expanduser("~/.claude"), ".state", "verification-gate.json")
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh).get(session_id) or {}
    except (OSError, json.JSONDecodeError) as exc:
        print(f"stop-graph-freshness: state read failed: {exc}", file=sys.stderr)
    return {}


def main() -> None:
    try:
        raw = (
            sys.stdin.buffer.read().decode("utf-8", errors="replace")
            if hasattr(sys.stdin, "buffer")
            else sys.stdin.read()
        )
        data = json.loads(raw) if raw.strip() else {}
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"stop-graph-freshness: stdin parse failed: {exc}", file=sys.stderr)
        sys.exit(0)

    if str(data.get("status") or "").lower() in {"aborted", "error"}:
        sys.exit(0)

    cfg = load_cfg()
    session_id = str(data.get("session_id") or data.get("conversation_id") or "unknown")
    entry = _load_entry(session_id)
    cwd = resolve_cwd(data) or str(entry.get("cwd") or data.get("cwd") or "")
    edited = entry.get("edited_files") or []
    if cwd:
        _has_crg, warns, refresh_result = refresh_incremental(
            [cwd], int(cfg.get("stop_refresh_timeout_sec", 30)), session_id=session_id
        )
        for w in warns:
            print(f"⚠️ {w}", file=sys.stderr)
        banner = str((refresh_result or {}).get("ui") or "").strip()
        fail = bool((refresh_result or {}).get("blocked") or not (refresh_result or {}).get("ok"))
        if banner and (fail or take_ui_slot(session_id, "refresh")):
            try:
                sys.stdout.write(json.dumps({"systemMessage": banner}, ensure_ascii=False) + "\n")
                sys.stdout.flush()
            except OSError as exc:
                print(f"stop-graph-freshness: ui write failed: {exc}", file=sys.stderr)

    has_edits = bool(edited)
    prompt = str(data.get("prompt") or data.get("text") or "").lower()
    user_skipped = any(k in prompt for k in ("跳过验证", "不用验证", "skip verify"))
    green = bool(
        has_edits
        and not user_skipped
        and entry.get("r20_replay_ok")
        and not has_unverified_edits(entry)
    )
    _ok, msg = run_sync_ps1_if_verified(has_edits=has_edits, verified_green=green)
    print(f"stop-graph-freshness: {msg}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
