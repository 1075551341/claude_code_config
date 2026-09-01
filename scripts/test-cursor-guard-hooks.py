#!/usr/bin/env python3
"""Cursor Guard hook 本地模拟测试（stdin → hook，校验 JSON + 行为断言）。

命令：
    python scripts/test-cursor-guard-hooks.py                                     # 跑全部用例，结果打屏
    python scripts/test-cursor-guard-hooks.py --output scripts/test-guard-result.json  # 同时写 JSON 报告
    python scripts/test-cursor-guard-hooks.py -o <路径>                            # --output 短写法

被测对象是 ~/.cursor/hooks 下的已部署副本，不是仓库模板；改了 templates/cursor-guard/
必须先 deploy 再跑：powershell -File scripts/deploy-cursor-guard.ps1
一般不直接调本脚本，用上层封装：scripts/test-cursor-guard-regression.ps1（自动清状态 + 设 UTF-8）。
退出码：0 = 全部通过；非 0 = 有用例失败。
"""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

CURSOR = Path(os.environ.get("USERPROFILE", Path.home())) / ".cursor"
HOOKS = CURSOR / "hooks"
STATE = CURSOR / ".state"
CLAUDE = Path(os.environ.get("USERPROFILE", Path.home())) / ".claude"
TEMPLATE_GUARD = CLAUDE / "templates" / "cursor-guard" / "guard-config.json"

TRANSIENT_STATE_FILES = (
    "compress-pending.json",
    "tool-counter.json",
    "context-nudge.json",
    "cursor-context.json",
    "context_monitor.json",
)


def setup_stdout_utf8() -> None:
    if sys.platform != "win32":
        return
    if isinstance(sys.stdout, io.TextIOWrapper) and sys.stdout.encoding.lower().startswith("utf"):
        return
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


@contextmanager
def state_backup(paths: list[Path]) -> Iterator[None]:
    backups: dict[Path, str | None] = {}
    for path in paths:
        backups[path] = path.read_text(encoding="utf-8") if path.exists() else None
    try:
        yield
    finally:
        for path, content in backups.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")


def clear_transient_state() -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    for name in TRANSIENT_STATE_FILES:
        (STATE / name).unlink(missing_ok=True)


def run_hook(
    name: str,
    payload: dict,
    *,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    script = HOOKS / name
    if not script.exists():
        return {"pass": False, "behavior_pass": False, "error": f"missing {script}"}

    proc_env = os.environ.copy()
    proc_env["GRAPH_FRESHNESS_SKIP_SYNC"] = "1"
    if env:
        proc_env.update(env)

    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(CURSOR),
        timeout=180,
        env=proc_env,
    )
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    parsed: dict[str, Any] | str | None = None
    json_ok = False
    if out:
        try:
            parsed = json.loads(out)
            json_ok = isinstance(parsed, dict)
        except json.JSONDecodeError:
            parsed = out
    return {
        "pass": proc.returncode == 0 and json_ok,
        "exit": proc.returncode,
        "json_ok": json_ok,
        "stdout": parsed,
        "stderr": err[:300] if err else "",
    }


def finish_case(case: dict[str, Any], *, behavior: bool, note: str = "") -> dict[str, Any]:
    case["behavior_pass"] = behavior
    case["pass"] = bool(case.get("pass")) and behavior
    if note:
        case["note"] = note
    return case


def stdout_text(case: dict[str, Any]) -> str:
    return json.dumps(case.get("stdout") or {}, ensure_ascii=False)


