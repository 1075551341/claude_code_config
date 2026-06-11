#!/usr/bin/env python3
"""Cursor Guard hook 本地模拟测试（stdin → hook，校验 JSON + 行为断言）。"""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
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

    with state_backup([counter, cursor_ctx, handoff, last_sess, pending_path, digest_path]):
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
        r_stop70 = run_hook("context_stop.py", {})
        results["tests"]["context_stop_70pct"] = finish_case(
            r_stop70,
            behavior="additional_context" in (r_stop70.get("stdout") or {})
            and "70" in stdout_text(r_stop70),
            note="isolated: no compress-pending",
        )

        counter.write_text(json.dumps({"count": 80, "est_tokens": 180000}), encoding="utf-8")
        r_stop90 = run_hook("context_stop.py", {})
        results["tests"]["context_stop_90pct"] = finish_case(
            r_stop90,
            behavior="followup_message" in (r_stop90.get("stdout") or {})
            and "/summarize" in stdout_text(r_stop90),
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
            and "codegraph 优先" in stdout_text(r_sb_new),
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
        and "codegraph 优先" in stdout_text(r_sb),
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
