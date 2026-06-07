#!/usr/bin/env python3
"""功能测试套件 — 深度验证配置正确性与效率（非仅结构验证）
TDD: RED → verify fails → GREEN → REFACTOR
"""
import json
import re
import sys
import yaml
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = Path(__file__).parent
FAIL, WARN, OK = 0, 0, 0

def fail(msg):
    global FAIL; FAIL += 1
    print(f"  ❌ {msg}")

def warn(msg):
    global WARN; WARN += 1
    print(f"  ⚠️  {msg}")

def ok(msg):
    global OK; OK += 1
    print(f"  ✅ {msg}")

def read_md(path):
    return Path(path).read_text(encoding='utf-8').replace('\r\n', '\n').lstrip('﻿')

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def parse_frontmatter(text):
    """解析 YAML frontmatter，返回 (dict, body_text)"""
    if not text.startswith('---\n'):
        return {}, text
    end = text.find('\n---\n', 4)
    if end == -1:
        return {}, text
    fm = yaml.safe_load(text[4:end])
    body = text[end+4:]
    # 可能有第二个 frontmatter block
    body_stripped = body.lstrip('\n')
    if body_stripped.startswith('---\n'):
        end2 = body_stripped.find('\n---\n', 4)
        if end2 != -1:
            fm2 = yaml.safe_load(body_stripped[4:end2])
            if fm2:
                fm.update(fm2)
            body = body_stripped[end2+4:]
    return (fm or {}), body


def resolve_owner_path(owner):
    """将 MANIFEST owner 解析为本地路径；config/ 映射 ~/.claude 根目录文件。"""
    if not owner or '/' not in owner:
        return None
    owner_type, owner_path = owner.split('/', 1)
    if owner_type == 'config':
        return BASE / owner_path
    if owner_type == 'skill':
        return BASE / 'skills' / owner_path / 'SKILL.md'
    if owner_type == 'rules':
        return BASE / 'rules' / owner_path
    if owner_type == 'catalog':
        return BASE / 'catalog' / owner_path
    if owner_type == 'plugin':
        candidates = [
            BASE / 'plugins' / 'marketplaces' / owner_path,
            BASE / 'plugins' / 'cache' / owner_path,
        ]
        # 版本化 cache: plugins/cache/vendor/name/VERSION
        parts = owner_path.split('/')
        if len(parts) == 2:
            vendor, name = parts
            cache_glob = BASE / 'plugins' / 'cache' / vendor / name
            if cache_glob.exists():
                versions = sorted([p for p in cache_glob.iterdir() if p.is_dir()], reverse=True)
                if versions:
                    candidates.insert(0, versions[0])
        for c in candidates:
            if c.exists():
                return c
        return None
    if owner_type in ('agent', 'hook', 'openspec', 'planning', 'spec', 'mcp', 'memory', 'templates'):
        return None  # 外部/制品，由调用方单独处理
    return None

# ═══════════════════════════════════════════════════════
# 测试 1: Skill 描述质量 — 不应使用泛化触发词
# ═══════════════════════════════════════════════════════
print("\n📋 测试 1: Skill 描述触发词质量")
GENERIC_TRIGGERS = [
    r'^when\s+needed', r'^when\s+required', r'^when\s+applicable',
    r'^general\s+purpose', r'^use\s+this\s+when', r'^trigger.*any',
    r'^any\s+time', r'^always', r'^catch-all',
]

skills_dir = BASE / 'skills'
for skill_dir in sorted(skills_dir.iterdir()):
    if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
        continue
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        fail(f"Skill [{skill_dir.name}] 缺少 SKILL.md")
        continue
    content = read_md(skill_md)
    fm, body = parse_frontmatter(content)
    desc = fm.get('description', '')
    if not desc:
        fail(f"Skill [{skill_dir.name}] 缺少 description")
        continue
    # 检查泛化触发词
    for pattern in GENERIC_TRIGGERS:
        if re.search(pattern, desc, re.IGNORECASE):
            warn(f"Skill [{skill_dir.name}] description 过于泛化: '{desc[:80]}'")
            break
    else:
        ok(f"Skill [{skill_dir.name}] description 合格: '{desc[:60]}...'")

