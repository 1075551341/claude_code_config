# -*- coding: utf-8 -*-
"""capability_resolver：Cursor scrape 降级与 interrupt。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HOOKS_DIR / "_lib"))

import capability_resolver as cr  # noqa: E402

PASSED: list[str] = []
FAILED: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASSED if cond else FAILED).append(name)
    mark = "OK " if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail and not cond else ""))


def main() -> int:
    print("=== capability_resolver tests ===")
    data = cr.load_capabilities()
    check("yaml loads", data is not None)
    if not data:
        print(f"passed={len(PASSED)} failed={len(FAILED)}")
        return 1 if FAILED else 0

    cursor_scrape = cr.resolve_capability("web_scrape", "cursor", data)
    check("cursor scrape provider none", cursor_scrape["provider"] == "none")
    check("cursor scrape fallback web_search", cursor_scrape["fallback"] == "web_search")
    check("cursor scrape usable via fallback", cursor_scrape["usable"] is True)

    cc_scrape = cr.resolve_capability("web_scrape", "claude-code", data)
    check("claude scrape plugin", cc_scrape["provider"] == "plugin")
    check("claude scrape name firecrawl", cc_scrape["name"] == "firecrawl")

    unknown = cr.resolve_capability("not_a_cap", "cursor", data)
    check("unknown interrupts", unknown["interrupt"] is True and unknown["usable"] is False)
    msg = cr.format_interrupt(cursor_scrape)
    check("fallback interrupt text", "fallback" in msg and "web_search" in msg)

    print(f"passed={len(PASSED)} failed={len(FAILED)}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    os.environ.setdefault("CLAUDE_HOME", str(HOOKS_DIR.parent))
    sys.exit(main())
