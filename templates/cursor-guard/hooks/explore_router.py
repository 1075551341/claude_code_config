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

# soft_block 仅拦截结构探索类工具；Read 始终 nudge，避免阻断定点深读
BLOCKABLE = {"Grep", "Glob"}

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


def _mark_codegraph_if_needed(tool_name: str, state: dict) -> None:
    lower = (tool_name or "").lower()
    if "codegraph" in lower:
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
        _mark_codegraph_if_needed(tool_name, state)

        msg = MESSAGES.get(tool_name)
        if not msg:
            return

        mode = str(explore.get("enforce_mode", "soft_block")).lower()
        cwd = data.get("cwd") or data.get("working_directory")
        index_ok = _codegraph_index_available(cwd, cfg["sync"]["claude_home"])

        # soft_block：Grep/Glob 且本会话尚未用过 codegraph → deny
        # 无索引 → 图谱保鲜硬门 deny（禁止 Grep 兜底）
        if (
            mode == "soft_block"
            and tool_name in BLOCKABLE
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
                        "请先 CallMcpTool codegraph_explore（或 codegraph_search），"
                        "再使用 Grep/Glob 作 fallback。"
                    ),
                }
            )
            return

        if mode == "soft_block" and tool_name in BLOCKABLE and not index_ok:
            # ensure 由 graph_freshness.py（90s）负责；此处只 deny，避免 5s 超时截断
            write_json(
                {
                    "permission": "deny",
                    "user_message": "已拦截：无 codegraph 索引",
                    "agent_message": (
                        f"【Cursor Guard · 图谱保鲜硬门】\n{msg}\n"
                        "未检测到 .codegraph 索引，禁止 Grep/Glob。"
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
