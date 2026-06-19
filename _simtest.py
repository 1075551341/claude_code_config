#!/usr/bin/env python3
import json, os, re, subprocess, sys
from pathlib import Path
BASE = Path(os.environ['USERPROFILE']) / '.claude'
PASS = [0]; FAIL = [0]; WARN = [0]
def ok(m): PASS[0]+=1; print(f'  [PASS] {m}')
def err(m): FAIL[0]+=1; print(f'  [FAIL] {m}')
def warn(m): WARN[0]+=1; print(f'  [WARN] {m}')
def read(p):
    try: return Path(p).read_text(encoding='utf-8')
    except: return None

print("="*60)
print("  S1: L0 alwaysApply entry files")
print("="*60)
r = read(BASE/"CLAUDE-ROUTER.mdc")
ok("CLAUDE-ROUTER.mdc") if r and "alwaysApply: true" in r and "P0" in r else err("CLAUDE-ROUTER.mdc")

c = read(BASE/"CLAUDE.md")
ok("CLAUDE.md") if c and "alwaysApply: true" in c and "SSOT" in c and "R1" in c else err("CLAUDE.md")

co = read(BASE/"rules"/"CORE.md")
ok("CORE.md") if co and "alwaysApply: true" in co and "R12" in co else err("CORE.md")

# S2: INDEX vs disk verification
print()
print("="*60)
print("  S2: INDEX vs disk completeness")
print("="*60)
for idx in ["skills-INDEX.md","agents-INDEX.md","rules-INDEX.md"]:
    ok(idx) if read(BASE/idx) else err(idx)

# skills
idx_s = set()
for m in re.finditer(r"\[([^\]]+)\]\(skills/([^/]+)/SKILL\.md\)", read(BASE/"skills-INDEX.md") or ""):
    idx_s.add(m.group(2))
disk_s = {d.name for d in (BASE/"skills").iterdir() if d.is_dir() and (d/"SKILL.md").exists()}
ok(f"skills INDEX==disk ({len(idx_s)})") if idx_s==disk_s else err(f"skills mismatch: +{idx_s-disk_s} -{disk_s-idx_s}")

# agents  
idx_a = {m.group(1) for m in re.finditer(r"\[([^\]]+)\]\(agents/([^)]+\.md)\)", read(BASE/"agents-INDEX.md") or "")}
disk_a = {f.stem for f in (BASE/"agents").iterdir() if f.suffix==".md" and f.name!="README.md"}
ok(f"agents INDEX==disk ({len(idx_a)})") if idx_a==disk_a else err(f"agents mismatch: +{idx_a-disk_a} -{disk_a-idx_a}")
