#!/usr/bin/env python3
"""文档/INDEX 维护提示与粗检（v11.3.4：业务仓也提示，不限 ~/.claude）。"""
from __future__ import annotations

from pathlib import Path

CODE_EXTS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs",
    ".java", ".kt", ".c", ".cpp", ".h", ".cs", ".rb", ".php", ".swift",
}


def hint_for_path(rel: str) -> list[str]:
    hints: list[str] = []
    posix = Path(rel).as_posix().replace("\\", "/")
    name = Path(rel).name
    suffix = Path(rel).suffix.lower()

    if posix.startswith("agents/") and posix.endswith(".md") and name != "README.md":
        hints.append("检查 agents-INDEX.md 是否需更新条目")
    elif "/skills/" in f"/{posix}" and name == "SKILL.md":
        hints.append("检查 skills-INDEX.md 是否需更新条目")
    elif posix.startswith("rules/") and posix.endswith(".md") and name != "README.md":
        hints.append("rules 经 sync.ps1 刷新到 ~/.cursor/plugins/local/claude-config/rules；检查 rules-INDEX.md")
    elif name in ("MANIFEST.yaml", "MANIFEST.yml"):
        hints.append("检查 concern 归属与 *-INDEX.md 一致性")
    elif posix.startswith("hooks/") or "templates/cursor-guard/" in posix:
        hints.append("运行 deploy-cursor-guard.ps1 部署到 ~/.cursor（不跑 sync.ps1）")
    elif name == "README.md" or posix.startswith("docs/") or "/docs/" in posix:
        hints.append("确认文档交叉链接与 CHANGELOG / INDEX 一致")

    if suffix in CODE_EXTS:
        hints.append("核对 README/注释是否仍准确；漏改写「无文档影响」或已同步路径")
        hints.append("Grep 残留引用须为 0；优先 codegraph_explore blast-radius")
    elif suffix in {".md", ".mdc"} and "检查" not in " ".join(hints):
        hints.append("确认 INDEX/CHANGELOG/交叉链接是否需同步（漏改：文档）")
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