def main() -> int:
    setup_stdout_utf8()
    parser = argparse.ArgumentParser(description="Cursor Guard hook regression")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Write JSON report to file (UTF-8)",
    )
    args = parser.parse_args()

    results: dict[str, Any] = {
        "cursor_home": str(CURSOR),
        "guard_version": None,
        "tests": {},
    }

    hooks_json = CURSOR / "hooks.json"
    guard_cfg_path = CURSOR / "guard-config.json"
    if hooks_json.exists():
        try:
            results["guard_version"] = json.loads(hooks_json.read_text(encoding="utf-8-sig")).get(
                "guard_version"
            )
        except json.JSONDecodeError:
            pass

    # --- 部署一致性 ---
    cfg_ok = guard_cfg_path.exists() and hooks_json.exists()
    if guard_cfg_path.exists() and TEMPLATE_GUARD.exists():
        deployed = json.loads(guard_cfg_path.read_text(encoding="utf-8-sig"))
        template = json.loads(TEMPLATE_GUARD.read_text(encoding="utf-8-sig"))
        cfg_ok = cfg_ok and deployed.get("version") == template.get("version")
    results["tests"]["deploy_config"] = finish_case(
        {"pass": cfg_ok, "json_ok": cfg_ok, "stdout": {"deployed": str(guard_cfg_path)}},
        behavior=cfg_ok,
        note="guard-config version matches template",
    )
    kws = []
    if guard_cfg_path.exists():
        try:
            kws = list(
                (json.loads(guard_cfg_path.read_text(encoding="utf-8-sig")).get("verification") or {}).get(
                    "prompt_keywords"
                )
                or []
            )
        except json.JSONDecodeError:
            kws = ["<unreadable>"]
    no_bare = "完成" not in kws
    results["tests"]["verification_keywords_no_bare_complete"] = finish_case(
        {"pass": no_bare, "json_ok": True, "stdout": {"prompt_keywords": kws}},
        behavior=no_bare,
        note="已部署 prompt_keywords 不得含裸词「完成」",
    )

    timeout_ok = False
    gf_timeout_ok = False
    mcp_timeout_ok = False
    matcher_ok = False
    se_ok = False
    tracker_matcher_ok = False
    ss_timeout = None
    se_timeout = None
    gf_timeout = None
    mcp_timeout = None
    if hooks_json.exists():
        try:
            hj = json.loads(hooks_json.read_text(encoding="utf-8-sig"))
            ss_timeout = (hj.get("hooks") or {}).get("sessionStart", [{}])[0].get("timeout")
            timeout_ok = int(ss_timeout or 0) >= 120
            se_timeout = (hj.get("hooks") or {}).get("sessionEnd", [{}])[0].get("timeout")
            se_ok = int(se_timeout or 0) >= 45
            tracker_matcher_ok = False
            gf_timeout = None
            mcp_timeout = None
            gf_timeout_ok = False
            mcp_timeout_ok = False
            matcher_ok = False
            for item in (hj.get("hooks") or {}).get("preToolUse") or []:
                if "graph_freshness.py" in str(item.get("command") or ""):
                    gf_timeout = item.get("timeout")
                    gf_timeout_ok = int(gf_timeout or 0) >= 90
                    matcher = str(item.get("matcher") or "")
                    matcher_ok = "CallDynamicTool" in matcher and "MCP:" in matcher
                    break
            for item in (hj.get("hooks") or {}).get("beforeMCPExecution") or []:
                if "graph_freshness.py" in str(item.get("command") or ""):
                    mcp_timeout = item.get("timeout")
                    mcp_timeout_ok = int(mcp_timeout or 0) >= 90
                    break
            for item in (hj.get("hooks") or {}).get("postToolUse") or []:
                if "verify_tracker.py" in str(item.get("command") or ""):
                    tracker_matcher_ok = "CallDynamicTool" in str(item.get("matcher") or "")
                    break
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            timeout_ok = False
            gf_timeout_ok = False
            mcp_timeout_ok = False
            matcher_ok = False
            se_ok = False
            tracker_matcher_ok = False
    results["tests"]["graph_freshness_timeouts"] = finish_case(
        {
            "pass": timeout_ok
            and gf_timeout_ok
            and mcp_timeout_ok
            and matcher_ok
            and se_ok
            and tracker_matcher_ok,
            "json_ok": True,
            "stdout": {
                "sessionStart": ss_timeout,
                "sessionEnd": se_timeout,
                "graph_freshness": gf_timeout,
                "beforeMCPExecution": mcp_timeout,
                "matcher_ok": matcher_ok,
                "tracker_matcher_ok": tracker_matcher_ok,
            },
        },
        behavior=timeout_ok
        and gf_timeout_ok
        and mcp_timeout_ok
        and matcher_ok
        and se_ok
        and tracker_matcher_ok,
        note="sessionStart ≥120s, sessionEnd ≥45s, graph_freshness preToolUse/beforeMCP ≥90s, matcher+verify_tracker include CallDynamicTool",
    )

    with tempfile.TemporaryDirectory() as td_nongit:
        r_gf_skip = run_hook(
            "graph_freshness.py",
            {"tool_name": "Grep", "cwd": td_nongit},
        )
        results["tests"]["graph_freshness_nongit_allow"] = finish_case(
            r_gf_skip,
            behavior=(r_gf_skip.get("stdout") or {}) == {},
            note="non-git cwd is not eligible → allow (empty JSON object)",
        )

    # --- codegraph 优先 ---
    for tool in ("Grep", "Read", "Glob"):
        key = f"explore_router_{tool}"
        r = run_hook("explore_router.py", {"tool_name": tool})
        msg = stdout_text(r)
        results["tests"][key] = finish_case(
            r,
            behavior="codegraph" in msg and "agent_message" in msg,
        )

    r_off = run_hook(
        "explore_router.py",
        {"tool_name": "Grep"},
        env={"CURSOR_GUARD_CODEGRAPH_FIRST": "0"},
    )
    results["tests"]["explore_router_disabled"] = finish_case(
        r_off,
        behavior=(r_off.get("stdout") or {}) == {},
        note="CURSOR_GUARD_CODEGRAPH_FIRST=0 → no nudge",
    )

    counter = STATE / "tool-counter.json"
    cursor_ctx = STATE / "cursor-context.json"
    handoff = STATE / "session-handoff.json"
    last_sess = STATE / "last-session.json"
    pending_path = STATE / "compress-pending.json"
    digest_path = STATE / "session-digest.md"
    pre_compact = STATE / "pre-compact-state.json"

    monitor = STATE / "context_monitor.json"
    with state_backup(
        [counter, cursor_ctx, monitor, handoff, last_sess, pending_path, digest_path]
    ):
        clear_transient_state()

        results["tests"]["context_pre_normal"] = run_hook(
            "context_pre_tool.py", {"tool_name": "Grep"}
        )
        results["tests"]["context_pre_normal"]["behavior_pass"] = (
            results["tests"]["context_pre_normal"].get("stdout") or {}
        ) == {}

        counter.write_text(json.dumps({"count": 50, "est_tokens": 140000}), encoding="utf-8")
        r_pre70 = run_hook("context_pre_tool.py", {"tool_name": "Read"})
        results["tests"]["context_pre_70pct"] = finish_case(
            r_pre70,
            behavior="70%" in stdout_text(r_pre70) and "agent_message" in stdout_text(r_pre70),
        )

        clear_transient_state()
        counter.write_text(json.dumps({"count": 50, "est_tokens": 140000}), encoding="utf-8")
        r_stop70 = run_hook("context_stop.py", {"conversation_id": "sess-warn-70"})
        results["tests"]["context_stop_70pct"] = finish_case(
            r_stop70,
            behavior="additional_context" in (r_stop70.get("stdout") or {})
            and "70" in stdout_text(r_stop70),
            note="isolated: no compress-pending, no stale preCompact %",
        )

        sid_force = "sess-force-90"
        counter.write_text(json.dumps({"count": 80, "est_tokens": 180000}), encoding="utf-8")
        r_stop90 = run_hook(
            "context_stop.py",
            {"session_id": "gen-a", "conversation_id": sid_force},
        )
        out90 = r_stop90.get("stdout") or {}
        results["tests"]["context_stop_90pct"] = finish_case(
            r_stop90,
            behavior="followup_message" not in out90
            and "additional_context" in out90
            and "/summarize" in stdout_text(r_stop90),
            note="90% must not followup_message (that is a new user turn)",
        )
        r_stop90b = run_hook(
            "context_stop.py",
            {"session_id": "gen-b", "conversation_id": sid_force},
        )
        out90b = r_stop90b.get("stdout") or {}
        results["tests"]["context_stop_90pct_no_repeat"] = finish_case(
            r_stop90b,
            behavior="followup_message" not in out90b
            and "【上下文≥90%】" not in stdout_text(r_stop90b),
            note="per-turn session_id must not restart a 90% agent loop",
        )

        (STATE / "context-nudge.json").unlink(missing_ok=True)
        counter.write_text(json.dumps({"count": 80, "est_tokens": 180000}), encoding="utf-8")
        r_stop90_unv = run_hook(
            "context_stop.py",
            {"session_id": "gen-unv", "conversation_id": "sess-force-90-unv"},
        )
        out90_unv = r_stop90_unv.get("stdout") or {}
        results["tests"]["context_stop_90pct_unverified_still_hints"] = finish_case(
            r_stop90_unv,
            behavior="followup_message" not in out90_unv
            and "additional_context" in out90_unv
            and "/summarize" in stdout_text(r_stop90_unv),
            note="完成门不再 followup 让位，90% 仍注入 additional_context",
        )

        clear_transient_state()
        counter.write_text(json.dumps({"count": 80, "est_tokens": 180000}), encoding="utf-8")
        r_echo = run_hook(
            "context_stop.py",
            {
                "session_id": "gen-echo",
                "conversation_id": "echo-force",
                "prompt": "【上下文≥90%】请建议用户发送 /summarize",
            },
        )
        results["tests"]["context_stop_90pct_echo_skip"] = finish_case(
            r_echo,
            behavior="followup_message" not in (r_echo.get("stdout") or {})
            and (r_echo.get("stdout") or {}) == {},
            note="incoming 90% hint must not spawn another Stop inject",
        )

        r_sum = run_hook(
            "compress_on_prompt.py",
            {"prompt": "/summarize", "conversation_id": sid_force},
        )
        r_after_sum = run_hook("context_stop.py", {"conversation_id": sid_force})
        results["tests"]["context_stop_after_summarize_quiet"] = finish_case(
            r_after_sum,
            behavior=(r_sum.get("stdout") or {}) == {}
            and "followup_message" not in (r_after_sum.get("stdout") or {}),
            note="/summarize resets estimate + FORCE latch; Stop must not keep followup",
        )

        cursor_ctx.write_text(
            json.dumps(
                {
                    "context_usage_percent": 85,
                    "context_tokens": 170000,
                    "context_window_size": 200000,
                }
            ),
            encoding="utf-8",
        )
        counter.write_text(json.dumps({"count": 5, "est_tokens": 10000}), encoding="utf-8")
        r_stop85 = run_hook("context_stop.py", {})
        results["tests"]["context_stop_cursor_85pct"] = finish_case(
            r_stop85,
            behavior="85%" in stdout_text(r_stop85),
        )

        # 显式压缩优先于 70% 迷你摘要
        pending_path.write_text(
            json.dumps({"session_id": "prio-test", "prompt": "压缩", "stage": "requested"}),
            encoding="utf-8",
        )
        counter.write_text(json.dumps({"count": 50, "est_tokens": 140000}), encoding="utf-8")
        r_prio = run_hook("context_stop.py", {"conversation_id": "prio-test"})
        results["tests"]["context_stop_extract_priority"] = finish_case(
            r_prio,
            behavior="followup_message" in (r_prio.get("stdout") or {})
            and "提取上下文" in stdout_text(r_prio),
        )

        r_pc = run_hook(
            "pre_compact_snapshot.py",
            {
                "trigger": "manual",
                "context_usage_percent": 85,
                "context_tokens": 169100,
                "context_window_size": 200000,
            },
        )
        results["tests"]["pre_compact_snapshot"] = finish_case(
            r_pc,
            behavior=pre_compact.exists()
            and "user_message" in (r_pc.get("stdout") or {})
            and "/summarize" in stdout_text(r_pc),
        )

        handoff.write_text(
            json.dumps({"reason": "test", "cursor_usage_percent": 85, "note": "测试交接"}),
            encoding="utf-8",
        )
        last_sess.write_text(json.dumps({"session_id": "old-session-id"}), encoding="utf-8")
        r_sb_new = run_hook(
            "session_bootstrap.py",
            {"conversation_id": "new-session-id-aa2c7adf"},
        )
        results["tests"]["session_bootstrap_new"] = finish_case(
            r_sb_new,
            behavior="上轮会话交接" in stdout_text(r_sb_new)
            and "codegraph 优先" in stdout_text(r_sb_new)
            and "user_message" in (r_sb_new.get("stdout") or {}),
        )

        # --- 显式提取 E2E ---
        clear_transient_state()
        e2e_sid = "e2e-extract-test"
        r_c1 = run_hook(
            "compress_on_prompt.py",
            {"prompt": "请提取上下文", "conversation_id": e2e_sid},
        )
        pending_ok = pending_path.exists()
        pending_data = json.loads(pending_path.read_text(encoding="utf-8")) if pending_ok else {}
        r_c2 = run_hook("context_stop.py", {"conversation_id": e2e_sid})
        r_c3 = run_hook(
            "capture_compress_digest.py",
            {
                "text": (
                    "【提取上下文】已完成: E2E 回归。进行中: 无。待定: 无。"
                    "路径: ~/.cursor/.state/session-digest.md"
                ),
                "conversation_id": e2e_sid,
            },
        )
        digest_ok = digest_path.exists() and "E2E 回归" in digest_path.read_text(encoding="utf-8")
        pending_cleared = not pending_path.exists()
        results["tests"]["e2e_explicit_extract"] = finish_case(
            {
                "pass": all(
                    x.get("pass") for x in (r_c1, r_c2, r_c3)
                ),
                "json_ok": True,
                "stdout": {
                    "step1_user_message": "user_message" in (r_c1.get("stdout") or {}),
                    "step2_followup": "followup_message" in (r_c2.get("stdout") or {}),
                    "step3_digest": digest_ok,
                    "pending_cleared": pending_cleared,
                    "pending_stage": pending_data.get("stage"),
                },
            },
            behavior=(
                pending_ok
                and pending_data.get("stage") == "requested"
                and "followup_message" in (r_c2.get("stdout") or {})
                and digest_ok
                and pending_cleared
            ),
            note="提取上下文 → pending → stop followup → digest → clear pending",
        )

        r_cp = run_hook("compress_on_prompt.py", {"prompt": "请压缩上下文", "conversation_id": "test"})
        results["tests"]["compress_on_prompt_passthrough"] = finish_case(
            r_cp,
            behavior=(r_cp.get("stdout") or {}) == {}
            and not pending_path.exists(),
            note="压缩上下文 与 /summarize 等效，不创建 pending",
        )

        r_ex = run_hook("compress_on_prompt.py", {"prompt": "提取上下文", "conversation_id": "extract-test"})
        results["tests"]["extract_on_prompt"] = finish_case(
            r_ex,
            behavior="user_message" in (r_ex.get("stdout") or {})
            and "提取上下文" in stdout_text(r_ex)
            and pending_path.exists(),
        )

        r_ps = run_hook("compress_on_prompt.py", {"prompt": "/summarize"})
        results["tests"]["compress_pass_summarize"] = finish_case(
            r_ps,
            behavior=(r_ps.get("stdout") or {}) == {},
            note="/summarize must not be intercepted",
        )

        results["tests"]["session_end"] = run_hook(
            "session_end.py", {"session_id": "end-test", "reason": "user_close"}
        )
        results["tests"]["session_end"]["behavior_pass"] = results["tests"]["session_end"].get(
            "pass", False
        )

    # session_bootstrap 在 state 恢复后（真实会话状态）
    r_sb = run_hook("session_bootstrap.py", {})
    results["tests"]["session_bootstrap"] = finish_case(
        r_sb,
        behavior="additional_context" in (r_sb.get("stdout") or {})
        and "codegraph 优先" in stdout_text(r_sb)
        and "user_message" in (r_sb.get("stdout") or {}),
    )

    results["tests"]["shell_guard_safe"] = run_hook(
        "shell_guard.py", {"command": "python --version"}
    )
    results["tests"]["shell_guard_safe"]["behavior_pass"] = (
        results["tests"]["shell_guard_safe"].get("stdout") or {}
    ) == {}

    r_deny = run_hook("shell_guard.py", {"command": "format C:"})
    results["tests"]["shell_guard_deny"] = finish_case(
        r_deny,
        behavior=isinstance(r_deny.get("stdout"), dict)
        and r_deny["stdout"].get("permission") == "deny",
    )

    results["tests"]["secret_scan_clean"] = run_hook(
        "prompt_secret_scan.py", {"prompt": "hello world"}
    )
    results["tests"]["secret_scan_clean"]["behavior_pass"] = results["tests"][
        "secret_scan_clean"
    ].get("pass", False)

    results["tests"]["maintenance_hints"] = run_hook(
        "maintenance_hints.py",
        {"file_path": str(CLAUDE / "rules" / "CORE.md")},
    )
    results["tests"]["maintenance_hints"]["behavior_pass"] = results["tests"][
        "maintenance_hints"
    ].get("pass", False)

    r_mh_repo = run_hook(
        "maintenance_hints.py",
        {"file_path": "C:/tmp-not-claude-home/app.py"},
    )
    results["tests"]["maintenance_hints_repo"] = finish_case(
        r_mh_repo,
        behavior="文档" in stdout_text(r_mh_repo) or "codegraph" in stdout_text(r_mh_repo),
        note="业务仓 .py 也应提示文档 companion / Grep",
    )

    vg_path = CLAUDE / ".state" / "verification-gate.json"
    with state_backup([vg_path]):
        sid_fe = "first-edit-hook-test"
        vg_path.parent.mkdir(parents=True, exist_ok=True)
        if vg_path.exists():
            vg_path.unlink()
        payload_fe = {
            "tool_name": "Write",
            "tool_input": {"file_path": str(CLAUDE / "tmp-first-edit-a.py")},
            "conversation_id": sid_fe,
        }
        r_fe1 = run_hook("first_edit_verify.py", payload_fe)
        results["tests"]["first_edit_once"] = finish_case(
            r_fe1,
            behavior="首次编辑后" in stdout_text(r_fe1)
            and (
                "additional_context" in (r_fe1.get("stdout") or {})
                or "agent_message" in (r_fe1.get("stdout") or {})
            ),
        )
        r_fe2 = run_hook("first_edit_verify.py", payload_fe)
        results["tests"]["first_edit_second_silent"] = finish_case(
            r_fe2,
            behavior=(r_fe2.get("stdout") or {}) == {},
            note="同一文件第二次编辑不再注入",
        )

        sid_vs = "verify-stop-hook-test"
        vg_path.write_text(
            json.dumps(
                {
                    sid_vs: {
                        "ts": time.time(),
                        "edited_files": [{"path": "a.py", "ts": 1}],
                        "verify_commands": [],
                        "r20_replay_ok": False,
                    }
                }
            ),
            encoding="utf-8",
        )
        r_vs = run_hook(
            "verification_stop.py",
            {"conversation_id": sid_vs, "status": "completed", "loop_count": 0},
        )
        results["tests"]["verification_stop_followup"] = finish_case(
            r_vs,
            behavior="followup_message" not in (r_vs.get("stdout") or {}),
            note="有未验证编辑 → 不 followup（完成门改规则驱动）",
        )
        with tempfile.TemporaryDirectory() as td_nograph:
            vg_path.write_text(
                json.dumps(
                    {
                        sid_vs: {
                            "ts": time.time(),
                            "cwd": td_nograph,
                            "edited_files": [{"path": "a.py", "ts": 1}],
                            "verify_commands": [{"command": "pytest", "ts": 2}],
                            "r20_replay_ok": True,
                        }
                    }
                ),
                encoding="utf-8",
            )
            r_vs_ok = run_hook(
                "verification_stop.py",
                {
                    "conversation_id": sid_vs,
                    "status": "completed",
                    "loop_count": 0,
                    "cwd": td_nograph,
                },
            )
            results["tests"]["verification_stop_pass"] = finish_case(
                r_vs_ok,
                behavior="followup_message" not in (r_vs_ok.get("stdout") or {}),
                note="有代码改动且 R20/测试已过：仍不 followup（双审由规则驱动）",
            )
            vg_path.write_text(
                json.dumps(
                    {
                        sid_vs: {
                            "ts": time.time(),
                            "cwd": td_nograph,
                            "edited_files": [{"path": "a.py", "ts": 1}],
                            "verify_commands": [{"command": "pytest", "ts": 2}],
                            "r20_replay_ok": True,
                            "reviews": [{"agent": "eng-reviewer", "ts": 3}],
                            "review_rounds": 1,
                            "review_pass_ok": True,
                        }
                    }
                ),
                encoding="utf-8",
            )
            r_vs_reviewed = run_hook(
                "verification_stop.py",
                {
                    "conversation_id": sid_vs,
                    "status": "completed",
                    "loop_count": 0,
                    "cwd": td_nograph,
                },
            )
            results["tests"]["verification_stop_pass_after_review"] = finish_case(
                r_vs_reviewed,
                behavior="followup_message" not in (r_vs_reviewed.get("stdout") or {}),
                note="独立审查 PASS/符合预期 → 不再 followup（省 token）",
            )

        with tempfile.TemporaryDirectory() as td_graph:
            graph_dir = Path(td_graph, ".code-review-graph")
            graph_dir.mkdir()
            (graph_dir / "graph.db").write_bytes(b"")
            vg_path.write_text(
                json.dumps(
                    {
                        sid_vs: {
                            "ts": time.time(),
                            "cwd": td_graph,
                            "edited_files": [{"path": "a.py", "ts": 1}],
                            "verify_commands": [{"command": "pytest", "ts": 2}],
                            "r20_replay_ok": True,
                        }
                    }
                ),
                encoding="utf-8",
            )
            r_vs_crg = run_hook(
                "verification_stop.py",
                {
                    "conversation_id": sid_vs,
                    "status": "completed",
                    "loop_count": 0,
                    "cwd": td_graph,
                },
            )
            results["tests"]["verification_stop_crg_required"] = finish_case(
                r_vs_crg,
                behavior="followup_message" not in (r_vs_crg.get("stdout") or {}),
                note="有图且无 crg_calls → 仍不 followup",
            )

        vg_path.write_text(
            json.dumps(
                {
                    sid_vs: {
                        "ts": time.time(),
                        "edited_files": [{"path": "a.py", "ts": 1}],
                        "last_tool": "CreatePlan",
                        "awaiting_plan_approval": True,
                        "r20_replay_ok": False,
                    }
                }
            ),
            encoding="utf-8",
        )
        r_plan = run_hook(
            "verification_stop.py",
            {"conversation_id": sid_vs, "status": "completed", "loop_count": 0},
        )
        results["tests"]["verification_stop_plan_skip"] = finish_case(
            r_plan,
            behavior="followup_message" not in (r_plan.get("stdout") or {}),
            note="CreatePlan / 计划未批准 → 不 followup",
        )
        vg_path.write_text(
            json.dumps(
                {
                    sid_vs: {
                        "ts": time.time(),
                        "edited_files": [
                            {
                                "path": str(Path.home() / ".cursor" / "plans" / "x.plan.md"),
                                "ts": 1,
                            }
                        ],
                        "r20_replay_ok": False,
                    }
                }
            ),
            encoding="utf-8",
        )
        r_plan_file = run_hook(
            "verification_stop.py",
            {"conversation_id": sid_vs, "status": "completed", "loop_count": 0},
        )
        results["tests"]["verification_stop_plan_file_skip"] = finish_case(
            r_plan_file,
            behavior="followup_message" not in (r_plan_file.get("stdout") or {}),
            note="仅 *.plan.md 编辑 → 不 followup",
        )
        sid_prod = "prod-createplan-chain"
        vg_path.write_text(json.dumps({}), encoding="utf-8")
        r_dyn = run_hook(
            "verify_tracker.py",
            {
                "tool_name": "CallDynamicTool",
                "tool_input": {"toolName": "CreatePlan", "name": "x", "overview": "y"},
                "conversation_id": sid_prod,
                "cwd": str(Path(tempfile.gettempdir())),
            },
        )
        plan_path = str(Path.home() / ".cursor" / "plans" / "prod-chain.plan.md")
        r_write_plan = run_hook(
            "verify_tracker.py",
            {
                "tool_name": "Write",
                "tool_input": {"path": plan_path},
                "conversation_id": sid_prod,
            },
        )
        st_prod = json.loads(vg_path.read_text(encoding="utf-8")) if vg_path.exists() else {}
        entry_prod = st_prod.get(sid_prod) or {}
        results["tests"]["verify_tracker_calldynamic_createplan"] = finish_case(
            r_dyn if r_dyn.get("exit") != 0 else r_write_plan,
            behavior=(
                (r_dyn.get("exit") == 0)
                and (r_write_plan.get("exit") == 0)
                and entry_prod.get("awaiting_plan_approval") is True
            ),
            note="CallDynamicTool CreatePlan 后写 plan.md 保持 awaiting",
        )
        r_prod_stop = run_hook(
            "verification_stop.py",
            {"conversation_id": sid_prod, "status": "completed", "loop_count": 0},
        )
        results["tests"]["verification_stop_createplan_write_plan_skip"] = finish_case(
            r_prod_stop,
            behavior="followup_message" not in (r_prod_stop.get("stdout") or {}),
            note="CreatePlan 生产链写 plan.md 后 Stop 不 followup",
        )
        r_fev_plan = run_hook(
            "first_edit_verify.py",
            {
                "tool_name": "Write",
                "tool_input": {"path": plan_path},
                "conversation_id": sid_prod,
            },
        )
        results["tests"]["first_edit_verify_plan_skip"] = finish_case(
            r_fev_plan,
            behavior="additional_context" not in (r_fev_plan.get("stdout") or {}),
            note="计划制品不注入五维验收",
        )
        r_sw = run_hook(
            "verify_tracker.py",
            {
                "tool_name": "CallDynamicTool",
                "tool_input": {
                    "toolName": "SwitchMode",
                    "arguments": {"target_mode_id": "agent"},
                },
                "conversation_id": sid_prod,
            },
        )
        r_code = run_hook(
            "verify_tracker.py",
            {
                "tool_name": "Write",
                "tool_input": {"path": "src/a.py"},
                "conversation_id": sid_prod,
                "cwd": str(Path(tempfile.gettempdir())),
            },
        )
        st_prod2 = json.loads(vg_path.read_text(encoding="utf-8")) if vg_path.exists() else {}
        entry_prod2 = st_prod2.get(sid_prod) or {}
        r_after = run_hook(
            "verification_stop.py",
            {"conversation_id": sid_prod, "status": "completed", "loop_count": 0},
        )
        results["tests"]["verification_stop_after_switch_agent_code_followup"] = finish_case(
            r_after if r_after.get("exit") != 0 else r_sw,
            behavior=(
                (r_sw.get("exit") == 0)
                and (r_code.get("exit") == 0)
                and entry_prod2.get("awaiting_plan_approval") is False
                and "followup_message" not in (r_after.get("stdout") or {})
            ),
            note="SwitchMode→agent 后写 src/a.py 仍不 followup",
        )
        r_gate_kw = run_hook(
            "verification_gate.py",
            {"conversation_id": "gate-kw-test", "prompt": "所有都完成后执行同步"},
        )
        results["tests"]["verification_gate_完成后_no_edit"] = finish_case(
            r_gate_kw,
            behavior=(r_gate_kw.get("stdout") or {}) == {},
            note="「完成后」无未验证编辑 → 不注入",
        )
        vg_path.write_text(
            json.dumps(
                {
                    "gate-unverified": {
                        "ts": time.time(),
                        "edited_files": [{"path": "a.py", "ts": 1}],
                        "verify_commands": [],
                    }
                }
            ),
            encoding="utf-8",
        )
        r_gate_unv = run_hook(
            "verification_gate.py",
            {
                "conversation_id": "gate-unverified",
                "prompt": "请继续实现剩余功能",
            },
        )
        results["tests"]["verification_gate_unverified_no_inject"] = finish_case(
            r_gate_unv,
            behavior=(r_gate_unv.get("stdout") or {}) == {},
            note="有未验证编辑也不注入完成门 additional_context",
        )
        r_gate_echo = run_hook(
            "verification_gate.py",
            {
                "conversation_id": sid_vs,
                "prompt": "【门控 · 完成前必做】\n补齐 R20",
            },
        )
        results["tests"]["verification_gate_echo_skip"] = finish_case(
            r_gate_echo,
            behavior=(r_gate_echo.get("stdout") or {}) == {},
            note="门控回灌 → 不重复注入",
        )
        r_nosid = run_hook(
            "verification_stop.py",
            {"status": "completed", "loop_count": 0},
        )
        results["tests"]["verification_stop_no_session"] = finish_case(
            r_nosid,
            behavior="followup_message" not in (r_nosid.get("stdout") or {}),
            note="无 session id → 不 followup",
        )
        vg_path.write_text(
            json.dumps(
                {
                    sid_vs: {
                        "ts": time.time(),
                        "cwd": str(Path(tempfile.gettempdir())),
                        "edited_files": [{"path": "a.py", "ts": 1}],
                        "verify_commands": [{"command": "pytest", "ts": 2}],
                        "r20_replay_ok": True,
                        "non_simple": True,
                        "review_rounds": 3,
                        "review_pass_ok": False,
                    }
                }
            ),
            encoding="utf-8",
        )
        r_capped = run_hook(
            "verification_stop.py",
            {
                "conversation_id": sid_vs,
                "status": "completed",
                "loop_count": 0,
                "cwd": str(Path(tempfile.gettempdir())),
            },
        )
        results["tests"]["verification_stop_review_capped"] = finish_case(
            r_capped,
            behavior="followup_message" not in (r_capped.get("stdout") or {}),
            note="修改→审查满 3 轮仍无 PASS → 不 followup 空转",
        )
        vg_path.write_text(
            json.dumps(
                {
                    sid_vs: {
                        "ts": time.time(),
                        "cwd": str(Path(tempfile.gettempdir())),
                        "edited_files": [{"path": "a.py", "ts": 1}],
                        "verify_commands": [{"command": "pytest", "ts": 2}],
                        "r20_replay_ok": True,
                        "non_simple": True,
                        "reviews": [{"agent": "eng-reviewer", "ts": 3}],
                        "review_rounds": 1,
                        "review_pass_ok": False,
                    }
                }
            ),
            encoding="utf-8",
        )
        r_modify = run_hook(
            "verification_stop.py",
            {
                "conversation_id": sid_vs,
                "status": "completed",
                "loop_count": 0,
                "cwd": str(Path(tempfile.gettempdir())),
            },
        )
        results["tests"]["verification_stop_modify_before_rereview"] = finish_case(
            r_modify,
            behavior="followup_message" not in (r_modify.get("stdout") or {}),
            note="NEEDS-CHANGES 后无新修改 → 仍不 followup（规则要求先改再审）",
        )
        sid_inc = "review-round-increment-test"
        now_inc = time.time()
        vg_path.write_text(
            json.dumps(
                {
                    sid_inc: {
                        "ts": now_inc,
                        "cwd": str(Path(tempfile.gettempdir())),
                        "edited_files": [{"path": "a.py", "ts": now_inc - 10}],
                        "verify_commands": [{"command": "pytest", "ts": now_inc - 9}],
                        "reviews": [],
                        "review_rounds": 0,
                    }
                }
            ),
            encoding="utf-8",
        )
        task_payload = {
            "tool_name": "Task",
            "tool_input": {
                "subagent_type": "eng-reviewer",
                "description": "Review",
                "prompt": "review",
            },
            "conversation_id": sid_inc,
            "cwd": str(Path(tempfile.gettempdir())),
        }
        r_t1 = run_hook("verify_tracker.py", task_payload)
        r_t2 = run_hook("verify_tracker.py", task_payload)
        st_inc = json.loads(vg_path.read_text(encoding="utf-8"))
        entry_inc = st_inc.get(sid_inc) or {}
        results["tests"]["verify_tracker_same_round_no_double_count"] = finish_case(
            r_t1 if r_t1.get("exit") != 0 else r_t2,
            behavior=(
                (r_t1.get("exit") == 0)
                and (r_t2.get("exit") == 0)
                and int(entry_inc.get("review_rounds") or 0) == 1
                and len(entry_inc.get("reviews") or []) == 2
            ),
            note="同轮连派 eng-reviewer 只 +1 轮次，禁止提前耗尽 3 轮",
        )
        sid_resume = "review-resume-skip-test"
        now_resume = time.time()
        vg_path.write_text(
            json.dumps(
                {
                    sid_resume: {
                        "ts": now_resume,
                        "cwd": str(Path(tempfile.gettempdir())),
                        "edited_files": [{"path": "a.py", "ts": now_resume - 10}],
                        "verify_commands": [{"command": "pytest", "ts": now_resume - 9}],
                        "reviews": [],
                        "review_rounds": 0,
                    }
                }
            ),
            encoding="utf-8",
        )
        resume_payload = {
            "tool_name": "Task",
            "tool_input": {
                "subagent_type": "eng-reviewer",
                "description": "Review",
                "prompt": "review",
                "resume": "prev-reviewer-id",
            },
            "conversation_id": sid_resume,
            "cwd": str(Path(tempfile.gettempdir())),
        }
        r_resume = run_hook("verify_tracker.py", resume_payload)
        st_resume = json.loads(vg_path.read_text(encoding="utf-8"))
        entry_resume = st_resume.get(sid_resume) or {}
        results["tests"]["verify_tracker_resume_not_counted"] = finish_case(
            r_resume,
            behavior=(
                (r_resume.get("exit") == 0)
                and len(entry_resume.get("reviews") or []) == 0
                and int(entry_resume.get("review_rounds") or 0) == 0
                and len(entry_resume.get("skipped_resumed_reviews") or []) == 1
            ),
            note="resume 上一轮审查者不计入独立审查",
        )
        entry_inc["edited_files"] = list(entry_inc.get("edited_files") or []) + [
            {"path": "b.py", "ts": time.time()}
        ]
        st_inc[sid_inc] = entry_inc
        vg_path.write_text(json.dumps(st_inc), encoding="utf-8")
        r_t3 = run_hook("verify_tracker.py", task_payload)
        st_inc2 = json.loads(vg_path.read_text(encoding="utf-8"))
        entry_inc2 = st_inc2.get(sid_inc) or {}
        results["tests"]["verify_tracker_new_edit_increments"] = finish_case(
            r_t3,
            behavior=(
                (r_t3.get("exit") == 0)
                and int(entry_inc2.get("review_rounds") or 0) == 2
            ),
            note="NEEDS-CHANGES 后有新修改再审 → 轮次 +1",
        )
        sid_pass = "r20-capture-pass-test"
        vg_path.write_text(
            json.dumps(
                {
                    sid_pass: {
                        "ts": time.time(),
                        "edited_files": [{"path": "a.py", "ts": 1}],
                    }
                }
            ),
            encoding="utf-8",
        )
        r_pass_bare = run_hook(
            "r20_capture.py",
            {
                "conversation_id": sid_pass,
                "text": "Independent review PASS of this change.",
            },
        )
        st_bare = json.loads(vg_path.read_text(encoding="utf-8"))
        results["tests"]["r20_capture_pass_requires_reviews"] = finish_case(
            r_pass_bare,
            behavior=(
                (r_pass_bare.get("exit") == 0)
                and (st_bare.get(sid_pass) or {}).get("review_pass_ok") is not True
            ),
            note="无 reviews 时正文 PASS 不得自报过审",
        )
        st_bare[sid_pass]["reviews"] = [{"agent": "eng-reviewer", "ts": 2}]
        vg_path.write_text(json.dumps(st_bare), encoding="utf-8")
        r_pass_ok = run_hook(
            "r20_capture.py",
            {
                "conversation_id": sid_pass,
                "text": "Independent review PASS of this change.",
            },
        )
        st_ok = json.loads(vg_path.read_text(encoding="utf-8"))
        results["tests"]["r20_capture_pass_with_reviews"] = finish_case(
            r_pass_ok,
            behavior=(
                (r_pass_ok.get("exit") == 0)
                and (st_ok.get(sid_pass) or {}).get("review_pass_ok") is True
            ),
            note="已有 reviews 且正文 PASS → review_pass_ok",
        )

    results["tests"]["sync_no_keyword"] = run_hook(
        "sync_on_prompt.py", {"prompt": "hello"}
    )
    results["tests"]["sync_no_keyword"]["behavior_pass"] = (
        results["tests"]["sync_no_keyword"].get("stdout") or {}
    ) == {}

    # codegraph 索引（软检查，不阻断 hook 测试）
    codegraph_dir = CLAUDE / ".codegraph"
    results["tests"]["codegraph_index"] = {
        "pass": True,
        "behavior_pass": codegraph_dir.is_dir(),
        "json_ok": True,
        "stdout": {"path": str(codegraph_dir), "exists": codegraph_dir.is_dir()},
        "note": "soft check: run codegraph init -i if missing",
    }
    if not codegraph_dir.is_dir():
        results["tests"]["codegraph_index"]["pass"] = True  # advisory only

    passed = sum(1 for t in results["tests"].values() if t.get("pass"))
    behavior_passed = sum(1 for t in results["tests"].values() if t.get("behavior_pass"))
    total = len(results["tests"])
    results["summary"] = {
        "json_exit": f"{passed}/{total} hooks returned valid JSON (exit 0)",
        "behavior": f"{behavior_passed}/{total} behavior assertions passed",
        "ok": behavior_passed == total,
    }

    report = json.dumps(results, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Report: {args.output}")
    print(report)

    return 0 if results["summary"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
