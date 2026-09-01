# -*- coding: utf-8 -*-
"""graph_freshness 单元测试。直接运行：python hooks/tests/test_graph_freshness.py"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

HOOKS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HOOKS_DIR / "_lib"))

import graph_freshness as gf  # noqa: E402

PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASSED if cond else FAILED).append(name)
    mark = "OK " if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail and not cond else ""))


def test_eligible_and_empty_registry() -> None:
    with tempfile.TemporaryDirectory() as td:
        check("non-git not eligible", gf.is_eligible(td) is False)
        git = Path(td, "repo")
        git.mkdir()
        (git / ".git").mkdir()
        check("git eligible", gf.is_eligible(str(git)) is True)
        registry = Path(td, ".code-review-graph")
        registry.mkdir()
        check("empty registry not project graph", gf.has_crg_graph(str(git)) is False)
        (git / ".code-review-graph").mkdir()
        (git / ".code-review-graph" / "graph.db").write_bytes(b"")
        check("graph.db counts as CRG", gf.has_crg_graph(str(git)) is True)


def test_clean_fs_path() -> None:
    check("slash drive /d:", gf._clean_fs_path("/d:/apdms/pdms") == "d:/apdms/pdms")
    check(
        "file uri file:///d:",
        gf._clean_fs_path("file:///d:/apdms/pdms") == "d:/apdms/pdms",
    )
    check("plain windows path", gf._clean_fs_path("d:/apdms/pdms") == "d:/apdms/pdms")
    with tempfile.TemporaryDirectory() as td:
        git = Path(td, "repo")
        git.mkdir()
        (git / ".git").mkdir()
        abs_git = str(git.resolve())
        if os.name == "nt" and len(abs_git) >= 3 and abs_git[1] == ":":
            slash = "/" + abs_git[0] + ":" + abs_git[2:].replace("\\", "/")
            file_uri = "file:///" + abs_git[0] + ":" + abs_git[2:].replace("\\", "/")
            check(
                "find_git_root /X:",
                os.path.normcase(gf.find_git_root(slash)) == os.path.normcase(abs_git),
                slash,
            )
            check(
                "find_git_root file:///X:",
                os.path.normcase(gf.find_git_root(file_uri)) == os.path.normcase(abs_git),
                file_uri,
            )
            check(
                "find_git_root plain",
                os.path.normcase(gf.find_git_root(abs_git)) == os.path.normcase(abs_git),
            )


def test_codegraph_markers() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td, "r")
        root.mkdir()
        (root / ".git").mkdir()
        cg = root / ".codegraph"
        cg.mkdir()
        check("empty .codegraph dir is not index", gf.has_codegraph_index(str(root)) is False)
        (cg / "config.json").write_text("{}", encoding="utf-8")
        check("config.json marker is index", gf.has_codegraph_index(str(root)) is True)


def test_tool_classify() -> None:
    check(
        "build_or_update is build",
        gf.is_build_tool("mcp__code-review-graph__build_or_update_graph_tool") is True,
    )
    check(
        "explore is query",
        gf.is_query_mcp("mcp__codegraph__codegraph_explore") is True,
    )
    check("Grep is fallback", gf.is_explore_fallback("Grep") is True)
    check("Write is write", gf.is_write_tool("Write") is True)
    check(
        "shell init is build",
        gf.is_build_tool("Bash", {"command": "codegraph init -i"}) is True,
    )
    check(
        "should deny Grep when classifying",
        gf.should_deny_tool("Grep") is True,
    )
    check(
        "should not deny Read",
        gf.should_deny_tool("Read") is False,
    )
    check(
        "should not deny graph shell",
        gf.should_deny_tool("Bash", {"command": "code-review-graph build"}) is False,
    )
    check(
        "should deny shell grep",
        gf.should_deny_tool("Bash", {"command": "rg foo"}) is True,
    )


def test_ensure_cache_and_deny(monkey_cmds: list | None = None) -> None:
    calls: list[list] = []

    def fake_run(argv, cwd, timeout_sec):
        calls.append(list(argv))
        joined = " ".join(str(a) for a in argv)
        root = Path(cwd)
        if "init" in joined:
            (root / ".codegraph").mkdir(exist_ok=True)
            (root / ".codegraph" / "config.json").write_text("{}", encoding="utf-8")
        if "build" in joined:
            (root / ".code-review-graph").mkdir(exist_ok=True)
            (root / ".code-review-graph" / "graph.db").write_bytes(b"")
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    orig = gf.run_cmd
    gf.run_cmd = fake_run  # type: ignore[method-assign]
    orig_which = gf.which_tool
    gf.which_tool = lambda name: f"/bin/{name}"  # type: ignore[method-assign]
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td, "repo")
            root.mkdir()
            (root / ".git").mkdir()
            result = gf.ensure_both(str(root), 40, session_id="s1")
            check("ensure without CLI success mocked", result["ok"] is True, json.dumps(result))
            check("init/build invoked", any("init" in str(c) or "build" in str(c) for c in calls))
            check("session_ok after ensure", gf.session_ok(str(root), "s1") is True)
            data = {
                "cwd": str(root),
                "session_id": "s1",
                "tool_name": "Grep",
            }
            decision, payload = gf.pretool_decision(data, 10)
            check("Grep allowed after ok session", decision == "allow")
    finally:
        gf.run_cmd = orig  # type: ignore[method-assign]
        gf.which_tool = orig_which  # type: ignore[method-assign]


def test_deny_when_cli_missing() -> None:
    orig_which = gf.which_tool
    gf.which_tool = lambda name: None  # type: ignore[method-assign]
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td, "repo")
            root.mkdir()
            (root / ".git").mkdir()
            result = gf.ensure_both(str(root), 20, session_id="s2")
            check("missing CLI blocks", result["blocked"] is True)
            data = {"cwd": str(root), "session_id": "s2", "tool_name": "Grep"}
            decision, payload = gf.pretool_decision(data, 5)
            check("Grep denied when blocked", decision == "deny")
            check("deny payload present", payload is not None)
    finally:
        gf.which_tool = orig_which  # type: ignore[method-assign]


def test_existing_graph_cli_fail_is_warning() -> None:
    orig = gf.run_cmd
    orig_which = gf.which_tool

    def fake_fail(argv, cwd, timeout_sec):
        return SimpleNamespace(returncode=1, stdout="", stderr="Dependent expansion capped")

    gf.run_cmd = fake_fail  # type: ignore[method-assign]
    gf.which_tool = lambda name: f"/bin/{name}"  # type: ignore[method-assign]
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td, "repo")
            root.mkdir()
            (root / ".git").mkdir()
            cg = root / ".codegraph"
            cg.mkdir()
            (cg / "config.json").write_text("{}", encoding="utf-8")
            crg = root / ".code-review-graph"
            crg.mkdir()
            (crg / "graph.db").write_bytes(b"")
            result = gf.ensure_both(str(root), 20, session_id="s-exist")
            check(
                "existing graphs CLI fail still ok",
                result.get("ok") is True and result.get("blocked") is not True,
                json.dumps(result),
            )
            check("warning recorded", bool(result.get("warnings")))
            decision, _payload = gf.pretool_decision(
                {"cwd": str(root), "session_id": "s-exist", "tool_name": "Grep"},
                5,
            )
            check("Grep allowed when graphs exist despite CLI fail", decision == "allow")
    finally:
        gf.run_cmd = orig  # type: ignore[method-assign]
        gf.which_tool = orig_which  # type: ignore[method-assign]


def test_incremental_keeps_session_id() -> None:
    orig = gf.run_cmd
    orig_which = gf.which_tool

    def fake_run(argv, cwd, timeout_sec):
        joined = " ".join(str(a) for a in argv)
        root = Path(cwd)
        if "init" in joined or "sync" in joined:
            (root / ".codegraph").mkdir(exist_ok=True)
            (root / ".codegraph" / "config.json").write_text("{}", encoding="utf-8")
        if "build" in joined or "update" in joined:
            (root / ".code-review-graph").mkdir(exist_ok=True)
            (root / ".code-review-graph" / "graph.db").write_bytes(b"")
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    gf.run_cmd = fake_run  # type: ignore[method-assign]
    gf.which_tool = lambda name: f"/bin/{name}"  # type: ignore[method-assign]
    try:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td, "repo")
            root.mkdir()
            (root / ".git").mkdir()
            result = gf.ensure_both(str(root), 40, session_id="s1")
            check("ensure s1 ok", result["ok"] is True)
            gf.refresh_incremental([str(root)], 20, session_id="")
            check("session_ok s1 after incremental", gf.session_ok(str(root), "s1") is True)
            check("session_ok s2 false after incremental", gf.session_ok(str(root), "s2") is False)
            entry = gf.entry_for(str(root))
            check("incremental preserved session_id", entry.get("session_id") == "s1")
    finally:
        gf.run_cmd = orig  # type: ignore[method-assign]
        gf.which_tool = orig_which  # type: ignore[method-assign]


def test_sync_skip_env() -> None:
    os.environ["GRAPH_FRESHNESS_SKIP_SYNC"] = "1"
    try:
        ok, msg = gf.run_sync_ps1_if_verified(has_edits=True, verified_green=True)
        check("skip env blocks sync", ok is False and "跳过" in msg)
        ok2, msg2 = gf.run_sync_ps1_if_verified(has_edits=False, verified_green=True)
        check("no edits skips sync", ok2 is False)
        ok3, msg3 = gf.run_sync_ps1_if_verified(has_edits=True, verified_green=False)
        check("not green skips sync", ok3 is False)
    finally:
        os.environ.pop("GRAPH_FRESHNESS_SKIP_SYNC", None)

    calls: list[int] = []
    orig = gf.run_sync_ps1

    def fake_sync(timeout_sec=None):
        calls.append(1)
        return True, "ran"

    gf.run_sync_ps1 = fake_sync  # type: ignore[method-assign]
    try:
        ok4, _ = gf.run_sync_ps1_if_verified(has_edits=True, verified_green=False)
        check("skip-verify analog does not call pwsh", ok4 is False and calls == [])
        ok5, _ = gf.run_sync_ps1_if_verified(has_edits=True, verified_green=True)
        check("green calls sync once", ok5 is True and calls == [1])
    finally:
        gf.run_sync_ps1 = orig  # type: ignore[method-assign]


def test_resolve_cwd() -> None:
    saved_env = {
        key: os.environ.pop(key, None)
        for key in (
            "VSCODE_CWD",
            "CURSOR_PROJECT_DIR",
            "CURSOR_CWD",
            "CURSOR_WORKSPACE",
            "CURSOR_HOME",
        )
    }
    orig_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as td:
            git = Path(td, "repo")
            git.mkdir()
            (git / ".git").mkdir()
            hook_home = Path(td, "cursor-home")
            hook_home.mkdir()
            git_abs = str(git.resolve())
            hook_abs = str(hook_home.resolve())
            got = gf.resolve_cwd({"cwd": hook_abs, "workspace_roots": [git_abs]})
            check(
                "workspace_roots beats hook-home cwd",
                os.path.normcase(got) == os.path.normcase(git_abs),
                got,
            )
            os.chdir(git_abs)
            got2 = gf.resolve_cwd({"cwd": git_abs})
            check(
                "explicit git cwd wins",
                os.path.normcase(got2) == os.path.normcase(git_abs),
                got2,
            )
            got3 = gf.resolve_cwd({"workspace_roots": [git_abs]})
            check(
                "workspace_roots when cwd missing",
                os.path.normcase(got3) == os.path.normcase(git_abs),
                got3,
            )
            os.chdir(hook_abs)
            cursor_home = Path(td, "fake-cursor")
            proj = cursor_home / "projects" / "slug"
            proj.mkdir(parents=True)
            (proj / ".workspace-trusted").write_text(
                json.dumps({"workspacePath": git_abs}),
                encoding="utf-8",
            )
            os.environ["CURSOR_HOME"] = str(cursor_home)
            got4 = gf.resolve_cwd({})
            check(
                "empty payload infers cursor workspace-trusted",
                os.path.normcase(got4) == os.path.normcase(git_abs),
                got4,
            )
            got5 = gf.resolve_cwd({"workspace_roots": [hook_abs]})
            check(
                "nongit workspace_roots does not infer other git",
                os.path.normcase(os.path.abspath(got5)) == os.path.normcase(hook_abs),
                got5,
            )
            got6 = gf.resolve_cwd({"cwd": hook_abs})
            check(
                "explicit nongit cwd does not infer other git",
                os.path.normcase(os.path.abspath(got6)) == os.path.normcase(hook_abs),
                got6,
            )
            if os.name == "nt" and len(git_abs) >= 3 and git_abs[1] == ":":
                uri = "/" + git_abs[0] + ":" + git_abs[2:].replace("\\", "/")
                got_uri = gf.resolve_cwd({"workspace_roots": [uri]})
                check(
                    "windows /d: workspace_roots finds git",
                    os.path.normcase(got_uri) == os.path.normcase(git_abs),
                    f"uri={uri} got={got_uri}",
                )
                file_uri = "file:///" + git_abs[0] + ":" + git_abs[2:].replace("\\", "/")
                got_file = gf.find_git_root(file_uri)
                check(
                    "file:///d: find_git_root",
                    os.path.normcase(got_file) == os.path.normcase(git_abs),
                    got_file,
                )
            os.chdir(orig_cwd)
            fallback = gf.resolve_cwd({})
            check("empty payload uses process cwd if git", bool(fallback) and os.path.isdir(fallback))
    finally:
        os.chdir(orig_cwd)
        for key, val in saved_env.items():
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val


def test_dynamic_mcp_classify() -> None:
    from crg_track import collect_tool_names

    names = collect_tool_names(
        "CallDynamicTool",
        {"namespace": "user-codegraph", "toolName": "codegraph_explore"},
    )
    check("dynamic tool nested name", "codegraph_explore" in names)
    check(
        "query mcp dynamic explore",
        gf.is_query_mcp(
            "CallDynamicTool",
            {"namespace": "user-codegraph", "toolName": "codegraph_explore"},
        )
        is True,
    )
    check(
        "build mcp still build",
        gf.is_build_tool(
            "CallDynamicTool",
            {"toolName": "build_or_update_graph_tool"},
        )
        is True,
    )


def test_empty_cwd_still_gates_git_process_cwd() -> None:
    orig_which = gf.which_tool
    orig_cwd = os.getcwd()
    saved_env = {
        key: os.environ.pop(key, None)
        for key in ("VSCODE_CWD", "CURSOR_PROJECT_DIR", "CURSOR_CWD", "CURSOR_HOME", "CURSOR_WORKSPACE")
    }
    gf.which_tool = lambda name: None  # type: ignore[method-assign]
    td = tempfile.mkdtemp()
    try:
        root = Path(td, "repo")
        root.mkdir()
        (root / ".git").mkdir()
        os.chdir(root)
        data = {"session_id": "s-empty-cwd", "tool_name": "Grep"}
        decision, payload = gf.pretool_decision(data, 5)
        check("empty payload cwd still denies git cwd", decision == "deny")
        check("deny payload present for empty cwd", payload is not None)
    finally:
        os.chdir(orig_cwd)
        gf.which_tool = orig_which  # type: ignore[method-assign]
        for key, val in saved_env.items():
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val
        shutil.rmtree(td, ignore_errors=True)


def test_cfg_timeouts() -> None:
    cfg = gf.load_cfg()
    check("session timeout 120", int(cfg.get("session_ensure_timeout_sec")) == 120)
    check("pretool timeout 90", int(cfg.get("pretool_ensure_timeout_sec")) == 90)
    check("stop timeout 30", int(cfg.get("stop_refresh_timeout_sec")) == 30)
    check("sync timeout 120", int(cfg.get("sync_ps1_timeout_sec")) == 120)
    check("subproject discovery default on", cfg.get("subproject_discovery") is True)


def test_subprojects_depth1_no_grandchild() -> None:
    with tempfile.TemporaryDirectory() as td:
        parent = Path(td, "ws")
        parent.mkdir()
        child = parent / "app"
        child.mkdir()
        (child / ".git").mkdir()
        grand = child / "nested"
        grand.mkdir()
        (grand / ".git").mkdir()
        found, overflow = gf.list_child_git_repos(str(parent), max_children=8)
        check("nongit parent finds depth-1 child", any(Path(p).name == "app" for p in found))
        check("nongit parent does not find grandchild", all(Path(p).name != "nested" for p in found))
        roots, meta = gf.collect_project_roots(str(child), {"enabled": True, "subproject_discovery": True, "subproject_max_children": 8})
        names = {Path(p).name for p in roots}
        check("git child includes self", "app" in names, str(names))
        check("git child includes nested once", "nested" in names, str(names))
        nested_kids, _ov = gf.list_child_git_repos(str(grand), max_children=8)
        check("grandchild list is empty (no further nest)", nested_kids == [])
        banner = gf.format_ui_banner({"ok": True, "codegraph": True, "crg": True, "root": str(child)}, action="ensure")
        check("ui banner has 成功", "成功" in banner and "会话同步双图" in banner)
        fail = gf.format_ui_banner({"ok": False, "codegraph": False, "crg": False, "root": str(child), "error": "x"}, action="ensure")
        check("ui banner has 失败", "失败" in fail)


def test_merge_hooks_idempotent() -> None:
    import importlib.util

    merge_path = HOOKS_DIR.parent / "scripts" / "_merge_editor_graph_hooks.py"
    spec = importlib.util.spec_from_file_location("merge_editor_graph_hooks", merge_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    first = mod.merge_hooks_obj({}, mod._trae_groups())
    second = mod.merge_hooks_obj(first, mod._trae_groups())
    check("merge SessionStart once", len(second.get("SessionStart") or []) == 1)
    check("merge PreToolUse once", len(second.get("PreToolUse") or []) == 1)
    check("merge Stop once", len(second.get("Stop") or []) == 1)
    cmds = [
        h.get("command", "")
        for g in second.get("PreToolUse") or []
        for h in (g.get("hooks") or [])
    ]
    check(
        "pre-graph command present",
        any("pre-graph-freshness.py" in c for c in cmds),
    )


def main() -> int:
    print("test_graph_freshness")
    test_eligible_and_empty_registry()
    test_clean_fs_path()
    test_codegraph_markers()
    test_tool_classify()
    test_ensure_cache_and_deny()
    test_deny_when_cli_missing()
    test_existing_graph_cli_fail_is_warning()
    test_incremental_keeps_session_id()
    test_sync_skip_env()
    test_resolve_cwd()
    test_dynamic_mcp_classify()
    test_empty_cwd_still_gates_git_process_cwd()
    test_cfg_timeouts()
    test_subprojects_depth1_no_grandchild()
    test_merge_hooks_idempotent()
    print(f"\n{len(PASSED)} passed, {len(FAILED)} failed")
    if FAILED:
        print("FAILED:", ", ".join(FAILED))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
