#!/usr/bin/env python3
"""防抖 + 调用 sync.ps1（Scope: rules|indexes|all）。"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

from config import load_guard_config, state_path
from impact_sync import SyncPlan, SyncScope


def _debounced(seconds: int) -> bool:
    debounce_file = state_path("last_sync.json")
    try:
        if not debounce_file.exists():
            return False
        data = json.loads(debounce_file.read_text(encoding="utf-8"))
        return (time.time() - data.get("ts", 0)) < seconds
    except (OSError, ValueError, json.JSONDecodeError):
        return False


def _mark_synced(scope: str, ok: bool) -> None:
    state_path("last_sync.json").write_text(
        json.dumps({"ts": time.time(), "scope": scope, "ok": ok}, indent=2),
        encoding="utf-8",
    )


def scope_to_ps1_arg(scope: SyncScope) -> str:
    if scope == SyncScope.RULES:
        return "rules"
    if scope == SyncScope.INDEXES:
        return "indexes"
    return "all"


def run_sync_plan(plan: SyncPlan, force: bool = False) -> tuple[bool, str]:
    cfg = load_guard_config()
    if not cfg["sync"]["auto_on_edit"] and not force:
        return False, "CURSOR_GUARD_AUTO_SYNC=0，已跳过"

    if plan.scope == SyncScope.NONE:
        hint = "; ".join(plan.messages) if plan.messages else "无需同步"
        return True, hint

    debounce = cfg["sync"]["debounce_seconds"]
    if not force and _debounced(debounce):
        return False, f"{debounce}s 内已同步，跳过"

    claude_home: Path = cfg["sync"]["claude_home"]
    sync_script = claude_home / "scripts" / "sync.ps1"
    if not sync_script.exists():
        return False, f"sync.ps1 不存在: {sync_script}"

    ps_scope = scope_to_ps1_arg(plan.scope)
    args = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(sync_script),
        "-Scope",
        ps_scope,
        "-Force",
    ]
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(claude_home),
        )
        ok = proc.returncode == 0
        if ok:
            _mark_synced(ps_scope, True)
            msg = f"已执行 sync.ps1 -Scope {ps_scope} -Force"
            if plan.changed:
                msg += f"（{plan.changed}）"
            if plan.messages:
                msg += "\n" + "\n".join(f"  • {m}" for m in plan.messages[:5])
            return True, msg
        err = (proc.stderr or proc.stdout or f"exit {proc.returncode}")[:400]
        return False, f"sync.ps1 失败: {err}"
    except subprocess.TimeoutExpired:
        return False, "sync.ps1 超时(120s)"
    except OSError as e:
        return False, f"sync.ps1 执行错误: {e}"


def run_full_sync(force: bool = True) -> tuple[bool, str]:
    plan = SyncPlan(scope=SyncScope.ALL, changed="explicit", messages=["显式全量同步"])
    return run_sync_plan(plan, force=force)
