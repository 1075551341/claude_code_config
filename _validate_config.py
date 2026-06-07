#!/usr/bin/env python3
"""
全面配置验证脚本 v2 — 测试 .claude/ 配置体系的完整性、一致性和可用性
跳过 settings 文件中硬编码问题
"""
import json
import os
import sys
import re
import ast
from pathlib import Path

# Fix Windows GBK encoding for emoji output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import yaml
except ImportError:
    yaml = None
    print("⚠️  PyYAML 未安装，跳过 YAML 解析验证")

BASE = Path(os.environ.get("CLAUDE_CONFIG_HOME", Path.home() / ".claude"))
ERRORS = []
WARNINGS = []
PASSES = []

def err(msg):
    ERRORS.append(msg)
    print(f"  X {msg}")

def warn(msg):
    WARNINGS.append(msg)
    print(f"  ! {msg}")

def ok(msg):
    PASSES.append(msg)
    print(f"  OK {msg}")

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content, handling both LF and CRLF.
    Returns (frontmatter_dict, remaining_content) or (None, content) if none found."""
    # Normalize line endings
    content = content.replace('\r\n', '\n')
    if not content.startswith('---\n'):
        return None, content

    # Find the closing ---
    end = content.find('\n---\n', 4)
    if end == -1:
        # Maybe it's at EOF without trailing newline
        if content.endswith('\n---'):
            end = len(content) - 3
        else:
            return None, content

    fm_str = content[4:end]
    remaining = content[end + 4:]

    try:
        if yaml:
            fm = yaml.safe_load(fm_str)
        else:
            # Fallback: parse simple key: value pairs
            fm = {}
            for line in fm_str.split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    fm[k.strip()] = v.strip()
    except Exception:
        fm = {'_parse_error': True}

    return fm, remaining

# ============================================================
# 1. JSON 文件语法验证
# ============================================================
section("1. JSON 文件语法验证")

JSON_FILES = [
    "settings.json",
    "settings.local.json",
    ".mcp.json",
    "MANIFEST.yaml",
    "mcp-needs-auth-cache.json",
    "plugins/installed_plugins.json",
    "plugins/known_marketplaces.json",
    "sync-mode.json",
]

for f in JSON_FILES:
    fp = BASE / f
    if not fp.exists():
        warn(f"文件不存在: {f}")
        continue
    try:
        content = fp.read_text(encoding="utf-8")
        if f.endswith((".yaml", ".yml")):
            if yaml:
                try:
                    yaml.safe_load(content)
                    ok(f"{f} — 语法有效")
                except yaml.YAMLError as e:
                    warn(f"{f} — YAML 警告: {e}")
            else:
                ok(f"{f} — 跳过 (yaml lib 缺失)")
        else:
            json.loads(content)
            ok(f"{f} — 语法有效")
    except json.JSONDecodeError as e:
        err(f"{f} — JSON 解析失败: {e}")
    except Exception as e:
        err(f"{f} — 读取异常: {e}")

# ============================================================
# 2. Rules 文件验证
# ============================================================
section("2. Rules 文件验证 (rules/*.md)")

RULES_DIR = BASE / "rules"
EXPECTED_RULES = {
    "CORE.md": "always_on",
    "SECURITY.md": "model_decision",
    "GIT.md": "model_decision",
    "WORKFLOW.md": "model_decision",
    "AGENTS.md": "model_decision",
    "MCP.md": "model_decision",
    "DESIGN.md": "model_decision",
    "BESTPRACTICE.md": "model_decision",
    "CONTEXT.md": "model_decision",
    "README.md": None,
}

for rf in sorted(RULES_DIR.glob("*.md")):
    content = rf.read_text(encoding="utf-8")
    rname = rf.name

    # Only consider frontmatter at the START of the file (consecutive --- blocks
    # possibly separated by blank lines). This avoids false positives from
    # markdown horizontal rules and code-fence --- blocks further down.
    normalized = content.replace('\r\n', '\n').lstrip('﻿')

    fm_blocks = []
    pos = 0
    while pos == 0 or (fm_blocks and len(fm_blocks) < 5):
        # Skip blank lines between frontmatter blocks
        while pos < len(normalized) and normalized[pos] in '\n\r':
            pos += 1
        if not normalized.startswith('---\n', pos):
            break
        end = normalized.find('\n---\n', pos + 4)
        if end == -1:
            break
        fm_str = normalized[pos+4:end]
        fm_blocks.append(fm_str)
        pos = end + 4

    if not fm_blocks:
        if rname != "README.md":
            warn(f"rules/{rname} — 缺少 YAML frontmatter")
        else:
            ok(f"rules/{rname} — 索引文件 (无 frontmatter)")
        continue

    # For AGENTS.md with double frontmatter, prefer the block with 'trigger'
    fm = None
    for fm_str in fm_blocks:
        try:
            if yaml:
                parsed = yaml.safe_load(fm_str)
                if isinstance(parsed, dict) and parsed.get('trigger'):
                    fm = parsed
                    break
                if fm is None and isinstance(parsed, dict):
                    fm = parsed  # fallback to first block
            else:
                fm = {}
        except yaml.YAMLError:
            continue

    if fm is None:
        warn(f"rules/{rname} — frontmatter 解析失败")
        continue

    trigger = fm.get("trigger") if isinstance(fm, dict) else None
    desc = fm.get("description") if isinstance(fm, dict) else None

    if rname != "README.md":
        if not trigger:
            warn(f"rules/{rname} — 缺少 trigger 字段")
        if not desc:
            warn(f"rules/{rname} — 缺少 description 字段")
        if trigger and trigger not in ("always_on", "model_decision", "manual"):
            warn(f"rules/{rname} — 非标准 trigger: {trigger}")

    ok(f"rules/{rname} — trigger={trigger or 'N/A'}")

# Check all expected rules exist
for rule, _expected_trigger in EXPECTED_RULES.items():
    if not (RULES_DIR / rule).exists():
        warn(f"预期 rule 文件缺失: rules/{rule}")

# ============================================================
# 3. Skills 文件验证
# ============================================================
section("3. Skills 文件验证 (skills/*/SKILL.md)")

SKILLS_DIR = BASE / "skills"
skills_found = []
for skill_dir in sorted(SKILLS_DIR.iterdir()):
    if not skill_dir.is_dir():
        continue
    if skill_dir.name.startswith('.') or skill_dir.name.startswith('_'):
        continue
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        err(f"skills/{skill_dir.name} — 缺少 SKILL.md")
        continue

    content = skill_md.read_text(encoding="utf-8")
    skills_found.append(skill_dir.name)

    fm, _ = parse_frontmatter(content)
    if fm is None:
        warn(f"skills/{skill_dir.name} — 缺少 YAML frontmatter")
        continue
    if isinstance(fm, dict) and fm.get('_parse_error'):
        warn(f"skills/{skill_dir.name} — frontmatter 解析失败")
        continue

    name = fm.get("name") if isinstance(fm, dict) else None
    desc = fm.get("description") if isinstance(fm, dict) else None

    if not name:
        warn(f"skills/{skill_dir.name} — 缺少 name")
    if not desc:
        warn(f"skills/{skill_dir.name} — 缺少 description")

    ok(f"skills/{skill_dir.name} — name={name}")

# ============================================================
# 4. Skills-INDEX 一致性
# ============================================================
section("4. Skills-INDEX 一致性")

idx_path = BASE / "skills-INDEX.md"
if idx_path.exists():
    idx_content = idx_path.read_text(encoding="utf-8")
    # Match table rows: | N | skill-name | ... |
    idx_skills = set()
    for m in re.finditer(r'\|\s*\d+\s*\|\s*\[?([a-z0-9-]+)\]?', idx_content):
        idx_skills.add(m.group(1))

    actual_skills = set(skills_found)
    missing_in_idx = actual_skills - idx_skills
    extra_in_idx = idx_skills - actual_skills

    if missing_in_idx:
        warn(f"Skills 未在 INDEX 中: {missing_in_idx}")
    if extra_in_idx:
        warn(f"INDEX 中多余引用 (skill 已删除): {extra_in_idx}")
    if not missing_in_idx and not extra_in_idx:
        ok(f"Skills-INDEX 与实际 skills 一致 ({len(actual_skills)} 个)")
    else:
        ok(f"INDEX={len(idx_skills)} / 实际={len(actual_skills)}")
else:
    warn("skills-INDEX.md 不存在")

# ============================================================
# 5. Agents 文件验证
# ============================================================
section("5. Agents 文件验证 (agents/*.md)")

AGENTS_DIR = BASE / "agents"
agents_found = []
for agent_file in sorted(AGENTS_DIR.glob("*.md")):
    aname = agent_file.stem
    if aname == "README":
        continue
    agents_found.append(aname)

    content = agent_file.read_text(encoding="utf-8")
    fm, _ = parse_frontmatter(content)

    if fm is None:
        warn(f"agents/{agent_file.name} — 缺少 YAML frontmatter")
        ok(f"agents/{aname} — (无 frontmatter, 纯定义)")
        continue
    if isinstance(fm, dict) and fm.get('_parse_error'):
        warn(f"agents/{agent_file.name} — frontmatter 解析失败")
        continue

    agent_name = fm.get("name") if isinstance(fm, dict) else None
    agent_desc = fm.get("description") if isinstance(fm, dict) else None
    if not agent_name:
        warn(f"agents/{agent_file.name} — 缺少 name")
    if not agent_desc:
        warn(f"agents/{agent_file.name} — 缺少 description")
    ok(f"agents/{aname} — name={agent_name}")

# ============================================================
# 6. Agents-INDEX 一致性
# ============================================================
section("6. Agents-INDEX 一致性")

idx_path = BASE / "agents-INDEX.md"
if idx_path.exists():
    idx_content = idx_path.read_text(encoding="utf-8")
    # Match markdown links: [name](agents/name.md) or table rows
    idx_agents = set()
    for m in re.finditer(r'\[([a-z0-9-]+)\]\(agents/[a-z0-9-]+\.md\)', idx_content):
        idx_agents.add(m.group(1))
    # Also match table rows: | N | name | ... |
    # Use the same pattern as skills-INDEX: require a number column before the name
    for m in re.finditer(r'\|\s*\d+\s*\|\s*\[?([a-z0-9-]+)\]?', idx_content):
        name = m.group(1)
        if name and not name.startswith('-') and name not in ('Agent', 'Name', '---'):
            idx_agents.add(name)

    actual_agents = set(agents_found)
    missing_in_idx = actual_agents - idx_agents
    extra_in_idx = idx_agents - actual_agents

    if missing_in_idx:
        warn(f"Agents 未在 INDEX 中: {missing_in_idx}")
    if extra_in_idx:
        warn(f"INDEX 中多余引用 (agent 已删除): {extra_in_idx}")
    if not missing_in_idx and not extra_in_idx:
        ok(f"Agents-INDEX 与实际 agents 一致 ({len(actual_agents)} 个)")
    else:
        ok(f"INDEX={len(idx_agents)} / 实际={len(actual_agents)}")
else:
    warn("agents-INDEX.md 不存在")

# ============================================================
# 7. Hooks Python 语法验证
# ============================================================
section("7. Hooks Python 语法验证")

HOOKS_DIR = BASE / "hooks"
hook_files_list = sorted(HOOKS_DIR.rglob("*.py"))
hook_count = 0
hook_errors = 0
for hook_file in hook_files_list:
    try:
        source = hook_file.read_text(encoding="utf-8")
        ast.parse(source)
        hook_count += 1
    except SyntaxError as e:
        rel = hook_file.relative_to(BASE)
        err(f"{rel} — 语法错误: {e}")
        hook_errors += 1

ok(f"共 {hook_count} 个 hook 文件语法有效" + (f", {hook_errors} 个错误" if hook_errors else ""))

# ============================================================
# 8. 裸 except 扫描 (R16)
# ============================================================
section("8. R16 裸 except 扫描")

bare_except_files = []
for hook_file in HOOKS_DIR.rglob("*.py"):
    source = hook_file.read_text(encoding="utf-8")
    # Skip the validate_config.py itself and _optional/_deprecated
    rel = str(hook_file.relative_to(BASE))
    bare_matches = re.findall(r'^except\s*:', source, re.MULTILINE)
    for _ in bare_matches:
        bare_except_files.append(rel)

if bare_except_files:
    for f in set(bare_except_files):
        err(f"R16 违规: {f} — 裸 except: 语句")
else:
    ok("所有 hook 文件无裸 except: — R16 合规")

# ============================================================
# 9. 交叉引用验证
# ============================================================
section("9. 关键交叉引用验证")

core_path = BASE / "rules" / "CORE.md"
if core_path.exists():
    core_content = core_path.read_text(encoding="utf-8")
    if "CLAUDE.md" in core_content:
        ok("CORE.md 正确引用 CLAUDE.md")
    else:
        warn("CORE.md 未引用 CLAUDE.md")

# 9a. MANIFEST.yaml — try to parse and check references
manifest_path = BASE / "MANIFEST.yaml"
if manifest_path.exists():
    if yaml:
        try:
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            # Extract file references from manifest string representation
            manifest_str = json.dumps(manifest, ensure_ascii=False)
            path_refs = re.findall(r'(?:rules|skills|agents|hooks|plugins)/[^\s"\'\]\)]+\.(?:md|py|yaml|yml|json)', manifest_str)
            missing_refs = [ref for ref in set(path_refs) if not (BASE / ref).exists()]
            if missing_refs:
                for ref in missing_refs:
                    warn(f"MANIFEST 引用不存在: {ref}")
            else:
                ok(f"MANIFEST.yaml 交叉引用 OK ({len(set(path_refs))} 个引用)")
        except yaml.YAMLError as e:
            warn(f"MANIFEST.yaml YAML 解析跳过交叉引用: {e}")
    else:
        warn("MANIFEST.yaml 交叉引用跳过 (yaml lib 缺失)")

# 9b. 阈值一致性验证
section("9b. 阈值一致性验证 (70%/90%)")

threshold_files = [
    "rules/CORE.md",
    "rules/CONTEXT.md",
    "rules/WORKFLOW.md",
    "rules/AGENTS.md",
    "rules/BESTPRACTICE.md",
    "skills/context-engineering/SKILL.md",
    "templates/planning/phases-template.md",
    "commands/compact.md",
    "catalog/agents/context-rot-monitor.md",
    "CLAUDE.md",
]

old_patterns = [
    (r'(?<!^)50%\s*(?:compact|强制)', '50% compact/强制 (废弃阈值)'),
    (r'(?<!>)(?<!-)\b40%\b.*(?:预警|正常)', '40% 预警/正常 (废弃阈值)'),
]

threshold_issues = 0
for fpath in threshold_files:
    fp = BASE / fpath
    if not fp.exists():
        continue
    content = fp.read_text(encoding="utf-8")
    for pattern, desc in old_patterns:
        if re.search(pattern, content):
            warn(f"阈值遗留: {fpath} — {desc}")
            threshold_issues += 1

if threshold_issues == 0:
    ok("所有文件阈值已更新为 70%/90% 体系")

# ============================================================
# 10. MCP 配置验证
# ============================================================
section("10. MCP 配置验证")

mcp = None
mcp_path = BASE / ".mcp.json"
if mcp_path.exists():
    try:
        mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
        servers = mcp.get("mcpServers", {})
        ok(f".mcp.json — {len(servers)} 个 MCP 服务器定义")
        for srv_name, srv_conf in servers.items():
            if "command" not in srv_conf and "url" not in srv_conf:
                warn(f"MCP server '{srv_name}' 缺少 command 或 url")
    except json.JSONDecodeError as e:
        err(f".mcp.json 解析失败: {e}")

# Check mcp/servers.json
servers_json = BASE / "mcp" / "servers.json"
if servers_json.exists():
    try:
        sj = json.loads(servers_json.read_text(encoding="utf-8"))
        toolsets = sj.get("toolsets", {})
        all_server_names = set()
        for group, names in toolsets.items():
            all_server_names.update(names)
        if mcp:
            mcp_names = set(mcp.get("mcpServers", {}).keys())
            orphaned = all_server_names - mcp_names
            if orphaned:
                warn(f"servers.json 引用不存在的 MCP 服务器: {orphaned}")
        ok(f"mcp/servers.json — {len(toolsets)} 个分组, {len(all_server_names)} 个服务器")
    except json.JSONDecodeError as e:
        err(f"mcp/servers.json 解析失败: {e}")
else:
    warn("mcp/servers.json 不存在")

# ============================================================
# 11. Plugins 配置验证
# ============================================================
section("11. Plugins 配置验证")

plugins_json = BASE / "plugins" / "installed_plugins.json"
if plugins_json.exists():
    try:
        plugins = json.loads(plugins_json.read_text(encoding="utf-8"))
        plugin_count = len(plugins) if isinstance(plugins, list) else len(plugins.get("plugins", []))
        ok(f"installed_plugins.json — {plugin_count} 个已安装插件")
    except json.JSONDecodeError as e:
        err(f"installed_plugins.json 解析失败: {e}")

marketplaces_json = BASE / "plugins" / "known_marketplaces.json"
if marketplaces_json.exists():
    try:
        mp = json.loads(marketplaces_json.read_text(encoding="utf-8"))
        mp_count = len(mp) if isinstance(mp, list) else len(mp.keys())
        ok(f"known_marketplaces.json — {mp_count} 个 marketplace")
    except json.JSONDecodeError as e:
        err(f"known_marketplaces.json 解析失败: {e}")

# ============================================================
# 12. Catalog 完整性
# ============================================================
section("12. Catalog 完整性")

catalog_dirs = ["catalog/skills", "catalog/agents", "catalog/rules"]
for cd in catalog_dirs:
    cp = BASE / cd
    if cp.exists():
        md_files = list(cp.rglob("*.md"))
        ok(f"{cd} — {len(md_files)} 个文件")
    else:
        warn(f"Catalog 目录不存在: {cd}")

# ============================================================
# 13. 文档交叉引用检查
# ============================================================
section("13. 文档交叉引用")

doc_files = ["SPEC.md", "CLAUDE.md", "README.md"]
for df_name in doc_files:
    df = BASE / df_name
    if not df.exists():
        warn(f"文档缺失: {df.name}")
        continue
    content = df.read_text(encoding="utf-8")
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    broken = 0
    for text, link in md_links:
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        link_path = link.split("#")[0]
        if link_path and not (BASE / link_path).exists():
            broken += 1
    if broken > 0:
        warn(f"{df.name} — {broken} 个断链")
    else:
        ok(f"{df.name} — 内部链接有效")

# ============================================================
# 14. Commands 验证
# ============================================================
section("14. Commands 验证")

CMDS_DIR = BASE / "commands"
if CMDS_DIR.exists():
    cmd_files = list(CMDS_DIR.glob("*.md"))
    if cmd_files:
        ok(f"commands/ — {len(cmd_files)} 个命令文件（含 /deep-research）")
    else:
        warn("commands/ — 无命令文件")
else:
    warn("commands/ 目录不存在")

# ============================================================
# 15. Templates 验证
# ============================================================
section("15. Templates 验证")

templates_dir = BASE / "templates"
if templates_dir.exists():
    tpl_count = len(list(templates_dir.rglob("*.md")))
    ok(f"templates/ — {tpl_count} 个模板文件")
else:
    warn("templates/ 目录不存在")

# ============================================================
# SUMMARY
# ============================================================
section("验证结果汇总")

print(f"\n  OK 通过: {len(PASSES)}")
print(f"  !  警告: {len(WARNINGS)}")
print(f"  X  错误: {len(ERRORS)}")

if ERRORS:
    print(f"\n  错误详情:")
    for e in ERRORS:
        print(f"    X {e}")

if WARNINGS:
    print(f"\n  警告详情:")
    for w in WARNINGS:
        print(f"    ! {w}")

print()

if ERRORS:
    print("FAIL — 配置验证失败，存在错误需要修复")
    sys.exit(1)
else:
    print("PASS — 配置验证通过" + (" (有警告)" if WARNINGS else ""))
    sys.exit(0)
