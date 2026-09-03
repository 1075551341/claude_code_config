#!/usr/bin/env python3
"""stop: 图谱收尾刷新 + 全绿后 sync.ps1（v11.4.10）。

Cursor stop 不能 permission deny；followup_message 会变成假用户回合刷会话面板。
完成验证改由规则驱动（修改→验证→独立审查）。本 hook 不再发出 followup_message。
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
from session_handoff import extract_session_id as handoff_session_id


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


def inherit_violation_msg(entry: dict, qg: dict) -> str:
    """Cursor 不能 deny；review 相位把非 inherit 审查者写成可见 user_message。"""
    pr = qg.get("parallel_review") or {}
    if not (
        pr.get("forbid_multiplier_models")
        or str((pr.get("require_model") or "")).strip().lower() == "inherit"
    ):
        return ""
    viol = entry.get("review_model_violations") or []
    if not viol:
        return ""
    shown = ", ".join(
        f"{v.get('agent')}={v.get('model')}" for v in viol[:6]
    )
    return (
        "独立审查子代理须 Task model=inherit（禁止倍率档）；"
        f"检测到非 inherit：{shown}"
    )


def _load_entry(path: Path, session_id: str) -> dict:
    if not session_id:
        return {}
    try:
        if path.exists():
            state = json.loads(path.read_text(encoding="utf-8"))
            return state.get(session_id) or {}
    except (OSError, json.JSONDecodeError) as e:
        print(f"verification_stop: state read failed: {e}", file=sys.stderr)
    return {}


def _verified_green(r20, entry: dict, data: dict, qg: dict) -> bool:
    """仅全绿才跑 sync.ps1：有编辑、已验证、R20 过、双审 skip/done。"""
    if r20 is None:
        return False
    if r20.is_awaiting_plan(entry, data):
        return False
    if not r20.counted_edit_items(entry):
        return False
    if r20.has_unverified_edits(entry):
        return False
    if not entry.get("r20_replay_ok"):
        return False
    phase = r20.dual_pass_phase(entry, qg)
    if phase in {"review", "modify", "verify", "capped"}:
        return False
    return True


def main() -> None:
    try:
        data = read_stdin()
        if str(data.get("status") or "").lower() in {"aborted", "error"}:
            return

        cfg = load_guard_config()
        claude_home = cfg["sync"]["claude_home"]
        session_id = handoff_session_id(data)
        entry = _load_entry(_state_path(claude_home), session_id)
        qg = _quality_gate_cfg(claude_home)

        r20 = None
        try:
            r20 = import_claude_lib(claude_home, "r20_replay")
        except Exception as e:
            print(f"verification_stop: r20_replay unavailable: {e}", file=sys.stderr)

        awaiting = bool(r20.is_awaiting_plan(entry, data) if r20 else False)
        cwd = str(entry.get("cwd") or data.get("cwd") or "")

        graph_ui = ""
        show_graph_ui = False
        gf = None
        try:
            gf = import_claude_lib(claude_home, "graph_freshness")
        except Exception as e:
            print(f"verification_stop: graph_freshness unavailable: {e}", file=sys.stderr)
        if gf is not None:
            try:
                cwd = gf.resolve_cwd(data) or cwd
                gcfg = gf.load_cfg()
                roots = [cwd] if cwd else []
                if roots:
                    phase = r20.dual_pass_phase(entry, qg) if r20 else ""
                    need_review_ensure = bool(
                        qg.get("require_dual_graph_before_review", True)
                        and phase == "review"
                    )
                    if need_review_ensure and hasattr(gf, "ensure_both"):
                        refresh_result = gf.ensure_both(
                            roots[0],
                            min(45, int(gcfg.get("pretool_ensure_timeout_sec", 90))),
                            session_id=session_id or "",
                        )
                        _has_crg = bool(refresh_result.get("crg"))
                        warns = list(refresh_result.get("warnings") or [])
                        if refresh_result.get("eligible") and (
                            refresh_result.get("blocked") or not refresh_result.get("ok")
                        ):
                            print(
                                "verification_stop: 独立审前双图 ensure 未就绪",
                                file=sys.stderr,
                            )
                    else:
                        _has_crg, warns, refresh_result = gf.refresh_incremental(
                            roots,
                            int(gcfg.get("stop_refresh_timeout_sec", 30)),
                            session_id=session_id or "",
                        )
                    for w in warns:
                        print(f"verification_stop: {w}", file=sys.stderr)
                    graph_ui = str((refresh_result or {}).get("ui") or "").strip()
                    fail = bool(
                        (refresh_result or {}).get("blocked")
                        or not (refresh_result or {}).get("ok")
                    )
                    show_graph_ui = bool(
                        graph_ui
                        and (fail or gf.take_ui_slot(session_id or "", "refresh"))
                    )
            except Exception as e:
                print(f"verification_stop: graph refresh failed: {e}", file=sys.stderr)
                graph_ui = "【收尾刷新双图】失败：refresh 异常"
                show_graph_ui = True

        if gf is not None and _verified_green(r20, entry, data, qg) and not awaiting:
            try:
                _ok, msg = gf.run_sync_ps1_if_verified(has_edits=True, verified_green=True)
                print(f"verification_stop: {msg}", file=sys.stderr)
            except Exception as e:
                print(f"verification_stop: sync.ps1 failed: {e}", file=sys.stderr)
        elif awaiting:
            print("verification_stop: 计划未批准，仅刷新图谱，不 followup", file=sys.stderr)
        else:
            print("verification_stop: 完成门不注入 followup_message（规则驱动双审）", file=sys.stderr)

        inherit_msg = ""
        phase = r20.dual_pass_phase(entry, qg) if r20 else ""
        if phase == "review":
            inherit_msg = inherit_violation_msg(entry, qg)
            if inherit_msg:
                print(f"verification_stop: {inherit_msg}", file=sys.stderr)

        parts = []
        if inherit_msg:
            parts.append(inherit_msg)
        if show_graph_ui and graph_ui:
            parts.append(graph_ui)
        if parts:
            write_json({"user_message": "\n".join(parts)})
    except Exception as e:
        print(f"verification_stop: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
