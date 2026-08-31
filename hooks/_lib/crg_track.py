#!/usr/bin/env python3
"""CRG 工具调用追踪与六维续轮文案（v11.4.5）。

Claude PostToolUse 与 Cursor verify_tracker / Stop 共用。
工具名含子串即可：detect_changes / get_impact_radius / get_minimal_context /
get_review_context / get_affected_flows。
"""
from __future__ import annotations

import os

CRG_MARKERS = (
    "detect_changes",
    "get_impact_radius",
    "get_minimal_context",
    "get_review_context",
    "get_affected_flows",
)

# 项目图标志。空的 ~/.code-review-graph（多仓 registry）不算项目已建图。
GRAPH_FILES = ("graph.db", "graph.sqlite", "graph.sqlite3")

SIX_RETRY_LINES = (
    "影响面不够细：补 CRG get_impact_radius + codegraph blast-radius，更新 IMPACT",
    "需求未达：对照需求指纹，「满足」覆盖 strong 关键词（承认/反驳/弃权）",
    "错改：清单差集 extras → 回滚或补登记 IMPACT",
    "漏改：Grep 残留=0；同类引用/INDEX/MANIFEST 同步",
    "原功能破坏：最后一次编辑后须有测试/冒烟观察输出",
    "文档未同步：「漏改」须含文档或「无文档影响」",
)


def _norm(name: str) -> str:
    return (name or "").lower().replace("-", "_")


def is_crg_tool(name: str) -> bool:
    n = _norm(name)
    if not n:
        return False
    return any(m in n for m in CRG_MARKERS)


def collect_tool_names(tool_name: str, tool_input=None) -> list[str]:
    names = [tool_name] if tool_name else []
    if isinstance(tool_input, dict):
        for key in ("name", "toolName", "tool", "mcp_tool", "tool_name", "namespace"):
            val = tool_input.get(key)
            if isinstance(val, str) and val:
                names.append(val)
        nested = tool_input.get("arguments")
        if isinstance(nested, dict):
            val = nested.get("name") or nested.get("toolName")
            if isinstance(val, str) and val:
                names.append(val)
    return names


def record_crg_call(entry: dict, tool_name: str, ts: float, tool_input=None) -> bool:
    """命中 CRG 工具则追加 entry['crg_calls']，返回是否写入。"""
    for name in collect_tool_names(tool_name, tool_input):
        if is_crg_tool(name):
            entry.setdefault("crg_calls", []).append({"tool": name[:160], "ts": ts})
            return True
    return False


def has_crg_since(entry: dict, since_ts: float) -> bool:
    if since_ts <= 0:
        return bool(entry.get("crg_calls"))
    return any(
        item.get("ts", 0) >= since_ts - 1
        for item in (entry.get("crg_calls") or [])
    )


def is_project_graph_dir(path: str) -> bool:
    """True only when the directory holds a built project graph, not an empty registry."""
    if not path or not os.path.isdir(path):
        return False
    return any(os.path.isfile(os.path.join(path, name)) for name in GRAPH_FILES)


def _git_root(start: str, max_up: int = 8) -> str:
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


def find_crg_root(start: str, max_up: int = 8) -> str:
    """Return the directory that contains `.code-review-graph/graph.db`, or ''.

    Walks from cwd up to the git root only, so a home-level registry or another
    repo's graph is not treated as this project's graph.
    """
    probe = os.path.abspath(start or "") if start else ""
    if not probe:
        return ""
    git = _git_root(probe, max_up)
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


def project_has_crg_graph(cwd: str, max_up: int = 6) -> bool:
    return bool(find_crg_root(cwd, max_up))


def six_retry_block() -> str:
    lines = ["六维纠错（续轮须逐项补观察证据）："]
    lines.extend(f"  • {item}" for item in SIX_RETRY_LINES)
    return "\n".join(lines)
