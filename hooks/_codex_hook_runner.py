#!/usr/bin/env python3
"""Codex Hook 适配器（v12.1）：把 Codex 的 hook 载荷/回包翻译成主干 hook 契约。

设计约束（`hooks/README.md`：Cursor Guard 经 import_claude_lib 引用，禁止再拷贝分叉）：
主干 22 个 hook 只认 Claude Code 的 `tool_name` 词表与 `hookSpecificOutput` 回包，
Codex 侧词表不同（`exec_command` / `apply_patch` / `permission` / `updated_input`）。
本文件是 **唯一** 的 Codex 适配面：入口归一化 + 出口翻译，使主干 hook 原文复用，
既不产生第二份 hook 实现，也不往各 hook 里塞平台分支。

用法（`~/.codex/hooks.json` 注册，不经 `_editor_hook_launcher.py`）：
    python ~/.claude/hooks/_codex_hook_runner.py <target-hook.py>

调试：`CODEX_HOOK_DEBUG=1` 时把原始载荷追加到 `~/.codex/hooks-probe.jsonl`。
失败策略：载荷不可解析 → 放行（exit 0），与主干 hook 的 fail-open 默认一致。
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent

# Codex/Claude 工具名 → 主干 hook 认识的规范名（Claude 词表）
TOOL_ALIASES = {
    # shell 类
    "exec_command": "Bash", "shell": "Bash", "Shell": "Bash", "bash": "Bash",
    "local_shell": "Bash", "container.exec": "Bash", "run_command": "Bash",
    "Bash": "Bash", "RunCommand": "Bash",
    # 写类（统一成 MultiEdit：一次 apply_patch 可含多文件增删改）
    "apply_patch": "MultiEdit", "Edit": "MultiEdit", "Write": "MultiEdit",
    "MultiEdit": "MultiEdit", "StrReplace": "MultiEdit", "SearchReplace": "MultiEdit",
    "edit_file": "MultiEdit", "WriteToFile": "MultiEdit", "notebookEdit": "MultiEdit",
    "EditNotebook": "MultiEdit", "NotebookEdit": "MultiEdit", "Delete": "MultiEdit",
    "TabWrite": "MultiEdit",
    # 读/搜索类
    "read_file": "Read", "Read": "Read", "TabRead": "Read", "ReadFile": "Read",
    "grep_search": "Grep", "Grep": "Grep", "search": "Grep",
    "Glob": "Glob", "list_dir": "Glob", "LS": "Glob",
    # 子代理 / 计划 / 网络
    "spawn_agent": "Task", "followup_task": "Task", "Task": "Task", "Agent": "Task",
    "subagent": "Task",
    "update_plan": "TodoWrite", "TodoWrite": "TodoWrite",
    "web_search": "WebSearch", "WebSearch": "WebSearch",
    "web_fetch": "WebFetch", "WebFetch": "WebFetch",
    "Skill": "Skill", "SlashCommand": "Skill",
}

EDIT_CANONICAL = "MultiEdit"
COMMAND_KEYS = ("command", "cmd", "shell_command", "script")
PATCH_KEYS = ("input", "patch", "diff", "commands")

# `*** Update File: p` / `*** Add File:` / `*** Delete File:` / `*** Move to:`
PATCH_FILE_RE = re.compile(
    r"^\*\*\*\s*(?:Update File|Add File|Delete File|Move to):\s*(.+?)\s*$", re.MULTILINE
)


def _decode(blob: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return blob.decode(enc)
        except UnicodeDecodeError:
            continue
    return blob.decode("utf-8", errors="replace")


def read_payload() -> dict:
    """读 stdin JSON，容忍 BOM、空输入与 Content-Length 分帧。"""
    try:
        blob = sys.stdin.buffer.read()
    except Exception:  # noqa: BLE001 - stdin 不可用时按空载荷处理
        return {}
    if not blob:
        return {}
    text = _decode(blob).lstrip("\ufeff").strip()
    if not text:
        return {}
    if text.lower().startswith("content-length:"):
        for sep in ("\r\n\r\n", "\n\n"):
            if sep in text:
                text = text.split(sep, 1)[1]
                break
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def first_str(data: dict, keys) -> str:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def unwrap_input(data: dict) -> dict:
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = data.get("toolInput") if isinstance(data.get("toolInput"), dict) else None
    if not isinstance(tool_input, dict):
        nested = data.get("params") if isinstance(data.get("params"), dict) else {}
        tool_input = nested.get("tool_input") if isinstance(nested.get("tool_input"), dict) else {}
    return dict(tool_input or {})


def raw_tool_name(data: dict, tool_input: dict) -> str:
    """MCP 工具在 Codex 侧可能是 CallMcpTool + server/tool 字段，展开成 mcp__server__tool。"""
    name = first_str(data, ("tool_name", "toolName", "tool", "name"))
    if name.lower() in {"callmcptool", "calldynamictool", "call_mcp_tool", "call_dynamic_tool"}:
        inner = first_str(tool_input, ("tool_name", "toolName", "tool", "name"))
        server = first_str(tool_input, ("server", "server_name", "serverName", "mcp_server"))
        if inner and server:
            return f"mcp__{server}__{inner}"
        if inner:
            return inner
    return name


def patch_blob(tool_input: dict) -> str:
    parts = []
    for key in PATCH_KEYS + COMMAND_KEYS:
        value = tool_input.get(key)
        if isinstance(value, str) and "***" in value:
            parts.append(value)
    return "\n".join(parts)


def edit_paths(tool_input: dict, cwd: str) -> list:
    """从 apply_patch 文本与常规路径字段提取被写文件，相对路径按 cwd 归一。"""
    out: list = []

    def push(raw: str) -> None:
        raw = raw.strip().strip('"').strip("'")
        if not raw or raw.startswith(("a/", "b/")) and len(raw) < 3:
            return
        if not os.path.isabs(raw) and cwd:
            raw = os.path.join(cwd, raw)
        norm = os.path.normpath(raw)
        if norm not in out:
            out.append(norm)

    for match in PATCH_FILE_RE.finditer(patch_blob(tool_input)):
        target = match.group(1)
        push(target)
    for key in ("file_path", "filePath", "path", "relative_path", "target_file", "file",
                "notebook_path", "destination"):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            push(value)
    for key in ("paths", "files", "file_paths", "relative_paths"):
        value = tool_input.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.strip():
                    push(item)
    return out


def looks_like_patch(command: str) -> bool:
    head = command.lstrip()[:64].lower()
    return head.startswith("apply_patch") or "*** begin patch" in command.lower()[:400]


def normalize(data: dict) -> dict:
    """Codex 载荷 → 主干 hook 契约载荷。"""
    tool_input = unwrap_input(data)
    raw = raw_tool_name(data, tool_input)
    cwd = first_str(data, ("cwd", "workspaceRoot", "workspace_root")) or os.getcwd()

    canonical = TOOL_ALIASES.get(raw, raw)
    command = first_str(tool_input, COMMAND_KEYS)

    if canonical == "Bash" and looks_like_patch(command):
        canonical = EDIT_CANONICAL

    out_input = dict(tool_input)
    if command:
        out_input["command"] = command
    if canonical == EDIT_CANONICAL:
        paths = edit_paths(tool_input, cwd)
        if paths:
            out_input["paths"] = paths
            out_input.setdefault("file_path", paths[0])
    if raw:
        out_input["_codex_tool"] = raw

    session = first_str(data, ("session_id", "sessionId", "conversation_id", "thread_id",
                              "threadId", "chat_id"))
    event = first_str(data, ("hook_event_name", "hookEventName", "event", "hookEvent"))

    normalized = {
        "session_id": session or os.environ.get("CODEX_THREAD_ID") or "unknown",
        "transcript_path": first_str(data, ("transcript_path", "transcriptPath")),
        "cwd": cwd,
        "hook_event_name": event,
        "tool_name": canonical,
        "tool_input": out_input,
        "platform": "codex",
    }
    if not normalized["transcript_path"]:
        normalized.pop("transcript_path")
    for key in ("permission_mode", "model", "user_prompt", "prompt"):
        if key in data:
            normalized[key] = data[key]
    return normalized


def translate_output(text: str, event: str) -> str | None:
    """主干/Claude 回包 → Codex 词表。未知字段丢弃，避免 Codex 解析告警。

    返回 None = 不是 JSON，原样透传；返回 "" = 翻译后为空，应抑制输出。
    """
    text = (text or "").strip()
    if not text:
        return ""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text
    if not isinstance(payload, dict):
        return text

    spec = payload.get("hookSpecificOutput")
    spec = spec if isinstance(spec, dict) else {}
    out: dict = {}

    decision = str(spec.get("permissionDecision") or payload.get("permission") or "").lower()
    reason = str(spec.get("permissionDecisionReason") or payload.get("reason") or "").strip()
    if decision in {"allow", "deny", "ask"}:
        out["permission"] = decision
    if reason:
        out["agent_message"] = reason
        out["user_message"] = reason

    extra = spec.get("additionalContext") or payload.get("systemMessage") or ""
    if isinstance(extra, str) and extra.strip():
        low = event.lower()
        body = extra.strip()
        if "post" in low:
            out["additional_context"] = body
        elif "pre" in low:
            out["agent_message"] = _merge(out.get("agent_message"), body)
        else:
            out["additional_context"] = body
            out["agent_message"] = _merge(out.get("agent_message"), body)

    updated = spec.get("updatedInput") or payload.get("updated_input")
    if isinstance(updated, dict):
        out["updated_input"] = updated

    follow_up = payload.get("followUpMessage") or payload.get("followup_message")
    if isinstance(follow_up, str) and follow_up.strip():
        out["followup_message"] = follow_up.strip()

    if payload.get("stopReason"):
        out["stop_reason"] = payload["stopReason"]

    if not out:
        return ""
    return json.dumps(out, ensure_ascii=False)


def _merge(existing, body: str) -> str:
    parts = [part for part in (str(existing or "").strip(), body.strip()) if part]
    return "\n\n".join(dict.fromkeys(parts))


EVENT_BY_PREFIX = (
    ("pre-userprompt-", "userPromptSubmit"),
    ("pre-compact-", "preCompact"),
    ("session-start-", "sessionStart"),
    ("stop-", "stop"),
    ("post-", "postToolUse"),
    ("pre-", "preToolUse"),
)


def infer_event(target: str, data: dict) -> str:
    """载荷/环境缺事件名时按主干 hook 文件名前缀推断（文件名本身编码了事件）。"""
    explicit = str(data.get("hook_event_name") or os.environ.get("CLAUDE_HOOK_EVENT") or "")
    if explicit:
        return explicit
    stem = Path(target).name
    for prefix, event in EVENT_BY_PREFIX:
        if stem.startswith(prefix):
            return event
    return ""


def probe_log(raw: dict) -> None:
    if os.environ.get("CODEX_HOOK_DEBUG", "").strip().lower() not in {"1", "true", "yes", "on"}:
        return
    target = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "hooks-probe.jsonl"
    try:
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(raw, ensure_ascii=False) + "\n")
    except OSError as exc:
        sys.stderr.write(f"codex-hook-runner: probe log failed ({target}): {exc}\n")


def main(argv) -> int:
    if len(argv) < 2:
        sys.stderr.write("usage: _codex_hook_runner.py <target-hook.py>\n")
        return 0
    target = argv[1]
    if not os.path.isabs(target):
        target = str(HOOKS_DIR / target)
    if not os.path.isfile(target):
        sys.stderr.write(f"codex-hook-runner: missing target hook {target}\n")
        return 2

    raw = read_payload()
    probe_log(raw)
    normalized = normalize(raw)
    event = infer_event(target, raw)
    normalized["hook_event_name"] = event

    env = dict(os.environ)
    env["CLAUDE_PLATFORM"] = "codex"
    env["PYTHONIOENCODING"] = "utf-8"
    declared_cwd = str(normalized.get("cwd") or "")
    child_cwd = declared_cwd if os.path.isdir(declared_cwd) else None
    try:
        proc = subprocess.run(
            [sys.executable, target],
            input=json.dumps(normalized, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            cwd=child_cwd,
        )
    except OSError as exc:
        sys.stderr.write(f"codex-hook-runner: spawn failed: {exc}\n")
        return 0

    translated = translate_output(proc.stdout or "", event)
    if translated is None:
        sys.stdout.write(proc.stdout or "")
    elif translated:
        sys.stdout.write(translated + "\n")
    sys.stdout.flush()
    if proc.stderr:
        sys.stderr.write(proc.stderr)
        sys.stderr.flush()
    return proc.returncode if proc.returncode in (0, 2) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
