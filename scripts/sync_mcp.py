#!/usr/bin/env python3
"""校验 .mcp.json 与派生视图一致（v10.17）。

命令：
    python scripts/sync_mcp.py      # 唯一用法，无参数；只读校验，不写任何文件

历史版本把 .mcp.json 的 mcpServers 写进 settings.json，这违反 rules/MCP.md §1
「settings.json 禁止定义 mcpServers（v3.0+）」。现改为只读校验：
  1. settings.json 不得含 mcpServers
  2. mcp/servers.json 的 always_* 并集必须与 .mcp.json 的键集完全一致
  3. mcp-configs/dev.json 的 servers 必须与 .mcp.json 的键集完全一致

退出码：0 一致；1 存在不一致（列出差异）。
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(rel):
    with open(os.path.join(BASE, rel), "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    problems = []

    mcp = load(".mcp.json")
    resident = set(mcp.get("mcpServers", {}))

    settings = load("settings.json")
    if "mcpServers" in settings:
        problems.append("settings.json 含 mcpServers（rules/MCP.md §1 禁止），请删除该键")

    servers = load("mcp/servers.json")
    toolsets = servers.get("toolsets", {})
    always = set()
    for name, items in toolsets.items():
        if name.startswith("always_"):
            always.update(items)
    if always != resident:
        problems.append(
            f"mcp/servers.json always_* 与 .mcp.json 不一致："
            f"多 {sorted(always - resident)} / 缺 {sorted(resident - always)}"
        )

    dev = set(load("mcp-configs/dev.json").get("servers", []))
    if dev != resident:
        problems.append(
            f"mcp-configs/dev.json servers 与 .mcp.json 不一致："
            f"多 {sorted(dev - resident)} / 缺 {sorted(resident - dev)}"
        )

    if problems:
        for p in problems:
            print(f"[FAIL] {p}")
        return 1

    print(f"[OK] MCP 常驻 {len(resident)} 项，servers.json / dev.json / settings.json 全部一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
