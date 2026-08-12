"""生成 catalog/INDEX.md — catalog 128 项此前无索引，导致「找不到就重造」。

命令：
    python scripts/gen-catalog-index.py     # 唯一用法，无参数；覆盖写 catalog/INDEX.md

新增/删除 catalog 下的 skill / agent / rule 后重跑本脚本。同名项（顶层权威 vs catalog 变体）
会自动进消歧表，无需手工维护。生成后如需把某项落到项目：
    python scripts/migrate-from-legacy.py --project <路径> --skill <名字>
"""
import os
import re

base = os.path.expanduser("~/.claude")


def read_front(path):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return ""
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    block = m.group(1) if m else text[:400]
    d = re.search(r"^description:\s*(.+)$", block, re.M)
    if d:
        return d.group(1).strip().strip("\"'")
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "-", "---")):
            return line
    return ""


def collect(kind):
    root = os.path.join(base, "catalog", kind)
    out = []
    for name in sorted(os.listdir(root)):
        p = os.path.join(root, name)
        if os.path.isdir(p):
            skill = os.path.join(p, "SKILL.md")
            if os.path.exists(skill):
                out.append((name, read_front(skill)))
        elif name.endswith(".md") and name != "README.md":
            out.append((name[:-3], read_front(p)))
    return out


def authoritative(kind):
    root = os.path.join(base, kind)
    names = set()
    for name in os.listdir(root):
        p = os.path.join(root, name)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "SKILL.md")):
            names.add(name)
        elif name.endswith(".md") and name not in ("README.md", "SKILL.md"):
            names.add(name[:-3])
    return names


skills = collect("skills")
agents = collect("agents")
rules = collect("rules")
auth_s, auth_a, auth_r = authoritative("skills"), authoritative("agents"), authoritative("rules")

dup_s = sorted(n for n, _ in skills if n in auth_s)
dup_a = sorted(n for n, _ in agents if n in auth_a)
dup_r = sorted(n for n, _ in rules if n in auth_r or n.replace(".md", "") in auth_r)

lines = []
lines.append("# Catalog INDEX — 变体库一页式清单")
lines.append("")
lines.append("> **权威 vs 变体**：`skills/` `agents/` `rules/` 是权威实现，会被路由加载；")
lines.append("> 本目录是**变体库**，不参与全局加载，只在 `migrate-from-legacy.py --skill|--agent|--rule`")
lines.append("> 复制到项目 `.claude/` 时使用。同名项一律以顶层权威版为准。")
lines.append("")
lines.append(f"规模：skills {len(skills)} / agents {len(agents)} / rules {len(rules)}")
lines.append("")
lines.append("## 同名项消歧（权威在顶层，此处为变体，勿加载）")
lines.append("")
lines.append("| 类型 | 同名项 |")
lines.append("| ---- | ------ |")
lines.append(f"| skills | {', '.join(f'`{n}`' for n in dup_s) or '（无）'} |")
lines.append(f"| agents | {', '.join(f'`{n}`' for n in dup_a) or '（无）'} |")
lines.append(f"| rules | {', '.join(f'`{n}`' for n in dup_r) or '（无）'} |")
lines.append("")

for title, items, dups in (
    ("Skills", skills, set(dup_s)),
    ("Agents", agents, set(dup_a)),
    ("Rules", rules, set(dup_r)),
):
    lines.append(f"## {title}（{len(items)}）")
    lines.append("")
    lines.append("| 名称 | 说明 |")
    lines.append("| ---- | ---- |")
    for name, desc in items:
        desc = re.sub(r"\s+", " ", desc)[:88]
        mark = " ⚠️变体" if name in dups else ""
        lines.append(f"| `{name}`{mark} | {desc} |")
    lines.append("")

lines.append("---")
lines.append("")
lines.append("v10.17.0 · 由 `scripts/gen-catalog-index.py` 生成，新增/删除 catalog 项后重跑该脚本")
open(os.path.join(base, "catalog", "INDEX.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("skills", len(skills), "agents", len(agents), "rules", len(rules))
print("dups skills:", dup_s)
print("dups agents:", dup_a)
print("dups rules:", dup_r)
