# -*- coding: utf-8 -*-
"""R20 会话终验标记检测（stop-verification-gate.has_requirements_replay）。

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

spec = importlib.util.spec_from_file_location(
    "stop_verification_gate",
    HOOKS_DIR / "stop-verification-gate.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PASSED = []
FAILED = []


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
            {
                "type": "assistant",
                "message": {
                    "content": "## 会话终验（R20）\n- 满足：a\n- 遗漏：无\n- 错改：无\n结论：DONE"
                },
            },
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
                        {"type": "text", "text": "会话终验\n遗漏：无\n错改：无"},
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
            {"type": "assistant", "message": {"content": "会话终验 R20\n遗漏：无\n错改：无"}},
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


def test_last_assistant_wins() -> None:
    path = write_transcript(
        [
            {"type": "assistant", "message": {"content": "会话终验 遗漏：无 错改：无"}},
            {"type": "assistant", "message": {"content": "另外再说一句"}},
        ]
    )
    try:
        check("last assistant wins (no marker)", mod.has_requirements_replay(path) is False)
    finally:
        os.remove(path)


def test_block_message_doc_only() -> None:
    msg = mod.build_block_message(
        ["R20 会话终验：未输出对照原始用户请求的满足/遗漏/错改清单"],
        False,
        1,
        3,
    )
    check("doc-only block omits 代码修改", "代码修改" not in msg)
    check("doc-only block omits 跑测试指令", "实际运行测试" not in msg)
    check("doc-only block asks R20", "会话终验（R20）" in msg)


def main() -> int:
    print("=== R20 replay marker tests ===")
    test_positive_string_content()
    test_positive_list_content()
    test_missing_marker()
    test_missing_cuogai()
    test_empty_path()
    test_last_assistant_wins()
    test_skip_empty_tool_use_assistant()
    test_missing_yilou()
    test_block_message_doc_only()
    print(f"passed={len(PASSED)} failed={len(FAILED)}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
