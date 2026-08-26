#!/usr/bin/env python3
"""R20 会话终验机械检测（v11.3.4）— 空模板不得过门。

Claude Stop 与 Cursor stop followup 共用，禁止再复制一份正则。
"""
from __future__ import annotations

import os
import re
import subprocess

_VERDICT_RE = re.compile(r"\b(PASS|NEEDS-CHANGES)\b")

_REQUIRED = ("遗漏", "错改", "漏改", "原功能")
_EMPTY_SATISFIED = {"", ".", "..", "...", "…", "无", "n/a", "na", "none"}
_PATH_RE = re.compile(
    r"(?:[A-Za-z]:)?[\\/][\w.\\/-]+|\S+\.(?:md|mdc|py|ts|tsx|js|json|ya?ml|toml|txt)\b"
)
_FIELD_RE = re.compile(
    r"(?:^|\n)\s*-?\s*(满足|遗漏|错改|漏改|原功能)\s*[：:]\s*(.*?)(?="
    r"(?:\n\s*-?\s*(?:满足|遗漏|错改|漏改|原功能)\s*[：:])|\n结论|$)",
    re.S,
)


def field_value(text: str, name: str) -> str:
    """取出终验字段正文；找不到返回空串。"""
    for match in _FIELD_RE.finditer(text):
        if match.group(1) == name:
            return match.group(2).strip()
    return ""


def replay_ok(text: str, requirements: dict | None = None) -> bool:
    """最后一条助手回复是否构成合格 R20（反空模板；v11.4 可选需求指纹实质比对）。

    requirements 非空且含 strong 特征时，「满足」行须覆盖指纹关键词——
    strong<5 全命中，≥5 允许 ≥80%（req_fingerprint.coverage_ok）。
    不传参行为与 v11.3 完全一致（Cursor 端旧调用兼容）。
    """
    if not text or not text.strip():
        return False
    if ("会话终验" not in text) and ("R20" not in text):
        return False
    if any(token not in text for token in _REQUIRED):
        return False

    satisfied = field_value(text, "满足")
    if satisfied.strip().lower() in _EMPTY_SATISFIED:
        return False

    if requirements:
        from req_fingerprint import coverage_ok

        ok, _detail = coverage_ok(requirements, satisfied)
        if not ok:
            return False

    missed = field_value(text, "漏改")
    if not missed:
        return False
    if not (
        "文档" in missed
        or "无文档影响" in missed
        or _PATH_RE.search(missed)
    ):
        return False

    original = field_value(text, "原功能")
    if not original:
        return False
    if not any(token in original for token in ("证据", "测试", "冒烟")):
        return False
    return True


def review_verdict_ok(text: str) -> bool:
    """v11.4：最后一条助手回复是否含独立审查结论标记（PASS / NEEDS-CHANGES）。"""
    if not text or not text.strip():
        return False
    return bool(_VERDICT_RE.search(text))


def has_unverified_edits(entry: dict) -> bool:
    """本会话有编辑且最后一次编辑后无验证命令。"""
    edited = entry.get("edited_files") or []
    if not edited:
        return False
    last_edit_ts = max((item.get("ts", 0) for item in edited), default=0)
    if last_edit_ts == 0:
        return False
    return not any(
        cmd.get("ts", 0) >= last_edit_ts - 1
        for cmd in (entry.get("verify_commands") or [])
    )


def cursor_should_followup(entry: dict) -> bool:
    """Cursor stop：有编辑且（无验证命令或 R20 未过）。"""
    if not (entry.get("edited_files") or []):
        return False
    if not entry.get("r20_replay_ok"):
        return True
    return has_unverified_edits(entry)


# ---- 方案A：清单制品 diff 差集校验（design-v2 v11.3.6）----


def _norm_path(p: str) -> str:
    p = p.strip().replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    return p


def git_dirty_set(cwd: str):
    """当前脏文件集；非 git 仓库返回 None。"""
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"], cwd=cwd or None,
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    files = set()
    for line in proc.stdout.splitlines():
        if len(line) > 3:
            rel = _norm_path(line[3:].strip().strip('"'))
            if rel.startswith(".claude/"):
                continue  # hook 自身运行时状态（清单制品等）不算变更面
            files.add(rel)
    return files


def manifest_log_path(cwd: str) -> str:
    return os.path.join(cwd or os.getcwd(), ".claude", "state", "impact-manifest.log")


def declared_impact(session_id: str, cwd: str) -> set:
    """本 session 在项目清单中声明的文件集。"""
    declared = set()
    try:
        with open(manifest_log_path(cwd), "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split("|")
                if len(parts) >= 3 and parts[0].strip() == "IMPACT" and parts[1].strip() == session_id:
                    for p in parts[2].split(","):
                        if p.strip():
                            declared.add(_norm_path(p))
    except OSError:
        pass
    return declared


def impact_diff_check(entry: dict, session_id: str, cwd: str = "") -> list:
    """Stop 门差集：当前脏集 − 会话基线集 − 声明清单 → 清单外变更列表。

    skip（返回 []）：无基线（非git/未记录）、无编辑、或 git 不可用。
    """
    baseline = entry.get("git_baseline")
    if not isinstance(baseline, list) or not baseline:
        return []
    if not (entry.get("edited_files") or []):
        return []
    current = git_dirty_set(cwd)
    if current is None:
        return []
    base = {_norm_path(p) for p in baseline}
    declared = declared_impact(session_id, cwd)
    extra = current - base - declared
    if extra:
        # 宽容匹配：清单声明为目录（以/结尾）或为某额外路径的后缀/前缀时不算清单外
        relaxed = set()
        for cur in extra:
            for dec in declared:
                if dec.endswith("/") and cur.startswith(dec):
                    relaxed.add(cur)
                elif cur.endswith(dec) or dec.endswith(cur):
                    relaxed.add(cur)
        extra -= relaxed
    return sorted(extra)
