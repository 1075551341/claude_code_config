#!/usr/bin/env python3
"""Final validation of .claude configuration"""
import json, os

base = r'C:\Users\DELL\.claude'
errors = []

# 1. Validate JSON files
for f in ['settings.json', '.mcp.json', 'config.json', '.claude.json']:
    path = os.path.join(base, f)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                json.load(fh)
        except Exception as e:
            errors.append(f'{f}: {e}')

# 2. Count resources
agents_dir = os.path.join(base, 'agents')
agent_count = len([f for f in os.listdir(agents_dir) if f.endswith('.md') and f != 'README.md'])

skills_dir = os.path.join(base, 'skills')
skill_count = len([d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))])

rules_dir = os.path.join(base, 'rules')
rule_count = len([f for f in os.listdir(rules_dir) if f.endswith('.md') and f != 'README.md'])

hooks_dir = os.path.join(base, 'hooks')
hook_count = len([f for f in os.listdir(hooks_dir) if f.endswith('.py')])

with open(os.path.join(base, '.mcp.json'), 'r', encoding='utf-8') as fh:
    mcp = json.load(fh)
mcp_count = len(mcp.get('mcpServers', {}))

# 3. MCP sync check
with open(os.path.join(base, 'settings.json'), 'r', encoding='utf-8') as fh:
    settings = json.load(fh)
settings_mcp = set(settings.get('mcpServers', {}).keys())
dot_mcp = set(mcp.get('mcpServers', {}).keys())
if settings_mcp != dot_mcp:
    errors.append(f'MCP mismatch: settings={len(settings_mcp)}, .mcp.json={len(dot_mcp)}')

# 4. Agent name consistency
with open(os.path.join(base, 'CLAUDE.md'), 'r', encoding='utf-8') as fh:
    claude_md = fh.read()
existing_agents = set(f.replace('.md','') for f in os.listdir(agents_dir) if f.endswith('.md') and f != 'README.md')
key_agents = ['code-reviewer', 'execution-planner', 'architect', 'security-reviewer', 'systematic-debugging', 'tdd-guide']
for a in key_agents:
    if a not in existing_agents:
        errors.append(f'Routed agent not found: {a}')

# 5. No hardcoded mcp prefixes
if 'mcp0_' in claude_md or 'mcp1_' in claude_md:
    errors.append('CLAUDE.md still has hardcoded mcp0/mcp1 prefixes')

# 6. Hooks all use launcher
hooks_config = settings.get('hooks', {})
for event_type, groups in hooks_config.items():
    for group in groups:
        for h in group.get('hooks', []):
            cmd = h.get('command', '')
            if '_editor_hook_launcher.py' not in cmd:
                errors.append(f'Hook without launcher: {cmd[:60]}')

# Print results
print('=== FINAL VALIDATION ===')
print(f'Agents: {agent_count}')
print(f'Skills: {skill_count}')
print(f'Rules: {rule_count}')
print(f'Hooks: {hook_count} files')
print(f'MCP servers: {mcp_count}')
print(f'CLAUDE.md: {len(claude_md)} chars, v3.3')
print()
if errors:
    print(f'ERRORS ({len(errors)}):')
    for e in errors:
        print(f'  - {e}')
else:
    print('ALL CHECKS PASSED')
