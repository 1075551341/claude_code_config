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
    "- 影响范围：已审查 CRG get_impact_radius 与 IMPACT 清单，与本次编辑一致\n"
    "- 问题是否解决：已解决（证据：python hooks/tests/test_r20_replay.py）\n"
    "结论：DONE"
)
SOLVED_LINE = "- 问题是否解决：已解决（证据：python hooks/tests/test_r20_replay.py）\n"
REVIEW_PASS = (
    "Independent review PASS\n"
    "- 满足：需求已落地（承认）\n"
    "- 遗漏：无\n"
    "- 错改：无\n"
    "- 漏改：无文档影响\n"
    "- 原功能：保持（证据：pytest）\n"
    "- 影响范围：CRG get_impact_radius\n"
    "- 问题是否解决：已解决（证据：pytest）\n"
)
IMPACT_LINE = "- 影响范围：已审查 CRG get_impact_radius 与 IMPACT 清单\n"


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
        "- 漏改：已同步 CHANGELOG.md\n- 原功能：保持（证据：冒烟跑通 test_r20_replay）\n"
        + IMPACT_LINE
        + SOLVED_LINE
    )
    check("漏改路径 accepted", r20_replay.replay_ok(text) is True)


def test_missing_impact_rejected() -> None:
    text = (
        "## 会话终验（R20）\n- 满足：同步文档\n- 遗漏：无\n- 错改：无\n"
        "- 漏改：无文档影响\n- 原功能：保持（证据：pytest）\n"
        "结论：DONE"
    )
    check("missing 影响范围 rejected", r20_replay.replay_ok(text) is False)
    empty_impact = (
        "## 会话终验（R20）\n- 满足：同步文档\n- 遗漏：无\n- 错改：无\n"
        "- 漏改：无文档影响\n- 原功能：保持（证据：pytest）\n"
        "- 影响范围：无\n" + SOLVED_LINE + "结论：DONE"
    )
    check("empty 影响范围 rejected", r20_replay.replay_ok(empty_impact) is False)
    missing_solved = (
        "## 会话终验（R20）\n- 满足：同步文档\n- 遗漏：无\n- 错改：无\n"
        "- 漏改：无文档影响\n- 原功能：保持（证据：pytest）\n"
        + IMPACT_LINE
        + "结论：DONE"
    )
    check("missing 问题是否解决 rejected", r20_replay.replay_ok(missing_solved) is False)


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
    check(
        "createplan skips followup despite edits",
        r20_replay.cursor_should_followup(
            {
                "edited_files": [{"path": "a.py", "ts": 2}],
                "last_tool": "CreatePlan",
            }
        )
        is False,
    )
    check(
        "awaiting_plan_approval skips followup",
        r20_replay.cursor_should_followup(
            {
                "edited_files": [{"path": "a.py", "ts": 2}],
                "awaiting_plan_approval": True,
            }
        )
        is False,
    )
    check(
        "plan mode payload skips followup",
        r20_replay.cursor_should_followup(
            {"edited_files": [{"path": "a.py", "ts": 2}]},
            {"composer_mode": "plan"},
        )
        is False,
    )
    check("gate echo detected", r20_replay.is_gate_echo("【门控 · 完成前必做】\nR20") is True)
    check("gate echo miss", r20_replay.is_gate_echo("完成后执行同步") is False)
    check(
        "review needed after verify",
        r20_replay.review_followup_needed(
            {
                "non_simple": True,
                "edited_files": [{"path": "a.py", "ts": 1}],
                "verify_commands": [{"command": "pytest", "ts": 2}],
                "last_pre_review_graph_ts": 3,
            },
            {"review_max_rounds": 5, "require_reviewer_min_files": 3},
        )
        is True,
    )
    check(
        "unverified first cycle is verify not review",
        r20_replay.dual_pass_phase(
            {
                "non_simple": True,
                "edited_files": [{"path": "a.py", "ts": 1}],
            }
        )
        == "verify",
    )
    check(
        "needs-changes without new edit is modify",
        r20_replay.dual_pass_phase(
            {
                "non_simple": True,
                "edited_files": [{"path": "a.py", "ts": 1}],
                "verify_commands": [{"command": "pytest", "ts": 2}],
                "reviews": [{"agent": "eng-reviewer", "ts": 3}],
                "review_rounds": 1,
            }
        )
        == "modify",
    )
    check(
        "needs-changes then edit without verify is verify",
        r20_replay.dual_pass_phase(
            {
                "non_simple": True,
                "edited_files": [
                    {"path": "a.py", "ts": 1},
                    {"path": "b.py", "ts": 4},
                ],
                "verify_commands": [{"command": "pytest", "ts": 2}],
                "reviews": [{"agent": "eng-reviewer", "ts": 3}],
                "review_rounds": 1,
            }
        )
        == "verify",
    )
    check(
        "needs-changes then edit+verify is review",
        r20_replay.dual_pass_phase(
            {
                "non_simple": True,
                "edited_files": [
                    {"path": "a.py", "ts": 1},
                    {"path": "b.py", "ts": 4},
                ],
                "verify_commands": [{"command": "pytest", "ts": 5}],
                "reviews": [{"agent": "eng-reviewer", "ts": 3}],
                "review_rounds": 1,
                "last_pre_review_graph_ts": 6,
            }
        )
        == "review",
    )
    check(
        "verified but stale graph is graph phase",
        r20_replay.dual_pass_phase(
            {
                "edited_files": [{"path": "a.py", "ts": 4}],
                "verify_commands": [{"command": "pytest", "ts": 5}],
            }
        )
        == "graph",
    )
    check(
        "session last_graph_refresh_ts does not unlock review",
        r20_replay.dual_pass_phase(
            {
                "edited_files": [{"path": "a.py", "ts": 4}],
                "verify_commands": [{"command": "pytest", "ts": 5}],
                "last_graph_refresh_ts": 6,
            }
        )
        == "graph",
    )
    check(
        "modify phase does not ask review-only",
        r20_replay.review_followup_needed(
            {
                "non_simple": True,
                "edited_files": [{"path": "a.py", "ts": 1}],
                "reviews": [{"agent": "eng-reviewer", "ts": 3}],
                "review_rounds": 1,
            }
        )
        is False,
    )
    check(
        "review capped",
        r20_replay.review_followup_needed(
            {
                "non_simple": True,
                "edited_files": [{"path": "a.py", "ts": 1}],
                "review_rounds": 5,
            },
            {"review_max_rounds": 5},
        )
        is False,
    )
    check(
        "phase capped",
        r20_replay.dual_pass_phase(
            {
                "non_simple": True,
                "edited_files": [{"path": "a.py", "ts": 1}],
                "review_rounds": 5,
            },
            {"review_max_rounds": 5},
        )
        == "capped",
    )
    check(
        "pass meets expected → done no second round",
        r20_replay.dual_pass_phase(
            {
                "edited_files": [{"path": "a.py", "ts": 1}],
                "verify_commands": [{"command": "pytest", "ts": 2}],
                "reviews": [{"agent": "eng-reviewer", "ts": 3}],
                "review_rounds": 1,
                "review_pass_ok": True,
            }
        )
        == "done",
    )
    check(
        "plan.md is artifact",
        r20_replay.is_plan_artifact(r"C:\Users\x\.cursor\plans\foo.plan.md") is True,
    )
    check(
        "src not plan artifact",
        r20_replay.is_plan_artifact("src/a.py") is False,
    )
    dyn = {}
    r20_replay.record_plan_tool(dyn, "CallDynamicTool", {"toolName": "CreatePlan"})
    check("CallDynamicTool CreatePlan awaiting", dyn.get("awaiting_plan_approval") is True)
    r20_replay.record_plan_tool(
        dyn, "Write", {"path": r"C:\Users\x\.cursor\plans\foo.plan.md"}
    )
    check("write plan.md keeps awaiting", dyn.get("awaiting_plan_approval") is True)
    check(
        "only plan.md no followup",
        r20_replay.cursor_should_followup(
            {
                "edited_files": [
                    {"path": r"C:\Users\x\.cursor\plans\foo.plan.md", "ts": 1}
                ],
                "r20_replay_ok": False,
            }
        )
        is False,
    )
    r20_replay.record_plan_tool(dyn, "Write", {})
    check("unknown write keeps awaiting", dyn.get("awaiting_plan_approval") is True)
    r20_replay.record_plan_tool(
        dyn,
        "CallDynamicTool",
        {"toolName": "SwitchMode", "arguments": {"target_mode_id": "agent"}},
    )
    check("switch agent clears awaiting", dyn.get("awaiting_plan_approval") is False)
    check(
        "default min_files=1 dual pass",
        r20_replay.dual_pass_in_scope({"edited_files": [{"path": "a.py", "ts": 1}]})
        is True,
    )
    check(
        "one py file dual pass min_files=1",
        r20_replay.dual_pass_in_scope(
            {"edited_files": [{"path": "a.py", "ts": 1}]},
            {"require_reviewer_min_files": 1},
        )
        is True,
    )
    check(
        "md only is dual pass",
        r20_replay.dual_pass_in_scope(
            {"edited_files": [{"path": "README.md", "ts": 1}]},
            {"require_reviewer_min_files": 1},
        )
        is True,
    )
    check(
        "is_plan_mode payload skips",
        r20_replay.cursor_should_followup(
            {"edited_files": [{"path": "a.py", "ts": 2}]},
            {"is_plan_mode": True},
        )
        is False,
    )
    empty = {}
    check(
        "PASS without reviews ignored",
        r20_replay.apply_review_verdict(empty, REVIEW_PASS) is False
        and empty.get("review_pass_ok") is not True,
    )
    with_rev = {"reviews": [{"agent": "eng-reviewer", "ts": 1}]}
    applied_empty = r20_replay.apply_review_verdict(with_rev, REVIEW_PASS)
    check(
        "apply_review_verdict does not fill empty review text",
        not str((with_rev.get("reviews") or [{}])[0].get("text") or "").strip(),
    )
    check(
        "empty review text cannot PASS",
        applied_empty is True and with_rev.get("review_pass_ok") is not True,
    )
    filled = {"reviews": [{"agent": "eng-reviewer", "ts": 1, "text": REVIEW_PASS}]}
    check(
        "PASS with review text sets ok",
        r20_replay.apply_review_verdict(filled, "") is True
        and filled.get("review_pass_ok") is True,
    )
    no_dims = {"reviews": [{"agent": "eng-reviewer", "ts": 1}]}
    check(
        "PASS without seven dims is unclean",
        r20_replay.apply_review_verdict(no_dims, "Independent review PASS") is True
        and no_dims.get("review_pass_ok") is False,
    )
    unclean = {"reviews": [{"agent": "eng-reviewer", "ts": 1, "text": REVIEW_PASS.replace("PASS", "PASS；README 须同步")}]}
    check(
        "PASS with 须同步 is unclean",
        r20_replay.apply_review_verdict(unclean, "") is True
        and unclean.get("review_pass_ok") is False,
    )
    needs = {"reviews": [{"agent": "eng-reviewer", "ts": 1}], "review_pass_ok": True}
    check(
        "NEEDS-CHANGES clears pass",
        r20_replay.apply_review_verdict(needs, "Verdict: NEEDS-CHANGES") is True
        and needs.get("review_pass_ok") is False,
    )
    review_needs = REVIEW_PASS.replace("PASS", "NEEDS-CHANGES").replace("已解决", "未解决")
    batch = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [
            {"agent": "eng-reviewer", "ts": 2, "text": REVIEW_PASS},
            {"agent": "ceo-reviewer", "ts": 3, "text": review_needs},
        ],
    }
    check(
        "batch NEEDS-CHANGES beats PASS",
        r20_replay.apply_review_verdict(batch, REVIEW_PASS) is True
        and batch.get("review_pass_ok") is False,
    )
    stale = {
        "edited_files": [{"path": "a.py", "ts": 5}],
        "reviews": [{"agent": "eng-reviewer", "ts": 2, "text": REVIEW_PASS}],
    }
    check(
        "parent PASS after new edit ignored",
        r20_replay.apply_review_verdict(stale, REVIEW_PASS) is False
        and stale.get("review_pass_ok") is not True,
    )
    check(
        "identify ceo short name",
        r20_replay.identify_reviewer("ceo") == "ceo-reviewer",
    )
    check(
        "identify designer",
        r20_replay.identify_reviewer("UI designer review") == "designer",
    )
    check(
        "identify dx short name",
        r20_replay.identify_reviewer("dx") == "dx-reviewer",
    )
    check(
        "identify security short name",
        r20_replay.identify_reviewer("security") == "security-reviewer",
    )
    check(
        "identify code-explorer is not reviewer",
        r20_replay.identify_reviewer("code-explorer") is None,
    )
    check(
        "identify mid-sentence security is not reviewer",
        r20_replay.identify_reviewer("fix the security of the hook") is None,
    )
    check(
        "identify implementer is not reviewer",
        r20_replay.identify_reviewer("change-implementer") is None,
    )
    check(
        "identify implementer prompt citing eng-reviewer is not reviewer",
        r20_replay.identify_reviewer(
            "You are change-implementer. Previous eng-reviewer NEEDS-CHANGES: fix tests."
        )
        is None,
    )
    check(
        "identify generalPurpose is not reviewer",
        r20_replay.identify_reviewer("generalPurpose") is None,
    )
    check(
        "identify eng-reviewer in prompt",
        r20_replay.identify_reviewer("You are eng-reviewer. Read only.") == "eng-reviewer",
    )
    blob = r20_replay.reviewer_dispatch_blob(
        {
            "subagent_type": "generalPurpose",
            "description": "Independent review",
            "prompt": "You are eng-reviewer. Tools: Read/Grep only.",
        }
    )
    check(
        "dispatch blob reads prompt",
        r20_replay.identify_reviewer(blob) == "eng-reviewer",
    )
    same = {"edited_files": [{"path": "a.py", "ts": 1}], "reviews": []}
    r20_replay.note_reviewer_dispatch(same, "eng-reviewer", 2)
    r20_replay.note_reviewer_dispatch(same, "ceo-reviewer", 3)
    check(
        "same-round dispatch increments once",
        int(same.get("review_rounds") or 0) == 1 and len(same.get("reviews") or []) == 2,
    )
    cap = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [{"agent": "eng-reviewer", "ts": 2}],
    }
    check("attach fills empty review", r20_replay.attach_review_text(cap, REVIEW_PASS, source="eng-reviewer") is True)
    check(
        "attached then verdict passes",
        r20_replay.apply_review_verdict(cap, "") is True
        and cap.get("review_pass_ok") is True,
    )
    check(
        "attach rejects non-verdict parent chatter",
        r20_replay.attach_review_text(
            {
                "edited_files": [{"path": "a.py", "ts": 1}],
                "reviews": [{"agent": "eng-reviewer", "ts": 2}],
            },
            "I'll dispatch eng-reviewer next.",
            source="eng-reviewer",
        )
        is False,
    )
    needs_no_dims = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [{"agent": "eng-reviewer", "ts": 2}],
    }
    check(
        "attach rejects NEEDS-CHANGES without seven dims",
        r20_replay.attach_review_text(needs_no_dims, "Verdict: NEEDS-CHANGES", source="eng-reviewer") is False
        and not str((needs_no_dims.get("reviews") or [{}])[0].get("text") or "").strip(),
    )
    blank_sat = (
        "Independent review PASS\n"
        "- 满足：\n"
        "- 遗漏：无\n"
        "- 错改：无\n"
        "- 漏改：无文档影响\n"
        "- 原功能：保持（证据：pytest）\n"
        "- 影响范围：CRG get_impact_radius\n"
        "- 问题是否解决：已解决（证据：pytest）\n"
    )
    check(
        "blank 满足 line is empty field",
        r20_replay.field_value(blank_sat, "满足") == "",
    )
    check(
        "blank 满足 does not swallow 遗漏",
        r20_replay.field_value(blank_sat, "遗漏") == "无",
    )
    check(
        "blank 满足 line fails seven dims",
        r20_replay.review_dimensions_ok(blank_sat) is False,
    )
    check(
        "attach rejects blank 满足 PASS",
        r20_replay.attach_review_text(
            {
                "edited_files": [{"path": "a.py", "ts": 1}],
                "reviews": [{"agent": "eng-reviewer", "ts": 2}],
            },
            blank_sat,
            source="eng-reviewer",
        )
        is False,
    )
    captured_ok = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [{"agent": "eng-reviewer", "ts": 2, "text": REVIEW_PASS}],
        "review_pass_ok": True,
    }
    check(
        "instructional PASS 或 NEEDS-CHANGES does not poison",
        r20_replay.apply_review_verdict(
            captured_ok, "回贴完整清单与 PASS 或 NEEDS-CHANGES"
        )
        is False
        and captured_ok.get("review_pass_ok") is True,
    )
    slash_ok = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [{"agent": "eng-reviewer", "ts": 2, "text": REVIEW_PASS}],
        "review_pass_ok": True,
    }
    check(
        "instructional PASS / NEEDS-CHANGES does not poison",
        r20_replay.apply_review_verdict(
            slash_ok, "结论：PASS / NEEDS-CHANGES"
        )
        is False
        and slash_ok.get("review_pass_ok") is True,
    )
    check(
        "instructional 结论 PASS / NEEDS-CHANGES is not a verdict",
        r20_replay.primary_verdict("结论：PASS / NEEDS-CHANGES") is None,
    )
    check(
        "instructional 结论 PASS 或 NEEDS-CHANGES is not a verdict",
        r20_replay.primary_verdict("结论：PASS 或 NEEDS-CHANGES") is None,
    )
    check(
        "instructional 状态 PASS / NEEDS-CHANGES is not a verdict",
        r20_replay.primary_verdict("状态: PASS / NEEDS-CHANGES") is None,
    )
    check(
        "pipe 状态 PASS is a verdict",
        r20_replay.primary_verdict("[一句话] | 状态: PASS") == "PASS",
    )
    needs_then_instr = (
        "Independent review NEEDS-CHANGES\n"
        "- 满足：结论行截断未修（承认）\n"
        "- 遗漏：无\n"
        "- 错改：无\n"
        "- 漏改：无文档影响\n"
        "- 原功能：保持（证据：pytest）\n"
        "- 影响范围：CRG get_impact_radius\n"
        "- 问题是否解决：部分解决（证据：pytest）\n"
        "结论：PASS / NEEDS-CHANGES\n"
    )
    check(
        "trailing instructional does not overwrite Independent review NEEDS-CHANGES",
        r20_replay.primary_verdict(needs_then_instr) == "NEEDS-CHANGES",
    )
    instr_only = (
        "结论：PASS / NEEDS-CHANGES\n"
        "- 满足：需求已落地（承认）\n"
        "- 遗漏：无\n"
        "- 错改：无\n"
        "- 漏改：无文档影响\n"
        "- 原功能：保持（证据：pytest）\n"
        "- 影响范围：CRG get_impact_radius\n"
        "- 问题是否解决：已解决（证据：pytest）\n"
    )
    instr_slot = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [{"agent": "eng-reviewer", "ts": 2}],
    }
    check(
        "instructional-only 结论 does not attach",
        r20_replay.attach_review_text(instr_slot, instr_only, source="eng-reviewer") is False
        and not str((instr_slot.get("reviews") or [{}])[0].get("text") or "").strip(),
    )
    trail_slot = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [{"agent": "eng-reviewer", "ts": 2}],
    }
    check(
        "NEEDS-CHANGES still attaches when trailing instructional 结论",
        r20_replay.attach_review_text(trail_slot, needs_then_instr, source="eng-reviewer") is True
        and r20_replay.primary_verdict(str((trail_slot.get("reviews") or [{}])[0].get("text") or ""))
        == "NEEDS-CHANGES",
    )
    mentioned = (
        "Independent review PASS\n"
        "- 满足：已处理正文里的 NEEDS-CHANGES 字样（承认）\n"
        "- 遗漏：无\n"
        "- 错改：无\n"
        "- 漏改：无文档影响\n"
        "- 原功能：保持（证据：pytest）\n"
        "- 影响范围：CRG get_impact_radius\n"
        "- 问题是否解决：已解决（证据：pytest）\n"
        "结论：PASS\n"
    )
    mentioned_entry = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [{"agent": "eng-reviewer", "ts": 2, "text": mentioned}],
    }
    check(
        "body NEEDS-CHANGES substring does not unclean 结论 PASS",
        r20_replay.apply_review_verdict(mentioned_entry, "") is True
        and mentioned_entry.get("review_pass_ok") is True,
    )
    parent_slot = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [{"agent": "eng-reviewer", "ts": 2}],
    }
    check(
        "parent seven-dim without source does not attach",
        r20_replay.attach_review_text(parent_slot, REVIEW_PASS) is False
        and not str((parent_slot.get("reviews") or [{}])[0].get("text") or "").strip(),
    )
    check(
        "payload text mentioning eng-reviewer is not a source",
        r20_replay.reviewer_source_from_payload(
            {"text": "You are eng-reviewer. " + REVIEW_PASS}
        )
        is None,
    )
    check(
        "payload agent_id is a source",
        r20_replay.reviewer_source_from_payload({"agent_id": "eng-reviewer"})
        == "eng-reviewer",
    )
    check(
        "nested input.prompt is not a source",
        r20_replay.reviewer_source_from_payload(
            {"input": {"prompt": "You are eng-reviewer."}, "text": REVIEW_PASS}
        )
        is None,
    )
    check(
        "tool_input.subagent_type is a source",
        r20_replay.reviewer_source_from_payload(
            {"tool_input": {"subagent_type": "eng-reviewer", "prompt": "review this"}}
        )
        == "eng-reviewer",
    )
    check(
        "tool_input.prompt alone is not a source",
        r20_replay.reviewer_source_from_payload(
            {"tool_input": {"prompt": "You are eng-reviewer."}}
        )
        is None,
    )
    mismatch = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [{"agent": "ceo-reviewer", "ts": 2}],
    }
    check(
        "attach refuses mismatched reviewer slot",
        r20_replay.attach_review_text(mismatch, REVIEW_PASS, source="eng-reviewer")
        is False
        and not str((mismatch.get("reviews") or [{}])[0].get("text") or "").strip(),
    )
    later_fill = (
        "- 满足：\n"
        "- 遗漏：无\n"
        "- 满足：后文非空（承认）\n"
        "- 错改：无\n"
        "- 漏改：无文档影响\n"
        "- 原功能：保持（证据：pytest）\n"
        "- 影响范围：CRG get_impact_radius\n"
        "- 问题是否解决：已解决（证据：pytest）\n"
    )
    check(
        "field_value uses last non-empty",
        r20_replay.field_value(later_fill, "满足") == "后文非空（承认）",
    )
    legend = (
        "Independent review PASS\n"
        "- 满足：需求已落地（承认）\n"
        "- 遗漏：无\n"
        "- 错改：无\n"
        "- 漏改：无文档影响\n"
        "- 原功能：保持（证据：pytest）\n"
        "- 影响范围：CRG get_impact_radius\n"
        "- 问题是否解决：已解决 | 未解决 | 部分解决\n"
    )
    check("legend-only 问题是否解决 fails dims", r20_replay.review_dimensions_ok(legend) is False)
    legend_suffix = (
        "Independent review PASS\n"
        "- 满足：需求已落地（承认）\n"
        "- 遗漏：无\n"
        "- 错改：无\n"
        "- 漏改：无文档影响\n"
        "- 原功能：保持（证据：pytest）\n"
        "- 影响范围：CRG get_impact_radius\n"
        "- 问题是否解决：已解决 | 未解决 | 部分解决（证据：pytest）\n"
    )
    check(
        "legend 问题是否解决 with suffix fails dims",
        r20_replay.review_dimensions_ok(legend_suffix) is False,
    )
    needs_ok = (
        "Independent review NEEDS-CHANGES\n"
        "- 满足：身份绑定未做（承认）\n"
        "- 遗漏：无\n"
        "- 错改：无\n"
        "- 漏改：无文档影响\n"
        "- 原功能：保持（证据：pytest）\n"
        "- 影响范围：CRG get_impact_radius\n"
        "- 问题是否解决：部分解决（证据：pytest）\n"
        "结论：NEEDS-CHANGES\n"
    )
    needs_slot = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [{"agent": "eng-reviewer", "ts": 2}],
    }
    check(
        "seven-dim NEEDS-CHANGES attaches to matching slot",
        r20_replay.attach_review_text(needs_slot, needs_ok, source="eng-reviewer") is True
        and "NEEDS-CHANGES" in str((needs_slot.get("reviews") or [{}])[0].get("text") or ""),
    )
    parallel = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [
            {"agent": "eng-reviewer", "ts": 2},
            {"agent": "ceo-reviewer", "ts": 3},
        ],
    }
    check("parallel attach first slot", r20_replay.attach_review_text(parallel, REVIEW_PASS, source="eng-reviewer") is True)
    check("parallel attach second slot", r20_replay.attach_review_text(parallel, REVIEW_PASS, source="ceo-reviewer") is True)
    check(
        "parallel both slots filled then PASS",
        r20_replay.apply_review_verdict(parallel, "") is True
        and parallel.get("review_pass_ok") is True
        and all(str(item.get("text") or "").strip() for item in parallel["reviews"]),
    )
    poisoned = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "reviews": [{"agent": "eng-reviewer", "ts": 2, "text": REVIEW_PASS}],
    }
    r20_replay.apply_review_verdict(poisoned, "")
    check(
        "parent incomplete PASS does not poison captured PASS",
        r20_replay.apply_review_verdict(poisoned, "Independent review PASS") is False
        and poisoned.get("review_pass_ok") is True,
    )
    passed = {"review_pass_ok": True}
    check(
        "counted edit clears review pass",
        r20_replay.clear_review_pass_if_counted(passed, ["a.py"]) is True
        and passed.get("review_pass_ok") is False,
    )
    keep = {"review_pass_ok": True}
    check(
        "plan artifact does not clear review pass",
        r20_replay.clear_review_pass_if_counted(keep, ["foo.plan.md"]) is False
        and keep.get("review_pass_ok") is True,
    )
    check(
        "md only without verify is graph not verify",
        r20_replay.dual_pass_phase(
            {"edited_files": [{"path": "README.md", "ts": 1}]},
        )
        == "graph",
    )
    check(
        "md only with pre-review graph is review",
        r20_replay.dual_pass_phase(
            {
                "edited_files": [{"path": "README.md", "ts": 1}],
                "last_pre_review_graph_ts": 2,
            }
        )
        == "review",
    )
    check(
        "resume str is resumed",
        r20_replay.is_resumed_subagent({"resume": "abc123"}) is True,
    )
    check(
        "empty resume not resumed",
        r20_replay.is_resumed_subagent({"resume": ""}) is False,
    )
    check(
        "missing resume not resumed",
        r20_replay.is_resumed_subagent({}) is False,
    )
    check(
        "false resume not resumed",
        r20_replay.is_resumed_subagent({"resume": False}) is False,
    )
    check(
        "graph shell is refresh call",
        r20_replay.is_graph_refresh_call("Bash", {"command": "codegraph sync"}) is True,
    )
    check(
        "graph pair with crg update is refresh call",
        r20_replay.is_graph_refresh_call(
            "Bash", {"command": "codegraph sync && code-review-graph update"}
        )
        is True,
    )
    check(
        "codegraph init -i is refresh call",
        r20_replay.is_graph_refresh_call("Bash", {"command": "codegraph init -i"}) is True,
    )
    check(
        "echo codegraph plus npm build is not refresh",
        r20_replay.is_graph_refresh_call(
            "Bash", {"command": "echo codegraph; npm run build"}
        )
        is False,
    )
    check(
        "echo codegraph sync is not refresh",
        r20_replay.is_graph_refresh_call("Bash", {"command": "echo codegraph sync"})
        is False,
    )
    check(
        "quoted echo codegraph sync is not refresh",
        r20_replay.is_graph_refresh_call(
            "Bash", {"command": "echo 'codegraph sync'"}
        )
        is False,
    )
    check(
        "npm run build alone is not refresh",
        r20_replay.is_graph_refresh_call("Bash", {"command": "npm run build"})
        is False,
    )
    check(
        "echo codegraph_sync is not refresh",
        r20_replay.is_graph_refresh_call("Bash", {"command": "echo codegraph_sync"}) is False,
    )
    check(
        "mcp tool name codegraph_sync is refresh",
        r20_replay.is_graph_refresh_call("codegraph_sync", {}) is True,
    )
    check(
        "codegraph_explore is not refresh",
        r20_replay.is_graph_refresh_call("codegraph_explore", {}) is False,
    )
    check(
        "pytest is not graph refresh",
        r20_replay.is_graph_refresh_call("Bash", {"command": "pytest -q"}) is False,
    )
    stamped = {"edited_files": [{"path": "a.py", "ts": 1}]}
    check(
        "stamp pre-review graph",
        r20_replay.record_pre_review_graph_refresh(stamped, 2) is True
        and stamped.get("last_pre_review_graph_ts") == 2
        and stamped.get("last_graph_refresh_ts") == 2,
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
    check("verify seven dims", "问题是否解决" in verify)
    check("verify no 只读免审", "只读免审" not in verify)
    check("verify rounds from json", "最多 5 轮" in verify)
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

        crg_payload = json.dumps(
            {
                "session_id": "fe-tracker-test",
                "tool_name": "CallDynamicTool",
                "tool_input": {"toolName": "detect_changes_tool"},
                "cwd": tmp,
            }
        )
        crg_run = subprocess.run(
            cmd,
            input=crg_payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        check("tracker crg call exit 0", crg_run.returncode == 0)
        state_path = Path(tmp) / ".state" / "verification-gate.json"
        recorded = False
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            recorded = bool((state.get("fe-tracker-test") or {}).get("crg_calls"))
        check("tracker records crg_calls", recorded)

        resume_payload = json.dumps(
            {
                "session_id": "fe-tracker-test",
                "tool_name": "Task",
                "tool_input": {
                    "subagent_type": "eng-reviewer",
                    "description": "Review",
                    "resume": "prev-id",
                },
                "cwd": tmp,
            }
        )
        resume_run = subprocess.run(
            cmd,
            input=resume_payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        check("tracker resume review exit 0", resume_run.returncode == 0)
        check(
            "tracker resume review nudges",
            "不计入独立审查" in (resume_run.stdout or ""),
        )
        skipped = False
        counted = False
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            entry = state.get("fe-tracker-test") or {}
            skipped = len(entry.get("skipped_resumed_reviews") or []) == 1
            counted = len(entry.get("reviews") or []) == 0
        check("tracker resume not counted as review", skipped and counted)

        gp_payload = json.dumps(
            {
                "session_id": "gp-review-test",
                "tool_name": "Write",
                "tool_input": {"file_path": str(Path(tmp) / "b.py")},
                "cwd": tmp,
            }
        )
        subprocess.run(
            cmd,
            input=gp_payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        gp_task = json.dumps(
            {
                "session_id": "gp-review-test",
                "tool_name": "Task",
                "tool_input": {
                    "subagent_type": "generalPurpose",
                    "description": "Independent review",
                    "prompt": "You are eng-reviewer. Tools Read/Grep only. Do not edit.",
                },
                "cwd": tmp,
            }
        )
        gp_run = subprocess.run(
            cmd,
            input=gp_task,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )
        check("tracker generalPurpose review exit 0", gp_run.returncode == 0)
        gp_counted = False
        gp_agent = ""
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            gp_entry = state.get("gp-review-test") or {}
            gp_reviews = gp_entry.get("reviews") or []
            gp_counted = len(gp_reviews) == 1 and int(gp_entry.get("review_rounds") or 0) == 1
            gp_agent = str((gp_reviews[0] or {}).get("agent") or "") if gp_reviews else ""
        check(
            "tracker records generalPurpose prompt as eng-reviewer",
            gp_counted and gp_agent == "eng-reviewer",
        )


def test_impact_diff_superset_blocked() -> None:
    """清单外变更（脏集−基线−声明 ≠ ∅）→ 返回额外文件列表。"""
    entry = {
        "edited_files": [{"path": "a.py", "ts": 1}],
        "git_baseline": ["README.md"],
    }
    with tempfile.TemporaryDirectory() as td:
        orig = r20_replay.git_dirty_set
        r20_replay.git_dirty_set = lambda cwd: {"README.md", "rogue.py"}  # noqa: E731
        try:
            extras = r20_replay.impact_diff_check(entry, "s1", td)
        finally:
            r20_replay.git_dirty_set = orig
    check("impact superset blocked", extras == ["rogue.py"], str(extras))


def test_impact_diff_subset_passes() -> None:
    """变更 ⊆ 基线∪声明清单 → 放行（空列表）。"""
    entry = {
        "edited_files": [{"path": "src/a.py", "ts": 1}],
        "git_baseline": ["src/b.py"],
    }
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, ".claude", "state", "impact-manifest.log")
        os.makedirs(os.path.dirname(log))
        with open(log, "w", encoding="utf-8") as fh:
            fh.write("IMPACT|s2|src/a.py|2026-08-25\n")
        orig = r20_replay.git_dirty_set
        r20_replay.git_dirty_set = lambda cwd: {"src/a.py"}  # noqa: E731
        try:
            extras = r20_replay.impact_diff_check(entry, "s2", td)
        finally:
            r20_replay.git_dirty_set = orig
    check("impact subset passes", extras == [], str(extras))


def test_impact_diff_disabled_skip() -> None:
    """无基线/无编辑 → 静默跳过（空列表）。"""
    check("impact no-entry skip", r20_replay.impact_diff_check({}, "s3", "") == [])
    entry = {"edited_files": [{"path": "a.py", "ts": 1}]}  # 有编辑但无基线（非git会话）
    check("impact no-baseline skip", r20_replay.impact_diff_check(entry, "s4", "") == [])


def test_fingerprint_coverage_pass() -> None:
    """v11.4：满足行覆盖 strong 指纹 → 合格。"""
    reqs = {"strong": ["impact-manifest", "req_fingerprint"], "weak": []}
    text = (
        "## 会话终验（R20）\n原始要求：实现 impact-manifest 自动登记与 req_fingerprint 实质比对\n"
        "- 满足：impact-manifest 自动落盘与 req_fingerprint 覆盖比对已实现并测试通过\n"
        "- 遗漏：无\n- 错改：无\n- 漏改：无文档影响\n"
        "- 原功能：保持（证据：python hooks/tests/test_r20_replay.py 全绿）\n"
        "- 影响范围：已审查 CRG get_impact_radius 与 IMPACT 清单\n"
        "- 问题是否解决：已解决（证据：python hooks/tests/test_r20_replay.py 全绿）\n"
        "结论：DONE"
    )
    check("fingerprint coverage pass", r20_replay.replay_ok(text, reqs) is True)


def test_fingerprint_coverage_fail() -> None:
    """v11.4：满足行为空话（未命中 strong 指纹）→ 不合格，即使五字段齐全。"""
    reqs = {"strong": ["impact-manifest", "req_fingerprint"], "weak": []}
    text = (
        "## 会话终验（R20）\n原始要求：实现自动登记\n"
        "- 满足：全部按要求完成了\n"
        "- 遗漏：无\n- 错改：无\n- 漏改：无文档影响\n"
        "- 原功能：保持（证据：pytest 全绿）\n"
        "- 影响范围：已审查 CRG get_impact_radius\n"
        "- 问题是否解决：已解决（证据：pytest 全绿）\n"
        "结论：DONE"
    )
    check("fingerprint coverage fail", r20_replay.replay_ok(text, reqs) is False)
    check("same text passes without fingerprint", r20_replay.replay_ok(text) is True)


def test_fingerprint_weak_only_noop() -> None:
    """v11.4：weak-only 需求不启用实质比对（防误伤），行为与无指纹一致。"""
    reqs = {"strong": [], "weak": ["同步", "文档"]}
    check("weak-only noop pass", r20_replay.replay_ok(VALID, reqs) is True)


def test_stop_does_not_stamp_pre_review_graph() -> None:
    src = (HOOKS_DIR / "stop-verification-gate.py").read_text(encoding="utf-8")
    check(
        "stop does not stamp pre-review graph",
        "record_pre_review_graph_refresh" not in src,
    )
    check(
        "stop does not attach review text",
        "attach_review_text" not in src,
    )
    cap_src = (HOOKS_DIR / "r20-capture.py").read_text(encoding="utf-8")
    check("claude r20-capture attaches", "attach_review_text" in cap_src)
    check("claude r20-capture binds source", "reviewer_source_from_payload" in cap_src)
    portable = (
        HOOKS_DIR.parent / "templates" / "editor-graph-hooks" / "r20_check.py"
    ).read_text(encoding="utf-8")
    check(
        "portable r20_check imports SSOT",
        "replay_detail" in portable and "_FIELD_RE" not in portable,
    )


def test_review_verdict_ok() -> None:
    check("verdict PASS detected", r20_replay.review_verdict_ok("eng-reviewer 结论：PASS — 无阻断项") is True)
    check("verdict NEEDS-CHANGES detected", r20_replay.review_verdict_ok("review verdict: NEEDS-CHANGES") is True)
    check("verdict lowercase rejected", r20_replay.review_verdict_ok("结论：pass") is False)
    check("verdict plain text rejected", r20_replay.review_verdict_ok("审查完成，没有问题") is False)
    check("verdict empty rejected", r20_replay.review_verdict_ok("") is False)
    check(
        "body PASS without heading rejected",
        r20_replay.review_verdict_ok("the tests PASS today") is False,
    )
    check(
        "instructional 结论 is not review_verdict_ok",
        r20_replay.review_verdict_ok("结论：PASS / NEEDS-CHANGES") is False,
    )


def test_crg_track() -> None:
    import crg_track

    check("detect_changes is crg", crg_track.is_crg_tool("mcp__code-review-graph__detect_changes_tool"))
    check("get_impact_radius is crg", crg_track.is_crg_tool("get_impact_radius_tool"))
    check("codegraph not crg", crg_track.is_crg_tool("codegraph_explore") is False)
    entry: dict = {}
    check(
        "record crg via toolName",
        crg_track.record_crg_call(entry, "CallDynamicTool", 10.0, {"toolName": "get_minimal_context_tool"}),
    )
    check("crg_calls stored", bool(entry.get("crg_calls")))
    check("has_crg_since true", crg_track.has_crg_since(entry, 9.0) is True)
    check("has_crg_since false future", crg_track.has_crg_since(entry, 99.0) is False)
    empty: dict = {}
    check("no graph empty cwd", crg_track.project_has_crg_graph("") is False)
    with tempfile.TemporaryDirectory() as td:
        empty = os.path.join(td, ".code-review-graph")
        os.mkdir(empty)
        check("empty registry dir is not a project graph", crg_track.project_has_crg_graph(td) is False)
        open(os.path.join(empty, "graph.db"), "wb").close()
        check("has graph.db", crg_track.project_has_crg_graph(td) is True)
        missing = crg_track.project_has_crg_graph(td) and not crg_track.has_crg_since({}, 1.0)
        check("graph without crg_calls is missing", missing is True)
    check("six retry has 影响面", "影响面" in crg_track.six_retry_block())
    msg = mod.build_block_message(["R20 会话终验：缺"], False, 1, 3)
    check("block message includes 短 R20", "短 R20" in msg)


def main() -> int:
    print("=== R20 replay marker tests ===")
    test_crg_track()
    test_fingerprint_coverage_pass()
    test_fingerprint_coverage_fail()
    test_fingerprint_weak_only_noop()
    test_review_verdict_ok()
    test_stop_does_not_stamp_pre_review_graph()
    test_positive_string_content()
    test_positive_list_content()
    test_empty_template_rejected()
    test_ellipsis_satisfied_rejected()
    test_keep_only_yuan_rejected()
    test_path_in_lougai_ok()
    test_missing_impact_rejected()
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
    test_impact_diff_superset_blocked()
    test_impact_diff_subset_passes()
    test_impact_diff_disabled_skip()
    print(f"passed={len(PASSED)} failed={len(FAILED)}")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
