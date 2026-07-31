#!/usr/bin/env python3
"""
Stop Hook: 会话结束强制刷新 codegraph + codebase-memory（忽略 debounce）。
确保下次打开/查询图谱为最新内容。
"""
import json
import sys
import io
from pathlib import Path

_LIB = Path(__file__).resolve().parent / "_lib"
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from knowledge_graph_sync import resolve_project_root, sync_knowledge_graphs  # noqa: E402


def main():
    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"stop-knowledge-graph-sync: stdout wrap failed: {e}", file=sys.stderr)

    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError) as e:
        print(f"stop-knowledge-graph-sync: stdin failed: {e}", file=sys.stderr)
        data = {}

    cwd = data.get("cwd") or data.get("working_directory") or None
    root = resolve_project_root(cwd, None)
    result = sync_knowledge_graphs(root, force=True, cbm_mode="fast")
    cg = (result.get("codegraph") or {}).get("ok")
    cbm = (result.get("cbm") or {}).get("ok")
    print(
        f"stop-knowledge-graph-sync: root={root} codegraph={'ok' if cg else 'skip/fail'} "
        f"cbm={'ok' if cbm else 'skip/fail'}",
        file=sys.stderr,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
