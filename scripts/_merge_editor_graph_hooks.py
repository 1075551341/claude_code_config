#!/usr/bin/env python3
"""Merge graph-freshness hooks into TRAE hooks.json and Qoder settings.json.

Idempotent. Does not wipe unrelated hook groups. Exit 0 even if a home is absent.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HOME = Path(os.environ.get("USERPROFILE") or Path.home())
CLAUDE = HOME / ".claude"
HOOKS = CLAUDE / "hooks"

SESSION = str(HOOKS / "session-start-bootstrap.py").replace("\\", "/")
PRE = str(HOOKS / "pre-graph-freshness.py").replace("\\", "/")
STOP = str(HOOKS / "stop-graph-freshness.py").replace("\\", "/")
PY = "python"


def _cmd(script: str) -> str:
    return f'{PY} "{script}"'


def _trae_groups() -> dict:
    return {
        "SessionStart": [
            {
                "hooks": [
                    {"type": "command", "command": _cmd(SESSION), "timeout": 120}
                ]
            }
        ],
        "PreToolUse": [
            {
                "matcher": r"Grep|Glob|Write|Edit|RunCommand|mcp__.*",
                "hooks": [
                    {"type": "command", "command": _cmd(PRE), "timeout": 90}
                ],
            }
        ],
        "Stop": [
            {
                "hooks": [
                    {"type": "command", "command": _cmd(STOP), "timeout": 150}
                ]
            }
        ],
    }


def _qoder_groups() -> dict:
    return {
        "SessionStart": [
            {
                "hooks": [
                    {"type": "command", "command": _cmd(SESSION), "timeout": 120}
                ]
            }
        ],
        "PreToolUse": [
            {
                "matcher": r"Grep|Glob|Write|Edit|Bash|mcp__.*",
                "hooks": [
                    {"type": "command", "command": _cmd(PRE), "timeout": 90}
                ],
            }
        ],
        "Stop": [
            {
                "hooks": [
                    {"type": "command", "command": _cmd(STOP), "timeout": 150}
                ]
            }
        ],
    }


def _has_command(group: dict, needle: str) -> bool:
    for hook in group.get("hooks") or []:
        cmd = str(hook.get("command") or "")
        if needle.replace("\\", "/") in cmd.replace("\\", "/"):
            return True
    return False


def merge_event(existing: list, incoming: list, needle: str) -> list:
    out = list(existing or [])
    for group in incoming:
        if any(_has_command(g, needle) for g in out):
            for g in out:
                if _has_command(g, needle):
                    g["hooks"] = group.get("hooks", g.get("hooks"))
                    if group.get("matcher"):
                        g["matcher"] = group["matcher"]
            continue
        out.append(group)
    return out


def merge_hooks_obj(hooks: dict, template: dict) -> dict:
    hooks = dict(hooks or {})
    needles = {
        "SessionStart": "session-start-bootstrap.py",
        "PreToolUse": "pre-graph-freshness.py",
        "Stop": "stop-graph-freshness.py",
    }
    for event, groups in template.items():
        needle = needles[event]
        hooks[event] = merge_event(hooks.get(event) or [], groups, needle)
    return hooks


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


MAX_QODER_REWRITE = 256 * 1024


def merge_trae(path: Path) -> str:
    if not path.parent.is_dir():
        return f"skip {path} (home missing)"
    data = {"version": 1, "hooks": {}}
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            return f"FAIL {path}: {exc}"
        if not isinstance(data, dict):
            return f"FAIL {path}: not an object"
    data["version"] = int(data.get("version") or 1)
    data["hooks"] = merge_hooks_obj(data.get("hooks") or {}, _trae_groups())
    write_json(path, data)
    return f"ok {path}"


def merge_qoder_settings(path: Path) -> str:
    if not path.parent.is_dir():
        return f"skip {path} (home missing)"
    if not path.is_file():
        data = {"hooks": {}}
    else:
        try:
            raw = path.read_text(encoding="utf-8-sig")
        except OSError as exc:
            return f"FAIL {path}: {exc}"
        if len(raw.encode("utf-8")) > MAX_QODER_REWRITE:
            return (
                f"skip {path}: settings.json too large; add hooks.SessionStart/"
                "PreToolUse/Stop manually (templates/editor-graph-hooks/README.md)"
            )
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return (
                f"skip {path}: not strict JSON (JSONC?). Add hooks segment manually — "
                "templates/editor-graph-hooks/README.md"
            )
        if not isinstance(data, dict):
            return f"FAIL {path}: not an object"
    data["hooks"] = merge_hooks_obj(data.get("hooks") or {}, _qoder_groups())
    write_json(path, data)
    return f"ok {path}"


def main() -> int:
    reports = [
        merge_trae(HOME / ".trae-cn" / "hooks.json"),
        merge_trae(HOME / ".trae" / "hooks.json"),
        merge_qoder_settings(HOME / ".qoder-cn" / "settings.json"),
        merge_qoder_settings(HOME / ".qoder" / "settings.json"),
    ]
    failed = [r for r in reports if r.startswith("FAIL")]
    for line in reports:
        print(line)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
