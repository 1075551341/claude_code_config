#!/usr/bin/env python3
"""编码守卫核心库（v11.4.2）。

Pre/Post 双阶段防乱码：
- Pre 侧（pre-encoding-snapshot.py）：编辑前快照文件签名（BOM/EOL/大小）
- Post 侧（post-encoding-check.py）：编辑后比对差异 + 绝对检查，警告注入

检测项：
- 严格 UTF-8 合法性（非法字节序列 = 损坏）
- U+FFFD 替换符 / GBK 双重编码特征串（锟斤拷等）
- BOM 增删（json/py 带 BOM 视为异常；正文出现游离 BOM 字符视为损坏）
- EOL 风格翻转 / 严重 mixed EOL

永不阻断：所有问题仅经 additionalContext 警告注入（exit 0），
提示 AI 回滚本次修改而非在其上继续叠加。
"""
from __future__ import annotations

import io
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from tool_paths import extract_edit_paths  # noqa: E402
from issue_state import claude_home  # noqa: E402

STATE_DIR = os.path.join(str(claude_home()), ".state")
STATE_FILE = os.path.join(STATE_DIR, "encoding-snapshots.json")
STALE_SECONDS = 24 * 3600
MAX_ENTRIES = 500

# GBK 双重编码 / 损坏特征串
MOJIBAKE_SIGNATURES = ("锟斤拷", "烫烫烫", "屯屯屯")

# 带 BOM 会破坏解析器或违反惯例的扩展名
BOM_FORBIDDEN_EXTS = {".json", ".jsonc", ".py"}

# mixed EOL 判定为「严重」的双方最小出现次数（避免偶发噪音）
MIXED_EOL_MIN = 10


def _wrap_stdout() -> None:
    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
    except Exception as e:  # noqa: BLE001 - 守卫永不因自身异常阻断主流程
        print(f"encoding_guard: stdout wrap failed: {e}", file=sys.stderr)


def detect_eol(data: bytes) -> str:
    crlf = data.count(b"\r\n")
    lf_total = data.count(b"\n")
    lone_lf = lf_total - crlf
    if crlf and lone_lf:
        return "mixed"
    if crlf:
        return "crlf"
    if lone_lf:
        return "lf"
    return "none"


def snapshot_signature(path: str) -> dict | None:
    """读取文件当前签名；文件不存在或不可读返回 None。"""
    try:
        if not os.path.isfile(path):
            return None
        with open(path, "rb") as f:
            data = f.read(8 * 1024 * 1024)
        return {
            "bom": data.startswith(b"\xef\xbb\xbf"),
            "eol": detect_eol(data),
            "size": len(data),
            "ts": time.time(),
        }
    except OSError as e:
        print(f"encoding_guard: snapshot {path} failed: {e}", file=sys.stderr)
        return None


def load_state() -> dict:
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"encoding_guard: state read failed: {e}", file=sys.stderr)
    return {}


def save_state(state: dict) -> None:
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        now = time.time()
        state = {k: v for k, v in state.items() if now - v.get("ts", 0) < STALE_SECONDS}
        if len(state) > MAX_ENTRIES:
            ordered = sorted(state.items(), key=lambda kv: kv[1].get("ts", 0))
            state = dict(ordered[-MAX_ENTRIES:])
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)
    except OSError as e:
        print(f"encoding_guard: state write failed: {e}", file=sys.stderr)


def take_snapshot(tool_name: str, tool_input: dict, cwd: str) -> list[str]:
    """Pre 阶段：记录本次写操作目标文件的签名，返回目标路径列表。"""
    paths = extract_edit_paths(tool_input, cwd)
    if not paths:
        return []
    state = load_state()
    for p in paths:
        sig = snapshot_signature(p)
        if sig is not None:
            state[p] = sig
        else:
            state.pop(p, None)  # 新建文件：清掉可能的陈旧快照
    save_state(state)
    return paths


