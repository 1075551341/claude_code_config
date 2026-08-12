#!/usr/bin/env python3
"""问题指纹追踪共享状态（v10.17.0）— 治「同问题重复处理」。

SSOT：`<claude_home>/.state/issue-tracker.json`。Claude Code 的
`pre-userprompt-issue-tracker.py` 与 Cursor Guard 的 `issue_tracker.py` 双端共用
同一份指纹算法与同一份状态文件，跨编辑器重复提问才能被识别（v10.16 之前两端
各写各的 state，Cursor 与 Claude 互不可见）。

`stop-verification-gate.py` 在验证全部通过时调用 `mark_session_resolved()`，把本
会话涉及的指纹标记为已解决 —— 这样下次命中走轻提示而非「禁止从头重做」硬提醒。
v10.16 写入了 `resolved` 字段却没有任何写 true 的位置，轻提示分支形同死代码。

测试隔离：设置环境变量 `CLAUDE_HOME` 指向临时目录即可（Windows 上 `HOME` 对
`Path.home()` 无效，勿依赖）。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

STATE_NAME = "issue-tracker.json"

DEFAULT_CFG = {
    "enabled": True,
    "max_age_days": 30,
    "min_interval_sec": 120,
    "min_prompt_len": 10,
}

# compact 后重问的判定间隔：同会话内两次提问间隔超过此值视为上下文已丢失
COMPACT_GAP_SEC = 3600

STOP_TOKENS = {
    "the", "and", "for", "with", "this", "that", "from", "what", "how", "why",
    "的", "了", "和", "是", "在", "我", "你", "请", "把", "给", "下", "一", "个",
    "这个", "那个", "一下", "什么", "怎么", "为什么", "现在", "还是",
}

PATH_RE = re.compile(
    r"[A-Za-z]:\\[\w\-.\\]+|/[\w\-./]+|[\w\-]+\.(?:py|ts|tsx|js|jsx|vue|go|rs|java|md|json|yaml|yml)"
)
ERROR_RE = re.compile(
    r"(?i)(error|failed|exception|traceback|报错|失败|错误|异常|不行|不能|无法)"
)
WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_\-]{2,}|[一-鿿]{2,}")


def claude_home() -> Path:
    return Path(os.environ.get("CLAUDE_HOME") or (Path.home() / ".claude"))


def state_file() -> Path:
    return claude_home() / ".state" / STATE_NAME


def load_state() -> dict:
    path = state_file()
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"issue_state: state read failed: {e}", file=sys.stderr)
    return {}


def save_state(state: dict, max_age_days: int) -> None:
    path = state_file()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        now = time.time()
        max_age = max_age_days * 86400
        pruned = {k: v for k, v in state.items() if now - v.get("last_ts", 0) < max_age}
        path.write_text(json.dumps(pruned, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError as e:
        print(f"issue_state: state write failed: {e}", file=sys.stderr)


def fingerprint(prompt: str, cwd: str) -> str:
    """归一化提取特征 token：文件路径/错误关键词/高信息词 top-8 + cwd → SHA1[:12]"""
    text = prompt.lower()
    features = set(PATH_RE.findall(prompt))
    # 具体错误关键词替代笼统 __error__，增加区分度
    for kw in ERROR_RE.findall(text):
        features.add(f"__err_{kw.lower()}__")
    words = [w for w in WORD_RE.findall(text) if w not in STOP_TOKENS and len(w) >= 3]
    freq: dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    top = sorted(freq, key=lambda w: (-freq[w], w))[:8]
    features.update(top)
    raw = "|".join(sorted(features)) + "@" + (cwd or "")
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def min_prompt_len(prompt: str, cfg: dict) -> int:
    """含错误关键词的短 prompt 放宽至 4 字符（覆盖「还是不行」「修一下」等追问短句）。"""
    return 4 if ERROR_RE.search(prompt.lower()) else int(cfg["min_prompt_len"])


def build_message(count: int, first_ts: float) -> str:
    first = time.strftime("%Y-%m-%d %H:%M", time.localtime(first_ts))
    return (
        f"【门控 · 疑似重复问题（第 {count} 次出现，首次 {first}）】\n"
        "该问题此前已处理过。禁止从头重来：\n"
        "1. claude-mem search 查历史决策/上轮结论（R18）\n"
        "2. 查上轮制品（.planning/ openspec/ spec/）与 stop-session-summary\n"
        "3. 上轮方案失败 → 必须换方案（R5 同方案≤2 次）+ 执行升档非简单 + verify_tier=全量\n"
        "4. 疑难/歧义未清 → 先 grill 澄清 + 影响面清单，用户确认后再改"
    )


def build_light_message(count: int, first_ts: float, reason: str) -> str:
    """轻提示（resolved 后命中 / compact 后重问）— 不强制禁止重做。"""
    first = time.strftime("%Y-%m-%d %H:%M", time.localtime(first_ts))
    return (
        f"【提示 · 疑似重复问题（第 {count} 次，首次 {first}，{reason}）】\n"
        "此问题此前已处理。建议先查上轮结论再决定是否重做。"
    )


def merge_config(user_cfg: dict | None) -> dict:
    cfg = dict(DEFAULT_CFG)
    for key in cfg:
        if user_cfg and key in user_cfg:
            cfg[key] = user_cfg[key]
    return cfg


def record(prompt: str, cwd: str, session_id: str, cfg: dict) -> str | None:
    """记录一次提问；命中历史指纹且过防抖窗口时返回注入文本，否则返回 None。"""
    fp = fingerprint(prompt, cwd)
    now = time.time()
    state = load_state()
    entry = state.get(fp)

    inject = None
    if entry is None:
        state[fp] = {
            "count": 1,
            "first_ts": now,
            "last_ts": now,
            "last_inject_ts": 0,
            "last_session_id": session_id,
            "sessions": [session_id],
            "resolved": False,
        }
    else:
        entry["count"] = int(entry.get("count", 1)) + 1
        prev_last_ts = float(entry.get("last_ts", now))
        prev_session = entry.get("last_session_id", "")
        entry["last_ts"] = now
        entry["last_session_id"] = session_id
        sessions = entry.setdefault("sessions", [])
        if session_id not in sessions:
            sessions.append(session_id)
            del sessions[:-10]
        debounce_ok = now - float(entry.get("last_inject_ts", 0)) >= int(cfg["min_interval_sec"])
        if debounce_ok:
            entry["last_inject_ts"] = now
            count = entry["count"]
            first_ts = float(entry.get("first_ts", now))
            if entry.get("resolved"):
                inject = build_light_message(count, first_ts, "已标记解决")
            elif prev_session == session_id and (now - prev_last_ts) > COMPACT_GAP_SEC:
                inject = build_light_message(count, first_ts, "疑似 compact 后重问")
            else:
                inject = build_message(count, first_ts)

    save_state(state, int(cfg["max_age_days"]))
    return inject


def mark_session_resolved(session_id: str, max_age_days: int = 30) -> int:
    """把本会话触碰过的指纹标记为已解决，返回标记数量。

    由 stop-verification-gate 在验证全部通过时调用。再次命中同指纹时改走轻提示，
    避免对「已修好又想微调」的正常追问强行注入禁止重做。
    """
    if not session_id:
        return 0
    state = load_state()
    marked = 0
    for entry in state.values():
        touched = entry.get("last_session_id") == session_id or session_id in (
            entry.get("sessions") or []
        )
        if touched and not entry.get("resolved"):
            entry["resolved"] = True
            entry["resolved_ts"] = time.time()
            marked += 1
    if marked:
        save_state(state, max_age_days)
    return marked
