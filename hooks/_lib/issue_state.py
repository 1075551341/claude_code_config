#!/usr/bin/env python3
"""问题指纹追踪共享状态（v11.1.1）— 治「同问题重复处理」。

SSOT：`<claude_home>/.state/issue-tracker.json`。Claude Code 的
`pre-userprompt-issue-tracker.py` 与 Cursor Guard 的 `issue_tracker.py` 双端共用
同一份指纹算法与同一份状态文件（Cursor 经 `import_claude_lib` 直接加载本源文件，
改动即时双端生效），跨编辑器重复提问才能被识别。

`stop-verification-gate.py` 在验证全部通过时调用 `mark_session_resolved()`，把本
会话涉及的指纹标记为已解决 —— 下次命中走轻提示；若解决后同问题仍反复出现
（回归），自动撤销 resolved 并重新升级硬提醒。

v11.1.1 判定重构（原 v10.17 实现为特征集 SHA1 精确匹配，粗糙/不准）：
  1. 相似匹配替代精确哈希 —— 条目存特征集（strong/weak 两层），命中 = 精确 key
     短路 或 同 cwd 条目加权相似度过阈（strong=overlap 系数、weak=Jaccard）。
  2. 中文按字符 bigram 切分（原整段连续中文被当作单 token，换措辞即漏检）。
  3. 泛化追问（「还是不行」「修一下」等短且无具体信号）不再独立成桶 ——
     续接同会话 2h 内最近条目，无可续接则忽略（原实现会让不相干问题共桶误报）。
  4. cwd 归一化（小写/正斜杠/去尾分隔符）—— CC 与 Cursor 传参形态不同不再破坏
     跨端识别。
  5. resolved 回归升级：已解决条目再连续命中 ≥2 次 → 撤销 resolved、恢复硬提醒。
  6. 泛化错误词（报错/失败/error…）不再作为指纹特征（区分度≈0），仅用于
     min_prompt_len 放宽与续接判定。

状态兼容：旧条目（无 features 字段）仅参与精确 key 匹配，按 max_age 自然老化。

测试隔离：设置环境变量 `CLAUDE_HOME` 指向临时目录即可（Windows 上 `HOME` 对
`Path.home()` 无效，勿依赖）。单元测试 → `hooks/tests/test_issue_state.py`。
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
    # 相似匹配阈值（strong+weak 加权分）；纯弱信号匹配自动抬高 +0.15（至少 0.6）
    "similarity_threshold": 0.5,
}

# compact 后重问的判定间隔：同会话内两次提问间隔超过此值视为上下文已丢失
COMPACT_GAP_SEC = 3600
# 泛化追问可续接同会话最近条目的时间窗
CONTINUATION_GAP_SEC = 7200
# 泛化追问判定：长度上限（strip 后）
CONTINUATION_MAX_LEN = 12
# 状态条目上限（按 last_ts 保留最新，防相似度扫描成本失控）
MAX_ENTRIES = 300
# 特征集截断上限
MAX_STRONG = 16
MAX_WEAK = 48

STOP_TOKENS = {
    "the", "and", "for", "with", "this", "that", "from", "what", "how", "why",
    "not", "can", "cannot", "please", "help", "still", "now", "just", "fix",
    "的", "了", "和", "是", "在", "我", "你", "请", "把", "给", "下", "一", "个",
    "这个", "那个", "一下", "什么", "怎么", "为什么", "现在", "还是", "不行",
    "不能", "无法", "问题", "报错", "错误", "失败", "异常", "修复", "修改",
    "帮我", "看看", "检查", "处理", "解决",
}

PATH_RE = re.compile(
    r"[A-Za-z]:[\\/][\w\-.\\/]+"
    r"|/[\w\-./]+"
    r"|[\w\-]+\.(?:py|ts|tsx|js|jsx|vue|go|rs|java|md|json|yaml|yml|ps1|sh|css|scss|html|sql|toml)\b"
)
ERROR_RE = re.compile(
    r"(?i)(error|failed|exception|traceback|报错|失败|错误|异常|不行|不能|无法|坏了|崩了)"
)
# 强信号：异常类名 / 错误码 / HTTP 状态码
EXC_RE = re.compile(r"\b[A-Z][a-zA-Z]*(?:Error|Exception|Warning)\b")
CODE_RE = re.compile(r"\b(?:E\d{2,5}|[45]\d{2}|0x[0-9A-Fa-f]{2,8})\b")
# 强信号：代码符号（CamelCase / snake_case / dotted.name / UPPER_CONST / kebab-case 文件名样式）
SYMBOL_RE = re.compile(
    r"\b[a-z]+(?:[A-Z][a-z0-9]+)+\b"          # camelCase
    r"|\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+\b"  # PascalCase
    r"|\b\w+_\w+(?:_\w+)*\b"                    # snake_case
    r"|\b[A-Z]{2,}(?:_[A-Z0-9]+)+\b"            # UPPER_CONST
    r"|\b[\w$]+\.[\w$]+(?:\.[\w$]+)+\b"          # dotted.path.name
)
BACKTICK_RE = re.compile(r"`([^`\n]{2,60})`")
EN_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9\-]{2,}")
CJK_RUN_RE = re.compile(r"[一-鿿]{2,}")


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
        if len(pruned) > MAX_ENTRIES:
            keep = sorted(pruned, key=lambda k: pruned[k].get("last_ts", 0), reverse=True)[:MAX_ENTRIES]
            pruned = {k: pruned[k] for k in keep}
        path.write_text(json.dumps(pruned, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError as e:
        print(f"issue_state: state write failed: {e}", file=sys.stderr)


# ── 特征提取与相似度 ─────────────────────────────────────────


def norm_cwd(cwd: str) -> str:
    """cwd 归一化：小写 + 正斜杠 + 去尾分隔符 —— CC 与 Cursor 传参形态差异不破坏跨端匹配。"""
    return (cwd or "").strip().lower().replace("\\", "/").rstrip("/")


def _norm_path_token(p: str) -> str:
    """路径特征取归一化文件名（大小写/目录前缀差异不影响匹配）。"""
    tail = p.strip().lower().replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]
    return tail or p.strip().lower()


def _cjk_bigrams(run: str) -> list[str]:
    if len(run) < 2:
        return []
    if len(run) == 2:
        return [run]
    return [run[i:i + 2] for i in range(len(run) - 1)]


def extract_features(prompt: str) -> dict:
    """分层特征：strong=路径/异常名/错误码/代码符号/反引号片段；weak=英文词+中文 bigram。

    泛化错误词（报错/error/…）不进特征——出现在几乎所有调试类 prompt 中，区分度≈0。
    """
    text = prompt.strip()
    lower = text.lower()

    strong: set[str] = set()
    for p in PATH_RE.findall(text):
        strong.add(_norm_path_token(p))
    for m in EXC_RE.findall(text):
        strong.add(m.lower())
    for m in CODE_RE.findall(text):
        strong.add(m.lower())
    for m in SYMBOL_RE.findall(text):
        tok = m.lower()
        if tok not in STOP_TOKENS and len(tok) >= 4:
            strong.add(tok)
    for m in BACKTICK_RE.findall(text):
        strong.add(m.strip().lower())

    weak: set[str] = set()
    for w in EN_WORD_RE.findall(lower):
        if w not in STOP_TOKENS and len(w) >= 3:
            weak.add(w)
    for run in CJK_RUN_RE.findall(text):
        for bg in _cjk_bigrams(run):
            if bg not in STOP_TOKENS:
                weak.add(bg)
    weak -= strong

    return {
        "strong": sorted(strong)[:MAX_STRONG],
        "weak": sorted(weak)[:MAX_WEAK],
    }


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _overlap(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def similarity(f1: dict, f2: dict) -> tuple[float, float]:
    """返回 (得分, 生效阈值加成)。

    - 双方均有强信号：0.6*overlap(strong) + 0.4*jaccard(weak)，加成 0
    - 任一方无强信号：退化为 jaccard(weak)，加成 +0.15（纯弱信号要求更高）
    """
    s1, s2 = set(f1.get("strong") or []), set(f2.get("strong") or [])
    w1, w2 = set(f1.get("weak") or []), set(f2.get("weak") or [])
    if s1 and s2:
        return 0.6 * _overlap(s1, s2) + 0.4 * _jaccard(w1, w2), 0.0
    return _jaccard(w1, w2), 0.15


def fingerprint(prompt: str, cwd: str) -> str:
    """特征集 + 归一化 cwd → SHA1[:12]（作为状态 key；匹配主要靠相似度，key 仅精确短路）。"""
    f = extract_features(prompt)
    raw = "|".join(f["strong"]) + "#" + "|".join(f["weak"]) + "@" + norm_cwd(cwd)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def is_generic_followup(prompt: str, features: dict) -> bool:
    """泛化追问：短、含错误词、无任何强信号 —— 不配独立成桶。"""
    text = prompt.strip()
    return (
        len(text) <= CONTINUATION_MAX_LEN
        and bool(ERROR_RE.search(text.lower()))
        and not features.get("strong")
    )


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
    """轻提示（resolved 后首次命中 / compact 后重问）— 不强制禁止重做。"""
    first = time.strftime("%Y-%m-%d %H:%M", time.localtime(first_ts))
    return (
        f"【提示 · 疑似重复问题（第 {count} 次，首次 {first}，{reason}）】\n"
        "此问题此前已处理。建议先查上轮结论再决定是否重做。"
    )


def build_regression_message(count: int, first_ts: float) -> str:
    first = time.strftime("%Y-%m-%d %H:%M", time.localtime(first_ts))
    return (
        f"【门控 · 已解决问题回归（第 {count} 次出现，首次 {first}）】\n"
        "该问题曾验证通过后又反复出现 —— 按回归处理：\n"
        "1. 先查上轮修复方案与验证记录（claude-mem / stop-session-summary）\n"
        "2. 上轮方案无效 → 必须换方案（R5）+ 执行升档非简单 + verify_tier=全量\n"
        "3. 确认根因后再改，禁止在旧补丁上叠补丁"
    )


def merge_config(user_cfg: dict | None) -> dict:
    cfg = dict(DEFAULT_CFG)
    for key in cfg:
        if user_cfg and key in user_cfg:
            cfg[key] = user_cfg[key]
    return cfg


def _find_match(state: dict, key: str, features: dict, cwd_n: str, threshold: float):
    """精确 key 短路，否则同 cwd 条目相似度扫描，返回 (entry_key, entry) 或 (None, None)。"""
    if key in state:
        return key, state[key]
    best_key, best_entry, best_score = None, None, 0.0
    for k, entry in state.items():
        ef = entry.get("features")
        if not ef:
            continue  # 旧格式条目：仅精确匹配
        if entry.get("cwd", "") != cwd_n:
            continue
        score, bump = similarity(features, ef)
        eff = min(max(threshold + bump, 0.6 if bump else threshold), 0.95)
        if score >= eff and score > best_score:
            best_key, best_entry, best_score = k, entry, score
    return best_key, best_entry


def _find_continuation(state: dict, session_id: str, now: float):
    """泛化追问续接目标：同会话 2h 内最近条目。"""
    best_key, best_entry = None, None
    for k, entry in state.items():
        if entry.get("last_session_id") != session_id:
            continue
        if now - float(entry.get("last_ts", 0)) > CONTINUATION_GAP_SEC:
            continue
        if best_entry is None or entry.get("last_ts", 0) > best_entry.get("last_ts", 0):
            best_key, best_entry = k, entry
    return best_key, best_entry


def _merge_entry_features(entry: dict, features: dict) -> None:
    """命中后把新特征并入条目（问题描述会演化），截断防膨胀。"""
    ef = entry.get("features")
    if not ef:
        entry["features"] = dict(features)
        return
    ef["strong"] = sorted(set(ef.get("strong") or []) | set(features.get("strong") or []))[:MAX_STRONG]
    ef["weak"] = sorted(set(ef.get("weak") or []) | set(features.get("weak") or []))[:MAX_WEAK]


def record(prompt: str, cwd: str, session_id: str, cfg: dict) -> str | None:
    """记录一次提问；命中历史条目且过防抖窗口时返回注入文本，否则返回 None。"""
    features = extract_features(prompt)
    cwd_n = norm_cwd(cwd)
    now = time.time()
    state = load_state()
    threshold = float(cfg.get("similarity_threshold", DEFAULT_CFG["similarity_threshold"]))

    generic = is_generic_followup(prompt, features)
    if generic:
        # 泛化追问不建新桶：续接同会话最近条目，无可续接则忽略
        _, entry = _find_continuation(state, session_id, now)
        if entry is None:
            return None
        merge_features = False
    else:
        key = fingerprint(prompt, cwd)
        _, entry = _find_match(state, key, features, cwd_n, threshold)
        merge_features = True
        if entry is None:
            state[key] = {
                "count": 1,
                "first_ts": now,
                "last_ts": now,
                "last_inject_ts": 0,
                "last_session_id": session_id,
                "sessions": [session_id],
                "resolved": False,
                "resolved_hits": 0,
                "cwd": cwd_n,
                "features": features,
            }
            save_state(state, int(cfg["max_age_days"]))
            return None

    inject = None
    entry["count"] = int(entry.get("count", 1)) + 1
    prev_last_ts = float(entry.get("last_ts", now))
    prev_session = entry.get("last_session_id", "")
    entry["last_ts"] = now
    entry["last_session_id"] = session_id
    sessions = entry.setdefault("sessions", [])
    if session_id not in sessions:
        sessions.append(session_id)
        del sessions[:-10]
    if merge_features:
        _merge_entry_features(entry, features)

    resolved_regression = False
    if entry.get("resolved"):
        entry["resolved_hits"] = int(entry.get("resolved_hits", 0)) + 1
        if entry["resolved_hits"] >= 2:
            # 已解决后仍反复出现 = 回归：撤销 resolved，恢复硬提醒
            entry["resolved"] = False
            entry["resolved_hits"] = 0
            resolved_regression = True

    debounce_ok = now - float(entry.get("last_inject_ts", 0)) >= int(cfg["min_interval_sec"])
    if debounce_ok:
        entry["last_inject_ts"] = now
        count = entry["count"]
        first_ts = float(entry.get("first_ts", now))
        if resolved_regression:
            inject = build_regression_message(count, first_ts)
        elif entry.get("resolved"):
            inject = build_light_message(count, first_ts, "已标记解决")
        elif prev_session == session_id and (now - prev_last_ts) > COMPACT_GAP_SEC:
            inject = build_light_message(count, first_ts, "疑似 compact 后重问")
        else:
            inject = build_message(count, first_ts)

    save_state(state, int(cfg["max_age_days"]))
    return inject


def mark_session_resolved(session_id: str, max_age_days: int = 30) -> int:
    """把本会话触碰过的指纹标记为已解决，返回标记数量。

    由 stop-verification-gate 在验证全部通过时调用。再次命中同指纹时改走轻提示；
    连续命中 ≥2 次自动视为回归并恢复硬提醒（见 record）。
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
            entry["resolved_hits"] = 0
            marked += 1
    if marked:
        save_state(state, max_age_days)
    return marked