def analyze_file(path: str) -> tuple[list[str], bytes]:
    """绝对检查：不依赖快照、对任何时点文件均成立的损坏特征。"""
    issues: list[str] = []
    try:
        with open(path, "rb") as f:
            data = f.read(8 * 1024 * 1024)
    except OSError as e:
        print(f"encoding_guard: read {path} failed: {e}", file=sys.stderr)
        return issues, b""

    try:
        text = data.decode("utf-8", "strict")
    except UnicodeDecodeError:
        issues.append("文件包含非法 UTF-8 字节序列（编码已损坏）")
        text = data.decode("utf-8", "replace")

    if text.count("\ufffd") > 0:
        issues.append(f"检出 {text.count(chr(0xfffd))} 处 U+FFFD 替换符（内容已损坏）")

    for sig in MOJIBAKE_SIGNATURES:
        if sig in text:
            issues.append(f"检出 GBK 双重编码特征串「{sig}」（历史乱码残留）")
            break

    body_bom_count = text.count("\ufeff")
    has_bom = data.startswith(b"\xef\xbb\xbf")
    stray = body_bom_count - (1 if has_bom else 0)
    if stray > 0:
        issues.append(f"正文中出现 {stray} 处游离 BOM 字符（U+FEFF）")

    ext = os.path.splitext(path)[1].lower()
    if has_bom and ext in BOM_FORBIDDEN_EXTS:
        issues.append(f"{ext} 文件不应携带 BOM（会破坏解析器）")

    crlf = data.count(b"\r\n")
    lone_lf = data.count(b"\n") - crlf
    if crlf >= MIXED_EOL_MIN and lone_lf >= MIXED_EOL_MIN:
        issues.append(f"严重 mixed EOL：CRLF={crlf} 与裸 LF={lone_lf} 混杂")

    return issues, data


def diff_issues(before: dict | None, path: str) -> list[str]:
    """比对编辑前后签名的差异类问题。"""
    if before is None:
        return []
    after = snapshot_signature(path)
    if after is None:
        return []
    issues: list[str] = []
    if after["bom"] != before["bom"]:
        change = "新增" if after["bom"] else "丢失"
        issues.append(f"BOM {change}（编辑前 {'有' if before['bom'] else '无'} BOM）")
    if before["eol"] in ("crlf", "lf", "mixed") and after["eol"] in ("crlf", "lf", "mixed"):
        label = {"crlf": "CRLF", "lf": "LF", "mixed": "mixed"}
        if after["eol"] != before["eol"]:
            issues.append(
                f"EOL 风格被改写：{label[before['eol']]} → {label[after['eol']]}"
            )
    return issues


def check_after_edit(tool_name: str, tool_input: dict, cwd: str) -> dict[str, list[str]]:
    """Post 阶段：对每个写入目标做绝对检查 + 快照比对。

    返回 {路径: [问题描述]}；只包含存在问题的文件。检查过的快照随即清除。
    """
    results: dict[str, list[str]] = {}
    state = load_state()
    dirty = False
    for p in extract_edit_paths(tool_input, cwd):
        if not os.path.isfile(p):
            continue
        before = state.pop(p, None)
        dirty = dirty or before is not None
        issues, _data = analyze_file(p)
        issues.extend(diff_issues(before, p))
        if issues:
            results[p] = issues
    if dirty:
        save_state(state)
    return results


def format_warning(results: dict[str, list[str]]) -> str:
    lines = ["[编码守卫] 本次编辑后检出编码/EOL 异常，请立即回滚或精准修复本次改动（禁止在损坏内容上继续叠加修改）："]
    for path, issues in results.items():
        name = os.path.basename(path)
        for issue in issues:
            lines.append(f"- {name}: {issue}")
    lines.append("- 稳定做法：用 Read 确认损坏范围后以 Edit 工具恢复原片段；新文件直接 Write 覆盖为正确内容")
    return "\n".join(lines)


def emit_warning(message: str, event: str) -> None:
    result = {
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": message,
        }
    }
    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    sys.stdout.flush()