# ═══════════════════════════════════════════════════════
# 测试 2: Rules 触发类型正确性
# ═══════════════════════════════════════════════════════
print("\n📋 测试 2: Rules 触发类型正确性")
RULES_DIR = BASE / 'rules'
ALWAYS_ON_RULES = {'CORE.md'}  # CORE.md should be always_on
MODEL_DECISION_RULES = {'AGENTS.md', 'BESTPRACTICE.md', 'CONTEXT.md',
                         'DESIGN.md', 'GIT.md', 'MCP.md', 'SECURITY.md',
                         'WORKFLOW.md'}

for rule_file in sorted(RULES_DIR.glob('*.md')):
    if rule_file.name == 'README.md':
        continue
    content = read_md(rule_file)
    fm, _ = parse_frontmatter(content)
    trigger = fm.get('trigger', 'unset')

    if rule_file.name in ALWAYS_ON_RULES:
        if trigger == 'always_on' or trigger == 'alwaysApply':
            ok(f"Rule [{rule_file.name}] 正确: trigger={trigger} (always_on)")
        else:
            fail(f"Rule [{rule_file.name}] 应为 always_on，实际 trigger={trigger}")
    elif rule_file.name in MODEL_DECISION_RULES:
        if trigger == 'model_decision':
            ok(f"Rule [{rule_file.name}] 正确: trigger={trigger}")
        else:
            fail(f"Rule [{rule_file.name}] 应为 model_decision，实际 trigger={trigger}")
    else:
        warn(f"Rule [{rule_file.name}] 未在预期分类中，trigger={trigger}")

# ═══════════════════════════════════════════════════════
# 测试 3: MANIFEST.yaml 防互博校验
# ═══════════════════════════════════════════════════════
print("\n📋 测试 3: MANIFEST.yaml 防互博校验")
manifest = yaml.safe_load(read_md(BASE / 'MANIFEST.yaml'))
concerns = manifest.get('concerns', {})

# 3a: 每个 concern 的 owner 必须存在
for name, c in concerns.items():
    owner = c.get('owner', '')
    if '/' not in owner:
        fail(f"Concern [{name}] owner 格式无效: '{owner}'")
        continue

    owner_type = owner.split('/', 1)[0]
    full_path = resolve_owner_path(owner)

    if full_path is not None:
        if not full_path.exists():
            fail(f"Concern [{name}] owner 不存在: {owner} → {full_path}")
        else:
            ok(f"Concern [{name}] → owner [{owner}] ✓")
    elif owner_type in ('agent', 'hook', 'openspec', 'planning', 'spec', 'mcp', 'memory', 'templates'):
        ok(f"Concern [{name}] → owner [{owner}] (外部/制品)")
    else:
        warn(f"Concern [{name}] owner type 未知: '{owner_type}'")

# 3b: 检查 concerns 间 excludes 双向一致性（excludes 可引用 agent/hook/skill 等外部键）
for name, c in concerns.items():
    excludes = c.get('excludes', [])
    for excl in excludes:
        if excl in concerns:
            rev_excludes = concerns[excl].get('excludes', [])
            if name not in rev_excludes:
                warn(f"互斥不对称: [{name}] excludes [{excl}], 但反向未声明")
            else:
                ok(f"互斥对称: [{name}] ↔ [{excl}]")

# 3c: depends_on 链有效性
for name, c in concerns.items():
    deps = c.get('depends_on', [])
    for dep in deps:
        dep_name = dep.split('/')[-1] if '/' in dep else dep
        valid_prefixes = ('rules/', 'skill/', 'agent/', 'agents/', 'plugin/', 'hook/', 'config/')
        if dep_name in concerns or dep.startswith(valid_prefixes):
            ok(f"Concern [{name}] depends_on [{dep}] ✓")
        else:
            warn(f"Concern [{name}] depends_on [{dep}] — 目标不在 concerns 中")

