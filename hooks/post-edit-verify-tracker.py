#!/usr/bin/env python3
"""
PostToolUse Hook: 完成验证追踪器 + 初次修改验收（v11.3.4；v11.4 IMPACT 自动登记）
按 session_id 记录本会话编辑文件/验证命令/审查委派，供 stop-verification-gate 硬门核查。
每个文件首次成功编辑后附加五维迷你验收 additionalContext（first_edit_nudged）。
v11.4：追踪到的编辑路径自动追加 IMPACT 行至项目 .claude/state/impact-manifest.log
—— 方案A清单差集不再依赖模型自觉落盘；写失败时才降级弹 IMPACT_REMINDER 兜底。
"""
import json
import sys
import io
import os
import re
import subprocess
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

from tool_paths import extract_edit_paths, is_edit_tool  # noqa: E402
from issue_state import claude_home  # noqa: E402  仅取 CLAUDE_HOME 解析，便于测试隔离
from first_edit_verify import compose_message, fresh_edit_paths, load_first_edit_message  # noqa: E402
from crg_track import record_crg_call  # noqa: E402
from r20_replay import (  # noqa: E402
    is_plan_artifact,
    is_resumed_subagent,
    record_plan_tool,
    write_review_record,
)

CLAUDE_HOME = str(claude_home())
STATE_DIR = os.path.join(CLAUDE_HOME, ".state")
STATE_FILE = os.path.join(STATE_DIR, "verification-gate.json")
CONFIG_FILE = os.path.join(CLAUDE_HOME, "config", "quality_gates.json")
STALE_SECONDS = 7 * 24 * 3600

DEFAULT_VERIFY_PATTERNS = [
    "pytest", "vitest", "jest", "npm test", "pnpm test", "yarn test",
    "npm run test", "npm run lint", "npm run build", "pnpm lint", "pnpm build",
    "tsc", "mypy", "ruff", "eslint", "clippy", "cargo test", "cargo check",
    "go test", "go vet",
]
DEFAULT_REVIEWER_AGENTS = ["eng-reviewer", "qa"]

IMPACT_GATE_KEY = "impact_manifest_gate"
IMPACT_REMINDER = (
    "⚠️ IMPACT 清单自动登记失败（v11.4 起由追踪器自动写入；本条为兜底）：请将影响面清单"
    "手动追加至 .claude/state/impact-manifest.log，格式 IMPACT|<session>|<路径1,路径2,...>|<时间戳>。"
    "Stop 门将校验「diff ⊆ 清单」，清单外变更会被拦截（错改/漏改硬证据）。"
)
RESUMED_REVIEW_REMINDER = (
    "⚠️ 本审查委派带 resume，不计入独立审查。"
    "每轮须全新 Task/Agent（禁止 resume 上一轮审查者），对照原始要求全量重扫；"
    "上轮清单仅作参考，不得限定范围。"
)


def detect_platform() -> str:
    if os.environ.get("CLAUDECODE"):
        return "claude-code"
    declared = (os.environ.get("CLAUDE_PLATFORM") or "").strip().lower()
    if declared:
        return declared
    for key in os.environ:
        if key.upper().startswith("CURSOR"):
            return "cursor"
    return "unknown"


def load_impact_gate() -> dict:
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("quality_gates", {}).get(IMPACT_GATE_KEY, {})
    except (OSError, json.JSONDecodeError) as e:
        print(f"post-edit-verify-tracker: gate config read failed: {e}", file=sys.stderr)
    return {}


def manifest_log_path(cwd: str) -> str:
    return os.path.join(cwd or os.getcwd(), ".claude", "state", "impact-manifest.log")


def git_dirty_set(cwd: str):
    """git status --porcelain 文件集；非 git 仓库返回 None（静默降级）。"""
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"], cwd=cwd or None,
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as e:
        print(f"post-edit-verify-tracker: git status failed: {e}", file=sys.stderr)
        return None
    if proc.returncode != 0:
        return None
    files = set()
    for line in proc.stdout.splitlines():
        if len(line) > 3:
            files.add(line[3:].strip().strip('"').replace("\\", "/"))
    return files


def append_impact_record(session_id: str, cwd: str, paths: list) -> bool:
    """v11.4：把本次追踪到的编辑路径自动登记进项目 IMPACT 清单。

    路径相对 cwd 归一化为正斜杠（与 r20_replay._norm_path 一致）；跨盘等 relpath
    失败时回退原路径。同一 session 多行合法——declared_impact 对各行取并集。
    """
    if not paths:
        return False
    path = manifest_log_path(cwd)
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        rel = []
        for p in paths[:50]:
            try:
                rel.append(os.path.relpath(p, cwd or ".").replace("\\", "/"))
            except ValueError:
                rel.append(str(p).replace("\\", "/"))
        line = f"IMPACT|{session_id}|{','.join(rel)}|{int(time.time())}\n"
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
        return True
    except OSError as e:
        print(f"post-edit-verify-tracker: impact autolog failed: {e}", file=sys.stderr)
        return False


def missing_impact_record(session_id: str, cwd: str) -> bool:
    """本 session 在项目清单中无 IMPACT 记录 → True。"""
    path = manifest_log_path(cwd)
    if not os.path.exists(path):
        return True
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split("|")
                if len(parts) >= 3 and parts[0].strip() == "IMPACT" and parts[1].strip() == session_id:
                    return False
    except OSError as e:
        print(f"post-edit-verify-tracker: manifest read failed: {e}", file=sys.stderr)
    return True


