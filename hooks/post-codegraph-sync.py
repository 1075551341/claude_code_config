#!/usr/bin/env python3
"""
PostToolUse Hook: 文件变更后增量刷新 codegraph + codebase-memory 知识图谱。
触发: Write|Edit|MultiEdit
扩展名命中代码/配置 → 同步；cbm 默认 90s debounce，codegraph 同。
"""
import json
import sys
import io
from pathlib import Path

# 保证可 import hooks/_lib
_LIB = Path(__file__).resolve().parent / "_lib"
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from knowledge_graph_sync import (  # noqa: E402
    resolve_project_root,
    should_trigger_for_file,
    sync_knowledge_graphs,
)


def main():
    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"post-codegraph-sync: stdout wrap failed: {e}", file=sys.stderr)

    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError) as e:
        print(f"post-codegraph-sync: stdin failed: {e}", file=sys.stderr)
        sys.exit(0)

    tool_input = data.get("tool_input") or data.get("input") or {}
    file_path = (
        tool_input.get("file_path")
        or tool_input.get("path")
        or tool_input.get("target_file")
        or ""
    )
    if file_path and not should_trigger_for_file(file_path):
        sys.exit(0)

    cwd = data.get("cwd") or data.get("working_directory") or None
    root = resolve_project_root(cwd, file_path or None)
    result = sync_knowledge_graphs(root, force=False, run_cbm=False)
    # 静默成功；失败已 stderr
    if result.get("skipped") and not result.get("codegraph") and not result.get("cbm"):
        sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    main()