# ═══════════════════════════════════════════════════════
# 测试 4: Agent 定义完整性
# ═══════════════════════════════════════════════════════
print("\n📋 测试 4: Agent 定义完整性")
AGENTS_DIR = BASE / 'agents'
for agent_file in sorted(AGENTS_DIR.glob('*.md')):
    if agent_file.name == 'README.md':
        continue
    content = read_md(agent_file)
    fm, body = parse_frontmatter(content)

    name = fm.get('name', agent_file.stem)
    desc = fm.get('description', '')
    if not desc:
        warn(f"Agent [{name}] 缺少 description")
    else:
        ok(f"Agent [{name}] 有 description")

    # 检查是否有清晰的角色定义
    role_markers = ['角色', 'Role', '职责', 'Responsibility', '##', '# ']
    has_role = any(m in body[:500] for m in role_markers)
    if has_role:
        ok(f"Agent [{name}] 有角色定义")
    else:
        warn(f"Agent [{name}] 缺少角色/职责定义")

# ═══════════════════════════════════════════════════════
# 测试 5: INDEX 交叉引用一致性
# ═══════════════════════════════════════════════════════
print("\n📋 测试 5: INDEX 交叉引用一致性")

# 5a: skills-INDEX.md
skills_index = BASE / 'skills-INDEX.md'
if skills_index.exists():
    idx_content = read_md(skills_index)
    idx_skills = set()
    for m in re.finditer(r'\|\s*\d+\s*\|\s*\[?([a-z0-9-]+)\]?', idx_content):
        name = m.group(1)
        if name and not name.startswith('-') and name not in ('Skill', 'Name', '---', '#'):
            idx_skills.add(name)

    actual_skills = set()
    for d in (BASE / 'skills').iterdir():
        if d.is_dir() and not d.name.startswith('.'):
            if (d / 'SKILL.md').exists():
                actual_skills.add(d.name)

    extra_in_idx = idx_skills - actual_skills
    missing_from_idx = actual_skills - idx_skills

    if extra_in_idx:
        for s in extra_in_idx:
            fail(f"skills-INDEX 引用了不存在的 skill: [{s}]")
    if missing_from_idx:
        for s in missing_from_idx:
            warn(f"Skill [{s}] 未在 skills-INDEX.md 中注册")
    if not extra_in_idx and not missing_from_idx:
        ok(f"skills-INDEX 完全一致: {len(actual_skills)} 个 skills")

# 5b: agents-INDEX.md
agents_index = BASE / 'agents-INDEX.md'
if agents_index.exists():
    idx_content = read_md(agents_index)
    idx_agents = set()
    for m in re.finditer(r'\|\s*\d+\s*\|\s*\[?([a-z0-9-]+)\]?', idx_content):
        name = m.group(1)
        if name and not name.startswith('-') and name not in ('Agent', 'Name', '---', '#'):
            idx_agents.add(name)

    actual_agents = set()
    for f in (BASE / 'agents').glob('*.md'):
        if f.name != 'README.md' and not f.name.startswith('.'):
            actual_agents.add(f.stem)

    extra_in_idx = idx_agents - actual_agents
    missing_from_idx = actual_agents - idx_agents

    if extra_in_idx:
        for s in extra_in_idx:
            fail(f"agents-INDEX 引用了不存在的 agent: [{s}]")
    if missing_from_idx:
        for s in missing_from_idx:
            warn(f"Agent [{s}] 未在 agents-INDEX.md 中注册")
    if not extra_in_idx and not missing_from_idx:
        ok(f"agents-INDEX 完全一致: {len(actual_agents)} 个 agents")

