#!/usr/bin/env python3
"""Rewrite markdown frontmatter for a target editor using sync-manifest frontmatter_map."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config" / "sync-manifest.json"
FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.S)


def load_map(editor: str) -> dict:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    top = data.get("frontmatter_map") or {}
    if isinstance(top.get(editor), dict):
        return top[editor]
    editors = data.get("editors") or {}
    spec = editors.get(editor) or {}
    fmap = spec.get("frontmatter_map") or {}
    return fmap if isinstance(fmap, dict) else {}


def parse_fm(text: str) -> tuple[dict, str]:
    match = FM_RE.match(text)
    if not match:
        return {}, text
    body = text[match.end():]
    raw = match.group(1)
    meta: dict = {}
    key = None
    acc: list[str] = []
    for line in raw.splitlines():
        if re.match(r"^[A-Za-z0-9_-]+:", line) and not line.startswith(" "):
            if key is not None:
                meta[key] = "\n".join(acc).strip()
            key, rest = line.split(":", 1)
            acc = [rest.strip()]
        else:
            acc.append(line)
    if key is not None:
        meta[key] = "\n".join(acc).strip()
    return meta, body


def dump_fm(meta: dict) -> str:
    lines = ["---"]
    for key, val in meta.items():
        if val is None or val == "":
            continue
        if "\n" in str(val):
            lines.append(f"{key}:")
            for item in str(val).splitlines():
                lines.append(item if item.startswith(" ") or item.startswith("-") else f"  {item}")
        else:
            lines.append(f"{key}: {val}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def transform(meta: dict, fmap: dict, always: bool) -> dict:
    keep = fmap.get("keep") or ["description", "name", "paths", "globs", "alwaysApply", "trigger"]
    rename = fmap.get("rename") or {}
    drop = set(fmap.get("drop") or [])
    add = dict(fmap.get("add") or {})
    out: dict = {}
    for key, val in meta.items():
        dest = rename.get(key, key)
        if dest in drop or key in drop:
            continue
        if keep != ["*"] and dest not in keep and key not in keep:
            continue
        out[dest] = val
    for key, val in add.items():
        if key not in out:
            out[key] = val
    if always and fmap.get("always_key"):
        out[fmap["always_key"]] = fmap.get("always_value", "true")
    if not always and fmap.get("lazy_trigger_key"):
        out.setdefault(fmap["lazy_trigger_key"], fmap.get("lazy_trigger_value", "model_decision"))
    return out


def convert(src: Path, dst: Path, editor: str, always: bool) -> None:
    text = src.read_text(encoding="utf-8")
    meta, body = parse_fm(text)
    fmap = load_map(editor)
    new_meta = transform(meta, fmap, always)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(dump_fm(new_meta) + body.lstrip("\n"), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--dst", required=True)
    parser.add_argument("--editor", required=True)
    parser.add_argument("--always", action="store_true")
    args = parser.parse_args()
    convert(Path(args.src), Path(args.dst), args.editor, args.always)
    return 0


if __name__ == "__main__":
    sys.exit(main())
