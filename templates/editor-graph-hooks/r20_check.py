#!/usr/bin/env python3
"""Portable R20 replay check (no Claude-home import).

SSOT of the rules: ~/.claude/hooks/_lib/r20_replay.py
This copy is for DSH / OpenCode (deploy to ~/.dsh/tools and ~/.config/opencode/scripts).

  python r20_check.py                 # stdin text → JSON {ok, reason}
  python r20_check.py --file path.md
Exit 0 = pass, 2 = fail.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

_REQUIRED = ("遗漏", "错改", "漏改", "原功能", "影响范围")
_EMPTY = {"", ".", "..", "...", "…", "无", "n/a", "na", "none"}
_PATH_RE = re.compile(
    r"(?:[A-Za-z]:)?[\\/][\w.\\/-]+|\S+\.(?:md|mdc|py|ts|tsx|js|json|ya?ml|toml|txt)\b"
)
_FIELD_RE = re.compile(
    r"(?:^|\n)\s*-?\s*(满足|遗漏|错改|漏改|原功能|影响范围|影响面)\s*[：:]\s*(.*?)(?="
    r"(?:\n\s*-?\s*(?:满足|遗漏|错改|漏改|原功能|影响范围|影响面)\s*[：:])|\n结论|$)",
    re.S,
)
_IMPACT_TOKENS = (
    "crg",
    "get_impact_radius",
    "impact",
    "blast-radius",
    "blast radius",
    "影响面",
    "影响范围",
)


def field_value(text: str, name: str) -> str:
    for match in _FIELD_RE.finditer(text):
        if match.group(1) == name:
            return match.group(2).strip()
    return ""


def replay_ok(text: str) -> tuple[bool, str]:
    """Return (ok, reason). Fingerprint coverage is Claude/Cursor-only (req_fingerprint)."""
    if not text or not text.strip():
        return False, "empty"
    if ("会话终验" not in text) and ("R20" not in text):
        return False, "missing R20 marker"
    missing = [token for token in _REQUIRED if token not in text]
    if missing:
        return False, "missing fields: " + ",".join(missing)

    satisfied = field_value(text, "满足")
    if satisfied.strip().lower() in _EMPTY:
        return False, "empty 满足"

    missed = field_value(text, "漏改")
    if not missed:
        return False, "empty 漏改"
    if not ("文档" in missed or "注释" in missed or "无文档影响" in missed or _PATH_RE.search(missed)):
        return False, "漏改 needs 文档/注释/路径"

    original = field_value(text, "原功能")
    if not original:
        return False, "empty 原功能"
    if not any(token in original for token in ("证据", "测试", "冒烟")):
        return False, "原功能 needs 证据/测试/冒烟"

    impact = field_value(text, "影响范围") or field_value(text, "影响面")
    if not impact or impact.strip().lower() in _EMPTY:
        return False, "empty 影响范围"
    lowered = impact.lower()
    if not any(token in lowered for token in _IMPACT_TOKENS):
        return False, "影响范围 needs CRG/get_impact_radius/IMPACT/blast"
    return True, "ok"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check R20 session replay text")
    parser.add_argument("--file", default="", help="read text from file instead of stdin")
    args = parser.parse_args(argv)
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                text = fh.read()
        except OSError as exc:
            payload = {"ok": False, "reason": f"read failed: {exc}"}
            sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
            return 2
    else:
        text = sys.stdin.read()
    ok, reason = replay_ok(text)
    sys.stdout.write(json.dumps({"ok": ok, "reason": reason}, ensure_ascii=False) + "\n")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
