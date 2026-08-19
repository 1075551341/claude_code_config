# -*- coding: utf-8 -*-
"""R20 会话终验标记检测（r20_replay.replay_ok + stop-verification-gate.has_requirements_replay）。

直接运行：`python hooks/tests/test_r20_replay.py`（退出码 0 = 全过）。
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HOOKS_DIR / "_lib"))

import r20_replay  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "stop_verification_gate",
    HOOKS_DIR / "stop-verification-gate.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PASSED = []
FAILED = []

VALID = (
    "## 会话终验（R20）\n"
    "原始要求：强化门控\n"
    "- 满足：空模板拦截与文档句检查已落地\n"
    "- 遗漏：无\n"
    "- 错改：无\n"
    "- 漏改：无文档影响\n"
    "- 原功能：保持（证据：python hooks/tests/test_r20_replay.py）\n"
    "结论：DONE"
)


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASSED if cond else FAILED).append(name)
    mark = "OK " if cond else "FAIL"
    print(f"  [{mark}] {name}" + (f" -- {detail}" if detail and not cond else ""))


def write_transcript(lines: list) -> str:
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as fh:
        for obj in lines:
            fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
    return path


def test_positive_string_content() -> None:
    path = write_transcript(
        [
            {"type": "user", "message": {"content": "做完了吗"}},
            {"type": "assistant", "message": {"content": VALID}},
        ]
    )
    try:
        check("positive string content", mod.has_requirements_replay(path) is True)
    finally:
        os.remove(path)


def test_positive_list_content() -> None:
    path = write_transcript(
        [
            {
                "type": "assistant",
                "message": {
                    "content": [
                        {"type": "text", "text": VALID},
                        {"type": "tool_use", "name": "x"},
                    ]
                },
            }
        ]
    )
    try:
        check("positive list content", mod.has_requirements_replay(path) is True)
    finally:
        os.remove(path)


def test_empty_template_rejected() -> None:
    empty = (
        "## 会话终验（R20）\n- 满足：a\n- 遗漏：无\n- 错改：无\n- 漏改：无\n- 原功能：保持\n结论：DONE"
    )
    check("empty template replay_ok false", r20_replay.replay_ok(empty) is False)
    path = write_transcript([{"type": "assistant", "message": {"content": empty}}])
    try:
        check("empty template gate false", mod.has_requirements_replay(path) is False)
    finally:
        os.remove(path)


def test_ellipsis_satisfied_rejected() -> None:
    text = (
        "## 会话终验（R20）\n- 满足：...\n- 遗漏：无\n- 错改：无\n"
        "- 漏改：无文档影响\n- 原功能：保持（证据：pytest）"
    )
    check("ellipsis 满足 rejected", r20_replay.replay_ok(text) is False)


def test_keep_only_yuan_rejected() -> None:
    text = (
        "## 会话终验（R20）\n- 满足：做了\n- 遗漏：无\n- 错改：无\n"
        "- 漏改：无文档影响\n- 原功能：保持"
    )
    check("原功能仅保持 rejected", r20_replay.replay_ok(text) is False)


def test_path_in_lougai_ok() -> None:
    text = (
        "## 会话终验（R20）\n- 满足：同步文档\n- 遗漏：无\n- 错改：无\n"
        "- 漏改：已同步 CHANGELOG.md\n- 原功能：保持（证据：冒烟跑通 test_r20_replay）"
    )
    check("漏改路径 accepted", r20_replay.replay_ok(text) is True)


def test_missing_marker() -> None:
    path = write_transcript(
        [{"type": "assistant", "message": {"content": "验证通过，测试全绿"}}]
    )
    try:
        check("missing marker", mod.has_requirements_replay(path) is False)
    finally:
        os.remove(path)


def test_missing_cuogai() -> None:
    path = write_transcript(
        [{"type": "assistant", "message": {"content": "会话终验 R20\n遗漏：无"}}]
    )
    try:
        check("missing 错改", mod.has_requirements_replay(path) is False)
    finally:
        os.remove(path)


def test_empty_path() -> None:
    check("empty path", mod.has_requirements_replay("") is False)
    check("missing file", mod.has_requirements_replay("Z:\\no-such-transcript.jsonl") is False)


def test_skip_empty_tool_use_assistant() -> None:
    path = write_transcript(
        [
            {"type": "assistant", "message": {"content": VALID}},
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "x"}]}},
        ]
    )
    try:
        check("skip empty tool_use assistant", mod.has_requirements_replay(path) is True)
    finally:
        os.remove(path)


def test_missing_yilou() -> None:
    path = write_transcript(
        [{"type": "assistant", "message": {"content": "会话终验 R20\n错改：无"}}]
    )
    try:
        check("missing 遗漏", mod.has_requirements_replay(path) is False)
    finally:
        os.remove(path)


def test_old_three_fields_fail() -> None:
    path = write_transcript(
        [
            {
                "type": "assistant",
                "message": {"content": "会话终验 R20\n遗漏：无\n错改：无"},
            }
        ]
    )
    try:
        check("old three fields fail", mod.has_requirements_replay(path) is False)
    finally:
        os.remove(path)


def test_missing_lougai() -> None:
    path = write_transcript(
        [
            {
                "type": "assistant",
                "message": {"content": "会话终验 R20\n遗漏：无\n错改：无\n原功能：保持（证据：x）"},
            }
        ]
    )
    try:
        check("missing 漏改", mod.has_requirements_replay(path) is False)
    finally:
        os.remove(path)


def test_missing_yuangongneng() -> None:
    path = write_transcript(
        [
            {
                "type": "assistant",
                "message": {"content": "会话终验 R20\n遗漏：无\n错改：无\n漏改：无文档影响"},
            }
        ]
    )
    try:
        check("missing 原功能", mod.has_requirements_replay(path) is False)
    finally:
        os.remove(path)


def test_last_assistant_wins() -> None:
    path = write_transcript(
        [
            {"type": "assistant", "message": {"content": VALID}},
            {"type": "assistant", "message": {"content": "另外再说一句"}},
        ]
    )
    try:
        check("last assistant wins (no marker)", mod.has_requirements_replay(path) is False)
    finally:
        os.remove(path)


def test_block_message_doc_only() -> None:
    msg = mod.build_block_message(
        ["R20 会话终验：未按原始要求逐条回放输出满足/遗漏/错改/漏改/原功能"],
        False,
        1,
        3,
    )
    check("doc-only block omits 代码修改", "代码修改" not in msg)
    check("doc-only block omits 跑测试指令", "实际运行测试" not in msg)
    check("doc-only block asks R20", "会话终验（R20）" in msg)
    check("doc-only block asks 漏改", "漏改" in msg)
    check("doc-only block asks 原功能", "原功能" in msg)


def test_cursor_should_followup() -> None:
    check("no edits no followup", r20_replay.cursor_should_followup({}) is False)
    check(
        "edits without r20 followup",
        r20_replay.cursor_should_followup({"edited_files": [{"path": "a.py", "ts": 2}]}) is True,
    )
    check(
        "r20 ok still unverified followup",
        r20_replay.cursor_should_followup(
            {
                "edited_files": [{"path": "a.py", "ts": 2}],
                "r20_replay_ok": True,
                "verify_commands": [],
            }
        )
        is True,
    )
    check(
        "r20 + verify no followup",
        r20_replay.cursor_should_followup(
            {
                "edited_files": [{"path": "a.py", "ts": 2}],
                "r20_replay_ok": True,
                "verify_commands": [{"command": "pytest", "ts": 3}],
            }
        )
        is False,
    )


def test_gate_reader_sections() -> None:
    from gate_reader import load_gate

    first = load_gate("first_edit")
    verify = load_gate("verify")
    p0 = load_gate("p0")
    impact = load_gate("impact")
    check("first_edit section", "需求" in first and "漏改" in first)
    check("first_edit covers blast-radius", "全部相关" in first)
    check("verify mentions followup or R20", "R20" in verify)
    check("p0 points at task-triage", "task-triage" in p0)
    check("impact not include first_edit heading", "初次修改验收门" not in impact)
    check("verify not include impact heading", "变更影响门" not in verify)
    import first_edit_verify as fev

    entry: dict = {}
    first = fev.fresh_edit_paths(entry, ["a.py", "b.py"])
    second = fev.fresh_edit_paths(entry, ["a.py", "c.py"])
    third = fev.fresh_edit_paths(entry, ["a.py", "b.py"])
    check("first edit two files", first == ["a.py", "b.py"])
    check("second edit only new file", second == ["c.py"])
    check("third edit none", third == [])


def test_claude_tracker_first_edit_injects() -> None:
    """Claude PostToolUse 追踪器须注入初次门（防 CLAUDE_HOME NameError）。"""
    import subprocess

    with tempfile.TemporaryDirectory() as tmp:
        env = os.environ.copy()
        env["CLAUDE_HOME"] = tmp
        payload = json.dumps(
            {
                "session_id": "fe-tracker-test",
                "tool_name": "Edit",
                "tool_input": {"file_path": str(Path(tmp) / "a.py")},
                "cwd": tmp,
            }
        )
        cmd = [sys.executable, str(HOOKS_DIR / "post-edit-verify-tracker.py")]
        first = subprocess.run(
            cmd,
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        check("tracker first edit exit 0", first.returncode == 0)
        out = first.stdout or ""
        check(
            "tracker first edit injects",
            "additionalContext" in out and ("首次编辑后" in out or "需求" in out),
        )
        second = subprocess.run(
            cmd,
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        check("tracker second edit exit 0", second.returncode == 0)
        check("tracker second edit silent", (second.stdout or "").strip() == "")


def main() -> int:
    print("=== R20 replay marker tests ===")
    test_positive_string_content()
    test_positive_list_content()
    test_empty_template_rejected()
    test_ellipsis_satisfied_rejected()
    test_keep_only_yuan_rejected()
    test_path_in_lougai_ok()
    test_missing_marker()
    test_missing_cuogai()
    test_empty_path()
    test_last_assistant_wins()
    test_skip_empty_tool_use_assistant()
    test_missing_yilou()
    test_old_three_fields_fail()
    test_missing_lougai()
    test_missing_yuangongneng()
    test_block_message_doc_only()
    test_cursor_should_followup()
    test_gate_reader_sections()
    test_claude_tracker_first_edit_injects()
    print(f"passed={len(PASSED)} failed={len(FAILED)}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
