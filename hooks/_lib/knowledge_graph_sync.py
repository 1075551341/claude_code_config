#!/usr/bin/env python3
"""双引擎知识图谱同步（codegraph + codebase-memory）。

供 PostToolUse / Stop / sync.ps1 共用。R16：异常 stderr 留痕，不静默吞掉。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

STATE_FILE = Path.home() / ".claude" / ".state" / "knowledge_graph_sync.json"
DEFAULT_DEBOUNCE_SEC = int(os.environ.get("KG_SYNC_DEBOUNCE_SEC", "90"))
CBM_PACKAGE = os.environ.get("CBM_MCP_PACKAGE", "codebase-memory-mcp@0.8.1")

CODE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".go", ".rs", ".java", ".rb", ".cs", ".php", ".kt",
}
CONFIG_EXTENSIONS = {
    ".md", ".mdc", ".yaml", ".yml", ".json", ".toml",
}


def resolve_project_root(cwd: str | None, file_path: str | None = None) -> str:
    """向上查找含 .codegraph 或 .git 的根；否则用 cwd。"""
    start = file_path or cwd or os.getcwd()
    p = Path(start).resolve()
    if p.is_file():
        p = p.parent
    for cand in [p, *p.parents]:
        if (cand / ".codegraph").is_dir() or (cand / ".git").is_dir():
            return str(cand)
    return str(p)


def load_state() -> dict:
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"knowledge_graph_sync: state read failed: {e}", file=sys.stderr)
    return {}


def save_state(state: dict) -> None:
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    except OSError as e:
        print(f"knowledge_graph_sync: state write failed: {e}", file=sys.stderr)


def should_trigger_for_file(file_path: str) -> bool:
    if not file_path:
        return True
    ext = Path(file_path).suffix.lower()
    return ext in CODE_EXTENSIONS or ext in CONFIG_EXTENSIONS


def _which(name: str) -> str | None:
    from shutil import which

    found = which(name)
    if found:
        return found
    if sys.platform == "win32" and not name.lower().endswith((".cmd", ".exe", ".bat")):
        return which(f"{name}.cmd") or which(f"{name}.exe")
    return None


def _run(cmd: list[str], cwd: str, timeout: int) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )
        out = (r.stdout or r.stderr or "").strip()
        if r.returncode == 0:
            return True, out[:500] if out else "ok"
        return False, out[:500] or f"exit {r.returncode}"
    except FileNotFoundError:
        return False, f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, f"timeout {timeout}s"
    except OSError as e:
        return False, str(e)


def sync_codegraph(project_root: str) -> tuple[bool, str]:
    if not (Path(project_root) / ".codegraph").is_dir():
        return False, "no .codegraph (skip; run codegraph init)"
    cg = _which("codegraph") or "codegraph"
    # `sync` 本身即为增量（自上次 index 以来的变更）；无 --incremental 选项
    detail = "codegraph failed"
    for cmd in (
        [cg, "sync", project_root],
        [cg, "sync"],
    ):
        ok, detail = _run(cmd, project_root, timeout=120)
        if ok:
            return True, f"codegraph: {detail or ' '.join(cmd)}"
    return False, detail


CBM_INDEX_HINT = (
    "cbm index missing/stale — run: powershell -File ~/.claude/scripts/cbm-index.ps1 "
    f"<repo_path>  (do NOT Grep as fallback)"
)


def sync_codebase_memory(project_root: str, mode: str = "fast") -> tuple[bool, str]:
    """通过 MCP CLI 刷新 codebase-memory 索引。"""
    payload = json.dumps({"repo_path": project_root, "mode": mode}, ensure_ascii=False)
    npx = _which("npx") or ("npx.cmd" if sys.platform == "win32" else "npx")
    cmd = [npx, "-y", CBM_PACKAGE, "cli", "index_repository", payload]
    ok, detail = _run(cmd, project_root, timeout=300)
    if ok:
        return True, f"cbm[{mode}]: {detail or 'indexed'}"
    lower = (detail or "").lower()
    if any(
        k in lower
        for k in ("not found", "no project", "not indexed", "missing", "does not exist", "stale")
    ):
        return False, f"cbm: {detail}; {CBM_INDEX_HINT}"
    return False, f"cbm: {detail}; if index missing run scripts/cbm-index.ps1 (no Grep fallback)"


def sync_knowledge_graphs(
    project_root: str,
    *,
    force: bool = False,
    run_codegraph: bool = True,
    run_cbm: bool = True,
    cbm_mode: str = "fast",
    debounce_sec: int | None = None,
) -> dict:
    """同步双引擎。force=True 忽略 debounce（Stop / sync.ps1）。"""
    root = str(Path(project_root).resolve())
    debounce = DEFAULT_DEBOUNCE_SEC if debounce_sec is None else debounce_sec
    state = load_state()
    now = time.time()
    proj_state = state.get(root, {})
    results = {"root": root, "codegraph": None, "cbm": None, "skipped": []}

    if run_codegraph:
        last_cg = float(proj_state.get("codegraph_ts", 0) or 0)
        if force or (now - last_cg) >= debounce:
            ok, detail = sync_codegraph(root)
            results["codegraph"] = {"ok": ok, "detail": detail}
            if ok:
                proj_state["codegraph_ts"] = now
            else:
                proj_state["codegraph_error"] = detail
                print(f"knowledge_graph_sync: {detail}", file=sys.stderr)
        else:
            results["skipped"].append("codegraph_debounce")

    if run_cbm:
        last_cbm = float(proj_state.get("cbm_ts", 0) or 0)
        if force or (now - last_cbm) >= debounce:
            ok, detail = sync_codebase_memory(root, mode=cbm_mode)
            results["cbm"] = {"ok": ok, "detail": detail}
            if ok:
                proj_state["cbm_ts"] = now
            else:
                proj_state["cbm_error"] = detail
                print(f"knowledge_graph_sync: {detail}", file=sys.stderr)
        else:
            results["skipped"].append("cbm_debounce")

    proj_state["last_run"] = now
    state[root] = proj_state
    # prune stale project entries (>30d)
    cutoff = now - 30 * 24 * 3600
    state = {
        k: v for k, v in state.items()
        if isinstance(v, dict) and float(v.get("last_run", 0) or 0) >= cutoff
    }
    state[root] = proj_state
    save_state(state)
    return results


if __name__ == "__main__":
    # CLI: python knowledge_graph_sync.py [--force] [path]
    args = sys.argv[1:]
    force = "--force" in args
    paths = [a for a in args if not a.startswith("-")]
    target = paths[0] if paths else str(Path.home() / ".claude")
    out = sync_knowledge_graphs(target, force=force)
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    try:
        print(payload)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((payload + "\n").encode("utf-8", errors="replace"))
    cg_ok = (out.get("codegraph") or {}).get("ok")
    cbm_ok = (out.get("cbm") or {}).get("ok")
    sys.exit(0 if cg_ok or cbm_ok or out.get("skipped") else 1)
