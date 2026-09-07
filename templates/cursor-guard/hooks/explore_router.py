#!/usr/bin/env python3
"""preToolUse: codegraph 优先探索路由（nudge | soft_block）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import _path  # noqa: F401

from hook_io import (
    ensure_hook_output,
    ensure_lib_path,
    extract_tool_name,
    import_claude_lib,
    read_stdin,
    setup_stdio,
    write_json,
)

ensure_lib_path()
setup_stdio()

from config import load_guard_config, state_path

MESSAGES = {
    "Grep": "结构/引用探索请优先 codegraph_explore 或 codegraph_search，Grep 仅作 fallback。",
    "Read": "大范围读文件前请先用 codegraph_explore；Read 用于定点深读。",
    "Glob": "目录结构探索请优先 codegraph_explore，Glob 仅作 fallback。",
}

EVERYTHING_MSG = (
    "工作区找文件请用 Glob；结构探索请用 codegraph_explore。"
    "everything 仅用于本机全盘/跨仓按文件名定位，禁止替代 Glob 或 codegraph。"
)

# soft_block 仅拦截结构探索类工具；Read 始终 nudge，避免阻断定点深读
BLOCKABLE = {"Grep", "Glob"}
EVERYTHING_TOOLS = {
    "everything_search",
    "everything_search_by_type",
    "everything_find_recent",
    "everything_file_details",
    "everything_count_stats",
}

STATE_NAME = "explore_router.json"


def _codegraph_index_available(cwd: str | None, claude_home: str | None = None) -> bool:
    if not cwd:
        return True  # 未知 cwd 时不降级误放行阻断语义；仍允许 soft_block
    if claude_home:
        try:
            gf = import_claude_lib(claude_home, "graph_freshness")
            return bool(gf.has_codegraph_index(cwd))
        except Exception as e:
            print(f"explore_router: graph_freshness index check failed: {e}", file=sys.stderr)
    try:
        p = Path(cwd).resolve()
        git_stop = None
        cur = p
        for _ in range(8):
            if (cur / ".git").exists():
                git_stop = cur
                break
            if cur.parent == cur:
                break
            cur = cur.parent
        cur = p
        for _ in range(8):
            cg = cur / ".codegraph"
            if cg.is_dir():
                names = {x.name for x in cg.iterdir()} - {".gitignore", "daemon.log"}
                if names:
                    return True
            if git_stop is not None and cur == git_stop:
                break
            if cur.parent == cur:
                break
            cur = cur.parent
    except OSError as e:
        print(f"explore_router: cwd resolve failed: {e}", file=sys.stderr)
        return False
    return False


def _load_state() -> dict:
    path = state_path(STATE_NAME)
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"explore_router: state read failed: {e}", file=sys.stderr)
    return {"codegraph_seen": False, "denied_count": 0}


def _save_state(state: dict) -> None:
    path = state_path(STATE_NAME)
    try:
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError as e:
        print(f"explore_router: state write failed: {e}", file=sys.stderr)


def _norm(name: str) -> str:
    return (name or "").lower().replace("-", "_")


def _is_everything_tool(tool_name: str, data: dict | None = None) -> bool:
    names = [tool_name]
    blob = (data or {}).get("tool_input") or (data or {}).get("arguments") or (data or {}).get("input")
    if isinstance(blob, dict):
        for key in ("name", "toolName", "tool", "mcp_tool", "tool_name", "namespace"):
            val = blob.get(key)
            if isinstance(val, str) and val:
                names.append(val)
    for name in names:
        n = _norm(name)
        if "everything_claude_code" in n:
            continue
        if n in EVERYTHING_TOOLS:
            return True
        for tool in EVERYTHING_TOOLS:
            if n.endswith(tool) or f"__{tool}" in n:
                return True
        if n in {"everything", "user_everything", "mcp__everything", "mcp_everything"}:
            return True
        if n.startswith("mcp__everything__") or n.startswith("mcp_everything_") or n.startswith("user_everything"):
            return True
    return False


def _mark_codegraph_if_needed(tool_name: str, state: dict, data: dict | None = None) -> None:
    names = [tool_name or ""]
    blob = (data or {}).get("tool_input") or (data or {}).get("arguments") or {}
    if isinstance(blob, dict):
        for key in ("name", "toolName", "namespace"):
            val = blob.get(key)
            if isinstance(val, str):
                names.append(val)
    if any("codegraph" in _norm(n) for n in names):
        state["codegraph_seen"] = True
        _save_state(state)


def main() -> None:
    try:
        data = read_stdin()
        cfg = load_guard_config()
        explore = cfg.get("explore", {})
        if not explore.get("codegraph_first") or not explore.get("nudge_on_grep_read"):
            return

        tool_name = extract_tool_name(data)
        state = _load_state()
        _mark_codegraph_if_needed(tool_name, state, data)

        everything = _is_everything_tool(tool_name, data)
        msg = MESSAGES.get(tool_name)
        if not msg and everything:
            msg = EVERYTHING_MSG
        if not msg:
            return

        mode = str(explore.get("enforce_mode", "soft_block")).lower()
        cwd = data.get("cwd") or data.get("working_directory")
        index_ok = _codegraph_index_available(cwd, cfg["sync"]["claude_home"])
        blockable = tool_name in BLOCKABLE or everything

        # soft_block：Grep/Glob/everything 且本会话尚未用过 codegraph → deny
        # 无索引 → 图谱保鲜硬门 deny（禁止 Grep 兜底）
        if (
            mode == "soft_block"
            and blockable
            and not state.get("codegraph_seen")
            and index_ok
        ):
            state["denied_count"] = int(state.get("denied_count", 0)) + 1
            _save_state(state)
            write_json(
                {
                    "permission": "deny",
                    "user_message": "已拦截：请先使用 codegraph_explore",
                    "agent_message": (
                        f"【Cursor Guard · codegraph soft_block】\n{msg}\n"
                        "请先调用 codegraph_explore（或 codegraph_search），"
                        "再使用 Grep/Glob/everything 作 fallback。"
                    ),
                }
            )
            return

        if mode == "soft_block" and blockable and not index_ok:
            # ensure 由 graph_freshness.py（90s）负责；此处只 deny，避免 5s 超时截断
            write_json(
                {
                    "permission": "deny",
                    "user_message": "已拦截：无 codegraph 索引",
                    "agent_message": (
                        f"【Cursor Guard · 图谱保鲜硬门】\n{msg}\n"
                        "未检测到 .codegraph 索引，禁止 Grep/Glob/everything。"
                        "SessionStart/pre-graph-freshness 会先 init；仍无图不得探索。"
                    ),
                }
            )
            return

        write_json({"agent_message": f"【Cursor Guard · codegraph 优先】\n{msg}"})
    except Exception as e:
        print(f"explore_router: {e}", file=sys.stderr)
    finally:
        ensure_hook_output()


if __name__ == "__main__":
    main()
