#!/usr/bin/env python3
"""Engineering principles merged into the iron laws (R21-R25, 18 sub-rules).

Source of truth: ~/.claude/rules/CORE.md `<!-- engineering-rules:start -->`.
The same R21-R25 section is injected into CLAUDE.md, OpenCode/DSH AGENTS.md and
their CORE.md; Cursor/Qoder/Trae entries inherit from CLAUDE.md and their CORE
copies inherit from rules/CORE.md via sync.ps1.

Usage:
    python scripts/principles.py sync [--dry-run]
    python scripts/principles.py check
    python scripts/principles.py status
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

HOME = Path.home()
CLAUDE = Path(os.environ.get("CLAUDE_HOME") or (HOME / ".claude"))
SOURCE = CLAUDE / "rules" / "CORE.md"
DOC = CLAUDE / "docs" / "ENGINEERING_PRINCIPLES.md"
TEMPLATE = CLAUDE / "templates" / "project-init" / "CLAUDE.md"
STALE_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:R2[6-9]|R3[0-8]|P(?:[4-9]|1[0-8]))(?![0-9])|R21-R38|P1[–-]P18"
)
CLAUDE_ENTRY = CLAUDE / "CLAUDE.md"
OC_AGENTS = HOME / ".config" / "opencode" / "AGENTS.md"
DSH_AGENTS = HOME / ".dsh" / "AGENTS.md"
OC_CORE = HOME / ".config" / "opencode" / "rules" / "CORE.md"
DSH_CORE = HOME / ".dsh" / "rules" / "CORE.md"

SYNC_TARGETS = [CLAUDE_ENTRY, OC_AGENTS, DSH_AGENTS, OC_CORE, DSH_CORE]
REQUIRED_TARGETS = [SOURCE, CLAUDE_ENTRY, OC_AGENTS, DSH_AGENTS, OC_CORE, DSH_CORE]
OPTIONAL_TARGETS = [
    HOME / ".cursor" / "plugins" / "local" / "claude-config" / "rules" / "00-AGENTS.mdc",
    HOME / ".qoder" / "rules" / "AGENTS.md",
    HOME / ".trae" / "user_rules" / "AGENTS.md",
    HOME / ".trae-cn" / "user_rules" / "AGENTS.md",
    HOME / ".cursor" / "plugins" / "local" / "claude-config" / "rules" / "CORE.mdc",
    HOME / ".qoder" / "rules" / "CORE.md",
    HOME / ".trae" / "user_rules" / "CORE.md",
    HOME / ".trae-cn" / "user_rules" / "CORE.md",
]
ALL_TARGETS = REQUIRED_TARGETS + OPTIONAL_TARGETS

START = "<!-- engineering-rules:start -->"
END = "<!-- engineering-rules:end -->"
HEADING = "### 工程原则（R21-R25，按类型合并）"
BUDGET = 17_408  # 17 KiB; platform global budget is 65,536 bytes.
GROUP_NAMES = {
    "R21": "核心思想",
    "R22": "简洁与设计",
    "R23": "架构",
    "R24": "代码质量",
    "R25": "工程决策",
}
GROUP_COUNTS = {"R21": 3, "R22": 3, "R23": 4, "R24": 5, "R25": 3}
EXPECTED_SUBS = {
    (21, 1), (21, 2), (21, 3),
    (22, 1), (22, 2), (22, 3),
    (23, 1), (23, 2), (23, 3), (23, 4),
    (24, 1), (24, 2), (24, 3), (24, 4), (24, 5),
    (25, 1), (25, 2), (25, 3),
}
EXPECTED_GROUPS = len(GROUP_NAMES)
EXPECTED_SUBS_COUNT = len(EXPECTED_SUBS)
EXPECTED_DOC_CONFLICTS = 10  # C1-C10; C8 is docs-only.
EXPECTED_CONFLICTS = EXPECTED_DOC_CONFLICTS - 1
GROUP_RE = re.compile(r"(?m)^#### R(\d+) (核心思想|简洁与设计|架构|代码质量|工程决策)$")
SUB_RE = re.compile(r"(?m)^- \*\*R(\d+)\.(\d+) ")
CONFLICT_RE = re.compile(r"(?m)^\| R\d+\.\d+\s*(?:/|、)")
OLD_BLOCK = "<!-- principles:start -->"
OLD_CORE_PHRASES = (
    "KISS / YAGNI / 依赖克制",
    "DRY + 单一职责",
    "最小改动集；删除过时代码优先于加兼容层",
    "依赖克制：先用已有依赖与能力",
)


def read_text(path: Path) -> tuple[str, bool, bool]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    lf_count = raw.count(b"\n")
    crlf_count = raw.count(b"\r\n")
    crlf = crlf_count > (lf_count - crlf_count)
    return raw.decode("utf-8-sig"), crlf, bom


def encoded_size(text: str, crlf: bool, bom: bool) -> int:
    text = text.replace("\r\n", "\n")
    data = text.encode("utf-8")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    if bom:
        data = b"\xef\xbb\xbf" + data
    return len(data)


def write_text(path: Path, text: str, crlf: bool, bom: bool) -> None:
    text = text.replace("\r\n", "\n")
    data = text.encode("utf-8")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    if bom:
        data = b"\xef\xbb\xbf" + data
    path.write_bytes(data)


def extract_block(text: str) -> str | None:
    start = text.find(START)
    end = text.find(END)
    if start < 0 or end < 0 or end < start:
        return None
    return text[start:end + len(END)].replace("\r\n", "\n")


def block_span_ok(text: str) -> bool:
    """A block must not swallow a following H2 section."""
    start = text.find(START)
    end = text.find(END)
    if start < 0 or end < start:
        return False
    return "\n## " not in text[start:end]


def validate_block(block: str) -> list[str]:
    errors: list[str] = []
    groups = GROUP_RE.findall(block)
    group_ids = {f"R{gid}" for gid, _ in groups}
    if len(groups) != EXPECTED_GROUPS:
        errors.append(f"R groups {len(groups)} != {EXPECTED_GROUPS}")
    if group_ids != set(GROUP_NAMES):
        errors.append(f"R group ids {sorted(group_ids)} != R21-R25")
    for gid, name in groups:
        if GROUP_NAMES.get(f"R{gid}") != name:
            errors.append(f"R{gid} group name {name!r} != {GROUP_NAMES.get(f'R{gid}')!r}")

    current_group = None
    section_order: list[str] = []
    section_counts: dict[str, int] = {}
    for line in block.splitlines():
        if line.startswith("#### "):
            gm = GROUP_RE.match(line)
            if gm:
                current_group = f"R{gm.group(1)}"
                section_order.append(current_group)
                section_counts.setdefault(current_group, 0)
            else:
                current_group = None
            continue
        sm = SUB_RE.match(line)
        if sm:
            gid = f"R{sm.group(1)}"
            if current_group != gid:
                errors.append(
                    f"sub-rule R{sm.group(1)}.{sm.group(2)} under {current_group or 'no group'}"
                )
            section_counts[current_group] = section_counts.get(current_group, 0) + 1
    if section_order != list(GROUP_NAMES):
        errors.append(f"R group order {section_order} != {list(GROUP_NAMES)}")
    if section_counts != GROUP_COUNTS:
        errors.append(f"R section counts {section_counts} != {GROUP_COUNTS}")

    subs = SUB_RE.findall(block)
    sub_ids = {(int(gid), int(sid)) for gid, sid in subs}
    if len(subs) != EXPECTED_SUBS_COUNT:
        errors.append(f"R sub-rules {len(subs)} != {EXPECTED_SUBS_COUNT}")
    if sub_ids != EXPECTED_SUBS:
        errors.append(f"R sub ids {sorted(sub_ids)} != expected")
    if [(int(gid), int(sid)) for gid, sid in subs] != sorted(EXPECTED_SUBS):
        errors.append("R sub-rules out of order")
    if HEADING not in block:
        errors.append(f"missing heading {HEADING}")

    conflict_rows = CONFLICT_RE.findall(block)
    if len(conflict_rows) != EXPECTED_CONFLICTS:
        errors.append(f"conflict rows {len(conflict_rows)} != {EXPECTED_CONFLICTS}")
    pairs = [
        line.split("|")[1].strip()
        for line in block.splitlines()
        if CONFLICT_RE.match(line)
    ]
    if len(pairs) != len(set(pairs)):
        errors.append("duplicate conflict row")
    conflict_refs = set()
    for line in block.splitlines():
        if CONFLICT_RE.match(line):
            conflict_refs.update(
                (int(gid), int(sid)) for gid, sid in re.findall(r"R(\d+)\.(\d+)", line)
            )
    missing_refs = conflict_refs - EXPECTED_SUBS
    if missing_refs:
        errors.append(f"conflict refs missing: {sorted(missing_refs)}")

    if OLD_BLOCK in block or "P1–P18" in block:
        errors.append("old P namespace still present")
    if "docs/ENGINEERING_PRINCIPLES.md" not in block:
        errors.append("missing doc pointer")
    return errors


def strip_old_p_block(text: str) -> str | None:
    start = text.find(OLD_BLOCK)
    end = text.find("<!-- principles:end -->")
    if start < 0 and end < 0:
        return text
    if (start < 0 or end < 0 or end < start
            or text.count(OLD_BLOCK) > 1
            or text.count("<!-- principles:end -->") > 1):
        return None
    return text[:start] + text[end + len("<!-- principles:end -->"):]


def replace_block(text: str, block: str) -> str | None:
    start = text.find(START)
    end = text.find(END)
    if start >= 0 and end >= start:
        return text[:start] + block + text[end + len(END):]
    return None


def migrate_block(text: str, block: str, path: Path) -> str | None:
    """One-time migration: drop the old P block, insert R21-R25 under 铁律."""
    old_start = text.find(OLD_BLOCK)
    old_end = text.find("<!-- principles:end -->")
    if old_start >= 0 and old_end > old_start:
        text = text[:old_start] + text[old_end + len("<!-- principles:end -->"):]
    iron = text.find("## 铁律")
    if iron >= 0:
        index = text.find("\n## ", iron + len("## 铁律"))
        if index < 0:
            index = len(text)
    elif path.name == "AGENTS.md":
        index = text.find("\n## 工具门控与路由")
        if index < 0:
            return None
        prefix = text[:index].rstrip("\r\n")
        suffix = text[index:].lstrip("\r\n")
        return prefix + "\n\n## 铁律\n\n" + block + "\n\n" + suffix
    else:
        return None
    prefix = text[:index].rstrip("\r\n")
    suffix = text[index:].lstrip("\r\n")
    return prefix + "\n\n" + block + "\n\n" + suffix


def reposition_block(text: str, block: str, path: Path) -> str | None:
    """Move an existing block under ## 铁律 and normalize surrounding blank lines."""
    start = text.find(START)
    end = text.find(END)
    if start >= 0 and end > start:
        before = text[:start].rstrip("\r\n")
        after = text[end + len(END):].lstrip("\r\n")
        text = before + "\n\n" + after
    if path.name in {"AGENTS.md", "CORE.md"}:
        iron = text.find("## 铁律")
        if iron < 0:
            return None
        index = text.find("\n## ", iron + len("## 铁律"))
        if index < 0:
            index = len(text)
    else:
        anchor = "\n## 工具门控"
        index = text.find(anchor)
        if index < 0:
            return None
    prefix = text[:index].rstrip("\r\n")
    suffix = text[index:].lstrip("\r\n")
    return prefix + "\n\n" + block + "\n\n" + suffix


