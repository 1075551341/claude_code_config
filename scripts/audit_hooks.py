#!/usr/bin/env python3
"""Audit hooks safety in settings.json"""
import json, os

base = r'C:\Users\DELL\.claude'
settings_path = os.path.join(base, 'settings.json')

with open(settings_path, 'r', encoding='utf-8') as f:
    settings = json.load(f)

hooks = settings.get('hooks', {})
launcher = '_editor_hook_launcher.py'

print('=== HOOKS SAFETY AUDIT ===\n')

all_safe = True
for event_type, groups in hooks.items():
    print(f'[{event_type}]')
    for i, group in enumerate(groups):
        matcher = group.get('matcher', '(empty)')
        for h in group.get('hooks', []):
            cmd = h.get('command', '')
            timeout = h.get('timeout', 0)
            uses_launcher = launcher in cmd
            status = 'OK' if uses_launcher else 'UNSAFE'
            if not uses_launcher:
                all_safe = False
            hook_name = cmd.split(launcher)[-1].strip().split('/')[-1] if uses_launcher else cmd[:60]
            print(f'  {status} | {matcher:25s} | {hook_name:40s} | timeout={timeout}ms')

print(f'\nAll hooks use launcher: {all_safe}')

print('\n=== POTENTIAL ISSUES ===')
issues = []

for event_type, groups in hooks.items():
    for group in groups:
        for h in group.get('hooks', []):
            timeout = h.get('timeout', 0)
            if timeout > 30000:
                cmd = h.get('command', '')
                hook_name = cmd.split(launcher)[-1].strip().split('/')[-1] if launcher in cmd else cmd[:40]
                issues.append(f'Long timeout: {hook_name} ({timeout}ms)')

for group in hooks.get('PreToolUse', []):
    matcher = group.get('matcher', '')
    num_hooks = len(group.get('hooks', []))
    if num_hooks > 4:
        issues.append(f'Many PreToolUse hooks for "{matcher}": {num_hooks} (may slow response)')

if issues:
    for issue in issues:
        print(f'  - {issue}')
else:
    print('  None found')
