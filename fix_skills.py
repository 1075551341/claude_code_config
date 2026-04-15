#!/usr/bin/env python3
import os, re
from pathlib import Path

fixed = []
for skill_dir in Path(".").iterdir():
    if not skill_dir.is_dir():
        continue
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        continue
    skill_name = skill_dir.name
    content = skill_file.read_text(encoding="utf-8")
    if re.search(r"^triggers:", content, re.MULTILINE):
        continue
    match = re.search(r"^description:\s*(.+?)\n", content, re.MULTILINE)
    if not match:
        continue
    desc = match.group(1).strip()
    clean_desc = re.sub(r"当需要|时调用此技能|触发词[：:]\s*", "", desc)
    triggers = re.split(r"[,，、\s]+", clean_desc)
    triggers = [t.strip() for t in triggers if t.strip() and 1 < len(t) < 20]
    triggers = triggers[:6]
    if not triggers:
        triggers = [skill_name.replace("-", " ")]
    triggers_str = ", ".join(triggers)
    new_content = re.sub(
        r"^(description:\s*.+?\n)",
        "\1triggers: [" + triggers_str + "]\n",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    skill_file.write_text(new_content, encoding="utf-8")
    fixed.append(skill_name)

print(f"Fixed {len(fixed)} skills")
for name in sorted(fixed):
    print(f"  - {name}")
