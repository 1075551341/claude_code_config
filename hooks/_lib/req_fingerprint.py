#!/usr/bin/env python3
"""需求指纹留存与覆盖比对（v11.4）— R20「满足」行从形式校验升级为实质比对。

数据位 SSOT：verification-gate.json entry["requirements"]（不新增状态文件）。
特征提取复用 issue_state.extract_features 的 strong/weak 分层（零新算法）：
strong=路径/异常类名/错误码/代码符号/反引号片段；weak=英文词+中文 bigram。

capture_requirements(): 会话首条有效 prompt 建档；后续 prompt 合并 strong/weak
（需求演化），按 MAX_STRONG/MAX_WEAK 截断。斜杠命令（/xxx）与非有效长度跳过。
coverage_ok(): 「满足」行须命中 strong——strong<5 时须全命中，≥5 时允许 ≥80%。
weak-only 需求不启用实质比对（区分度不足，防误伤）。

写入端：pre-userprompt-issue-tracker.py（Claude Code）、Cursor Guard issue_tracker.py
（经 import_claude_lib 同源）、opencode 插件 gate_cli.py capture-req 子命令。
读取端：stop-verification-gate.has_requirements_replay / r20_replay.replay_ok。
"""
from __future__ import annotations

import json
import os
import sys
import time

MIN_PROMPT_LEN = 12
STRONG_COVERAGE_RATIO = 0.8


def _state_path() -> str:
    from issue_state import claude_home

    return str(claude_home() / ".state" / "verification-gate.json")


def load_gate_state() -> dict:
    try:
        with open(_state_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"req_fingerprint: state read failed: {e}", file=sys.stderr)
        return {}


def save_gate_state(state: dict) -> None:
    try:
        path = _state_path()
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)
    except OSError as e:
        print(f"req_fingerprint: state write failed: {e}", file=sys.stderr)


def capture_requirements(entry: dict, prompt: str) -> bool:
    """把一条用户 prompt 的分层特征合并进 entry["requirements"]；有变更返回 True。"""
    from issue_state import MAX_STRONG, MAX_WEAK, extract_features

    text = (prompt or "").strip()
    if len(text) < MIN_PROMPT_LEN or text.startswith("/"):
        return False
    feats = extract_features(text)
    if not feats.get("strong") and not feats.get("weak"):
        return False
    req = entry.get("requirements")
    if not isinstance(req, dict):
        entry["requirements"] = {"strong": list(feats["strong"]), "weak": list(feats["weak"])}
        return True
    merged_s = sorted(set(req.get("strong") or []) | set(feats.get("strong") or []))[:MAX_STRONG]
    merged_w = sorted(set(req.get("weak") or []) | set(feats.get("weak") or []))[:MAX_WEAK]
    if merged_s != req.get("strong") or merged_w != req.get("weak"):
        req["strong"], req["weak"] = merged_s, merged_w
        return True
    return False


def save_requirements(session_id: str, prompt: str) -> bool:
    """便捷入口：读全局状态→合并→仅在有变更时写回。失败静默降级（已打 stderr）。

    v11.4.1：建档时补 started_ts/ts（否则无编辑会话的指纹条目无时间戳，
    新鲜度探针与 7 天清理都无法命中）。
    """
    if not session_id or session_id == "unknown":
        return False
    state = load_gate_state()
    now = time.time()
    entry = state.setdefault(session_id, {})
    entry.setdefault("started_ts", now)
    entry["ts"] = now
    changed = capture_requirements(entry, prompt)
    if changed:
        save_gate_state(state)
    return changed


def coverage_ok(requirements: dict, satisfied_text: str) -> tuple[bool, str]:
    """「满足」行是否覆盖需求指纹 strong 集；返回 (是否合格, 明细)。"""
    strong = [s for s in ((requirements or {}).get("strong") or []) if s]
    if not strong:
        return True, "no-strong-features"
    text = (satisfied_text or "").lower()
    hit = sum(1 for s in strong if s.lower() in text)
    detail = f"{hit}/{len(strong)} strong"
    if len(strong) >= 5:
        return hit / len(strong) >= STRONG_COVERAGE_RATIO, detail
    return hit == len(strong), detail
