# -*- coding: utf-8 -*-
"""hook_io.parse_hook_json / read_stdin 单元测试。"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parents[2] / "templates" / "cursor-guard" / "hooks" / "_lib"
sys.path.insert(0, str(LIB))

import hook_io as hio  # noqa: E402

PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASSED if cond else FAILED).append(name)
    mark = "OK " if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail and not cond else ""))


def test_parse_variants() -> None:
    payload = {"tool_name": "Grep", "cwd": r"C:\Users\DELL\.claude"}
    compact = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    pretty = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    check("compact", hio.parse_hook_json(compact) == payload)
    check("pretty", hio.parse_hook_json(pretty) == payload)
    check("utf8 bom", hio.parse_hook_json(b"\xef\xbb\xbf" + compact) == payload)
    check("empty", hio.parse_hook_json(b"") == {})
    check("incomplete object is None", hio.parse_hook_json(b"{") is None)
    framed = f"Content-Length: {len(compact)}\r\n\r\n".encode("ascii") + compact
    check("content-length frame", hio.parse_hook_json(framed) == payload)
    extra = compact + b"\n{\"ignored\": true}"
    check("raw_decode trailing extra", hio.parse_hook_json(extra) == payload)
    utf16 = json.dumps(payload).encode("utf-16")
    check("utf-16 bom", hio.parse_hook_json(utf16) == payload)
    check("prefix junk", hio.parse_hook_json(b"debug-hook\n" + pretty) == payload)


def test_read_stdin_pretty_and_bom() -> None:
    payload = {"conversation_id": "abc", "workspace_roots": ["/c:/Users/DELL/.claude"]}
    pretty = json.dumps(payload, indent=2).encode("utf-8")
    old = sys.stdin
    try:
        sys.stdin = io.TextIOWrapper(io.BytesIO(pretty), encoding="utf-8")
        check("read pretty", hio.read_stdin() == payload)
        sys.stdin = io.TextIOWrapper(io.BytesIO(b"\xef\xbb\xbf" + pretty), encoding="utf-8")
        check("read bom pretty", hio.read_stdin() == payload)
        sys.stdin = io.TextIOWrapper(io.BytesIO(b""), encoding="utf-8")
        check("read empty", hio.read_stdin() == {})
    finally:
        sys.stdin = old


def main() -> int:
    print("test_cursor_hook_io")
    test_parse_variants()
    test_read_stdin_pretty_and_bom()
    print(f"  passed={len(PASSED)} failed={len(FAILED)}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