# ═══════════════════════════════════════════════════════
# 测试 6: Hook 脚本可执行性
# ═══════════════════════════════════════════════════════
print("\n📋 测试 6: Hook 脚本结构完整性")
HOOKS_DIR = BASE / 'hooks'
for hook_file in sorted(HOOKS_DIR.glob('*.py')):
    if hook_file.name.startswith('_'):
        continue
    content = hook_file.read_text(encoding='utf-8')
    has_shebang = content.startswith('#!/') or '#!/usr' in content[:100]
    has_main = 'def main' in content or 'if __name__' in content
    has_except = 'except' in content
    has_bare_except = bool(re.search(r'except\s*:', content) and not
                          re.search(r'except\s+(Exception|BaseException|ValueError|'
                                     r'TypeError|KeyError|OSError|IOError|RuntimeError)', content))

    if has_shebang or has_main:
        ok(f"Hook [{hook_file.name}] 结构完整 (shebang={'✓' if has_shebang else '✗'}, main={'✓' if has_main else '✗'})")
    else:
        warn(f"Hook [{hook_file.name}] 缺少 shebang 或 main")

    if has_bare_except:
        fail(f"Hook [{hook_file.name}] 含裸 except: (违反 R16)")
    elif has_except:
        ok(f"Hook [{hook_file.name}] 异常处理规范 ✓")

# ═══════════════════════════════════════════════════════
# 测试 7: MCP 配置一致性
# ═══════════════════════════════════════════════════════
print("\n📋 测试 7: MCP 配置一致性")
mcp_json = BASE / '.mcp.json'
servers_json = BASE / 'mcp' / 'servers.json'

if mcp_json.exists():
    mcp = read_json(mcp_json)
    mcp_servers = set(mcp.get('mcpServers', {}).keys())
    ok(f".mcp.json 包含 {len(mcp_servers)} 个 MCP 服务器")

    if servers_json.exists():
        servers = read_json(servers_json)
        toolsets = servers.get('toolsets', {})
        all_grouped = set()
        for group, names in toolsets.items():
            for name in names:
                all_grouped.add(name)
                if name not in mcp_servers:
                    fail(f"MCP servers.json [{name}] (group={group}) 不在 .mcp.json 中")

        # 检查 .mcp.json 中的服务器是否都在某个分组中
        ungrouped = mcp_servers - all_grouped
        if ungrouped:
            warn(f"MCP 服务器未分组: {ungrouped}")
        else:
            ok("所有 MCP 服务器都有分组映射")

        # 检查 settings.json 不应有 mcpServers
        settings = read_json(BASE / 'settings.json')
        if 'mcpServers' in settings:
            fail("settings.json 不应包含 mcpServers (违反 MCP.md 规范)")
        else:
            ok("settings.json 无冗余 mcpServers ✓")

# ═══════════════════════════════════════════════════════
# 测试 8: 插件配置完整性
# ═══════════════════════════════════════════════════════
print("\n📋 测试 8: 插件配置完整性")
installed = read_json(BASE / 'plugins' / 'installed_plugins.json')
known = read_json(BASE / 'plugins' / 'known_marketplaces.json')

if isinstance(installed, list):
    enabled = [p for p in installed if p.get('enabled', True)]
    disabled = [p for p in installed if not p.get('enabled', True)]
    ok(f"已安装 {len(installed)} 个插件 (启用 {len(enabled)}, 禁用 {len(disabled)})")
elif isinstance(installed, dict):
    plugins_dict = installed.get('plugins', installed)
    enabled = {k: v for k, v in plugins_dict.items() if isinstance(v, dict) and v.get('enabled', True)}
    disabled = {k: v for k, v in plugins_dict.items() if isinstance(v, dict) and not v.get('enabled', True)}
    ok(f"已安装 {len(plugins_dict)} 个插件 (启用 {len(enabled)}, 禁用 {len(disabled)})")

if isinstance(known, dict):
    marketplaces = known.get('marketplaces', known)
    ok(f"已知 {len(marketplaces)} 个市场")

# ═══════════════════════════════════════════════════════
# 测试 9: 70%/90% 阈值一致性
# ═══════════════════════════════════════════════════════
print("\n📋 测试 9: 70%/90% 阈值一致性")
THRESHOLD_FILES = [
    'rules/CORE.md', 'rules/CONTEXT.md', 'rules/WORKFLOW.md',
    'rules/AGENTS.md', 'rules/BESTPRACTICE.md', 'CLAUDE.md',
]
OLD_PATTERNS = [
    (r'(?<!<)(?:50|55|60)%\s*(?:择机|强制|compact)', '旧阈值 50-60%'),
    (r'(?:75|80)%\s*(?:强制)', '旧阈值 75-80%'),
]

