#!/usr/bin/env python3
"""写工具识别与文件路径解析（v10.17.0）。

背景：`settings.json` 的 PostToolUse matcher 原本只有 `Edit|Write|MultiEdit`，
serena / fs 等 MCP 写工具完全绕过验证追踪器，Stop 硬门因此判定「本会话没改过代码」
直接放行 —— 这是「改完影响其他功能」类回归的主要漏网通道。本模块统一回答两个问题：
这次工具调用是不是写操作、它写了哪些文件。

Claude Code 的 MCP 工具名形如 `mcp__serena__replace_symbol_body`，Cursor 侧可能是
`mcp_serena_replace_symbol_body`，两种前缀都覆盖。
"""
from __future__ import annotations

import os

# 原生编辑工具（Claude Code + Cursor 双端）
NATIVE_EDIT_TOOLS = {
    "Edit",
    "Write",
    "MultiEdit",
    "NotebookEdit",
    "StrReplace",
    "EditNotebook",
    "Delete",
}

# MCP 工具名中出现即视为写操作的动词
MCP_WRITE_VERBS = (
    "write",
    "edit",
    "replace",
    "insert",
    "rename",
    "delete",
    "move",
    "create_directory",
    "apply_refactor",
)

# 从工具入参里取文件路径的候选键（按优先级）
PATH_KEYS = (
    "file_path",
    "notebook_path",
    "path",
    "relative_path",
    "filePath",
    "target_file",
    "file",
    "destination",
    "source",
)

# 值为路径列表的候选键
PATH_LIST_KEYS = ("paths", "files", "file_paths", "relative_paths")


def is_mcp_tool(tool_name: str) -> bool:
    return tool_name.startswith("mcp__") or tool_name.startswith("mcp_")


def is_edit_tool(tool_name: str) -> bool:
    """原生编辑工具，或名字里带写动词的 MCP 工具。"""
    if tool_name in NATIVE_EDIT_TOOLS:
        return True
    if is_mcp_tool(tool_name):
        lowered = tool_name.lower()
        return any(verb in lowered for verb in MCP_WRITE_VERBS)
    return False


def extract_edit_paths(tool_input: dict, cwd: str = "") -> list[str]:
    """从工具入参解析被写文件路径；相对路径按 cwd 归一为绝对路径。

    serena 用 `relative_path`、fs 用 `path`、原生工具用 `file_path`，
    统一在这里处理，避免各 hook 各写一套解析。
    """
    if not isinstance(tool_input, dict):
        return []

    raw: list[str] = []
    for key in PATH_KEYS:
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            raw.append(value.strip())
    for key in PATH_LIST_KEYS:
        value = tool_input.get(key)
        if isinstance(value, list):
            raw.extend(v.strip() for v in value if isinstance(v, str) and v.strip())

    out: list[str] = []
    for path in raw:
        norm = normalize_path(path, cwd)
        if norm and norm not in out:
            out.append(norm)
    return out


def normalize_path(path: str, cwd: str = "") -> str:
    try:
        if not os.path.isabs(path) and cwd:
            path = os.path.join(cwd, path)
        return os.path.normpath(path)
    except (TypeError, ValueError):
        return path
