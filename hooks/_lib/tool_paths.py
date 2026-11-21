#!/usr/bin/env python3
"""写工具识别与文件路径解析（v14 精简版）。

回答两个问题：这次工具调用是不是写操作、它写了哪些文件。
覆盖原生编辑工具与 MCP 写工具（名字里带写动词）；不依赖其它 _lib 模块。
"""
from __future__ import annotations

import os

NATIVE_EDIT_TOOLS = {
    "Edit",
    "Write",
    "MultiEdit",
    "NotebookEdit",
    "StrReplace",
    "EditNotebook",
    "Delete",
}

MCP_WRITE_VERBS = (
    "write",
    "edit",
    "replace",
    "insert",
    "rename",
    "delete",
    "move",
    "create_directory",
    "create_text",
    "apply_refactor",
)

MEMORY_TOOLS = (
    "write_memory",
    "delete_memory",
    "edit_memory",
    "read_memory",
    "list_memories",
    "rename_memory",
)

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

PATH_LIST_KEYS = ("paths", "files", "file_paths", "relative_paths")


def is_mcp_tool(tool_name: str) -> bool:
    return tool_name.startswith("mcp__") or tool_name.startswith("mcp_")


def _collect_tool_names(tool_name: str, tool_input) -> list[str]:
    names = [tool_name] if tool_name else []
    if isinstance(tool_input, dict):
        for key in ("name", "tool_name", "tool"):
            value = tool_input.get(key)
            if isinstance(value, str) and value.strip():
                names.append(value.strip())
    return names


def is_edit_tool(tool_name: str, tool_input=None) -> bool:
    """原生编辑工具，或名字里带写动词的 MCP 写工具。"""
    for name in _collect_tool_names(tool_name, tool_input):
        lowered = (name or "").lower()
        if any(tool in lowered for tool in MEMORY_TOOLS):
            continue
        if name in NATIVE_EDIT_TOOLS:
            return True
        if is_mcp_tool(name) and any(verb in lowered for verb in MCP_WRITE_VERBS):
            return True
    return False


def extract_edit_paths(tool_input: dict, cwd: str = "") -> list[str]:
    """从工具入参解析被写文件路径；相对路径按 cwd 归一为绝对路径。"""
    if not isinstance(tool_input, dict):
        return []

    blobs = [tool_input]
    nested = tool_input.get("arguments")
    if isinstance(nested, dict):
        blobs.append(nested)

    raw: list[str] = []
    for blob in blobs:
        for key in PATH_KEYS:
            value = blob.get(key)
            if isinstance(value, str) and value.strip():
                raw.append(value.strip())
        for key in PATH_LIST_KEYS:
            value = blob.get(key)
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