def block_under_iron_law(text: str) -> bool:
    start = text.find(START)
    if start < 0:
        return False
    before = text[:start]
    index = before.rfind("\n## ")
    if index < 0:
        return False
    heading = before[index + 1:].splitlines()[0].strip()
    return heading == "## 铁律" or heading.startswith("## 铁律（")


def sync(dry_run: bool) -> int:
    if not SOURCE.exists():
        print(f"ERROR: source missing: {SOURCE}", file=sys.stderr)
        return 1
    text, _, _ = read_text(SOURCE)
    if (text.count(START) != 1 or text.count(END) != 1
            or OLD_BLOCK in text or "<!-- principles:end -->" in text):
        print(f"ERROR: source has malformed/duplicate markers: {SOURCE}", file=sys.stderr)
        return 1
    if not block_under_iron_law(text):
        print(f"ERROR: source block is not under ## 铁律: {SOURCE}", file=sys.stderr)
        return 1
    if not block_span_ok(text):
        print(f"ERROR: source block spans a following ## section: {SOURCE}", file=sys.stderr)
        return 1
    floor = text.find("\n## 工具链地板")
    if floor >= 0 and text.find(START) > floor:
        print(f"ERROR: source block must be before ## 工具链地板: {SOURCE}", file=sys.stderr)
        return 1
    block = extract_block(text)
    if not block:
        print(f"ERROR: source block missing: {SOURCE}", file=sys.stderr)
        return 1
    errors = validate_block(block)
    if errors:
        for error in errors:
            print(f"ERROR: source block: {error}", file=sys.stderr)
        return 1

    pending: list[tuple[Path, str, bool, bool]] = []
    for path in SYNC_TARGETS:
        if not path.exists():
            print(f"ERROR: missing required target: {path}", file=sys.stderr)
            return 1
        original, crlf, bom = read_text(path)
        if OLD_BLOCK in original and "<!-- principles:end -->" not in original:
            print(f"ERROR: malformed old P block (missing end): {path}", file=sys.stderr)
            return 1
        if "<!-- principles:end -->" in original and OLD_BLOCK not in original:
            print(f"ERROR: malformed old P block (missing start): {path}", file=sys.stderr)
            return 1
        current = strip_old_p_block(original)
        if current is None:
            print(f"ERROR: malformed old P block (order/duplicate): {path}", file=sys.stderr)
            return 1
        if (current.count(START) > 1 or current.count(END) > 1
                or current.count(START) != current.count(END)
                or (current.count(START) == 1
                    and current.find(START) > current.find(END))):
            print(f"ERROR: invalid principles markers: {path}", file=sys.stderr)
            return 1
        if current.count(START) == 1 and current.count(END) == 1 and not block_span_ok(current):
            print(f"ERROR: target block spans a following ## section: {path}", file=sys.stderr)
            return 1
        if path.name == "CORE.md":
            updated = reposition_block(current, block, path)
            if updated is None:
                updated = migrate_block(current, block, path)
        else:
            updated = replace_block(current, block)
            if updated is None:
                updated = migrate_block(current, block, path)
        if updated is None:
            print(f"ERROR: missing principles markers: {path}", file=sys.stderr)
            return 1
        if updated.count(START) != 1 or updated.count(END) != 1:
            print(f"ERROR: update would break markers: {path}", file=sys.stderr)
            return 1
        if OLD_BLOCK in updated or "<!-- principles:end -->" in updated:
            print(f"ERROR: update would leave old P markers: {path}", file=sys.stderr)
            return 1
        if not block_span_ok(updated):
            print(f"ERROR: update would make block span a following ## section: {path}", file=sys.stderr)
            return 1
        if not block_under_iron_law(updated):
            print(f"ERROR: update would place block outside ## 铁律: {path}", file=sys.stderr)
            return 1
        if updated.replace("\r\n", "\n") == original.replace("\r\n", "\n"):
            print(f"unchanged: {path}")
            continue
        size = encoded_size(updated, crlf, bom)
        if path.name == "AGENTS.md" and size > BUDGET:
            print(f"ERROR: {path} would be {size} > {BUDGET} bytes; abort", file=sys.stderr)
            return 1
        pending.append((path, updated, crlf, bom))

    changed = 0
    for path, updated, crlf, bom in pending:
        changed += 1
        if dry_run:
            print(f"would update: {path}")
        else:
            write_text(path, updated, crlf, bom)
            print(f"updated: {path}")

    if dry_run:
        print("dry-run: no files written")
    else:
        print(f"sync complete: {changed} file(s) updated")
    return 0


