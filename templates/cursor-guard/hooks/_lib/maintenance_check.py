#!/usr/bin/env python3
"""文档/INDEX 维护提示与粗检（不解析 MANIFEST）。"""
from __future__ import annotations

from pathlib import Path


def hint_for_path(rel: str) -> list[str]:
    hints: list[str] = []
    if rel.startswith("agents/") and rel.endswith(".md") and rel != "agents/README.md":
        hints.append("检查 agents-INDEX.md 是否需更新条目")
    elif rel.startswith("skills/") and rel.endswith("/SKILL.md"):
        hints.append("检查 skills-INDEX.md 是否需更新条目")
    elif rel.startswith("rules/") and rel.endswith(".md") and rel != "rules/README.md":
        hints.append("rules 将自动 sync 到 ~/.cursor/rules；检查 rules-INDEX.md")
    elif rel == "MANIFEST.yaml":
        hints.append("检查 concern 归属与 *-INDEX.md 一致性")
    elif rel.startswith("hooks/") or rel.startswith("templates/cursor-guard/"):
        hints.append("运行 deploy-cursor-guard.ps1 部署到 ~/.cursor（不跑 sync.ps1）")
    elif rel == "README.md" or rel.startswith("docs/"):
        hints.append("确认文档交叉链接与 SYNC_GUIDE / CURSOR_EDITOR_SETUP 一致")
    return hints


def index_drift_report(claude_home: Path) -> list[str]:
    """INDEX mtime 粗检：源目录最新文件是否新于 INDEX。"""
    reports: list[str] = []
    checks = (
        ("agents", "agents-INDEX.md", "*.md"),
        ("skills", "skills-INDEX.md", "**/SKILL.md"),
        ("rules", "rules-INDEX.md", "*.md"),
    )
    for subdir, index_name, pattern in checks:
        src_dir = claude_home / subdir
        index_file = claude_home / index_name
        if not src_dir.is_dir() or not index_file.exists():
            continue
        try:
            if pattern.startswith("**/"):
                files = list(src_dir.glob(pattern))
            else:
                files = list(src_dir.glob(pattern))
            files = [f for f in files if f.name != "README.md"]
            if not files:
                continue
            latest = max(f.stat().st_mtime for f in files)
            idx_mtime = index_file.stat().st_mtime
            if latest > idx_mtime + 1:
                reports.append(f"{index_name} 可能过期（源 {subdir}/ 有更新）")
        except OSError:
            continue
    return reports
