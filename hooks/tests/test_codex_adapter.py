# -*- coding: utf-8 -*-
"""Codex hook 适配器测试：载荷归一化 + 回包翻译（hooks/_codex_hook_runner.py）。

守住两类回归：
1. Codex 词表（exec_command / apply_patch / CallMcpTool）未映射成主干 hook 认识的名字，
   写操作不被记账，Stop 硬门误判「本会话未改代码」直接放行。
2. 主干 hook 用 Claude 词表回包（hookSpecificOutput），Codex 不识别，deny 静默变 allow。
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent
RUNNER = HOOKS / "_codex_hook_runner.py"

_spec = importlib.util.spec_from_file_location("codex_hook_runner", RUNNER)
assert _spec and _spec.loader
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)

PATCH_MULTI = (
    "*** Begin Patch\n"
    "*** Update File: src/app.py\n"
    "@@\n"
    "-pass\n"
    "+return 1\n"
    "*** Add File: src/new.py\n"
    "+x = 1\n"
    "*** End Patch\n"
)

ECHO_HOOK = (
    "import json,os,sys\n"
    "d=json.load(sys.stdin)\n"
    "ti=d.get('tool_input',{})\n"
    "sys.stderr.write('TOOL:%s|P:%d|PLAT:%s|SESS:%s|CMD:%s\\n' % (\n"
    "    d.get('tool_name',''), len(ti.get('paths',[])), d.get('platform',''),\n"
    "    d.get('session_id',''), ti.get('command','')))\n"
    "act=os.environ.get('FIXTURE_ACTION','allow')\n"
    "if act=='deny':\n"
    "    print(json.dumps({'hookSpecificOutput':{'permissionDecision':'deny',"
    "'permissionDecisionReason':'fixture-deny'}}))\n"
    "    sys.exit(2)\n"
    "if act=='context':\n"
    "    print(json.dumps({'hookSpecificOutput':{'additionalContext':'fixture-c'}}))\n"
    "    sys.exit(0)\n"
    "print(json.dumps({'continue':True,'note':'irrelevant'}))\n"
    "sys.exit(0)\n"
)


def _echo_path() -> str:
    fd, path = tempfile.mkstemp(suffix=".py", prefix="codex_echo_")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(ECHO_HOOK)
    return path


def _run(payload: str, action: str = "allow") -> subprocess.CompletedProcess:
    target = _echo_path()
    env = dict(os.environ)
    env["FIXTURE_ACTION"] = action
    try:
        return subprocess.run(
            [sys.executable, str(RUNNER), target],
            input=payload, capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=env,
        )
    finally:
        os.unlink(target)


def test_apply_patch_multi_file_becomes_edit_with_paths() -> None:
    out = runner.normalize({
        "hook_event_name": "preToolUse",
        "tool_name": "apply_patch",
        "tool_input": {"input": PATCH_MULTI},
        "cwd": "C:\\repo",
        "session_id": "s1",
    })
    assert out["tool_name"] == "MultiEdit"
    paths = out["tool_input"]["paths"]
    assert any(p.endswith("app.py") for p in paths), paths
    assert any(p.endswith("new.py") for p in paths), paths
    assert out["tool_input"]["file_path"] == paths[0]
    assert out["platform"] == "codex"
    assert out["session_id"] == "s1"


def test_shell_cmd_key_is_normalized() -> None:
    out = runner.normalize({
        "hook_event_name": "preToolUse",
        "tool_name": "exec_command",
        "tool_input": {"cmd": "pytest -q"},
        "cwd": "C:\\repo",
    })
    assert out["tool_name"] == "Bash"
    assert out["tool_input"]["command"] == "pytest -q"


def test_apply_patch_over_shell_counts_as_edit() -> None:
    out = runner.normalize({
        "tool_name": "exec_command",
        "tool_input": {"cmd": "apply_patch <<'EOF'\n*** Begin Patch\n"
                               "*** Update File: docs/a.md\n*** End Patch\n"},
        "cwd": "C:\\repo",
    })
    assert out["tool_name"] == "MultiEdit"
    assert out["tool_input"]["paths"][0].endswith("a.md")


def test_mcp_wrapper_expands_to_server_tool() -> None:
    out = runner.normalize({
        "tool_name": "CallMcpTool",
        "tool_input": {"server": "codegraph", "tool_name": "codegraph_explore"},
        "cwd": "C:\\repo",
    })
    assert out["tool_name"] == "mcp__codegraph__codegraph_explore"


def test_session_id_falls_back_to_thread_id() -> None:
    out = runner.normalize({"tool_name": "Read", "thread_id": "thr-9"})
    assert out["session_id"] == "thr-9"


def test_alias_table_maps_common_tools() -> None:
    pairs = {"shell": "Bash", "read_file": "Read", "spawn_agent": "Task",
             "WebFetch": "WebFetch", "update_plan": "TodoWrite"}
    for name, want in pairs.items():
        assert runner.normalize({"tool_name": name})["tool_name"] == want, name


def test_unknown_tool_kept_verbatim() -> None:
    assert runner.normalize({"tool_name": "view_image"})["tool_name"] == "view_image"


def test_deny_reply_translated_and_exit2_preserved() -> None:
    proc = _run(json.dumps({"tool_name": "apply_patch",
                            "tool_input": {"input": "*** Update File: a.py\n"}}), "deny")
    assert proc.returncode == 2, proc.stderr
    body = json.loads(proc.stdout.strip())
    assert body["permission"] == "deny"
    assert "fixture-deny" in body["agent_message"]
    assert "hookSpecificOutput" not in body


def test_context_reply_uses_snake_case() -> None:
    proc = _run(json.dumps({"tool_name": "Read"}), "context")
    body = json.loads(proc.stdout.strip())
    assert body["additional_context"] == "fixture-c"


def test_irrelevant_fields_are_dropped() -> None:
    proc = _run(json.dumps({"tool_name": "Read"}), "allow")
    assert proc.stdout.strip() == "", proc.stdout
    assert proc.returncode == 0


def test_child_sees_normalized_vocabulary() -> None:
    proc = _run(json.dumps({
        "hook_event_name": "preToolUse",
        "tool_name": "exec_command",
        "tool_input": {"cmd": "git status"},
        "cwd": "C:\\repo",
        "session_id": "abc",
    }))
    line = proc.stderr.strip().splitlines()[-1]
    assert "TOOL:Bash" in line, line
    assert "PLAT:codex" in line, line
    assert "SESS:abc" in line, line
    assert "CMD:git status" in line, line


def test_garbage_stdin_fails_open() -> None:
    proc = _run("this is not json")
    assert proc.returncode == 0, proc.stderr


def test_missing_target_hook_is_explicit_error() -> None:
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "no-such-hook.py"],
        input="{}", capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 2
    assert "missing target hook" in proc.stderr


def _main() -> int:
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS " + name)
            except Exception as exc:  # noqa: BLE001 - 汇总用
                failed += 1
                print("FAIL %s: %s" % (name, exc))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_main())
