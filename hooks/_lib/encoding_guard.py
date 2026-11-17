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
import hashlib
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from tool_paths import extract_edit_paths  # noqa: E402

# Every pre/post invocation owns a separate file; no shared read-modify-write map.
STATE_DIR = Path(os.environ.get("CLAUDE_HOOK_STATE_DIR", str(Path(__file__).resolve().parents[2] / ".state" / "encoding")))
STALE_SECONDS = 24 * 3600
MAX_ENTRIES = 1000

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


def state_path(path: str, session_id: str = "", tool_use_id: str = "") -> Path:
    identity = "\0".join((session_id, tool_use_id, os.path.normcase(os.path.abspath(path))))
    return STATE_DIR / (hashlib.sha256(identity.encode("utf-8")).hexdigest() + ".json")


def prune_state() -> None:
    """Bound cache retention; abandoned snapshots must not live indefinitely."""
    if not STATE_DIR.exists():
        return
    entries = []
    for entry in STATE_DIR.glob("*.json"):
        try:
            entries.append((entry.stat().st_mtime, entry))
        except FileNotFoundError:
            continue  # another post hook consumed its own snapshot
    # A killed writer may leave a temporary file. Never remove a live writer's file.
    for temporary in STATE_DIR.glob(".snapshot-*"):
        try:
            if time.time() - temporary.stat().st_mtime > STALE_SECONDS:
                temporary.unlink(missing_ok=True)
        except FileNotFoundError:
            continue
        except OSError as exc:
            print(f"encoding_guard: temporary cleanup failed: {type(exc).__name__}", file=sys.stderr)
    entries.sort(reverse=True)
    now = time.time()
    for index, (mtime, entry) in enumerate(entries):
        if now - mtime > STALE_SECONDS or index >= MAX_ENTRIES:
            try:
                entry.unlink(missing_ok=True)
            except OSError as exc:
                print(f"encoding_guard: cache cleanup failed: {type(exc).__name__}", file=sys.stderr)


def write_snapshot(target: Path, signature: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=STATE_DIR, prefix=".snapshot-", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(signature, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def take_snapshot(tool_name: str, tool_input: dict, cwd: str, session_id: str = "", tool_use_id: str = "") -> list[str]:
    """Store this session/invocation's BOM and EOL signature atomically."""
    paths = extract_edit_paths(tool_input, cwd)
    if not paths:
        return []
    prune_state()
    for path in paths:
        target = state_path(path, session_id, tool_use_id)
        signature = snapshot_signature(path)
        if signature is not None:
            write_snapshot(target, signature)
        else:
            target.unlink(missing_ok=True)
    return paths


def consume_snapshot(path: str, session_id: str, tool_use_id: str) -> dict | None:
    target = state_path(path, session_id, tool_use_id)
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) and time.time() - data.get("ts", 0) < STALE_SECONDS else None
    except FileNotFoundError:
        return None
    except (OSError, ValueError, TypeError) as exc:
        print(f"encoding_guard: snapshot read failed: {type(exc).__name__}", file=sys.stderr)
        return None
    finally:
        target.unlink(missing_ok=True)


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


def check_after_edit(tool_name: str, tool_input: dict, cwd: str, session_id: str = "", tool_use_id: str = "") -> dict[str, list[str]]:
    """Run absolute checks and consume only the matching pre-hook snapshot."""
    results: dict[str, list[str]] = {}
    for path in extract_edit_paths(tool_input, cwd):
        before = consume_snapshot(path, session_id, tool_use_id)
        if not os.path.isfile(path):
            continue
        issues, _data = analyze_file(path)
        issues.extend(diff_issues(before, path))
        if issues:
            results[path] = issues
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
