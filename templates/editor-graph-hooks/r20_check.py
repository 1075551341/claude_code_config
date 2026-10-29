#!/usr/bin/env python3
"""Portable R20 replay check — imports hooks/_lib/r20_replay.py (SSOT).

Do not fork field regex here. Deploy copies r20_replay.py next to this file
(and/or keep ~/.claude/hooks/_lib on the machine).

  python r20_check.py                 # stdin text → JSON {ok, reason}
  python r20_check.py --file path.md
Exit 0 = pass, 2 = fail.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_replay_detail():
    here = Path(__file__).resolve().parent
    candidates = [
        here,
        here / "_lib",
        Path.home() / ".claude" / "hooks" / "_lib",
    ]
    if len(here.parts) >= 3 and here.name == "editor-graph-hooks":
        candidates.insert(1, here.parents[1] / "hooks" / "_lib")
    for folder in candidates:
        if (folder / "r20_replay.py").is_file():
            path = str(folder)
            if path not in sys.path:
                sys.path.insert(0, path)
            break
    from r20_replay import replay_detail

    return replay_detail


replay_ok = _load_replay_detail()


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
