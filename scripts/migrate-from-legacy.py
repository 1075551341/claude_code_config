#!/usr/bin/env python3
"""Copy domain skills/agents/rules from catalog/ to project .claude/."""
import argparse
import shutil
from pathlib import Path

CLAUDE = Path.home() / ".claude"
CATALOG = CLAUDE / "catalog"


def copy_item(kind: str, name: str, dest: Path, dry_run: bool) -> None:
    src_dir = CATALOG / kind / name
    src_file = CATALOG / kind / f"{name}.md"
    if kind == "skills":
        src = src_dir if src_dir.is_dir() else None
        dst = dest / "skills" / name
    elif kind == "agents":
        src = src_file if src_file.is_file() else src_dir / ".." / f"{name}.md"
        if not Path(src).exists():
            alt = list((CATALOG / "agents").glob(f"*{name}*"))
            src = alt[0] if alt else None
        dst = dest / "agents" / f"{name}.md"
    else:
        src = CATALOG / "rules" / f"RULES_{name.upper()}.md"
        if not src.exists():
            src = next(CATALOG / "rules").glob(f"*{name}*", None)
        dst = dest / "rules" / f"{name.lower()}.md"

    if src is None or not Path(src).exists():
        print(f"SKIP {kind}/{name}: not found in catalog")
        return
    if dry_run:
        print(f"DRY-RUN copy {src} -> {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if Path(src).is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)
    print(f"OK {kind}/{name} -> {dst}")


def main():
    p = argparse.ArgumentParser(description="Migrate catalog items to project .claude")
    p.add_argument("--project", required=True, help="Project root path")
    p.add_argument("--skill", action="append", default=[])
    p.add_argument("--agent", action="append", default=[])
    p.add_argument("--rule", action="append", default=[])
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    dest = Path(args.project) / ".claude"
    for s in args.skill:
        copy_item("skills", s, dest, args.dry_run)
    for a in args.agent:
        copy_item("agents", a, dest, args.dry_run)
    for r in args.rule:
        copy_item("rules", r, dest, args.dry_run)


if __name__ == "__main__":
    main()
