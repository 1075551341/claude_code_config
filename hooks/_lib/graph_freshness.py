#!/usr/bin/env python3
"""图谱保鲜（codegraph + CRG）— 双端/多端共用（v11.4.6）。

SessionStart 真正 init/update；无图 blocked → PreToolUse deny。
Stop 增量刷新；仅验证全绿后跑 sync.ps1。
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import time

from crg_track import collect_tool_names, find_crg_root, is_crg_tool, is_project_graph_dir

STATE_NAME = "graph-freshness.json"
CODEGRAPH_MARKERS = (
    "index.sqlite",
    "graph.db",
    "codegraph.db",
    "daemon.pid",
    "config.json",
)
BUILD_MARKERS = (
    "build_or_update",
    "run_postprocess",
    "embed_graph",
)
WRITE_TOOLS = {
    "edit",
    "write",
    "multiedit",
    "strreplace",
    "delete",
    "editnotebook",
}
EXPLORE_FALLBACK = {"grep", "glob"}
GRAPH_SHELL_RE = re.compile(
    r"\b(codegraph|code-review-graph)\b",
    re.I,
)
GRAPH_SHELL_ACTION_RE = re.compile(
    r"\b(init|sync|index|build|update)\b",
    re.I,
)
SHELL_GREP_RE = re.compile(r"\b(grep|rg|findstr|git\s+grep)\b", re.I)

DEFAULT_CFG = {
    "enabled": True,
    "session_ensure_timeout_sec": 120,
    "pretool_ensure_timeout_sec": 90,
    "stop_refresh_timeout_sec": 30,
    "sync_ps1_timeout_sec": 120,
    "require_both_graphs": True,
    "subproject_discovery": True,
    "subproject_max_children": 8,
}

# 发现子 git 时跳过的目录名。禁止走进图谱目录，避免「图的图」。
DISCOVERY_EXCLUDE = {
    "node_modules",
    "dist",
    "build",
    "out",
    "venv",
    ".venv",
    ".git",
    ".claude",
    ".cloud",
    ".codegraph",
    ".code-review-graph",
    "vendor",
    "target",
    ".tox",
    "__pycache__",
    "site-packages",
    ".next",
    ".nuxt",
    "coverage",
}

DENY_MSG = (
    "【图谱保鲜硬门】eligible git 仓必须先有 codegraph 与 code-review-graph，"
    "且本次已同步更新。SessionStart/本调用已尝试 init|sync / build|update，仍无图或失败。"
    "禁止 Grep/Glob/编辑/查询类 MCP。请安装 CLI 后执行："
    " `codegraph init -i` 与 `code-review-graph build`（或 MCP build_or_update_graph_tool）。"
)


def claude_home() -> str:
    return os.path.normpath(os.path.expanduser(os.environ.get("CLAUDE_HOME") or "~/.claude"))


def state_path() -> str:
    return os.path.join(claude_home(), ".state", STATE_NAME)


def config_path() -> str:
    return os.path.join(claude_home(), "config", "quality_gates.json")


def load_cfg() -> dict:
    cfg = dict(DEFAULT_CFG)
    path = config_path()
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as fh:
                user = json.load(fh).get("graph_freshness") or {}
            if isinstance(user, dict):
                for key in cfg:
                    if key in user:
                        cfg[key] = user[key]
    except (OSError, json.JSONDecodeError) as exc:
        print(f"graph_freshness: config read failed: {exc}", file=sys.stderr)
    return cfg


def cwd_key(cwd: str) -> str:
    return os.path.normcase(os.path.abspath(cwd or "")).replace("\\", "/")


_PATH_KEYS = (
    "cwd",
    "working_directory",
    "workspace_path",
    "project_path",
    "projectPath",
    "repo_root",
    "file_path",
    "path",
    "target_file",
)
_ENV_KEYS = (
    "CURSOR_PROJECT_DIR",
    "CURSOR_CWD",
    "VSCODE_CWD",
    "CURSOR_WORKSPACE",
)


def _clean_fs_path(val: str) -> str:
    s = (val or "").strip().strip('"')
    if not s:
        return ""
    if s.startswith("file://"):
        s = s[7:]
        if s.startswith("/") and len(s) >= 3 and s[2] == ":":
            s = s[1:]
    return s


def _add_candidate(out: list[str], val) -> None:
    if isinstance(val, str):
        cleaned = _clean_fs_path(val)
        if cleaned:
            out.append(cleaned)
        return
    if isinstance(val, dict):
        for key in ("path", "uri", "folder", "root"):
            _add_candidate(out, val.get(key))


def _workspace_root_candidates(data: dict) -> list[str]:
    out: list[str] = []
    roots = data.get("workspace_roots")
    if isinstance(roots, str):
        _add_candidate(out, roots)
    elif isinstance(roots, list):
        for item in roots:
            _add_candidate(out, item)
    return out


def _nested_path_candidates(data: dict) -> list[str]:
    out: list[str] = []
    blobs = [data]
    for key in ("tool_input", "arguments", "input"):
        blob = data.get(key)
        if isinstance(blob, dict):
            blobs.append(blob)
            nested = blob.get("arguments")
            if isinstance(nested, dict):
                blobs.append(nested)
    for blob in blobs:
        for key in _PATH_KEYS:
            _add_candidate(out, blob.get(key))
    return out


def _first_git(candidates: list[str]) -> str:
    seen: set[str] = set()
    for raw in candidates:
        if not raw:
            continue
        key = cwd_key(raw)
        if key in seen:
            continue
        seen.add(key)
        root = find_git_root(raw)
        if root:
            return root
    return ""


def infer_editor_workspace(cursor_home: str | None = None) -> str:
    """Cursor 用户级 hook 进程 cwd 是 ~/.cursor（非 git）。从编辑器状态还原工作区。

    优先最新 `.workspace-trusted`；recentlyViewedFiles 仅当其 git 根落在已信任工作区内。
    """
    home = cursor_home or os.environ.get("CURSOR_HOME") or os.path.join(
        os.path.expanduser("~"), ".cursor"
    )
    viewed: list[str] = []
    trusted: list[str] = []
    ide = os.path.join(home, "ide_state.json")
    try:
        if os.path.isfile(ide):
            with open(ide, "r", encoding="utf-8-sig") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                for item in data.get("recentlyViewedFiles") or []:
                    if isinstance(item, dict):
                        _add_candidate(viewed, item.get("absolutePath"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"graph_freshness: ide_state read failed: {exc}", file=sys.stderr)

    proj = os.path.join(home, "projects")
    try:
        if os.path.isdir(proj):
            kids = [
                os.path.join(proj, name)
                for name in os.listdir(proj)
                if os.path.isdir(os.path.join(proj, name))
            ]
            kids.sort(key=lambda p: os.path.getmtime(p), reverse=True)
            for child in kids:
                trusted_file = os.path.join(child, ".workspace-trusted")
                if not os.path.isfile(trusted_file):
                    continue
                try:
                    with open(trusted_file, "r", encoding="utf-8-sig") as fh:
                        data = json.load(fh)
                except (OSError, json.JSONDecodeError) as exc:
                    print(
                        f"graph_freshness: workspace-trusted read failed: {exc}",
                        file=sys.stderr,
                    )
                    continue
                if isinstance(data, dict):
                    _add_candidate(trusted, data.get("workspacePath"))
    except OSError as exc:
        print(f"graph_freshness: cursor projects scan failed: {exc}", file=sys.stderr)
    found = _first_git(trusted)
    if found:
        return found
    trusted_keys = {cwd_key(find_git_root(p)) for p in trusted if find_git_root(p)}
    for path in viewed:
        root = find_git_root(path)
        if root and (not trusted_keys or cwd_key(root) in trusted_keys):
            return root
    return ""


def resolve_cwd(data: dict | None = None) -> str:
    """Resolve git workspace. Prefer workspace_roots over hook-home cwd.

    Cursor 用户级 hook 的进程 cwd / payload.cwd 经常是 ~/.cursor（非 git）。
    官方公共字段是 workspace_roots；先选 git-eligible，再回退编辑器状态。
    """
    data = data or {}
    workspace_roots = _workspace_root_candidates(data)
    nested = _nested_path_candidates(data)
    env_paths: list[str] = []
    for env_key in _ENV_KEYS:
        val = os.environ.get(env_key)
        if val and val.strip():
            env_paths.append(val.strip())
    try:
        proc = os.getcwd()
    except OSError:
        proc = ""

    found = _first_git(workspace_roots)
    if found:
        return found
    if workspace_roots:
        # 当前窗口已声明且全非 git：禁止 infer 到另一个仓
        for raw in workspace_roots:
            try:
                if raw and os.path.isdir(raw):
                    return raw
            except OSError:
                continue
        return workspace_roots[0]
    payload_cwds: list[str] = []
    if isinstance(data, dict):
        for key in ("cwd", "working_directory", "workspace_path"):
            _add_candidate(payload_cwds, data.get(key))
    found = _first_git(payload_cwds)
    if found:
        return found
    if payload_cwds:
        for raw in payload_cwds:
            try:
                if raw and os.path.isdir(raw):
                    return raw
            except OSError:
                continue
        return payload_cwds[0]
    found = _first_git(env_paths)
    if found:
        return found
    proc_key = cwd_key(proc) if proc else ""
    found = _first_git([p for p in nested if cwd_key(p) != proc_key])
    if found:
        return found
    found = _first_git(([proc] if proc else []) + nested)
    if found:
        return found
    found = infer_editor_workspace()
    if found:
        return found
    for raw in workspace_roots + nested + env_paths + ([proc] if proc else []):
        try:
            if raw and os.path.isdir(raw):
                return raw
        except OSError:
            continue
    return proc


def load_state() -> dict:
    path = state_path()
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return data
    except (OSError, json.JSONDecodeError) as exc:
        print(f"graph_freshness: state read failed: {exc}", file=sys.stderr)
    return {"by_cwd": {}}


def save_state(state: dict) -> None:
    path = state_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"graph_freshness: state write failed: {exc}", file=sys.stderr)


def entry_for(cwd: str, state: dict | None = None) -> dict:
    st = state if state is not None else load_state()
    return dict((st.get("by_cwd") or {}).get(cwd_key(cwd)) or {})


def _put_entry(cwd: str, entry: dict) -> None:
    st = load_state()
    by_cwd = st.setdefault("by_cwd", {})
    by_cwd[cwd_key(cwd)] = entry
    save_state(st)


def find_git_root(start: str, max_up: int = 8) -> str:
    probe = os.path.abspath(start or "") if start else ""
    if not probe:
        return ""
    for _ in range(max_up):
        git = os.path.join(probe, ".git")
        if os.path.isdir(git) or os.path.isfile(git):
            return probe
        parent = os.path.dirname(probe)
        if parent == probe:
            break
        probe = parent
    return ""


def is_eligible(cwd: str) -> bool:
    return bool(find_git_root(cwd))


def _discovery_blocked(cwd: str) -> bool:
    """禁止从 $HOME / 盘符根做子项目扫描（会扫到无穷仓库）。"""
    if not cwd:
        return True
    try:
        probe = os.path.normcase(os.path.abspath(cwd))
        home = os.path.normcase(os.path.abspath(os.path.expanduser("~")))
    except OSError:
        return True
    if probe == home:
        return True
    parent = os.path.dirname(home.rstrip("\\/"))
    if parent and probe == os.path.normcase(parent):
        return True
    rest = probe.rstrip("\\/")
    if len(rest) <= 3 and ":" in rest:
        return True
    return False


def _safe_under(parent: str, child: str) -> bool:
    """子路径必须落在父目录 realpath 下，挡住符号链接逃逸/自环。"""
    try:
        real_p = os.path.normcase(os.path.realpath(parent))
        real_c = os.path.normcase(os.path.realpath(child))
    except OSError:
        return False
    if real_c == real_p:
        return False
    prefix = real_p.rstrip("\\/") + os.sep
    return real_c.startswith(prefix)


def list_child_git_repos(parent: str, *, max_children: int = 8) -> tuple[list[str], int]:
    """只扫 depth-1 子目录里的独立 git 根。不递归、不走进图谱目录。

    返回 (roots, overflow_count)。overflow>0 表示还有子仓被封顶丢掉，
    绝不继续向下发现孙项目——这是防无穷嵌套同步的硬保证。
    """
    found: list[str] = []
    overflow = 0
    if not parent or _discovery_blocked(parent):
        return found, 0
    try:
        names = sorted(os.listdir(parent))
    except OSError:
        return found, 0
    cap = max(1, int(max_children))
    for name in names:
        if name in DISCOVERY_EXCLUDE or name.startswith("."):
            continue
        child = os.path.join(parent, name)
        try:
            if not os.path.isdir(child) or not _safe_under(parent, child):
                continue
            git = os.path.join(child, ".git")
            if not (os.path.isdir(git) or os.path.isfile(git)):
                continue
        except OSError:
            continue
        if len(found) >= cap:
            overflow += 1
            continue
        found.append(os.path.abspath(child))
    return found, overflow


def collect_project_roots(cwd: str, cfg: dict | None = None) -> tuple[list[str], dict]:
    """工作区要同步的 git 根列表：自身（若是 git）+ depth-1 子仓。

    子仓再发现被禁止：每个根交给 ensure_root，ensure_root 不再 collect。
    """
    cfg = cfg or load_cfg()
    meta = {"overflow": 0, "discovery_blocked": False}
    if not cfg.get("enabled", True):
        return [], meta
    discover = bool(cfg.get("subproject_discovery", True))
    max_children = max(1, int(cfg.get("subproject_max_children", 8)))
    root = find_git_root(cwd)
    if not discover:
        return ([root] if root else []), meta
    if _discovery_blocked(cwd or ""):
        meta["discovery_blocked"] = True
        return ([root] if root else []), meta
    scan = root or (os.path.abspath(cwd) if cwd else "")
    kids, overflow = list_child_git_repos(scan, max_children=max_children)
    meta["overflow"] = overflow
    ordered: list[str] = []
    seen: set[str] = set()
    for path in ([root] if root else []) + kids:
        key = cwd_key(path)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(path)
    return ordered, meta


def _has_codegraph_markers(cg_dir: str) -> bool:
    if not os.path.isdir(cg_dir):
        return False
    if any(os.path.isfile(os.path.join(cg_dir, name)) for name in CODEGRAPH_MARKERS):
        return True
    try:
        entries = [f for f in os.listdir(cg_dir) if f not in (".gitignore", "daemon.log")]
    except OSError:
        return False
    return bool(entries)


def find_codegraph_root(start: str, max_up: int = 8) -> str:
    """Look for `.codegraph/` from cwd up to the git root only (never into $HOME)."""
    probe = os.path.abspath(start or "") if start else ""
    if not probe:
        return ""
    git = find_git_root(probe, max_up)
    for _ in range(max_up):
        if _has_codegraph_markers(os.path.join(probe, ".codegraph")):
            return probe
        if git and os.path.normcase(probe) == os.path.normcase(git):
            break
        parent = os.path.dirname(probe)
        if parent == probe:
            break
        probe = parent
    return ""


def has_codegraph_index(cwd: str) -> bool:
    return bool(find_codegraph_root(cwd))


def has_crg_graph(cwd: str) -> bool:
    return bool(find_crg_root(cwd))


def graphs_present(cwd: str) -> tuple[bool, bool]:
    return has_codegraph_index(cwd), has_crg_graph(cwd)


def which_tool(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    if os.name == "nt":
        for ext in (".cmd", ".bat", ".exe"):
            found = shutil.which(name + ext)
            if found:
                return found
    return None


def run_cmd(argv: list, cwd: str, timeout_sec: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        argv,
        cwd=cwd or None,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
    )


def _run_named(name: str, args: list[str], cwd: str, timeout_sec: int) -> tuple[bool, str]:
    exe = which_tool(name)
    if not exe:
        return False, f"{name} CLI 未找到（PATH）"
    try:
        proc = run_cmd([exe, *args], cwd, timeout_sec)
    except subprocess.TimeoutExpired:
        return False, f"{name} {' '.join(args)} 超时（{timeout_sec}s）"
    except OSError as exc:
        return False, f"{name} 执行失败: {exc}"
    if proc.returncode != 0:
        err = ((proc.stderr or "") + (proc.stdout or "")).strip()[:400]
        return False, f"{name} {' '.join(args)} 非零退出: {err or proc.returncode}"
    return True, ""


def ensure_codegraph(root: str, timeout_sec: int, incremental_only: bool = False) -> tuple[bool, str]:
    if has_codegraph_index(root):
        ok, err = _run_named("codegraph", ["sync"], root, timeout_sec)
        if ok:
            return True, ""
        if which_tool("codegraph") is None:
            return True, "codegraph CLI 缺失，已有索引：跳过 sync"
        return False, err
    if incremental_only:
        return False, "无 .codegraph 索引（Stop 仅增量，不 init）"
    return _run_named("codegraph", ["init", "-i"], root, timeout_sec)


def ensure_crg(root: str, timeout_sec: int, incremental_only: bool = False) -> tuple[bool, str]:
    if has_crg_graph(root):
        found = find_crg_root(root) or root
        ok, err = _run_named("code-review-graph", ["update"], found, timeout_sec)
        if ok:
            return True, ""
        if which_tool("code-review-graph") is None:
            return True, "code-review-graph CLI 缺失，已有 graph.db：跳过 update"
        return False, err
    if incremental_only:
        return False, "无 CRG graph.db（Stop 仅增量，不 build）"
    return _run_named("code-review-graph", ["build"], root, timeout_sec)


def ensure_root(
    root: str,
    timeout_sec: int,
    *,
    incremental_only: bool = False,
    session_id: str = "",
    require_both: bool | None = None,
) -> dict:
    """只处理一个 git 根：不发现子项目、不向上建图。"""
    mode = "refresh" if incremental_only else "ensure"
    result = {
        "eligible": True,
        "ok": True,
        "blocked": False,
        "codegraph": False,
        "crg": False,
        "root": root,
        "project": os.path.basename(os.path.normpath(root)) or root,
        "warnings": [],
        "error": "",
        "skipped": False,
        "mode": mode,
    }
    cfg = load_cfg()
    require_both = bool(cfg.get("require_both_graphs", True) if require_both is None else require_both)
    prev = entry_for(root)
    sid = session_id or str(prev.get("session_id") or "")
    half = max(20, int(timeout_sec) // 2)
    cg_ok, cg_err = ensure_codegraph(root, half, incremental_only)
    crg_ok, crg_err = ensure_crg(root, half, incremental_only)
    result["codegraph"] = has_codegraph_index(root)
    result["crg"] = has_crg_graph(root)
    warnings = []
    if cg_err:
        warnings.append(cg_err)
    if crg_err:
        warnings.append(crg_err)
    result["warnings"] = warnings
    if require_both:
        result["ok"] = bool(result["codegraph"] and result["crg"] and cg_ok and crg_ok)
    else:
        result["ok"] = bool((result["codegraph"] and cg_ok) or (result["crg"] and crg_ok))
    if incremental_only and result["codegraph"] and result["crg"]:
        result["ok"] = True
    result["blocked"] = result["eligible"] and not result["ok"]
    if result["blocked"]:
        result["error"] = "; ".join(warnings) or "图谱 ensure 失败"
    _put_entry(
        root,
        {
            "ok": result["ok"],
            "blocked": result["blocked"],
            "codegraph": result["codegraph"],
            "crg": result["crg"],
            "ts": time.time(),
            "session_id": sid,
            "error": result["error"],
            "incremental_only": incremental_only,
        },
    )
    return result


def _failed_root(root: str, mode: str, error: str) -> dict:
    return {
        "eligible": True,
        "ok": False,
        "blocked": True,
        "codegraph": False,
        "crg": False,
        "root": root,
        "project": os.path.basename(os.path.normpath(root)) or root,
        "warnings": [],
        "error": error,
        "skipped": False,
        "mode": mode,
    }


def _attach_ui(result: dict, *, action: str) -> dict:
    result["ui"] = format_ui_banner(result, action=action)
    return result


def ensure_both(
    cwd: str,
    timeout_sec: int,
    *,
    incremental_only: bool = False,
    session_id: str = "",
) -> dict:
    """同步工作区双图：git 根自身 + depth-1 子仓；子仓不再向下发现。"""
    mode = "refresh" if incremental_only else "ensure"
    action = "refresh" if incremental_only else "ensure"
    result = {
        "eligible": False,
        "ok": True,
        "blocked": False,
        "codegraph": False,
        "crg": False,
        "root": "",
        "warnings": [],
        "error": "",
        "skipped": False,
        "mode": mode,
        "results": [],
        "discovered": [],
        "overflow": 0,
    }
    cfg = load_cfg()
    if not cfg.get("enabled", True):
        result["skipped"] = True
        result["root"] = cwd or ""
        return _attach_ui(result, action=action)
    projects, meta = collect_project_roots(cwd, cfg)
    result["overflow"] = int(meta.get("overflow") or 0)
    if not projects:
        result["skipped"] = True
        result["root"] = cwd or ""
        return _attach_ui(result, action=action)
    result["eligible"] = True
    result["root"] = projects[0]
    result["discovered"] = [os.path.basename(os.path.normpath(p)) for p in projects]
    per = max(20, int(timeout_sec) // max(1, len(projects)))
    results: list[dict] = []
    if len(projects) == 1:
        results.append(
            ensure_root(
                projects[0],
                per,
                incremental_only=incremental_only,
                session_id=session_id,
            )
        )
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(3, len(projects))) as pool:
            futures = {
                pool.submit(
                    ensure_root,
                    path,
                    per,
                    incremental_only=incremental_only,
                    session_id=session_id,
                ): path
                for path in projects
            }
            for future in concurrent.futures.as_completed(futures):
                path = futures[future]
                try:
                    results.append(future.result())
                except Exception as exc:
                    results.append(_failed_root(path, mode, f"子项目执行异常: {exc}"))
        results.sort(key=lambda item: str(item.get("root") or ""))
    result["results"] = results
    result["codegraph"] = all(bool(item.get("codegraph")) for item in results)
    result["crg"] = all(bool(item.get("crg")) for item in results)
    result["warnings"] = [w for item in results for w in (item.get("warnings") or [])]
    if result["overflow"]:
        result["warnings"].append(
            f"子项目已封顶 {cfg.get('subproject_max_children', 8)} 个，另有 {result['overflow']} 个未同步（禁止再向下嵌套）"
        )
    result["ok"] = all(bool(item.get("ok")) for item in results)
    result["blocked"] = any(bool(item.get("blocked")) for item in results)
    if result["blocked"]:
        result["error"] = (
            "; ".join(item.get("error") or "" for item in results if item.get("error"))
            or "图谱 ensure 失败"
        )
    if len(results) == 1:
        one = results[0]
        result["root"] = one.get("root") or result["root"]
        result["codegraph"] = bool(one.get("codegraph"))
        result["crg"] = bool(one.get("crg"))
        result["ok"] = bool(one.get("ok"))
        result["blocked"] = bool(one.get("blocked"))
        result["error"] = one.get("error") or result.get("error") or ""
    return _attach_ui(result, action=action)


def session_ok(cwd: str, session_id: str = "") -> bool:
    cfg = load_cfg()
    projects, _meta = collect_project_roots(cwd, cfg)
    if not projects:
        return False
    for root in projects:
        entry = entry_for(root)
        if not entry.get("ok"):
            return False
        if session_id and entry.get("session_id") and entry.get("session_id") != session_id:
            return False
        cg, crg = graphs_present(root)
        if cfg.get("require_both_graphs", True):
            if not (cg and crg):
                return False
        elif not (cg or crg):
            return False
    return True


def format_ui_banner(result: dict, *, action: str = "ensure") -> str:
    """会话界面一行：成功/失败都显式写出（非日志）。"""
    verb = "会话同步双图" if action == "ensure" else "收尾刷新双图"
    results = result.get("results") or []
    if result.get("skipped") and not results:
        where = result.get("root") or ""
        extra = f" @ {where}" if where else ""
        return f"【{verb}】跳过：非 git 仓或已关闭{extra}"
    overflow = int(result.get("overflow") or 0)
    cap_note = f"；子项目已封顶，另有 {overflow} 个未再嵌套同步" if overflow else ""
    if len(results) > 1:
        bits = []
        for item in results:
            name = item.get("project") or os.path.basename(str(item.get("root") or "")) or "?"
            bits.append(f"{name}={'成功' if item.get('ok') else '失败'}")
        status = "成功" if result.get("ok") else "失败"
        return f"【{verb}】{status}：{'；'.join(bits)}{cap_note}"
    cg = "有" if result.get("codegraph") else "无"
    crg = "有" if result.get("crg") else "无"
    loc = f" @ {result.get('root')}" if result.get("root") else ""
    if result.get("ok"):
        return f"【{verb}】成功：codegraph={cg} CRG={crg}{loc}{cap_note}"
    warn = "; ".join(result.get("warnings") or [])[:300]
    err = result.get("error") or warn or "ensure 失败"
    return f"【{verb}】失败：codegraph={cg} CRG={crg}{loc}。{err}{cap_note}"


def format_status(result: dict) -> str:
    if result.get("skipped") and not (result.get("results") or []):
        where = result.get("root") or ""
        extra = f"（cwd={where}）" if where else ""
        return f"图谱保鲜：非 git 仓或已关闭，跳过{extra}"
    results = result.get("results") or []
    if len(results) > 1:
        return format_ui_banner(
            result, action="refresh" if result.get("mode") == "refresh" else "ensure"
        )
    if result.get("ok"):
        return (
            f"✅ 图谱就绪（codegraph={'有' if result.get('codegraph') else '无'} "
            f"CRG={'有' if result.get('crg') else '无'} @ {result.get('root')}）"
        )
    warn = "; ".join(result.get("warnings") or [])[:500]
    return f"⛔ 图谱未就绪，禁止后续探索/编辑。{warn}"


def take_ui_slot(session_id: str, kind: str) -> bool:
    """每种 UI 提示每会话只占一次（Stop 刷新用）。SessionStart 不调用。"""
    sid = (session_id or "").strip()
    if not sid:
        return True
    st = load_state()
    shown = st.setdefault("ui_shown", {})
    key = f"{sid}:{kind}"
    if shown.get(key):
        return False
    shown[key] = time.time()
    cutoff = time.time() - 7 * 24 * 3600
    st["ui_shown"] = {k: v for k, v in shown.items() if isinstance(v, (int, float)) and v >= cutoff}
    save_state(st)
    return True


def _norm_tool(name: str) -> str:
    return (name or "").lower().replace("-", "_")


def is_build_tool(tool_name: str, tool_input=None, command: str = "") -> bool:
    cmd = command or extract_shell_command(tool_input)
    if cmd and GRAPH_SHELL_RE.search(cmd) and GRAPH_SHELL_ACTION_RE.search(cmd):
        return True
    for name in collect_tool_names(tool_name, tool_input):
        n = _norm_tool(name)
        if any(m in n for m in BUILD_MARKERS):
            return True
    return False


def is_query_mcp(tool_name: str, tool_input=None) -> bool:
    names = collect_tool_names(tool_name, tool_input)
    if _norm_tool(tool_name) in {"callmcptool", "call_mcp_tool"}:
        names = names + [tool_name]
    for name in names:
        n = _norm_tool(name)
        if any(m in n for m in BUILD_MARKERS):
            continue
        if "codegraph" in n:
            return True
        if "code_review_graph" in n or "code-review-graph" in (name or "").lower():
            return True
        if is_crg_tool(name):
            return True
    return False


def is_write_tool(tool_name: str) -> bool:
    n = _norm_tool(tool_name)
    if n in WRITE_TOOLS:
        return True
    if "mcp__serena" in n or "mcp_serena" in n or "mcp__fs" in n or "mcp_fs" in n:
        return True
    return False


def is_explore_fallback(tool_name: str) -> bool:
    return _norm_tool(tool_name) in EXPLORE_FALLBACK


def extract_shell_command(tool_input) -> str:
    if not isinstance(tool_input, dict):
        return ""
    for key in ("command", "shell_command"):
        val = tool_input.get(key)
        if isinstance(val, str) and val.strip():
            return val
    return ""


def should_deny_tool(tool_name: str, tool_input=None) -> bool:
    """True when this tool must not run while graphs are blocked."""
    cmd = extract_shell_command(tool_input)
    if is_build_tool(tool_name, tool_input, cmd):
        return False
    n = _norm_tool(tool_name)
    if n in {"bash", "runcommand", "shell"}:
        if cmd and GRAPH_SHELL_RE.search(cmd) and GRAPH_SHELL_ACTION_RE.search(cmd):
            return False
        if cmd and SHELL_GREP_RE.search(cmd):
            return True
        return False
    if is_explore_fallback(tool_name):
        return True
    if is_write_tool(tool_name):
        return True
    if is_query_mcp(tool_name, tool_input):
        return True
    return False


def detect_platform(data: dict) -> str:
    env = os.environ
    if env.get("CURSOR_APP_VERSION") or env.get("CURSOR_CHANNEL"):
        return "cursor"
    if env.get("TRAE_ENV_FILE") or "trae" in (env.get("TERM_PROGRAM") or "").lower():
        return "trae"
    tool = str(data.get("tool_name") or data.get("tool") or "")
    if tool == "RunCommand":
        return "trae"
    if tool in {"StrReplace", "CallMcpTool", "CallDynamicTool"}:
        return "cursor"
    return "claude"


def deny_payload(msg: str, platform: str) -> dict:
    if platform == "cursor":
        return {
            "permission": "deny",
            "user_message": "已拦截：图谱未就绪",
            "agent_message": msg,
        }
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": msg,
            "additionalContext": msg,
        }
    }


def pretool_decision(data: dict, timeout_sec: int | None = None) -> tuple[str, dict | None]:
    """Return ('allow'|'deny', payload_or_none)."""
    cfg = load_cfg()
    if not cfg.get("enabled", True):
        return "allow", None
    cwd = resolve_cwd(data)
    projects, _meta = collect_project_roots(cwd, cfg)
    if not projects:
        return "allow", None
    tool_name = str(data.get("tool_name") or data.get("tool") or data.get("name") or "")
    tool_input = data.get("tool_input") or data.get("arguments") or data.get("input") or {}
    if isinstance(tool_input, dict):
        nested = tool_input.get("name") or tool_input.get("toolName")
        if isinstance(nested, str) and nested and not tool_name:
            tool_name = nested
    session_id = str(data.get("session_id") or data.get("conversation_id") or "")
    cmd = extract_shell_command(tool_input)
    if is_build_tool(tool_name, tool_input, cmd):
        return "allow", None
    if not should_deny_tool(tool_name, tool_input) and session_ok(cwd, session_id):
        return "allow", None
    if not should_deny_tool(tool_name, tool_input):
        return "allow", None
    if session_ok(cwd, session_id):
        return "allow", None
    tmo = int(timeout_sec if timeout_sec is not None else cfg["pretool_ensure_timeout_sec"])
    result = ensure_both(cwd, tmo, incremental_only=False, session_id=session_id)
    if result.get("ok"):
        return "allow", None
    platform = detect_platform(data)
    msg = DENY_MSG + ((" " + result.get("error", "")) if result.get("error") else "")
    return "deny", deny_payload(msg, platform)


def refresh_incremental(
    roots: list, timeout_sec: int, session_id: str = ""
) -> tuple[bool, list[str], dict]:
    """Stop 侧：每个工作区 depth-1 项目根各 sync/update 一次。

    返回 (has_crg, warnings, aggregate)。aggregate['ui'] 供会话界面展示。
    子仓只处理一层，禁止递归发现。
    """
    cfg = load_cfg()
    seen: set[str] = set()
    projects: list[str] = []
    overflow = 0
    for root in roots or []:
        found, meta = collect_project_roots(root or "", cfg)
        overflow += int(meta.get("overflow") or 0)
        for path in found:
            key = cwd_key(path)
            if key in seen:
                continue
            seen.add(key)
            projects.append(path)
    if not projects:
        empty = {
            "eligible": False,
            "ok": True,
            "blocked": False,
            "skipped": True,
            "root": (roots[0] if roots else ""),
            "results": [],
            "mode": "refresh",
            "overflow": overflow,
            "warnings": [],
            "codegraph": False,
            "crg": False,
            "error": "",
        }
        return False, [], _attach_ui(empty, action="refresh")
    per = max(8, int(timeout_sec) // max(1, len(projects)))
    results = [
        ensure_root(path, per, incremental_only=True, session_id=session_id)
        for path in projects
    ]
    aggregate = {
        "eligible": True,
        "ok": all(bool(item.get("ok")) for item in results),
        "blocked": any(bool(item.get("blocked")) for item in results),
        "codegraph": all(bool(item.get("codegraph")) for item in results),
        "crg": any(bool(item.get("crg")) for item in results),
        "root": projects[0],
        "warnings": [w for item in results for w in (item.get("warnings") or [])],
        "error": "",
        "skipped": False,
        "mode": "refresh",
        "results": results,
        "overflow": overflow,
    }
    if overflow:
        aggregate["warnings"].append(
            f"子项目已封顶 {cfg.get('subproject_max_children', 8)} 个，另有 {overflow} 个未再嵌套同步"
        )
    if aggregate["blocked"]:
        aggregate["error"] = (
            "; ".join(item.get("error") or "" for item in results if item.get("error"))
            or "图谱 refresh 失败"
        )
    has_crg = bool(aggregate["crg"]) or any(
        is_project_graph_dir(os.path.join(str(item.get("root") or ""), ".code-review-graph"))
        or has_crg_graph(str(item.get("root") or ""))
        for item in results
    )
    return has_crg, list(aggregate["warnings"]), _attach_ui(aggregate, action="refresh")


def which_pwsh() -> str | None:
    return which_tool("pwsh") or which_tool("powershell")


def run_sync_ps1(timeout_sec: int | None = None) -> tuple[bool, str]:
    if os.environ.get("GRAPH_FRESHNESS_SKIP_SYNC", "").strip().lower() in ("1", "true", "yes", "on"):
        return False, "GRAPH_FRESHNESS_SKIP_SYNC=1，跳过"
    cfg = load_cfg()
    tmo = int(timeout_sec if timeout_sec is not None else cfg["sync_ps1_timeout_sec"])
    script = os.path.join(claude_home(), "scripts", "sync.ps1")
    if not os.path.isfile(script):
        return False, f"sync.ps1 不存在: {script}"
    exe = which_pwsh()
    if not exe:
        return False, "pwsh/powershell 未找到"
    args = [
        exe,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        script,
        "-Scope",
        "rules",
    ]
    try:
        proc = run_cmd(args, claude_home(), tmo)
    except subprocess.TimeoutExpired:
        return False, f"sync.ps1 超时（{tmo}s）"
    except OSError as exc:
        return False, f"sync.ps1 执行失败: {exc}"
    if proc.returncode != 0:
        err = ((proc.stderr or "") + (proc.stdout or "")).strip()[:400]
        return False, f"sync.ps1 非零退出: {err or proc.returncode}"
    return True, "sync.ps1 -Scope rules 已执行"


def run_sync_ps1_if_verified(*, has_edits: bool, verified_green: bool) -> tuple[bool, str]:
    """仅本会话有编辑且验证全绿时跑 sync.ps1。"""
    if not has_edits:
        return False, "无编辑，跳过 sync.ps1"
    if not verified_green:
        return False, "验证未全绿，跳过 sync.ps1"
    return run_sync_ps1()
