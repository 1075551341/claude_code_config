#!/usr/bin/env python3
"""PreToolUse: 图谱保鲜硬门（v11.4.6）。

无图/ensure 失败则 deny 查询 MCP、Grep/Glob、写工具。
建图类 CLI/MCP 放行。Claude Code / TRAE / Qoder 共用。
"""
from __future__ import annotations

import json
import sys
import io
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception as e:
    print(f"⚠️ {e}", file=sys.stderr)

from graph_freshness import detect_platform, load_cfg, pretool_decision  # noqa: E402


def main() -> None:
    try:
        raw = (
            sys.stdin.buffer.read().decode("utf-8", errors="replace")
            if hasattr(sys.stdin, "buffer")
            else sys.stdin.read()
        )
        data = json.loads(raw) if raw.strip() else {}
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"pre-graph-freshness: stdin parse failed: {exc}", file=sys.stderr)
        sys.exit(0)

    cfg = load_cfg()
    decision, payload = pretool_decision(data, cfg.get("pretool_ensure_timeout_sec"))
    if decision != "deny" or not payload:
        sys.exit(0)

    platform = detect_platform(data)
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    if platform == "claude":
        reason = (
            (payload.get("hookSpecificOutput") or {}).get("permissionDecisionReason")
            or "图谱未就绪"
        )
        sys.stderr.write(reason + "\n")
        sys.stderr.flush()
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
