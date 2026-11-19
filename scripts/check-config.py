#!/usr/bin/env python3
"""Read-only checks for the local configuration's contracts, not fixed file counts."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDIT_PROBE = ("Edit", "Write", "MultiEdit", "NotebookEdit", "mcp__serena__replace_symbol_body", "mcp__filesystem__write_file")
HOOKS = {"pre-bash-guard.py": ("PreToolUse",5), "pre-encoding-snapshot.py": ("PreToolUse",5), "post-encoding-check.py": ("PostToolUse",10), "post-secret-detector.py": ("PostToolUse",10)}
CROSS_TOOL = re.compile(r"(?:[A-Za-z]:[/\\]Users[/\\][^/\\\s]+|~)[/\\](?:\.codex|\.agents|\.cursor|\.qoder(?:-cn)?|\.trae(?:-cn)?|\.dsh|\.openchamber|\.config[/\\]opencode)(?:[/\\]|\b)", re.I)
MODEL = re.compile(r"\b(?:claude-(?:opus|sonnet|haiku)-[\w.-]+|gpt-[0-9][\w.-]*|gemini-\d[\w.-]*|deepseek-chat|kimi-k2)\b", re.I)
SECRET = re.compile(r"(?:sk-ant-[A-Za-z0-9_-]{20,}|\bgh[pousr]_[A-Za-z0-9]{25,}|\bsk-[A-Za-z0-9_-]{32,})")
RETIRED = ("skills/task-triage/", "skills/brainstorming/", "skills/writing-plans/", "skills/executing-plans/", "skills/change-impact-analysis/", "skills/skill-router/", "skills/ship/", "rules/CORE.md", "rules/DELEGATION.md", "rules/MCP.md", "rules/SECURITY.md", "check-adapters.py", "templates/harness-adapter.md")
INDEX_HEADING = re.compile(r"^## (技能|角色|规则)（(\d+)）\s*$")


def frontmatter(path: Path) -> dict[str,str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return {}
    if "---" not in lines[1:]:
        raise ValueError("unclosed frontmatter")
    result={}
    for line in lines[1:lines[1:].index("---")+1]:
        match=re.match(r"^([\w-]+):\s*(.*)$",line)
        if match: result[match[1]]=match[2].strip().strip("\"'")
    return result


def hook_records(settings: dict) -> list[tuple[str,str,str,int]]:
    out=[]
    for event,groups in settings.get("hooks",{}).items():
        if not isinstance(groups,list): raise ValueError("hook event must contain a list")
        for group in groups:
            matcher=group.get("matcher","")
            re.compile(matcher)
            for hook in group.get("hooks",[]):
                if hook.get("type") != "command": raise ValueError("expected local command hook")
                command=hook.get("command","")
                match=re.search(r'(?:"([^"\n]+\.py)"|([^\s"\n]+\.py))',command)
                if not match: raise ValueError("hook has no script path")
                script=match[1] or match[2]
                timeout=hook.get("timeout")
                if not isinstance(timeout,int) or isinstance(timeout,bool) or not 1<=timeout<=30: raise ValueError("hook timeout must use bounded seconds")
                out.append((event,matcher,script,timeout))
    return out


def active_texts(root: Path) -> list[Path]:
    paths=[root/n for n in ("CLAUDE.md","README.md")]
    for folder in ("skills","agents","commands","rules","templates","snippets"):
        paths.extend((root/folder).rglob("*.md"))
    paths.extend(root/p for p in ("hooks/README.md","scripts/README.md"))
    return sorted({p for p in paths if p.is_file()})


def check(root: Path) -> tuple[list[str],list[str]]:
    errors=[]; warnings=[]
    def require(condition: bool, message: str):
        if not condition: errors.append(message)
    names={}
    skillpaths=sorted((root/"skills").glob("*/SKILL.md"))
    require(bool(skillpaths),"no discoverable skills")
    for path in skillpaths:
        rel=path.relative_to(root)
        try: meta=frontmatter(path)
        except (OSError,ValueError): errors.append(f"invalid skill metadata: {rel}");continue
        name=meta.get("name","")
        require(bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",name)) and len(name)<=64,f"invalid skill name: {rel}")
        require(name==path.parent.name,f"skill directory/name mismatch: {rel}")
        require(0<len(meta.get("description",""))<=1024,f"missing/oversized description: {rel}")
        require(name not in names,f"duplicate skill: {name}");names[name]=path
        body=path.read_text(encoding="utf-8")
        require("1%" not in body and "每个任务必审" not in meta.get("description",""),f"overbroad trigger: {rel}")
        if name=="test-driven-development":require("显式" in meta.get("description","") or "explicit" in meta.get("description","").lower(),"TDD must be explicitly invoked")
    for folder in ("agents","commands"):
        for path in (root/folder).glob("*.md"):
            try:meta=frontmatter(path)
            except (OSError,ValueError): errors.append(f"invalid metadata: {path.relative_to(root)}");continue
            require(bool(meta.get("description")),f"missing description: {path.relative_to(root)}")
            if folder=="agents":require(meta.get("name")==path.stem,f"agent name mismatch: {path.name}")
    require((root/"CLAUDE.md").is_file(), "missing entry: CLAUDE.md")
    require(not (root/"AGENTS.md").exists(), "remove global AGENTS.md; Claude uses CLAUDE.md")
    if (root/"CLAUDE.md").exists():
        require("@AGENTS.md" not in (root/"CLAUDE.md").read_text(encoding="utf-8"), "Claude entry must be self-contained without @AGENTS.md")
    for path in active_texts(root):
        text=path.read_text(encoding="utf-8");rel=path.relative_to(root)
        require(not CROSS_TOOL.search(text),f"cross-tool runtime dependency: {rel}")
        require(not MODEL.search(text),f"model binding in active instructions: {rel}")
        require(not SECRET.search(text),f"credential-like literal in active instructions: {rel}")
        for old in RETIRED: require(old not in text,f"retired reference in {rel}: {old}")
        # Check only concrete local paths; examples with placeholders are not references.
        for value in re.findall(r'`((?:skills|agents|commands|rules|hooks|scripts|tools)/[^`\s]+\.(?:md|py|ps1|json))`',text):
            if any(token in value for token in ("<",">","*","{","...")):continue
            require((root/value).is_file(),f"broken local reference in {rel}: {value}")
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if re.match(r"[A-Za-z][\w+.-]*:",target) or target.startswith(("#","/","~")) or any(c in target for c in "<>*{} "): continue
            target=target.split("#",1)[0]
            if target and not target.startswith("../"):
                require((path.parent/target).exists(),f"broken markdown link in {rel}")
    records={}
    for filename in ("settings.example.json","settings.json"):
        path=root/filename
        if not path.exists():
            if filename=="settings.json":warnings.append("local settings absent; example is not activation")
            else:errors.append("settings.example.json missing")
            continue
        try:
            config=json.loads(path.read_text(encoding="utf-8"));rows=hook_records(config)
            require("autoCompactWindow" not in config,"remove fixed context window override")
            require(set(config.get("hooks",{}))=={"PreToolUse","PostToolUse"},f"unexpected automatic hook events: {filename}")
            byname={Path(script).name:(event,matcher,timeout) for event,matcher,script,timeout in rows}
            require(len(byname)==len(rows),f"duplicate hook registration: {filename}")
            require(set(byname)==set(HOOKS),f"missing or unexpected default hook capability: {filename}")
            for name,(event,timeout) in HOOKS.items():
                row=byname.get(name)
                require(bool(row) and row[0]==event and row[2]==timeout,f"wrong hook event/timeout: {filename}:{name}")
                require((root/"hooks"/name).is_file(),f"missing hook implementation: {name}")
                if row:
                    probes=("Bash","PowerShell","Shell") if name=="pre-bash-guard.py" else EDIT_PROBE
                    for tool in probes:require(bool(re.fullmatch(row[1],tool)),f"hook misses {tool}: {filename}:{name}")
            for event,matcher,script,timeout in rows:
                if filename=="settings.json":require(Path(script).is_file(),f"local hook path missing: {Path(script).name}")
            records[filename]=[(e,m,Path(s).name,t) for e,m,s,t in rows]
        except (OSError,ValueError,TypeError,AttributeError) as exc:errors.append(f"invalid hook config {filename}: {type(exc).__name__}")
    if len(records)==2:require(records['settings.json']==records['settings.example.json'],"example/local hook behavior differs")
    for path in [root/".mcp.json",*(root/"mcp-configs").glob("*.json")]:
        if path.name.endswith('.private.json'):continue
        try:
            config=json.loads(path.read_text(encoding="utf-8"));servers=config.get("mcpServers",{})
            require(isinstance(servers,dict),f"invalid server map: {path.name}")
            if path.name==".mcp.json":require(not servers,"project MCP defaults must remain opt-in")
            for name,server in servers.items():
                require(isinstance(server,dict) and bool(server.get('command') or server.get('url')),f"MCP missing launcher: {path.name}:{name}")
                if not isinstance(server,dict):continue
                serialized=json.dumps(server)
                require(not CROSS_TOOL.search(serialized),f"cross-tool MCP launcher: {path.name}:{name}")
                require(not SECRET.search(serialized),f"credential-like literal in public MCP config: {path.name}:{name}")
                for key,value in server.get('env',{}).items():
                    if re.search(r"(?:TOKEN|SECRET|PASSWORD|API_?KEY)",key,re.I) and value:
                        require(isinstance(value,str) and bool(re.fullmatch(r"\$\{[A-Za-z_][A-Za-z0-9_]*(?::-[^}]*)?\}",value)),f"credential environment value must be a reference: {path.name}:{name}")
                require('${workspaceFolder}' not in json.dumps(server),f"unsupported workspace placeholder: {path.name}:{name}")
                if server.get('url'):require(server.get('type') in {'http','sse'},f"remote MCP needs explicit transport: {path.name}:{name}")
        except (OSError,ValueError,TypeError,AttributeError) as exc:errors.append(f"invalid MCP config {path.name}: {type(exc).__name__}")
    check_catalog_index(root, require)
    return errors,warnings


def check_catalog_index(root: Path, require) -> None:
    catalog = root/"catalog"
    if not catalog.is_dir():
        return
    index = catalog/"INDEX.md"
    require(index.is_file(), "missing catalog/INDEX.md")
    if not index.is_file():
        return
    text = index.read_text(encoding="utf-8")
    claimed = {match.group(1): int(match.group(2)) for match in (INDEX_HEADING.match(line) for line in text.splitlines()) if match}
    require(set(claimed)=={"技能","角色","规则"}, "catalog INDEX missing count headings")
    skills_disk = {path.parent.name for path in (root/"catalog"/"skills").glob("*/SKILL.md")}
    agents_disk = {path.stem for path in (root/"catalog"/"agents").glob("*.md") if path.name.lower()!="readme.md"}
    rules_disk = {path.stem for path in (root/"catalog"/"rules").glob("*.md") if path.name.lower()!="readme.md"}
    skills_idx, agents_idx, rules_idx = set(), set(), set()
    for target in re.findall(r"\]\(([^)]+)\)", text):
        target = target.split("#", 1)[0]
        if target.startswith("skills/") and target.endswith("/SKILL.md"):
            skills_idx.add(Path(target).parts[1])
        elif target.startswith("agents/") and target.endswith(".md") and Path(target).stem.lower()!="readme":
            agents_idx.add(Path(target).stem)
        elif target.startswith("rules/") and target.endswith(".md") and Path(target).stem.lower()!="readme":
            rules_idx.add(Path(target).stem)
    require(claimed.get("技能")==len(skills_disk), f"catalog skill heading {claimed.get('技能')} != disk {len(skills_disk)}")
    require(claimed.get("角色")==len(agents_disk), f"catalog agent heading {claimed.get('角色')} != disk {len(agents_disk)}")
    require(claimed.get("规则")==len(rules_disk), f"catalog rule heading {claimed.get('规则')} != disk {len(rules_disk)}")
    require(skills_idx==skills_disk, "catalog INDEX skill set differs from disk")
    require(agents_idx==agents_disk, "catalog INDEX agent set differs from disk")
    require(rules_idx==rules_disk, "catalog INDEX rule set differs from disk")


def main() -> int:
    errors,warnings=check(ROOT)
    for warning in warnings:print("WARN: "+warning)
    for error in errors:print("FAIL: "+error)
    if errors:return 1
    print("PASS: local references, metadata, hook coverage/timeouts, catalog index and opt-in MCP contracts")
    print("skills=%d agents=%d commands=%d"%(len(list((ROOT/'skills').glob('*/SKILL.md'))),len(list((ROOT/'agents').glob('*.md'))),len(list((ROOT/'commands').glob('*.md')))))
    print("Runtime activation must be checked separately in a fresh native session.")
    return 0


if __name__=="__main__":sys.exit(main())