for fpath in THRESHOLD_FILES:
    full = BASE / fpath
    if not full.exists():
        warn(f"阈值文件不存在: {fpath}")
        continue
    content = read_md(full)

    # 检查新阈值存在
    has_70 = '70%' in content and ('择机' in content or 'compact' in content.lower())
    has_90 = '90%' in content and ('强制' in content or 'forced' in content.lower())

    if has_70 and has_90:
        ok(f"[{fpath}] 70%/90% 阈值正确 ✓")
    elif has_70:
        warn(f"[{fpath}] 有 70% 但缺少明确 90% 强制触发")
    elif has_90:
        warn(f"[{fpath}] 有 90% 但缺少明确 70% 择机触发")
    else:
        fail(f"[{fpath}] 缺少 70%/90% 阈值")

    # 检查旧阈值残留
    for pattern, label in OLD_PATTERNS:
        if re.search(pattern, content):
            warn(f"[{fpath}] 可能含旧阈值残留: {label}")

# ═══════════════════════════════════════════════════════
# 测试 10: CLAUDE.md 指针有效性
# ═══════════════════════════════════════════════════════
print("\n📋 测试 10: CLAUDE.md 指针有效性")
claude_md = read_md(BASE / 'CLAUDE.md')
# 提取所有文件路径引用
refs = set()
for m in re.finditer(r'`([^`]+\.(?:md|yaml|json|py|ps1|sh|mdc))`', claude_md):
    refs.add(m.group(1))
# 也匹配裸路径
for m in re.finditer(r'(?:→|见|详见|位置[：:])\s*`?([a-zA-Z0-9_/.-]+\.[a-z]{2,4})`?', claude_md):
    refs.add(m.group(1))

checked = 0
for ref in sorted(refs):
    # 跳过外部 URL 和变量引用
    if ref.startswith(('http', '${', '$', '\\$', '~/')):
        continue
    # 跳过明显不是文件路径的
    if ' ' in ref or ref.startswith('<'):
        continue
    full = BASE / ref
    if full.exists():
        checked += 1
    else:
        # 尝试去掉可能的路径前缀
        alt = BASE / ref.split('/')[-1]
        if alt.exists():
            checked += 1
        else:
            warn(f"CLAUDE.md 引用文件不存在: {ref}")

ok(f"CLAUDE.md 指针检查完成: {checked} 个有效引用")

# ═══════════════════════════════════════════════════════
# 测试 11: P0 Skill 存在性
# ═══════════════════════════════════════════════════════
print("\n📋 测试 11: P0 强制 Skill 存在性")
p0_skills = manifest.get('p0_skills', [])
for skill_name in p0_skills:
    skill_path = BASE / 'skills' / skill_name / 'SKILL.md'
    if skill_path.exists():
        ok(f"P0 Skill [{skill_name}] 存在 ✓")
    else:
        fail(f"P0 Skill [{skill_name}] 缺失: {skill_path}")

# ═══════════════════════════════════════════════════════
# 测试 12: 五阶段 × 五柱覆盖
# ═══════════════════════════════════════════════════════
print("\n📋 测试 12: 五阶段 × 五柱覆盖")
phases = manifest.get('phases', {})
pillars = manifest.get('pillars', {})
required_phases = ['plan', 'spec', 'execute', 'verify', 'learn']
for phase_name in required_phases:
    if phase_name in phases:
        ok(f"阶段 [{phase_name}] 已定义")
    else:
        fail(f"阶段 [{phase_name}] 缺失")

required_pillars = ['superpowers', 'gsd', 'openspec', 'gstack', 'claude_mem']
for pillar_name in required_pillars:
    if pillar_name in pillars:
        ok(f"柱 [{pillar_name}] 已定义 (v{pillars[pillar_name].get('version', '?')})")
    else:
        fail(f"柱 [{pillar_name}] 缺失")