def check() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not SOURCE.exists():
        print(f"ERROR: source missing: {SOURCE}", file=sys.stderr)
        return 1
    source_text, _, _ = read_text(SOURCE)
    if OLD_BLOCK in source_text or "<!-- principles:end -->" in source_text:
        errors.append("source: old P markers present")
    source_block = extract_block(source_text)
    if not source_block:
        print(f"ERROR: source block missing: {SOURCE}", file=sys.stderr)
        return 1
    for error in validate_block(source_block):
        errors.append(f"source: {error}")
    if source_text.count(START) != 1 or source_text.count(END) != 1:
        errors.append("source: markers must appear exactly once")
    if not block_under_iron_law(source_text):
        errors.append("source: R21-R25 block is not under ## 铁律")
    if not block_span_ok(source_text):
        errors.append("source: R21-R25 block spans a following ## section")
    floor = source_text.find("\n## 工具链地板")
    if floor >= 0 and source_text.find(START) > floor:
        errors.append("source: R21-R25 block must be before ## 工具链地板")

    if not DOC.exists():
        errors.append(f"missing doc: {DOC}")
    else:
        doc_text, _, _ = read_text(DOC)
        doc_subs = {(int(gid), int(sid)) for gid, sid in SUB_RE.findall(doc_text)}
        if doc_subs != EXPECTED_SUBS:
            errors.append(f"doc: R sub ids {sorted(doc_subs)} != expected")
        doc_conflicts = {int(x) for x in re.findall(r"(?m)^### C(\d+) ", doc_text)}
        if doc_conflicts != set(range(1, EXPECTED_DOC_CONFLICTS + 1)):
            errors.append(
                f"doc: C1-C{EXPECTED_DOC_CONFLICTS} headings "
                f"{sorted(doc_conflicts)} != 1..{EXPECTED_DOC_CONFLICTS}"
            )
        if "裁决" not in doc_text:
            errors.append("doc: missing conflict decisions")

    for path in ALL_TARGETS:
        if not path.exists():
            if path in REQUIRED_TARGETS:
                errors.append(f"missing required target: {path}")
            else:
                warnings.append(f"missing optional target: {path}")
            continue
        text, _, _ = read_text(path)
        if OLD_BLOCK in text:
            errors.append(f"{path}: old principles block still present")
        if "<!-- principles:end -->" in text and OLD_BLOCK not in text:
            errors.append(f"{path}: orphan old principles:end marker")
        block = extract_block(text)
        if not block:
            errors.append(f"missing engineering-rules block: {path}")
            continue
        if text.count(START) != 1 or text.count(END) != 1:
            errors.append(f"{path}: markers must appear exactly once")
        if not block_span_ok(text):
            errors.append(f"{path}: block spans a following ## section")
        if not block_under_iron_law(text):
            errors.append(f"{path}: R21-R25 block is not under ## 铁律")
        if path.name == "CORE.md":
            floor = text.find("\n## 工具链地板")
            if floor >= 0 and text.find(START) > floor:
                errors.append(f"{path}: R21-R25 block must be before ## 工具链地板")
        for error in validate_block(block):
            errors.append(f"{path}: {error}")
        if block != source_block:
            errors.append(f"{path}: R21-R25 block drifted from source")

    for path in (SOURCE, OC_CORE, DSH_CORE):
        if not path.exists():
            continue
        text, _, _ = read_text(path)
        for phrase in OLD_CORE_PHRASES:
            if phrase in text:
                errors.append(f"{path}: old duplicate principle phrase: {phrase}")

    for path in [*ALL_TARGETS, TEMPLATE]:
        if not path.exists():
            continue
        text, _, _ = read_text(path)
        match = STALE_RE.search(text)
        if match:
            errors.append(f"{path}: stale rule id: {match.group(0)}")

    for path in (OC_AGENTS, DSH_AGENTS):
        if path.exists():
            size = path.stat().st_size
            if size > BUDGET:
                errors.append(f"{path}: {size} > {BUDGET} bytes")
            elif size > BUDGET - 512:
                warnings.append(f"{path}: close to budget: {size}/{BUDGET}")

    if warnings:
        for warning in warnings:
            print(f"WARN: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    present = sum(1 for path in ALL_TARGETS if path.exists())
    print(f"OK: {present}/{len(ALL_TARGETS)} targets, R21-R25, {EXPECTED_GROUPS} groups, {EXPECTED_SUBS_COUNT} sub-rules, {EXPECTED_CONFLICTS} conflicts")
    return 0


def status() -> int:
    if not SOURCE.exists():
        print(f"ERROR: source missing: {SOURCE}", file=sys.stderr)
        return 1
    text, _, _ = read_text(SOURCE)
    block = extract_block(text)
    if not block:
        print(f"ERROR: source block missing: {SOURCE}", file=sys.stderr)
        return 1
    groups = GROUP_RE.findall(block)
    subs = SUB_RE.findall(block)
    print(f"source: {SOURCE} block={len(block.encode('utf-8'))} bytes")
    print(f"rules: groups={len(groups)} subs={len(subs)} conflicts={len(CONFLICT_RE.findall(block))}")
    for path in ALL_TARGETS:
        if not path.exists():
            print(f"MISSING  {path}")
            continue
        current, _, _ = read_text(path)
        target_block = extract_block(current)
        state = "OK" if target_block == block else ("DRIFT" if target_block else "NO-BLOCK")
        size = path.stat().st_size
        remaining = BUDGET - size if path.name == "AGENTS.md" else 0
        suffix = f" remaining={remaining}" if path.name == "AGENTS.md" else ""
        print(f"{state:8} {size:6} bytes{suffix}  {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Engineering principles R21-R25")
    parser.add_argument("command", choices=["sync", "check", "status"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.command == "sync":
        return sync(args.dry_run)
    if args.command == "check":
        return check()
    return status()


if __name__ == "__main__":
    sys.exit(main())
