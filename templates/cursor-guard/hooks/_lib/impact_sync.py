#!/usr/bin/env python3
"""MANIFEST 影响图 → Cursor 同步计划（不重复 junction 逻辑）。"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# v11 常量单源：~/.claude/config/sync-manifest.json（与 sync.ps1 / check.ps1 共用）；
# 读取失败时回退内置默认（内容须与 manifest 一致）。
_DEFAULT_SYNC_FILES = frozenset(
    {
        "CLAUDE.md",
        "SPEC.md",
        "MANIFEST.yaml",
        "skills-INDEX.md",
        "agents-INDEX.md",
        "rules-INDEX.md",
    }
)


def _load_sync_files() -> frozenset[str]:
    manifest = Path.home() / ".claude" / "config" / "sync-manifest.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        files = data.get("root_files")
        if isinstance(files, list) and files:
            return frozenset(str(f) for f in files)
    except (OSError, ValueError):
        pass
    return _DEFAULT_SYNC_FILES


SYNC_FILES = _load_sync_files()
JUNCTION_PREFIXES = ("skills/", "agents/")
NO_SYNC_PREFIXES = ("hooks/", "scripts/", "plugins/", "commands/", ".git/")
NO_SYNC_EXACT = frozenset({"settings.json", ".mcp.json"})


class SyncScope(str, Enum):
    NONE = "none"
    RULES = "rules"
    INDEXES = "indexes"
    ALL = "all"


@dataclass
class SyncPlan:
    scope: SyncScope = SyncScope.NONE
    messages: list[str] = field(default_factory=list)
    changed: str = ""

    def merge(self, other: SyncScope) -> None:
        order = [SyncScope.NONE, SyncScope.RULES, SyncScope.INDEXES, SyncScope.ALL]
        if order.index(other) > order.index(self.scope):
            self.scope = other


def _parse_manifest_concerns(manifest_path: Path) -> list[dict]:
    if not manifest_path.exists():
        return []
    text = manifest_path.read_text(encoding="utf-8")
    concerns: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        m = re.match(r"^  (\w+):\s*$", line)
        if m:
            if current:
                concerns.append(current)
            current = {"name": m.group(1), "owner": "", "depends_on": []}
            continue
        if not current:
            continue
        om = re.match(r"^\s+owner:\s+(.+)$", line)
        if om:
            current["owner"] = om.group(1).strip()
            continue
        dm = re.match(r"^\s+depends_on:\s+\[(.+)\]\s*$", line)
        if dm:
            items = re.findall(r"[\w./-]+", dm.group(1))
            current["depends_on"] = items
    if current:
        concerns.append(current)
    return concerns


def _owner_to_scope(owner: str) -> SyncScope:
    if not owner:
        return SyncScope.NONE
    if owner.startswith("rules/"):
        return SyncScope.RULES
    if owner.startswith(("skill/", "agent/")):
        return SyncScope.NONE
    if owner.startswith(("hook/", "plugin/", "mcp/")):
        return SyncScope.NONE
    return SyncScope.NONE


def _dep_matches(rel: str, dep: str) -> bool:
    dep = dep.strip()
    if not dep:
        return False
    if dep.endswith("/"):
        return rel.startswith(dep) or rel + "/" == dep
    return rel == dep or rel.startswith(dep + "/")


def resolve_sync_plan(changed_path: str | Path, claude_home: Path) -> SyncPlan:
    """根据变更路径生成同步计划。"""
    plan = SyncPlan()
    try:
        p = Path(changed_path).resolve()
        base = claude_home.resolve()
        if base not in p.parents and p != base:
            return plan
        rel = p.relative_to(base).as_posix()
    except (ValueError, OSError):
        return plan

    plan.changed = rel

    if any(rel.startswith(prefix) for prefix in NO_SYNC_PREFIXES):
        plan.messages.append(f"{rel}: Claude Code 专用，不同步到 Cursor")
        return plan

    if rel in NO_SYNC_EXACT or rel.endswith("/settings.json"):
        plan.messages.append(f"{rel}: 配置文件不同步")
        return plan

    if rel.startswith(JUNCTION_PREFIXES):
        plan.messages.append(f"{rel}: skills/agents 目录联接已实时可见，无需 sync")
        return plan

    if rel.startswith("rules/") and rel.endswith(".md") and rel != "rules/README.md":
        plan.merge(SyncScope.RULES)
        plan.messages.append(
            f"{rel}: 刷新 rules → Cursor plugin *.mdc（唯一生效通道）"
            " + qoder-cn rules/*.mdc + trae-cn user_rules/*.md（v11.1 多编辑器）"
        )
        return plan

    if rel in SYNC_FILES:
        plan.merge(SyncScope.INDEXES)
        plan.messages.append(f"{rel}: 刷新总纲/索引软链")
        return plan

    manifest = _parse_manifest_concerns(claude_home / "MANIFEST.yaml")
    extra_scopes: list[SyncScope] = []

    for c in manifest:
        owner = c.get("owner", "")
        if owner and _dep_matches(rel, owner):
            s = _owner_to_scope(owner)
            if s != SyncScope.NONE:
                extra_scopes.append(s)

        for dep in c.get("depends_on", []):
            if not _dep_matches(rel, dep):
                continue
            s = _owner_to_scope(owner)
            if s != SyncScope.NONE:
                extra_scopes.append(s)
                plan.messages.append(
                    f"MANIFEST {c.get('name')}: 依赖 {dep} 变更 → 同步 {owner}"
                )

    for s in extra_scopes:
        plan.merge(s)

    if plan.scope == SyncScope.NONE and not plan.messages:
        plan.messages.append(f"{rel}: 无编辑器同步目标")

    return plan


# Cursor 规则的唯一生效通道是 local plugin 实体副本（~/.cursor/rules 不生效，
# sync.ps1 也只往 plugin 目录写）。v10.16 之前这里查 ~/.cursor/rules，
# 结果每个会话都报「过期规则 AGENTS, BESTPRACTICE, CORE...」的假警报。
CURSOR_PLUGIN_RULES = Path.home() / ".cursor" / "plugins" / "local" / "claude-config" / "rules"


def _editor_rule_channels() -> list[tuple[str, Path, str]]:
    """v11.1 多编辑器规则落点：[(编辑器名, 通道目录, 扩展名)]。

    清单单源 sync-manifest.json editors 段；cursor 走 plugin 常量，此处只列其余
    编辑器中「已启用 + home 在装 + 有规则通道」者。读取失败回退内置默认。
    """
    defaults = [
        ("qoder-cn", Path.home() / ".qoder-cn" / "rules", ".mdc"),
        ("trae-cn", Path.home() / ".trae-cn" / "user_rules", ".md"),
    ]
    manifest = Path.home() / ".claude" / "config" / "sync-manifest.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        editors = data.get("editors")
        if not isinstance(editors, dict):
            return [(n, d, e) for n, d, e in defaults if d.parent.is_dir()]
        out: list[tuple[str, Path, str]] = []
        for name, cfg in editors.items():
            if name in ("_comment", "cursor") or not isinstance(cfg, dict):
                continue
            if cfg.get("enabled") is False or not cfg.get("rules_channel"):
                continue
            home = Path(str(cfg.get("home", "")).replace("~", str(Path.home()), 1))
            if not home.is_dir():
                continue
            out.append((name, home / str(cfg["rules_channel"]), str(cfg.get("rules_ext") or ".md")))
        return out
    except (OSError, ValueError):
        return [(n, d, e) for n, d, e in defaults if d.parent.is_dir()]


def rules_out_of_sync(claude_home: Path) -> tuple[bool, str]:
    """比较 rules 源 .md 与各编辑器落点副本是否漂移（Cursor plugin + qoder/trae 等）。

    以**内容**为准而非 mtime：sync.ps1 是拷贝部署，mtime 天然晚于源文件，
    但重装/回滚等场景 mtime 也可能倒挂，只有内容比对才能给出可信结论。
    """
    rules_src = claude_home / "rules"
    if not rules_src.is_dir() or not CURSOR_PLUGIN_RULES.is_dir():
        return False, "rules 目录缺失，跳过检测"
    src_rules = [md for md in rules_src.glob("*.md") if md.name != "README.md"]

    def _stale_in(target_dir: Path, ext: str) -> list[str]:
        found: list[str] = []
        for md in src_rules:
            dst = target_dir / f"{md.stem}{ext}"
            try:
                if not dst.exists() or md.read_text(encoding="utf-8") != dst.read_text(encoding="utf-8"):
                    found.append(md.stem)
            except OSError:
                found.append(md.stem)
        return found

    parts: list[str] = []
    stale_cursor = _stale_in(CURSOR_PLUGIN_RULES, ".mdc")
    if stale_cursor:
        tail = "..." if len(stale_cursor) > 8 else ""
        parts.append(f"cursor: {', '.join(stale_cursor[:8])}{tail}")
    for ed_name, chan_dir, ext in _editor_rule_channels():
        if not chan_dir.is_dir():
            parts.append(f"{ed_name}: 通道缺失（跑 sync.ps1）")
            continue
        stale = _stale_in(chan_dir, ext)
        if stale:
            tail = "..." if len(stale) > 8 else ""
            parts.append(f"{ed_name}: {', '.join(stale[:8])}{tail}")
    if parts:
        return True, f"过期规则 — {'; '.join(parts)}"
    return False, "rules 已同步"