# ═══════════════════════════════════════════════════════
# 测试 13: COMMANDS 完整性
# ═══════════════════════════════════════════════════════
print("\n📋 测试 13: Commands 目录完整性")
cmds_dir = BASE / 'commands'
if cmds_dir.exists():
    for cmd_file in sorted(cmds_dir.glob('*.md')):
        content = read_md(cmd_file)
        fm, _ = parse_frontmatter(content)
        if fm.get('description'):
            ok(f"Command [{cmd_file.stem}] 有 description")
        else:
            warn(f"Command [{cmd_file.stem}] 缺少 description")

# ═══════════════════════════════════════════════════════
# 测试 14: 安全规则关键要素检查
# ═══════════════════════════════════════════════════════
print("\n📋 测试 14: 安全规则关键要素")
sec_content = read_md(BASE / 'rules' / 'SECURITY.md')
security_markers = [
    ('OWASP', 'OWASP Top 10'),
    ('注入', '注入攻击防护'),
    ('XSS', 'XSS 防护'),
    ('敏感数据', '敏感数据处理'),
    ('密钥管理', '密钥管理'),
    ('R16', 'R16 错误暴漏'),
    ('ML 注入', 'ML 注入防御'),
]
for marker, label in security_markers:
    if marker.lower() in sec_content.lower():
        ok(f"安全规则: {label} ✓")
    else:
        warn(f"安全规则缺少: {label}")

# ═══════════════════════════════════════════════════════
# 测试 15: 输出压缩配置
# ═══════════════════════════════════════════════════════
print("\n📋 测试 15: 输出压缩/Shell压缩配置")
# RTK
rtk_md = BASE / 'RTK.md'
if rtk_md.exists():
    ok("RTK.md 存在 (Shell 压缩)")
else:
    warn("RTK.md 缺失")

# caveman
caveman_skill = BASE / 'skills' / 'caveman-compress' / 'SKILL.md'
if caveman_skill.exists():
    ok("caveman-compress skill 存在 (输出压缩)")
else:
    warn("caveman-compress skill 缺失")

# ═══════════════════════════════════════════════════════
# 测试 16: CONTEXT.md 上下文工程规则关键要素
# ═══════════════════════════════════════════════════════
print("\n📋 测试 16: 上下文工程规则完整度")
ctx_content = read_md(BASE / 'rules' / 'CONTEXT.md')
context_markers = [
    ('三态制品', '三态制品通信'),
    ('codegraph', 'codegraph 策略'),
    ('Understand-Anything', 'UA 策略'),
    ('claude-mem', '三层搜索'),
    ('压缩', '压缩策略'),
]
for marker, label in context_markers:
    if marker.lower() in ctx_content.lower():
        ok(f"CONTEXT.md: {label} ✓")
    else:
        warn(f"CONTEXT.md 缺少: {label}")

# ═══════════════════════════════════════════════════════
# 测试 17: P0 数量跨文档一致（防左右手互博）
# ═══════════════════════════════════════════════════════
print("\n📋 测试 17: P0 技能跨文档一致性")
p0_manifest = set(manifest.get('p0_skills', []))
p0_expected = {
    'using-superpowers', 'brainstorming', 'change-impact-analysis',
    'verification-before-completion', 'systematic-debugging',
}
if p0_manifest == p0_expected:
    ok(f"MANIFEST p0_skills 正确: {len(p0_manifest)} 个")
else:
    fail(f"MANIFEST p0_skills 不一致: 缺 {p0_expected - p0_manifest} 多 {p0_manifest - p0_expected}")

claude_p0_mentions = len(re.findall(r'P0.*?(?:5|五)', read_md(BASE / 'CLAUDE.md')))
skills_idx_p0 = read_md(BASE / 'skills-INDEX.md')
if 'P0必须=5' in skills_idx_p0.replace(' ', ''):
    ok("skills-INDEX P0=5 与 MANIFEST 一致")
else:
    warn("skills-INDEX 未声明 P0=5")

