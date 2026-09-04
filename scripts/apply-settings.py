# -*- coding: utf-8 -*-
"""Apply hooks.snippet.json into settings.json without touching secrets."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNIPPET = ROOT / "templates" / "claude-settings" / "hooks.snippet.json"
SETTINGS = ROOT / "settings.json"
HOME = str(ROOT).replace("\\", "/")


def main() -> None:
    snippet = json.loads(SNIPPET.read_text(encoding="utf-8"))
    hooks = json.loads(json.dumps(snippet["hooks"]).replace("{{CLAUDE_HOME}}", HOME))
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    settings["hooks"] = hooks
    settings["_comment"] = (
        "Claude Code 主配置 v12 | MCP 权威源: .mcp.json | hooks 由 templates/claude-settings/hooks.snippet.json 生成"
    )
    settings.pop("_hooks_section", None)
    settings.pop("_mcp_section", None)
    if "env" in settings:
        settings["env"].pop("ANTHROPIC_AUTH_TOKEN", None)
    enabled = settings.setdefault("enabledPlugins", {})
    enabled.pop("warp@claude-code-warp", None)
    enabled.pop("claude-code-setup@claude-plugins-official", None)
    extra = settings.get("extraKnownMarketplaces") or {}
    extra.pop("claude-code-warp", None)
    settings["extraKnownMarketplaces"] = extra
    SETTINGS.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("applied hooks from snippet; warp ghost plugin removed")


if __name__ == "__main__":
    main()
