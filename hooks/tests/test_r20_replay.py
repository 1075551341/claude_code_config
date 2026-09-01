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
    "结论：DONE"
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
        "- 影响范围：无\n结论：DONE"
    )
    check("empty 影响范围 rejected", r20_replay.replay_ok(empty_impact) is False)


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
            },
            {"review_max_rounds": 3, "require_reviewer_min_files": 3},
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
            }
        )
        == "review",
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
                "review_rounds": 3,
            },
            {"review_max_rounds": 3},
        )
        is False,
    )
    check(
        "phase capped",
        r20_replay.dual_pass_phase(
            {
                "non_simple": True,
                "edited_files": [{"path": "a.py", "ts": 1}],
                "review_rounds": 3,
            },
            {"review_max_rounds": 3},
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
        "md only not dual pass",
        r20_replay.dual_pass_in_scope(
            {"edited_files": [{"path": "README.md", "ts": 1}]},
            {"require_reviewer_min_files": 1},
        )
        is False,
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
        r20_replay.apply_review_verdict(empty, "Independent review PASS") is False
        and empty.get("review_pass_ok") is not True,
    )
    with_rev = {"reviews": [{"agent": "eng-reviewer", "ts": 1}]}
    check(
        "PASS with reviews sets ok",
        r20_replay.apply_review_verdict(with_rev, "Independent review PASS") is True
        and with_rev.get("review_pass_ok") is True,
    )
    unclean = {"reviews": [{"agent": "eng-reviewer", "ts": 1}]}
    check(
        "PASS with 须同步 is unclean",
        r20_replay.apply_review_verdict(unclean, "Independent review PASS；README 须同步")
        is True
        and unclean.get("review_pass_ok") is False,
    )
    needs = {"reviews": [{"agent": "eng-reviewer", "ts": 1}], "review_pass_ok": True}
    check(
        "NEEDS-CHANGES clears pass",
        r20_replay.apply_review_verdict(needs, "Verdict: NEEDS-CHANGES") is True
        and needs.get("review_pass_ok") is False,
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
        "- 影响范围：已审查 CRG get_impact_radius 与 IMPACT 清单\n结论：DONE"
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
        "- 影响范围：已审查 CRG get_impact_radius\n结论：DONE"
    )
    check("fingerprint coverage fail", r20_replay.replay_ok(text, reqs) is False)
    check("same text passes without fingerprint", r20_replay.replay_ok(text) is True)


def test_fingerprint_weak_only_noop() -> None:
    """v11.4：weak-only 需求不启用实质比对（防误伤），行为与无指纹一致。"""
    reqs = {"strong": [], "weak": ["同步", "文档"]}
    check("weak-only noop pass", r20_replay.replay_ok(VALID, reqs) is True)


def test_review_verdict_ok() -> None:
    check("verdict PASS detected", r20_replay.review_verdict_ok("eng-reviewer 结论：PASS — 无阻断项") is True)
    check("verdict NEEDS-CHANGES detected", r20_replay.review_verdict_ok("review verdict: NEEDS-CHANGES") is True)
    check("verdict lowercase rejected", r20_replay.review_verdict_ok("结论：pass") is False)
    check("verdict plain text rejected", r20_replay.review_verdict_ok("审查完成，没有问题") is False)
    check("verdict empty rejected", r20_replay.review_verdict_ok("") is False)


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