def load_config() -> dict:
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f).get("verification_gate", {})
            return {
                "verify_command_patterns": cfg.get("verify_command_patterns", DEFAULT_VERIFY_PATTERNS),
                "reviewer_agents": cfg.get("reviewer_agents", DEFAULT_REVIEWER_AGENTS),
            }
    except (OSError, json.JSONDecodeError) as e:
        print(f"post-edit-verify-tracker: config read failed: {e}", file=sys.stderr)
    return {
        "verify_command_patterns": DEFAULT_VERIFY_PATTERNS,
        "reviewer_agents": DEFAULT_REVIEWER_AGENTS,
    }


def load_state() -> dict:
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"post-edit-verify-tracker: state read failed: {e}", file=sys.stderr)
    return {}


def save_state(state: dict) -> None:
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        now = time.time()
        state = {k: v for k, v in state.items() if now - v.get("ts", 0) < STALE_SECONDS}
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)
    except OSError as e:
        print(f"post-edit-verify-tracker: state write failed: {e}", file=sys.stderr)


def is_verify_command(command: str, patterns: list) -> bool:
    cmd = command.lower()
    for pat in patterns:
        if re.search(r"(?<![\w-])" + re.escape(pat.lower()) + r"(?![\w-])", cmd):
            return True
    return False


def main():
    try:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"post-edit-verify-tracker: stdout wrap failed: {e}", file=sys.stderr)

    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        print(f"post-edit-verify-tracker: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    session_id = str(data.get("session_id") or data.get("conversation_id") or "unknown")
    tool_name = str(data.get("tool_name") or "")
    tool_input = data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}
    cwd = str(data.get("cwd") or "")

    cfg = load_config()
    now = time.time()
    state = load_state()
    entry = state.setdefault(session_id, {
        "ts": now, "started_ts": now, "cwd": cwd,
        "edited_files": [], "verify_commands": [], "reviews": [], "blocks": 0,
    })
    entry["ts"] = now
    entry.setdefault("started_ts", now)
    if cwd:
        entry["cwd"] = cwd

    changed = False
    first_edit_msg = None
    record_plan_tool(entry, tool_name, tool_input)
    changed = True
    if is_edit_tool(tool_name):
        paths = extract_edit_paths(tool_input, cwd)
        plan_only = bool(paths) and all(is_plan_artifact(p) for p in paths)
        for path in paths:
            entry["edited_files"].append({"path": path, "ts": now})
            changed = True
        fresh = [] if plan_only else fresh_edit_paths(entry, paths)
        if fresh:
            first_edit_msg = compose_message(load_first_edit_message(CLAUDE_HOME), fresh)
            changed = True

        gate = load_impact_gate()
        platforms = [str(x) for x in (gate.get("platforms") or ["claude-code", "cursor"])]
        if gate.get("enabled") and str(data.get("platform") or detect_platform()) in platforms:
            dirty = git_dirty_set(cwd)
            if dirty is not None:
                entry.setdefault("git_baseline", sorted(dirty))
                changed = True
                logged = append_impact_record(session_id, cwd, paths)
                if not logged or missing_impact_record(session_id, cwd):
                    first_edit_msg = (
                        f"{first_edit_msg}\n\n{IMPACT_REMINDER}" if first_edit_msg else IMPACT_REMINDER
                    )
    elif tool_name == "Bash":
        command = str(tool_input.get("command") or "")
        if command and is_verify_command(command, cfg["verify_command_patterns"]):
            entry["verify_commands"].append({"command": command[:300], "ts": now})
            changed = True
    elif tool_name in ("Task", "Agent"):
        agent = str(tool_input.get("subagent_type") or tool_input.get("description") or "").lower()
        for reviewer in cfg["reviewer_agents"]:
            if reviewer.lower() in agent:
                if is_resumed_subagent(tool_input):
                    entry.setdefault("skipped_resumed_reviews", []).append(
                        {"agent": reviewer, "ts": now}
                    )
                    changed = True
                    first_edit_msg = (
                        f"{first_edit_msg}\n\n{RESUMED_REVIEW_REMINDER}"
                        if first_edit_msg
                        else RESUMED_REVIEW_REMINDER
                    )
                    break
                last_rev = 0.0
                for item in entry.get("reviews") or []:
                    last_rev = max(last_rev, float(item.get("ts", 0) or 0))
                last_edit = 0.0
                for item in entry.get("edited_files") or []:
                    last_edit = max(last_edit, float(item.get("ts", 0) or 0))
                if last_edit > last_rev:
                    entry["review_rounds"] = int(entry.get("review_rounds") or 0) + 1
                entry["reviews"].append({"agent": reviewer, "ts": now, "resume": False})
                entry["review_pass_ok"] = False
                changed = True
                write_review_record(session_id, entry)
                break

    if record_crg_call(entry, tool_name, now, tool_input):
        changed = True

    if changed:
        save_state(state)
    if first_edit_msg:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": first_edit_msg,
            }
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    sys.exit(0)


if __name__ == "__main__":
    main()
