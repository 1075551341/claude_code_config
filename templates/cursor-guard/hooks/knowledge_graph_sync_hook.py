#!/usr/bin/env python3
"""postToolUse / stop / sessionEnd: 刷新 codegraph + codebase-memory 知识图谱。

复用 ~/.claude/hooks/_lib/knowledge_graph_sync.py（SSOT）。
- Write|StrReplace：debounce 增量
- stop / sessionEnd：force 全量刷新（保证下次查询最新）
"""
from __future__ import annotations

import sys
from pathlib import Path

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    extract_file_path,
    read_stdin,
    setup_stdio,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config  # noqa: E402


def _import_kg_sync(claude_home: Path):
    lib = claude_home / "hooks" / "_lib"
    if str(lib) not in sys.path:
        sys.path.insert(0, str(lib))
    from knowledge_graph_sync import (  # noqa: WPS433
        resolve_project_root,
        should_trigger_for_file,
        sync_knowledge_graphs,
    )

    return resolve_project_root, should_trigger_for_file, sync_knowledge_graphs


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        kg = cfg.get("knowledge_graph", {})
        if not kg.get("enabled", True):
            return
        if cfg.get("profile") == "minimal":
            return

        claude_home = Path(cfg["sync"]["claude_home"])
        resolve_project_root, should_trigger_for_file, sync_knowledge_graphs = _import_kg_sync(
            claude_home
        )

        event = str(data.get("hook_event_name") or data.get("event") or "").lower()
        force = (
            "--force" in sys.argv
            or event in ("stop", "sessionend", "session_end")
            or bool(data.get("force"))
        )

        file_path = extract_file_path(data) or ""
        if not force and file_path and not should_trigger_for_file(file_path):
            return

        cwd = data.get("cwd") or data.get("working_directory") or None
        root = resolve_project_root(cwd, file_path or None)
        result = sync_knowledge_graphs(
            root,
            force=force,
            run_codegraph=kg.get("codegraph", True),
            run_cbm=False,  # codebase-memory 已禁用
        )
        cg = (result.get("codegraph") or {}).get("ok")
        cbm_res = result.get("cbm")
        skipped = result.get("skipped") or []
        if cbm_res is None:
            cbm_label = "disabled"
        elif cbm_res.get("ok"):
            cbm_label = "ok"
        elif "cbm_debounce" in skipped:
            cbm_label = "skip"
        else:
            cbm_label = "fail"
        cg_label = (
            "ok" if cg else ("skip" if "codegraph_debounce" in skipped else "fail")
        )
        print(
            f"knowledge_graph_sync_hook: force={force} root={root} "
            f"codegraph={cg_label} cbm={cbm_label}",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"knowledge_graph_sync_hook: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
