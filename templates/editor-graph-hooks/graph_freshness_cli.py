#!/usr/bin/env python3
"""Portable dual-graph freshness CLI (codegraph + code-review-graph).

Harness copies live under ~/.dsh/tools and ~/.config/opencode/scripts.
No Claude-home import. SSOT of this file: ~/.claude/templates/editor-graph-hooks/

  ensure  — eligible git: init|sync + build|update
  refresh — incremental sync/update only (no init/build)
  status  — report whether both graphs exist (no CLI spawn)

If --cwd is not inside a git repo, depth-1 child git repos under it are
discovered and processed per sub-project (parallel, aggregated in the
top-level "results" array). Disable via config "subproject_discovery":
false or --no-subprojects.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys

CODEGRAPH_MARKERS = (
    "index.sqlite",
    "graph.db",
    "codegraph.db",
    "daemon.pid",
    "config.json",
)
GRAPH_FILES = ("graph.db", "graph.sqlite", "graph.sqlite3")
DEFAULT_CFG = {
    "enabled": True,
    "session_ensure_timeout_sec": 120,
    "stop_refresh_timeout_sec": 30,
    "require_both_graphs": True,
    "subproject_discovery": True,
    "subproject_max_children": 8,
}


def load_cfg(path: str) -> dict:
    cfg = dict(DEFAULT_CFG)
    if not path or not os.path.isfile(path):
        return cfg
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"graph-freshness-cli: config read failed: {exc}", file=sys.stderr)
        return cfg
    user = raw.get("graph_freshness") if isinstance(raw.get("graph_freshness"), dict) else raw
    if isinstance(user, dict):
        for key in cfg:
            if key in user:
                cfg[key] = user[key]
    return cfg


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


def is_project_graph_dir(path: str) -> bool:
    if not path or not os.path.isdir(path):
        return False
    return any(os.path.isfile(os.path.join(path, name)) for name in GRAPH_FILES)


def find_crg_root(start: str, max_up: int = 8) -> str:
    probe = os.path.abspath(start or "") if start else ""
    if not probe:
        return ""
    git = find_git_root(probe, max_up)
    for _ in range(max_up):
        if is_project_graph_dir(os.path.join(probe, ".code-review-graph")):
            return probe
        if git and os.path.normcase(probe) == os.path.normcase(git):
            break
        parent = os.path.dirname(probe)
        if parent == probe:
            break
        probe = parent
    return ""


DISCOVERY_EXCLUDE = {
    "node_modules", "dist", "build", "out", "venv", ".venv",
    ".git", ".claude", ".cloud", ".codegraph", ".code-review-graph",
    "vendor", "target", ".tox", "__pycache__", "site-packages",
    ".next", ".nuxt", "coverage",
}


def _norm(path: str) -> str:
    return os.path.normcase(os.path.abspath(path or "")).replace("\\", "/")


def _discovery_blocked(cwd: str) -> bool:
    if not cwd:
        return True
    try:
        probe = os.path.normcase(os.path.abspath(cwd))
        home = os.path.normcase(os.path.abspath(os.path.expanduser("~")))
    except OSError:
        return True
    if probe == home:
        return True
    rest = probe.rstrip("\\/")
    if len(rest) <= 3 and ":" in rest:
        return True
    return False


def _safe_under(parent: str, child: str) -> bool:
    try:
        real_p = os.path.normcase(os.path.realpath(parent))
        real_c = os.path.normcase(os.path.realpath(child))
    except OSError:
        return False
    if real_c == real_p:
        return False
    return real_c.startswith(real_p.rstrip("\\/") + os.sep)


def list_child_git_repos(parent: str, *, max_children: int = 8) -> tuple[list[str], int]:
    """Depth-1 only. Never recurses; never walks into graph dirs."""
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


def discover_subprojects(cwd: str, max_children: int = 8) -> list[str]:
    found, _overflow = list_child_git_repos(cwd, max_children=max_children)
    return found


def collect_project_roots(
    cwd: str, *, discover: bool = True, max_children: int = 8
) -> tuple[list[str], dict]:
    meta = {"overflow": 0, "discovery_blocked": False}
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
        key = _norm(path)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(path)
    return ordered, meta


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
    if find_codegraph_root(root):
        ok, err = _run_named("codegraph", ["sync"], root, timeout_sec)
        if ok:
            return True, ""
        if which_tool("codegraph") is None:
            return True, "codegraph CLI 缺失，已有索引：跳过 sync"
        return False, err
    if incremental_only:
        return False, "无 .codegraph 索引（refresh 仅增量，不 init）"
    return _run_named("codegraph", ["init", "-i"], root, timeout_sec)


def ensure_crg(root: str, timeout_sec: int, incremental_only: bool = False) -> tuple[bool, str]:
    if find_crg_root(root):
        found = find_crg_root(root) or root
        ok, err = _run_named("code-review-graph", ["update"], found, timeout_sec)
        if ok:
            return True, ""
        if which_tool("code-review-graph") is None:
            return True, "code-review-graph CLI 缺失，已有 graph.db：跳过 update"
        return False, err
    if incremental_only:
        return False, "无 CRG graph.db（refresh 仅增量，不 build）"
    return _run_named("code-review-graph", ["build"], root, timeout_sec)


def ensure_root(
    root: str,
    timeout_sec: int,
    *,
    incremental_only: bool = False,
    require_both: bool = True,
) -> dict:
    """ensure/refresh 单个 git 项目根（原单仓语义保持不变）。

    只处理给定根：不做子项目发现、不递归；图谱根被该项目的 git 根夹住
    （find_codegraph_root / find_crg_root 以 git 根为界），绝不写入父目录
    或兄弟项目。
    """
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
    half = max(20, int(timeout_sec) // 2)
    cg_ok, cg_err = ensure_codegraph(root, half, incremental_only)
    crg_ok, crg_err = ensure_crg(root, half, incremental_only)
    result["codegraph"] = bool(find_codegraph_root(root))
    result["crg"] = bool(find_crg_root(root))
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
        result["error"] = "; ".join(warnings) or f"子项目图谱 {mode} 失败"
    return result


def _failed_result(child: str, mode: str, error: str) -> dict:
    return {
        "eligible": True,
        "ok": False,
        "blocked": True,
        "codegraph": False,
        "crg": False,
        "root": child,
        "project": os.path.basename(os.path.normpath(child)) or child,
        "warnings": [],
        "error": error,
        "skipped": False,
        "mode": mode,
    }


def format_ui_banner(result: dict, *, action: str = "ensure") -> str:
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


def _attach_ui(result: dict, *, action: str) -> dict:
    result["ui"] = format_ui_banner(result, action=action)
    return result


def ensure_both(
    cwd: str,
    timeout_sec: int,
    *,
    incremental_only: bool = False,
    require_both: bool = True,
    enabled: bool = True,
    subproject_discovery: bool = True,
    max_children: int = 8,
) -> dict:
    """git 根自身 + depth-1 子仓；ensure_root 不再发现，禁止无穷嵌套。"""
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
    if not enabled:
        result["skipped"] = True
        result["root"] = cwd or ""
        return _attach_ui(result, action=action)
    projects, meta = collect_project_roots(
        cwd,
        discover=subproject_discovery,
        max_children=max_children,
    )
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
        try:
            results.append(
                ensure_root(
                    projects[0], per,
                    incremental_only=incremental_only, require_both=require_both,
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append(_failed_result(projects[0], mode, f"子项目执行异常: {exc}"))
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(3, len(projects))) as pool:
            futures = {
                pool.submit(
                    ensure_root, path, per,
                    incremental_only=incremental_only, require_both=require_both,
                ): path
                for path in projects
            }
            for future in concurrent.futures.as_completed(futures):
                path = futures[future]
                try:
                    results.append(future.result())
                except Exception as exc:  # noqa: BLE001
                    results.append(_failed_result(path, mode, f"子项目执行异常: {exc}"))
        results.sort(key=lambda item: str(item.get("root") or ""))
    result["results"] = results
    result["codegraph"] = all(bool(item.get("codegraph")) for item in results)
    result["crg"] = all(bool(item.get("crg")) for item in results)
    result["warnings"] = [w for item in results for w in (item.get("warnings") or [])]
    if result["overflow"]:
        result["warnings"].append(
            f"子项目已封顶 {max_children} 个，另有 {result['overflow']} 个未再嵌套同步"
        )
    result["ok"] = all(bool(item.get("ok")) for item in results)
    result["blocked"] = any(bool(item.get("blocked")) for item in results)
    if result["blocked"]:
        result["error"] = (
            "; ".join(item.get("error") or "" for item in results if item.get("error"))
            or "子项目图谱同步失败"
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


def default_config_path() -> str:
    env = (os.environ.get("GRAPH_FRESHNESS_CONFIG") or "").strip()
    if env:
        return os.path.expanduser(env)
    here = os.path.dirname(os.path.abspath(__file__))
    sibling = os.path.join(here, "graph-freshness.json")
    if os.path.isfile(sibling):
        return sibling
    parent = os.path.join(os.path.dirname(here), "graph-freshness.json")
    if os.path.isfile(parent):
        return parent
    home_cfg = os.path.join(os.path.expanduser("~"), ".dsh", "config", "graph-freshness.json")
    if os.path.isfile(home_cfg):
        return home_cfg
    oc_cfg = os.path.join(os.path.expanduser("~"), ".config", "opencode", "graph-freshness.json")
    if os.path.isfile(oc_cfg):
        return oc_cfg
    return ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dual-graph freshness (codegraph + CRG)")
    parser.add_argument("mode", choices=("ensure", "refresh", "status"))
    parser.add_argument("--cwd", default=os.getcwd())
    parser.add_argument("--config", default="")
    parser.add_argument("--timeout", type=int, default=0)
    parser.add_argument(
        "--no-subprojects",
        action="store_true",
        help="disable depth-1 sub-project discovery (git 根自身仍会同步)",
    )
    args = parser.parse_args(argv)
    cfg = load_cfg(args.config or default_config_path())
    cwd = os.path.abspath(os.path.expanduser(args.cwd))
    if args.mode == "status":
        discover = (not args.no_subprojects) and bool(cfg.get("subproject_discovery", True))
        max_children = max(1, int(cfg.get("subproject_max_children", 8)))
        projects, meta = collect_project_roots(
            cwd, discover=discover, max_children=max_children
        )
        if not projects:
            payload = {
                "mode": "status",
                "eligible": False,
                "root": cwd,
                "codegraph": False,
                "crg": False,
                "ok": True,
                "skipped": True,
                "overflow": int(meta.get("overflow") or 0),
                "results": [],
            }
        else:
            results = []
            require_both = bool(cfg.get("require_both_graphs", True))
            for path in projects:
                cg = bool(find_codegraph_root(path))
                crg = bool(find_crg_root(path))
                ok = (cg and crg) if require_both else (cg or crg)
                results.append({
                    "project": os.path.basename(os.path.normpath(path)),
                    "root": path,
                    "eligible": True,
                    "codegraph": cg,
                    "crg": crg,
                    "ok": ok,
                })
            payload = {
                "mode": "status",
                "eligible": True,
                "root": projects[0],
                "discovered": [r["project"] for r in results],
                "results": results,
                "codegraph": all(r["codegraph"] for r in results),
                "crg": all(r["crg"] for r in results),
                "ok": all(r["ok"] for r in results),
                "skipped": False,
                "overflow": int(meta.get("overflow") or 0),
            }
        payload["ui"] = format_ui_banner(payload, action="ensure")
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return 0 if payload["ok"] or payload["skipped"] else 2
    incremental = args.mode == "refresh"
    timeout = args.timeout or int(
        cfg["stop_refresh_timeout_sec"] if incremental else cfg["session_ensure_timeout_sec"]
    )
    result = ensure_both(
        cwd,
        timeout,
        incremental_only=incremental,
        require_both=bool(cfg.get("require_both_graphs", True)),
        enabled=bool(cfg.get("enabled", True)),
        subproject_discovery=(not args.no_subprojects)
        and bool(cfg.get("subproject_discovery", True)),
        max_children=max(1, int(cfg.get("subproject_max_children", 8))),
    )
    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    if result.get("skipped"):
        return 0
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
