# -*- coding: utf-8 -*-
"""Normalize frontmatter for 7 L3 skills (v10.5 validate)."""
from __future__ import annotations

import re
from pathlib import Path

SKILLS = [
    "code-refactoring",
    "frontend-design-pattern-applier",
    "frontend-library-advisor",
    "frontend-refactor-proposer",
    "skill-creator",
    "skill-reviewer",
    "test-edge-case-analyzer",
]
BASE = Path.home() / ".claude" / "skills"


def main() -> None:
    for name in SKILLS:
        path = BASE / name / "SKILL.md"
        text = path.read_text(encoding="utf-8").lstrip("\n")
        lines = text.splitlines()
        body_start = None
        for i, line in enumerate(lines):
            if i > 0 and line.startswith("# "):
                body_start = i
                break
        if body_start is None:
            print("NO BODY", name)
            continue
        header = "\n".join(lines[:body_start])

        def grab(key: str) -> str | None:
            m = re.search(rf"^{re.escape(key)}:\s*(.*)$", header, re.M)
            return m.group(1).strip() if m else None

        name_v = grab("name") or name
        desc_m = re.search(r"description:\s*'([^']*)'", header, re.S)
        if desc_m:
            desc = "'" + desc_m.group(1) + "'"
        else:
            desc_m = re.search(r'description:\s*"([^"]*)"', header, re.S)
            if desc_m:
                desc = '"' + desc_m.group(1) + '"'
            else:
                desc = grab("description") or '""'

        license_v = grab("license")
        tags = grab("tags")
        ver_m = re.search(r"version:\s*([0-9.]+)", header)
        version = ver_m.group(1) if ver_m else None

        fm_lines = ["---", f"name: {name_v}", f"description: {desc}"]
        if license_v:
            fm_lines.append(f"license: {license_v}")
        if tags:
            fm_lines.append(f"tags: {tags}")
        if version:
            fm_lines.append("metadata:")
            fm_lines.append(f"  version: {version}")
        fm_lines.append("loading_tier: L3")
        fm_lines.append("disable-model-invocation: true")
        fm_lines.append("---")

        body = "\n".join(lines[body_start:]).lstrip("\n")
        new = "\n".join(fm_lines) + "\n\n" + body
        if not new.endswith("\n"):
            new += "\n"
        path.write_text(new, encoding="utf-8")
        print("fixed", name, "ver", version)


if __name__ == "__main__":
    main()
