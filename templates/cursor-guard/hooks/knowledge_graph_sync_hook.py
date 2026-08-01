#!/usr/bin/env python3
"""postToolUse / stop / sessionEnd: refresh codegraph knowledge graph.

SSOT: ~/.claude/hooks/_lib/knowledge_graph_sync.py
- Write|StrReplace: debounce sync
- stop / sessionEnd: force refresh
Fail-open: never break the agent; missing .codegraph is skip not error.
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


def _label(ok, skipped: list, missing_key: str, debounce_key: str) -> str:
    if missing_key in skipped or debounce_key in skipped:
        return "skip"
    if ok:
        return "ok"
    if ok is None:
        return "skip"
    return "fail"


def main() -> int:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        kg = cfg.get("knowledge_graph", {})
        if not kg.get("enabled", True):
            return 0
        if cfg.get("profile") == "minimal":
            return 0

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
            return 0

        cwd = data.get("cwd") or data.get("working_directory") or None
        root = resolve_project_root(cwd, file_path or None)
        result = sync_knowledge_graphs(
            root,
            force=force,
            run_codegraph=kg.get("codegraph", True),
            run_cbm=False,  # codebase-memory disabled
        )
        skipped = result.get("skipped") or []
        cg_res = result.get("codegraph") or {}
        cbm_res = result.get("cbm")

        cg_label = _label(
            cg_res.get("ok"),
            skipped,
            "codegraph_missing",
            "codegraph_debounce",
        )
        if cg_res.get("skipped"):
            cg_label = "skip"

        if cbm_res is None:
            cbm_label = "disabled"
        elif "cbm_debounce" in skipped:
            cbm_label = "skip"
        elif cbm_res.get("ok"):
            cbm_label = "ok"
        else:
            cbm_label = "fail"

        # Only emit stderr on real failures — Cursor Execution Log treats noisy
        # stderr as errors even when exit code is 0.
        if cg_label == "fail" or cbm_label == "fail":
            print(
                f"knowledge_graph_sync_hook: force={force} root={root} "
                f"codegraph={cg_label} cbm={cbm_label}",
                file=sys.stderr,
            )
        return 0
    except Exception as e:
        # Fail-open: log and continue agent
        print(f"knowledge_graph_sync_hook: {e}", file=sys.stderr)
        return 0
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    raise SystemExit(main())