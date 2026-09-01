#!/usr/bin/env python3
"""Cursor hook stdin/stdout 工具。"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_emitted = False
_MAX_STDIN = 16 * 1024 * 1024


def setup_stdio() -> None:
    try:
        if hasattr(sys.stdout, "buffer"):
            import io

            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
    except Exception as e:
        print(f"cursor-guard: stdout setup failed: {e}", file=sys.stderr)


def ensure_lib_path() -> None:
    lib = Path(__file__).resolve().parent
    if str(lib) not in sys.path:
        sys.path.insert(0, str(lib))


def import_claude_lib(claude_home, module_name):
    """载入 Claude 侧共享库（`<claude_home>/hooks/_lib/<module>.py`）。

    指纹算法、写工具路径解析等逻辑双端共用一份实现，避免 Cursor 与 Claude Code
    行为漂移；调用方负责 try/except 并在不可用时降级（R16 不静默）。
    """
    import importlib

    lib = Path(claude_home) / "hooks" / "_lib"
    if str(lib) not in sys.path:
        sys.path.insert(0, str(lib))
    return importlib.import_module(module_name)


def _decode_blob(blob: bytes) -> str:
    if blob.startswith(b"\xff\xfe") or blob.startswith(b"\xfe\xff"):
        return blob.decode("utf-16", errors="replace")
    if blob.startswith(b"\xef\xbb\xbf"):
        return blob[3:].decode("utf-8", errors="replace")
    sample = blob[:64]
    if sample and sample.count(b"\x00") >= max(2, len(sample) // 4):
        try:
            return blob.decode("utf-16-le")
        except UnicodeDecodeError:
            pass
    return blob.decode("utf-8", errors="replace")


def parse_hook_json(blob: bytes | str) -> dict | None:
    """Parse Cursor hook stdin. None = incomplete/invalid; {} = empty or non-object JSON."""
    if isinstance(blob, str):
        blob = blob.encode("utf-8")
    if not blob or not blob.strip():
        return {}
    text = _decode_blob(blob).lstrip("\ufeff")
    stripped = text.lstrip()
    if stripped.lower().startswith("content-length:"):
        body = ""
        for sep in ("\r\n\r\n", "\n\n"):
            if sep in text:
                body = text.split(sep, 1)[1]
                break
        if not body.strip():
            return None
        text = body
    starts = [i for i in (text.find("{"), text.find("[")) if i >= 0]
    if not starts:
        return None
    text = text[min(starts) :]
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        try:
            obj, _end = json.JSONDecoder().raw_decode(text)
        except json.JSONDecodeError:
            return None
    if isinstance(obj, dict):
        return obj
    return {}


def _debug_stdin(blob: bytes, reason: str) -> None:
    if os.environ.get("CURSOR_GUARD_DEBUG", "").strip().lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return
    print(f"cursor-guard: stdin {reason} ({len(blob)} bytes)", file=sys.stderr)
    try:
        state = Path.home() / ".cursor" / ".state"
        state.mkdir(parents=True, exist_ok=True)
        dump = state / "hook-stdin-fail.bin"
        if not dump.exists():
            dump.write_bytes(blob[:4096])
    except OSError as exc:
        print(f"cursor-guard: stdin dump failed: {exc}", file=sys.stderr)


def read_stdin() -> dict:
    """读取 Cursor stdin JSON。

    Cursor 3.18 可能发送：UTF-8 BOM、pretty-print 多行、Content-Length 帧、或无尾换行。
    拼到合法对象即返回；空输入返回 {}。解析失败默认静默（避免 Hooks 面板被 STDERR 刷红），
    `CURSOR_GUARD_DEBUG=1` 时才写 stderr / 落盘前 4KB。
    """
    try:
        if sys.stdin is None or sys.stdin.closed:
            return {}
        if sys.stdin.isatty():
            return {}
        buf = sys.stdin.buffer if hasattr(sys.stdin, "buffer") else None
        if buf is None:
            raw = sys.stdin.read()
            parsed = parse_hook_json(raw if isinstance(raw, bytes) else raw.encode("utf-8"))
            return parsed if parsed is not None else {}
        first = buf.readline()
        if not first.strip():
            rest = buf.read(_MAX_STDIN)
            parsed = parse_hook_json(rest)
            return parsed if parsed is not None else {}
        blob = first
        while True:
            parsed = parse_hook_json(blob)
            if parsed is not None:
                return parsed
            line = buf.readline()
            if not line:
                rest = buf.read(_MAX_STDIN)
                if rest:
                    blob += rest
                    parsed = parse_hook_json(blob)
                    if parsed is not None:
                        return parsed
                break
            blob += line
            if len(blob) > _MAX_STDIN:
                break
        parsed = parse_hook_json(blob)
        if parsed is not None:
            return parsed
        _debug_stdin(blob, "unparsed")
        return {}
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        _debug_stdin(b"", f"parse failed: {exc}")
        return {}


def write_json(obj: dict) -> None:
    global _emitted
    _emitted = True
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def ensure_hook_output() -> None:
    """Cursor 要求 hook stdout 必须为合法 JSON；无动作时输出 {}。"""
    global _emitted
    if not _emitted:
        write_json({})


def extract_file_path(data: dict) -> str:
    for key in ("file_path", "path"):
        val = data.get(key)
        if isinstance(val, str) and val:
            return val
    tool_input = data.get("tool_input") or data.get("input") or {}
    if isinstance(tool_input, dict):
        for key in ("file_path", "path", "target_file"):
            val = tool_input.get(key)
            if isinstance(val, str) and val:
                return val
    return ""


def extract_tool_name(data: dict) -> str:
    for key in ("tool_name", "tool", "name"):
        val = data.get(key)
        if isinstance(val, str) and val:
            if val in {"CallMcpTool", "call_mcp_tool", "CallDynamicTool", "call_dynamic_tool"}:
                break
            return val
    tool_input = data.get("tool_input") or data.get("arguments") or data.get("input") or {}
    if isinstance(tool_input, dict):
        for key in ("toolName", "tool_name", "mcp_tool", "tool", "name"):
            val = tool_input.get(key)
            if isinstance(val, str) and val:
                key_n = val.strip().lower().replace("_", "")
                if key == "name" and key_n not in {
                    "createplan",
                    "switchmode",
                    "write",
                    "strreplace",
                    "edit",
                    "multiedit",
                    "delete",
                    "shell",
                    "task",
                }:
                    continue
                return val
        nested = tool_input.get("arguments")
        if isinstance(nested, dict):
            val = nested.get("toolName") or nested.get("tool_name") or nested.get("name")
            if isinstance(val, str) and val:
                return val
    for key in ("tool_name", "tool", "name"):
        val = data.get(key)
        if isinstance(val, str) and val:
            return val
    return ""


def extract_prompt(data: dict) -> str:
    for key in ("prompt", "text", "message", "content"):
        val = data.get(key)
        if isinstance(val, str):
            return val
    return ""