# ═══════════════════════════════════════════════════════
# 测试 18: 按需加载 — 仅 CORE always_on
# ═══════════════════════════════════════════════════════
print("\n📋 测试 18: 按需加载策略")
always_on_count = 0
for rule_file in (BASE / 'rules').glob('*.md'):
    if rule_file.name == 'README.md':
        continue
    fm, _ = parse_frontmatter(read_md(rule_file))
    if fm.get('trigger') in ('always_on', 'alwaysApply'):
        always_on_count += 1
if always_on_count == 1:
    ok("仅 CORE.md 为 always_on（其余 model_decision）")
else:
    fail(f"always_on 规则数量异常: {always_on_count}（期望 1）")

# ═══════════════════════════════════════════════════════
# 测试 19: 跨编辑器同步配置
# ═══════════════════════════════════════════════════════
print("\n📋 测试 19: 跨编辑器同步配置")
sync_mode = read_json(BASE / 'sync-mode.json')
if sync_mode.get('mode') in ('index', 'full'):
    ok(f"sync-mode.json mode={sync_mode.get('mode')}")
else:
    fail("sync-mode.json 缺少有效 mode")

sync_script = BASE / 'scripts' / 'sync.ps1'
sync_guide = BASE / 'docs' / 'SYNC_GUIDE.md'
if sync_script.exists() and sync_guide.exists():
    ok("sync.ps1 + SYNC_GUIDE.md 存在")
else:
    fail("同步脚本或文档缺失")

cursor_claude = Path.home() / '.cursor' / 'CLAUDE.md'
if cursor_claude.exists():
    ok("Cursor CLAUDE.md 已部署")
else:
    warn("Cursor CLAUDE.md 未链接 — 运行 scripts/sync.ps1")

# ═══════════════════════════════════════════════════════
# 测试 20: CodeGraph + Firecrawl 降本增效配置
# ═══════════════════════════════════════════════════════
print("\n📋 测试 20: CodeGraph / 外部搜索 MCP")
mcp = read_json(BASE / '.mcp.json')
servers = read_json(BASE / 'mcp' / 'servers.json')
mcp_names = set(mcp.get('mcpServers', {}).keys())
dev_group = set(servers.get('toolsets', {}).get('dev', []))
if 'codegraph' in mcp_names and 'codegraph' in dev_group:
    ok("codegraph 在 .mcp.json 且 dev 分组")
else:
    fail("codegraph MCP 未正确配置于 dev 分组")
if 'crawl' in mcp_names:
    ok("Firecrawl (crawl) MCP 已配置")
else:
    fail("Firecrawl crawl MCP 缺失")

ctx = read_md(BASE / 'rules' / 'CONTEXT.md')
if 'codegraph' in ctx.lower() and ('firecrawl' in ctx.lower() or 'crawl' in ctx.lower()):
    ok("CONTEXT.md 含 codegraph + 外部搜索策略")
else:
    warn("CONTEXT.md 缺少 codegraph/外部搜索说明")

# ═══════════════════════════════════════════════════════
# 测试 21: 非简单任务有计划（五阶段 + 命令）
# ═══════════════════════════════════════════════════════
print("\n📋 测试 21: 五阶段工作流可执行性")
required_cmds = ['discuss', 'plan', 'execute', 'verify', 'compact', 'deep-research']
for cmd in required_cmds:
    cmd_path = BASE / 'commands' / f'{cmd}.md'
    if cmd_path.exists():
        fm, _ = parse_frontmatter(read_md(cmd_path))
        if fm.get('description'):
            ok(f"Command /{cmd} 有 description")
        else:
            warn(f"Command /{cmd} 缺少 description")
    else:
        fail(f"Command /{cmd}.md 缺失")

phases_tpl = BASE / 'templates' / 'planning' / 'phases-template.md'
if phases_tpl.exists():
    ok("phases-template.md 存在（GSD 多阶段计划）")
else:
    warn("phases-template.md 缺失")

