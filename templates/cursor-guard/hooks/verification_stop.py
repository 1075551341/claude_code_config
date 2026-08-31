#!/usr/bin/env python3
"""stop: 完成验证 followup 硬门（v11.4.8）。

计划未批准 / CreatePlan / 零编辑 / 无 session id → 不 followup。
非简单双审：修改→验证→审查循环最多 3 轮；禁止只连审不改。
未验证编辑或 R20 不合格时用短 followup_message 续轮。
loop_limit 对齐 quality_gates.json verification_gate.max_blocks。
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
    if not session_id:
        return {}
    try:
        if path.exists():
            state = json.loads(path.read_text(encoding="utf-8"))
            return state.get(session_id) or {}
    except (OSError, json.JSONDecodeError) as e:
        print(f"verification_stop: state read failed: {e}", file=sys.stderr)
    return {}


def _slim_followup(body: str, reasons: list, loop_count: int, max_blocks: int) -> str:
    extra = (
        "\n补齐后才能结束：\n"
        + "\n".join(f"  • {r}" for r in reasons)
        + f"\n（followup {loop_count + 1}/{max_blocks}；跳过请说「跳过验证」）"
    )
    return body.rstrip() + extra


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
        skip_prompt = str(data.get("prompt") or data.get("text") or "").lower()
        user_skipped = any(k in skip_prompt for k in skip_keywords)

        session_id = handoff_session_id(data)
        if not session_id:
            print("verification_stop: 无 conversation_id/session_id，跳过 followup", file=sys.stderr)
            return

        entry = _load_entry(_state_path(claude_home), session_id)

        r20 = None
        crg = None
        try:
            r20 = import_claude_lib(claude_home, "r20_replay")
        except Exception as e:
            print(f"verification_stop: r20_replay unavailable: {e}", file=sys.stderr)
        try:
            crg = import_claude_lib(claude_home, "crg_track")
        except Exception as e:
            print(f"verification_stop: crg_track unavailable: {e}", file=sys.stderr)

        awaiting = bool(r20.is_awaiting_plan(entry, data) if r20 else False)
        if awaiting:
            print("verification_stop: 计划未批准 / CreatePlan，跳过 followup", file=sys.stderr)

        if r20 is not None:
            should = r20.cursor_should_followup(entry, data)
        else:
            should = bool(entry.get("edited_files")) and not awaiting

        edited = entry.get("edited_files") or []
        cwd = str(entry.get("cwd") or data.get("cwd") or "")
        last_edit_ts = max((item.get("ts", 0) for item in edited), default=0)
        doc_ext = {str(x).lower() for x in qg.get("doc_only_extensions", [".md", ".txt", ".rst", ".markdown"])}
        has_code_edit = any(
            Path(str(item.get("path") or "")).suffix.lower() not in doc_ext
            for item in edited
        )

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
                    _has_crg, warns, refresh_result = gf.refresh_incremental(
                        roots,
                        int(gcfg.get("stop_refresh_timeout_sec", 30)),
                        session_id=session_id,
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
                        and (fail or gf.take_ui_slot(session_id, "refresh"))
                    )
            except Exception as e:
                print(f"verification_stop: graph refresh failed: {e}", file=sys.stderr)
                graph_ui = "【收尾刷新双图】失败：refresh 异常"
                show_graph_ui = True

        def emit_graph_ui(extra: dict | None = None) -> None:
            payload = dict(extra or {})
            if show_graph_ui and graph_ui:
                payload["user_message"] = graph_ui
            if payload:
                write_json(payload)

        if loop_count >= max_blocks:
            print(
                f"verification_stop: loop_count={loop_count} ≥ max_blocks={max_blocks}，放行 DONE_WITH_CONCERNS",
                file=sys.stderr,
            )
            emit_graph_ui()
            return

        if user_skipped:
            print("verification_stop: 用户跳过验证，放行", file=sys.stderr)
            emit_graph_ui()
            return

        extra_reasons = []
        if (not awaiting) and edited and r20 is not None:
            extras = r20.impact_diff_check(entry, session_id, cwd)
            if extras:
                shown = ", ".join(extras[:8])
                extra_reasons.append(f"清单差集：{shown} 不在 IMPACT 声明内（错改或漏登）")
        if (
            (not awaiting)
            and edited
            and crg is not None
            and qg.get("require_crg_when_graph", True)
            and has_code_edit
            and crg.project_has_crg_graph(cwd)
            and not crg.has_crg_since(entry, last_edit_ts)
        ):
            extra_reasons.append(
                "项目已建 .code-review-graph/ 但最后一次代码编辑后未调用 CRG"
                "（get_minimal_context / get_impact_radius / detect_changes / get_review_context）"
            )

        need_review = False
        need_modify = False
        review_capped = False
        if r20 is not None and not awaiting:
            phase = r20.dual_pass_phase(entry, qg)
            need_review = phase == "review"
            need_modify = phase == "modify"
            review_capped = phase == "capped"
            if review_capped:
                print(
                    "verification_stop: 修改→审查已满上限仍无 PASS，放行 DONE_WITH_CONCERNS",
                    file=sys.stderr,
                )

        if extra_reasons and edited and not awaiting:
            should = True
        if need_review or need_modify:
            should = True

        if not should:
            if review_capped:
                print(
                    "verification_stop: 审查达上限仍无 PASS，不将 sync 视为全绿",
                    file=sys.stderr,
                )
                emit_graph_ui()
                return
            if gf is not None and edited and not awaiting:
                try:
                    _ok, msg = gf.run_sync_ps1_if_verified(has_edits=True, verified_green=True)
                    print(f"verification_stop: {msg}", file=sys.stderr)
                except Exception as e:
                    print(f"verification_stop: sync.ps1 failed: {e}", file=sys.stderr)
            emit_graph_ui()
            return

        reasons = []
        if not awaiting:
            if not entry.get("r20_replay_ok"):
                reasons.append("缺少合格 R20（六行：满足/遗漏/错改/漏改/原功能/影响范围）")
            if r20 is not None and r20.has_unverified_edits(entry):
                reasons.append("最后一次编辑后无测试/lint/构建运行记录")
            elif r20 is None:
                reasons.append("验证证据不完整")
            reasons.extend(extra_reasons)
            if need_modify:
                rounds = int(entry.get("review_rounds") or 0)
                max_rounds = int(qg.get("review_max_rounds", 3))
                reasons.append(
                    f"非简单双审：须先按未满足项修改并验证，再审全部修改是否符合预期"
                    f"（第 {rounds + 1}/{max_rounds} 轮）。禁止只连审不改。"
                )
            if need_review:
                rounds = int(entry.get("review_rounds") or 0)
                max_rounds = int(qg.get("review_max_rounds", 3))
                reasons.append(
                    f"非简单双审：委派 eng-reviewer 对照原始要求审全部修改"
                    f"（第 {rounds + 1}/{max_rounds} 轮；PASS 才可完成）"
                )
            if review_capped:
                reasons.append("修改→审查已满 3 轮仍未符合预期，标 DONE_WITH_CONCERNS，禁止再 followup 空转")

        if awaiting or not reasons:
            print("verification_stop: 无待补项或计划等待，跳过 followup", file=sys.stderr)
            emit_graph_ui()
            return

        if review_capped and not extra_reasons and entry.get("r20_replay_ok"):
            emit_graph_ui()
            return

        body = load_gate("verify", claude_home)
        follow = {"followup_message": _slim_followup(body, reasons, loop_count, max_blocks)}
        if show_graph_ui and graph_ui:
            follow["user_message"] = graph_ui
        write_json(follow)
    except Exception as e:
        print(f"verification_stop: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
