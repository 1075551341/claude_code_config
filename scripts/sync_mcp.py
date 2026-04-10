#!/usr/bin/env python3
"""Sync MCP servers from .mcp.json to settings.json"""
import json, os

base = r'C:\Users\DELL\.claude'

with open(os.path.join(base, '.mcp.json'), 'r', encoding='utf-8') as f:
    mcp_config = json.load(f)

with open(os.path.join(base, 'settings.json'), 'r', encoding='utf-8') as f:
    settings = json.load(f)

# Sync: use .mcp.json as source of truth for mcpServers
settings['mcpServers'] = mcp_config.get('mcpServers', {})
settings['_mcp_section'] = f"MCP 服务器配置（共 {len(settings['mcpServers'])} 个，与 .mcp.json 同步）"

with open(os.path.join(base, 'settings.json'), 'w', encoding='utf-8') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print(f"Synced {len(settings['mcpServers'])} MCP servers from .mcp.json to settings.json")