# ═══════════════════════════════════════════════════════
# 测试 22: 插件与本地工具无冲突
# ═══════════════════════════════════════════════════════
print("\n📋 测试 22: 插件冲突检测")
installed = read_json(BASE / 'plugins' / 'installed_plugins.json')
plugins_list = installed if isinstance(installed, list) else installed.get('plugins', [])
disabled_names = []
for p in (plugins_list if isinstance(plugins_list, list) else []):
    name = p.get('name', '') if isinstance(p, dict) else str(p)
    if isinstance(p, dict) and p.get('enabled') is False:
        disabled_names.append(name)
# dict format
if isinstance(plugins_list, dict):
    for k, v in plugins_list.items():
        if isinstance(v, dict) and v.get('enabled') is False:
            disabled_names.append(k)

conflict_plugins = ['ralph-loop', 'claude-md-management']
for cp in conflict_plugins:
    found = any(cp in str(d) for d in disabled_names)
    if found or cp in str(installed):
        ok(f"冲突插件 [{cp}] 已识别（应禁用）")
    else:
        warn(f"未在 installed_plugins 中找到 [{cp}]")

claude_plugins_section = read_md(BASE / 'CLAUDE.md')
if '同名 Skill 解析' in claude_plugins_section and '后加载覆盖先加载' in claude_plugins_section:
    ok("CLAUDE.md 声明本地 skill 覆盖插件同名 skill 策略")
else:
    warn("CLAUDE.md 缺少同名 skill 解析说明")

# ═══════════════════════════════════════════════════════
# 测试 23: R16 错误暴露（hooks + 验证脚本）
# ═══════════════════════════════════════════════════════
print("\n📋 测试 23: R16 错误暴露机制")
validate_script = BASE / '_validate_config.py'
if validate_script.exists():
    src = validate_script.read_text(encoding='utf-8')
    if 'sys.exit(1)' in src and '裸 except' in src:
        ok("_validate_config.py 失败时 exit(1) + R16 扫描")
    else:
        warn("_validate_config.py 缺少 exit(1) 或 R16 扫描")
core_md = read_md(BASE / 'rules' / 'CORE.md')
if 'R16' in core_md and 'except:pass' in core_md.replace(' ', ''):
    ok("CORE.md 声明 R16 禁止裸 except:pass")
else:
    warn("CORE.md R16 声明不完整")

# ═══════════════════════════════════════════════════════
# 测试 24: 文档结构完整性（要求 1）
# ═══════════════════════════════════════════════════════
print("\n📋 测试 24: 文档结构完整性")
doc_chain = ['CLAUDE.md', 'SPEC.md', 'MANIFEST.yaml', 'README.md',
             'skills-INDEX.md', 'agents-INDEX.md', 'docs/SYNC_GUIDE.md']
for doc in doc_chain:
    if (BASE / doc).exists():
        ok(f"文档链: {doc}")
    else:
        fail(f"文档链缺失: {doc}")

# ═══════════════════════════════════════════════════════
# 测试 25: change-impact-analysis 归属与触发
# ═══════════════════════════════════════════════════════
print("\n📋 测试 25: 变更影响分析归属")
if 'change_impact' in concerns:
    ci_owner = concerns['change_impact'].get('owner', '')
    if ci_owner == 'skill/change-impact-analysis':
        ok("MANIFEST concern change_impact → skill/change-impact-analysis")
    else:
        fail(f"change_impact owner 错误: {ci_owner}")
else:
    fail("MANIFEST 缺少 change_impact concern")

cia_skill = BASE / 'skills' / 'change-impact-analysis' / 'SKILL.md'
if cia_skill.exists():
    ok("change-impact-analysis skill 存在")
else:
    fail("change-impact-analysis skill 缺失")

# ═══════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"结果: {OK} 通过 | {WARN} 警告 | {FAIL} 失败")
print(f"{'='*60}")

if FAIL > 0:
    print(f"\n🔴 {FAIL} 项失败 — 需要修复")
    sys.exit(1)
elif WARN > 0:
    print(f"\n🟡 {WARN} 项警告 — 建议检查")
    sys.exit(0)
else:
    print(f"\n🟢 全部通过!")
    sys.exit(0)
