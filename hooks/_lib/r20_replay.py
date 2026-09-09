#!/usr/bin/env python3
"""R20 会话终验机械检测（v11.3.4）— 空模板不得过门。

Claude Stop 与 Cursor 记账共用，禁止再复制一份正则。Cursor 完成门不再 followup。
"""
from __future__ import annotations

import os
import re
import subprocess

_VERDICT_RE = re.compile(r"\b(PASS|NEEDS-CHANGES)\b")
_UNCLEAN_PASS_RE = re.compile(
    r"(未同步|须同步|应同步|存在文档漂移|注释不一致)"
)

_REQUIRED = ("遗漏", "错改", "漏改", "原功能", "影响范围", "问题是否解决")
_EMPTY_SATISFIED = {"", ".", "..", "...", "…", "无", "n/a", "na", "none"}
_SOLVED_TOKENS = ("已解决", "未解决", "部分解决")
_PATH_RE = re.compile(
    r"(?:[A-Za-z]:)?[\\/][\w.\\/-]+|\S+\.(?:md|mdc|py|ts|tsx|js|json|ya?ml|toml|txt)\b"
)
_FIELD_NAMES = (
    "满足|遗漏|错改|漏改|原功能|影响范围|影响面|问题是否解决"
)
_FIELD_RE = re.compile(
    rf"(?:^|\n)\s*-?\s*({_FIELD_NAMES})\s*[：:]\s*(.*?)(?="
    rf"(?:\n\s*-?\s*(?:{_FIELD_NAMES})\s*[：:])|\n结论|$)",
    re.S,
)
_GRAPH_PAIR_RE = re.compile(
    r"\b(codegraph|code-review-graph)(?:\s+|-)(init|sync|index|build|update)\b",
    re.I,
)
_GRAPH_MCP_MARKERS = (
    "build_or_update",
    "codegraph_sync",
    "codegraph_init",
    "codegraph_index",
)
_NO_REVIEWER_STEM = frozenset({"code"})
DEFAULT_DOC_EXTS = (".md", ".txt", ".rst", ".markdown")
_IMPACT_TOKENS = (
    "crg",
    "get_impact_radius",
    "impact",
    "blast-radius",
    "blast radius",
    "影响面",
    "影响范围",
)


def field_value(text: str, name: str) -> str:
    """取出终验字段正文；找不到返回空串。"""
    for match in _FIELD_RE.finditer(text):
        if match.group(1) == name:
            return match.group(2).strip()
    return ""


def replay_ok(text: str, requirements: dict | None = None) -> bool:
    """最后一条助手回复是否构成合格 R20（反空模板；v11.4 可选需求指纹实质比对）。

    requirements 非空且含 strong 特征时，「满足」行须覆盖指纹关键词——
    strong<5 全命中，≥5 允许 ≥80%（req_fingerprint.coverage_ok）。
    不传参行为与 v11.3 完全一致（Cursor 端旧调用兼容）。
    """
    if not text or not text.strip():
        return False
    if ("会话终验" not in text) and ("R20" not in text):
        return False
    if any(token not in text for token in _REQUIRED):
        return False

    satisfied = field_value(text, "满足")
    if satisfied.strip().lower() in _EMPTY_SATISFIED:
        return False

    if requirements:
        from req_fingerprint import coverage_ok

        ok, _detail = coverage_ok(requirements, satisfied)
        if not ok:
            return False

    missed = field_value(text, "漏改")
    if not missed:
        return False
    if not (
        "文档" in missed
        or "注释" in missed
        or "无文档影响" in missed
        or _PATH_RE.search(missed)
    ):
        return False

    original = field_value(text, "原功能")
    if not original:
        return False
    if not any(token in original for token in ("证据", "测试", "冒烟")):
        return False

    impact = field_value(text, "影响范围") or field_value(text, "影响面")
    if not impact or impact.strip().lower() in _EMPTY_SATISFIED:
        return False
    lowered = impact.lower()
    if not any(token in lowered for token in _IMPACT_TOKENS):
        return False
    return review_dimensions_ok(text)


def is_resumed_subagent(tool_input) -> bool:
    """Task/Agent 带非空 resume 则沿用上轮上下文，不计入独立审查。"""
    if not isinstance(tool_input, dict):
        return False
    resume = tool_input.get("resume")
    if resume is None or resume is False:
        return False
    if isinstance(resume, str) and not resume.strip():
        return False
    return True


def review_verdict_ok(text: str) -> bool:
    """v11.4：最后一条助手回复是否含独立审查结论标记（PASS / NEEDS-CHANGES）。"""
    if not text or not text.strip():
        return False
    return bool(_VERDICT_RE.search(text))


DEFAULT_REVIEWER_AGENTS = (
    "eng-reviewer",
    "ceo-reviewer",
    "designer",
    "dx-reviewer",
    "qa",
    "security-reviewer",
    "code-reviewer",
)


def review_dimensions_ok(text: str) -> bool:
    """独立审查 / R20 七维是否齐全（缺一则本轮无效）。"""
    if not text or not text.strip():
        return False
    for name in ("满足", "遗漏", "错改", "漏改", "原功能"):
        if name not in text:
            return False
    if "影响范围" not in text and "影响面" not in text:
        return False
    if "问题是否解决" not in text:
        return False
    solved = field_value(text, "问题是否解决")
    if not solved or solved.strip().lower() in _EMPTY_SATISFIED:
        return False
    return any(token in solved for token in _SOLVED_TOKENS)


def identify_reviewer(agent_blob: str, reviewer_agents=None) -> str | None:
    """从 Task/Agent 描述识别审查者。

    全名（eng-reviewer、security-reviewer、designer…）可出现在 blob 任意处。
    简称（ceo / dx / security / qa）仅当整个 blob 或首个 token 精确等于该词，
    避免 code-explorer 命中 code-reviewer、或正文里的 security 误识别。
    永不使用 stem ``code``。
    """
    blob = (agent_blob or "").strip()
    if not blob:
        return None
    lower = blob.lower()
    names = [str(n) for n in (reviewer_agents or DEFAULT_REVIEWER_AGENTS) if n]
    names.sort(key=len, reverse=True)
    for name in names:
        n = name.lower()
        if "-" in n or len(n) > 3:
            if n in lower:
                return name
    first = lower.split()[0]
    first = first.split("/")[-1].strip(".,;:\"'`")
    for name in names:
        n = name.lower()
        stem = n[:-9] if n.endswith("-reviewer") else n
        if not stem or stem in _NO_REVIEWER_STEM:
            continue
        if lower == stem or lower == n or first == stem or first == n:
            return name
    return None


def reviewer_dispatch_blob(tool_input=None, extra=None) -> str:
    """拼接 Task/Agent 的 subagent_type + description + prompt（含嵌套 arguments）。"""
    parts: list[str] = []

    def add(blob) -> None:
        if not isinstance(blob, dict):
            return
        for key in ("subagent_type", "description", "prompt"):
            val = blob.get(key)
            if isinstance(val, str) and val.strip():
                parts.append(val.strip())
        for nest in ("arguments", "tool_input", "input"):
            nested = blob.get(nest)
            if isinstance(nested, dict):
                add(nested)

    add(extra)
    add(tool_input)
    return " ".join(parts)


def note_reviewer_dispatch(entry: dict, reviewer: str, ts: float, *, resumed: bool = False) -> bool:
    """记录审查委派。同轮连派不增加 review_rounds；resume 不计入 reviews。"""
    if not isinstance(entry, dict) or not reviewer:
        return False
    stamp = float(ts or 0)
    if resumed:
        entry.setdefault("skipped_resumed_reviews", []).append(
            {"agent": reviewer, "ts": stamp}
        )
        return True
    reviews = entry.setdefault("reviews", [])
    if not isinstance(reviews, list):
        reviews = []
        entry["reviews"] = reviews
    last_rev = _last_item_ts(reviews)
    last_edit = _last_item_ts(entry.get("edited_files") or [])
    if last_edit > last_rev:
        entry["review_rounds"] = int(entry.get("review_rounds") or 0) + 1
    reviews.append({"agent": reviewer, "ts": stamp})
    entry["last_review_dispatch_ts"] = stamp
    entry["review_pass_ok"] = False
    return True


def _current_round_reviews(entry: dict) -> list:
    reviews = [item for item in (entry.get("reviews") or []) if isinstance(item, dict)]
    edit_ts = _last_item_ts(counted_edit_items(entry))
    if edit_ts <= 0:
        return reviews
    return [item for item in reviews if float(item.get("ts") or 0) > edit_ts]


def attach_review_text(entry: dict, text: str) -> bool:
    """把审查正文填到本轮最后一条空 reviews[].text。仅 capture 调用。"""
    blob = (text or "").strip()
    if not blob or not isinstance(entry, dict):
        return False
    round_reviews = _current_round_reviews(entry)
    for item in reversed(round_reviews):
        if not str(item.get("text") or "").strip():
            item["text"] = blob
            return True
        return False
    return False


def clear_review_pass_if_counted(entry: dict, paths) -> bool:
    """非计划制品的新编辑使既有 review_pass_ok 失效。"""
    if not isinstance(entry, dict):
        return False
    if not any(p and not is_plan_artifact(str(p)) for p in (paths or [])):
        return False
    if entry.get("review_pass_ok") is True:
        entry["review_pass_ok"] = False
        return True
    return False


def _looks_like_review_verdict(text: str) -> bool:
    blob = text or ""
    return "NEEDS-CHANGES" in blob or bool(re.search(r"\bPASS\b", blob))


def _verdict_unclean(text: str) -> bool:
    blob = text or ""
    return (
        "NEEDS-CHANGES" in blob
        or bool(_UNCLEAN_PASS_RE.search(blob))
        or not review_dimensions_ok(blob)
    )


def _round_review_texts(entry: dict, extra: str = "") -> tuple[list[str], bool, list]:
    """本轮 reviews[] 已捕获正文 + 可选当前回复。不改写空 text。"""
    round_items = _current_round_reviews(entry)
    has_empty = False
    texts: list[str] = []
    for item in round_items:
        body = str(item.get("text") or "").strip()
        if not body:
            has_empty = True
            continue
        if body not in texts:
            texts.append(body)
    blob = (extra or "").strip()
    if blob and _looks_like_review_verdict(blob) and blob not in texts:
        texts.append(blob)
    return texts, has_empty, round_items


def apply_review_verdict(entry: dict, text: str) -> bool:
    """按本轮 reviews[] 批次聚合写入 review_pass_ok。禁止自报 PASS。

    不把父消息填进空 reviews[].text（那是 r20_capture.attach_review_text 的职责）。
    本轮存在空 text 的审查槽 → 不能 PASS。
    批次内任一 NEEDS-CHANGES、缺七维、或不干净 PASS → 整轮不通过。
    全部干净 PASS 且本轮审查槽均有正文才记 pass。
    """
    if not isinstance(entry, dict):
        return False
    texts, has_empty, round_items = _round_review_texts(entry, text)
    extra = (text or "").strip()
    if not round_items:
        if extra and "NEEDS-CHANGES" in extra:
            if entry.get("review_pass_ok") is not False:
                entry["review_pass_ok"] = False
                return True
        return False
    unclean = has_empty or (not texts) or any(_verdict_unclean(blob) for blob in texts)
    if unclean:
        if entry.get("review_pass_ok") is not False:
            entry["review_pass_ok"] = False
            return True
        return False
    all_pass = all(
        review_verdict_ok(blob) and re.search(r"\bPASS\b", blob) for blob in texts
    )
    if all_pass and not entry.get("review_pass_ok"):
        entry["review_pass_ok"] = True
        return True
    return False


def is_plan_artifact(path: str) -> bool:
    """Cursor/计划落盘：.cursor/plans/ 与 *.plan.md 不计完成门。"""
    if not path or not str(path).strip():
        return False
    n = str(path).replace("\\", "/").lower()
    if n.endswith(".plan.md"):
        return True
    return "/.cursor/plans/" in n or n.endswith("/.cursor/plans")


def counted_edit_items(entry: dict) -> list:
    """完成门口径：去掉计划制品。"""
    out = []
    for item in entry.get("edited_files") or []:
        path = str(item.get("path") or "")
        if not path or is_plan_artifact(path):
            continue
        out.append(item)
    return out


def is_doc_path(path: str, doc_exts=None) -> bool:
    """是否为完成门口径的文档路径（.md/.txt/.rst/.markdown）。"""
    ext = os.path.splitext(str(path or ""))[1].lower()
    skip = {str(x).lower() for x in (doc_exts or DEFAULT_DOC_EXTS)}
    return bool(ext) and ext in skip


def counted_edits_are_docs_only(entry: dict, doc_exts=None) -> bool:
    edited = counted_edit_items(entry)
    if not edited:
        return False
    return all(is_doc_path(str(item.get("path") or ""), doc_exts) for item in edited)


def has_unverified_edits(entry: dict) -> bool:
    """本会话有（非计划制品）代码编辑且最后一次编辑后无验证命令。

    纯文档会话不要求 pytest：否则 README 会卡在 verify，进不了刷图/审查。
    """
    edited = counted_edit_items(entry)
    if not edited:
        return False
    if counted_edits_are_docs_only(entry):
        return False
    last_edit_ts = max((item.get("ts", 0) for item in edited), default=0)
    if last_edit_ts == 0:
        return False
    return not any(
        cmd.get("ts", 0) >= last_edit_ts - 1
        for cmd in (entry.get("verify_commands") or [])
    )


GATE_HEADER = "【门控 · 完成前必做】"
PLAN_MODE_VALUES = frozenset({"plan", "planning", "ask"})
AGENT_MODE_VALUES = frozenset({"agent", "edit", "implementation"})
PLAN_TOOL_NAMES = frozenset({"createplan", "switchmode"})
_WRAPPER_TOOLS = frozenset({"calldynamictool", "callmcptool"})
_EDIT_TOOL_KEYS = frozenset({"write", "strreplace", "edit", "multiedit", "editnotebook", "delete"})
COMPLETION_KEYWORDS = (
    "完成了",
    "修好了",
    "测试通过",
    "声称完成",
    "done",
    "搞定",
    "fixed",
)


def _inner_from_blob(blob: dict) -> str:
    for key in ("toolName", "name", "tool_name", "tool"):
        val = blob.get(key)
        if isinstance(val, str) and val.strip():
            key_n = val.strip().lower().replace("_", "")
            if key_n not in _WRAPPER_TOOLS:
                return val.strip()
    nested = blob.get("arguments") or blob.get("tool_input") or blob.get("input")
    if isinstance(nested, dict):
        return _inner_from_blob(nested)
    return ""


def unwrap_tool_name(name: str, data: dict | None = None) -> str:
    """CallDynamicTool / CallMcpTool 解析内层 CreatePlan / SwitchMode。"""
    raw = (name or "").strip()
    key = raw.lower().replace("_", "")
    if key not in _WRAPPER_TOOLS:
        return raw
    if isinstance(data, dict):
        inner = _inner_from_blob(data)
        if inner:
            return inner
        for nest_key in ("tool_input", "arguments", "input"):
            blob = data.get(nest_key)
            if isinstance(blob, dict):
                inner = _inner_from_blob(blob)
                if inner:
                    return inner
    return raw


def payload_tool_name(data: dict | None) -> str:
    """Stop/工具载荷里的工具名；没有则空串。"""
    if not isinstance(data, dict):
        return ""
    for key in ("tool_name", "toolName", "last_tool_name", "lastToolName"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return unwrap_tool_name(val.strip(), data)
    tool = data.get("tool")
    if isinstance(tool, dict):
        val = tool.get("name") or tool.get("toolName")
        if isinstance(val, str) and val.strip():
            return unwrap_tool_name(val.strip(), data)
    return ""


def _mode_value(data: dict) -> str:
    if data.get("is_plan_mode") is True:
        return "plan"
    for key in (
        "composer_mode",
        "mode",
        "agent_mode",
        "plan_mode",
        "current_mode",
        "conversation_state",
    ):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip().lower()
    composer = data.get("composer")
    if isinstance(composer, dict):
        val = composer.get("mode") or composer.get("composer_mode")
        if isinstance(val, str) and val.strip():
            return val.strip().lower()
    return ""


def switchmode_target(data: dict | None) -> str:
    if not isinstance(data, dict):
        return ""
    blobs: list[dict] = [data]
    for key in ("tool_input", "input", "arguments"):
        nested = data.get(key)
        if isinstance(nested, dict):
            blobs.append(nested)
            inner = nested.get("arguments") or nested.get("tool_input") or nested.get("input")
            if isinstance(inner, dict):
                blobs.append(inner)
    for blob in blobs:
        val = blob.get("target_mode_id") or blob.get("target_mode")
        if val:
            return str(val).strip().lower()
    return ""


def is_awaiting_plan(entry: dict | None, data: dict | None = None) -> bool:
    """CreatePlan / Plan 模式 / 等待用户点 Build：禁止完成门 followup。"""
    entry = entry or {}
    if entry.get("awaiting_plan_approval"):
        return True
    last = unwrap_tool_name(str(entry.get("last_tool") or "")).lower().replace("_", "")
    if last == "createplan":
        return True
    if last == "switchmode" and str(entry.get("last_mode_target") or "").lower() in PLAN_MODE_VALUES:
        return True
    if not isinstance(data, dict):
        return False
    if _mode_value(data) in PLAN_MODE_VALUES:
        return True
    tool = payload_tool_name(data).lower().replace("_", "")
    if tool == "createplan":
        return True
    if tool == "switchmode" and switchmode_target(data) in PLAN_MODE_VALUES:
        return True
    return False


def is_gate_echo(text: str) -> bool:
    """followup 回灌成用户消息时不再二次注入。"""
    return bool(text) and GATE_HEADER in text


def cursor_should_followup(entry: dict, data: dict | None = None) -> bool:
    """Cursor stop：有非计划制品编辑且非计划等待，且（无验证命令或 R20 未过）。"""
    if is_awaiting_plan(entry, data):
        return False
    if not counted_edit_items(entry):
        return False
    if not entry.get("r20_replay_ok"):
        return True
    return has_unverified_edits(entry)


def unique_code_edit_count(entry: dict, doc_exts=None) -> int:
    """会话内非文档、非计划制品编辑路径去重计数。"""
    skip = {str(x).lower() for x in (doc_exts or DEFAULT_DOC_EXTS)}
    seen = set()
    for item in counted_edit_items(entry):
        path = str(item.get("path") or "")
        ext = os.path.splitext(path)[1].lower()
        if not path or ext in skip:
            continue
        seen.add(os.path.normcase(os.path.normpath(path)))
    return len(seen)


def _last_item_ts(items) -> float:
    if not items:
        return 0.0
    return max(float(item.get("ts", 0) or 0) for item in items)


def dual_pass_in_scope(entry: dict, cfg: dict | None = None) -> bool:
    """是否走修改→验证→独立审查循环（有交付物编辑即启用，含文档）。"""
    cfg = cfg or {}
    if is_awaiting_plan(entry):
        return False
    edited = counted_edit_items(entry)
    if not edited:
        return False
    n = len({str(item.get("path") or "") for item in edited if item.get("path")})
    if n < 1:
        return False
    if bool(entry.get("non_simple")):
        return True
    min_files = int(cfg.get("require_reviewer_min_files", 1))
    return n >= min_files


def graph_fresh_for_review(entry: dict, cfg: dict | None = None) -> bool:
    """审查前须在 last_edit 之后做过增量刷图（Stop 刷新不计）。"""
    cfg = cfg or {}
    if not cfg.get("require_refresh_before_review", True):
        return True
    edit_ts = _last_item_ts(counted_edit_items(entry))
    graph_ts = float(entry.get("last_pre_review_graph_ts") or 0)
    return graph_ts > edit_ts


def is_graph_refresh_call(tool_name: str, tool_input=None) -> bool:
    """Bash/MCP 是否为 codegraph 或 CRG 的 init/sync/build/update。

    Shell 必须是相邻的 CLI+动作（``codegraph sync`` / ``code-review-graph update``）。
    MCP 标记只看工具名，不扫描 Bash command，避免 ``echo codegraph; npm run build``。
    """
    raw = (tool_name or "").strip()
    blob = tool_input if isinstance(tool_input, dict) else {}
    cmd = str(blob.get("command") or blob.get("cmd") or "")
    if _GRAPH_PAIR_RE.search(cmd):
        return True
    name_hay = " ".join(
        part
        for part in (
            raw,
            str(blob.get("toolName") or ""),
            str(blob.get("name") or ""),
        )
        if part
    ).lower().replace("-", "_")
    if any(marker in name_hay for marker in _GRAPH_MCP_MARKERS):
        return True
    inner = blob.get("arguments") or blob.get("tool_input") or blob.get("input")
    if isinstance(inner, dict) and inner is not blob:
        return is_graph_refresh_call(
            str(inner.get("toolName") or inner.get("name") or ""), inner
        )
    return False


def record_pre_review_graph_refresh(entry: dict, ts: float) -> bool:
    """审查前刷图记账。Stop 完成刷新不得调用。"""
    prev = float(entry.get("last_pre_review_graph_ts") or 0)
    stamp = float(ts or 0)
    if stamp <= prev:
        return False
    entry["last_pre_review_graph_ts"] = stamp
    entry["last_graph_refresh_ts"] = stamp
    return True


def dual_pass_phase(entry: dict, cfg: dict | None = None) -> str:
    """双审相位。

    一轮 = 修改 → 验证 → 审查前刷图 → 全新独立审查（七维一次找齐）。
    独立审查干净 PASS / 符合预期 → done。
    下一轮必须全新开审（禁止 resume）。最多 review_max_rounds 轮。

    返回: skip | done | capped | modify | verify | graph | review
    """
    cfg = cfg or {}
    if not dual_pass_in_scope(entry, cfg):
        return "skip"
    if entry.get("review_pass_ok"):
        return "done"
    max_rounds = int(cfg.get("review_max_rounds", 5))
    rounds = int(entry.get("review_rounds") or 0)
    if rounds >= max_rounds:
        return "capped"
    review_ts = _last_item_ts(entry.get("reviews") or [])
    edit_ts = _last_item_ts(counted_edit_items(entry))
    if rounds > 0 and edit_ts <= review_ts:
        return "modify"
    if has_unverified_edits(entry):
        return "verify"
    if not graph_fresh_for_review(entry, cfg):
        return "graph"
    return "review"


def review_followup_needed(entry: dict, cfg: dict | None = None) -> bool:
    """当前应委派独立审查（已修改并验证、尚未达上限）。"""
    return dual_pass_phase(entry, cfg) == "review"


def _edit_paths_from_input(tool_input) -> list[str]:
    if not isinstance(tool_input, dict):
        return []
    paths: list[str] = []
    for key in ("path", "file_path", "target_file", "target_notebook"):
        val = tool_input.get(key)
        if isinstance(val, str) and val.strip():
            paths.append(val.strip())
    nested = tool_input.get("arguments") or tool_input.get("tool_input")
    if isinstance(nested, dict):
        paths.extend(_edit_paths_from_input(nested))
    return paths


def record_plan_tool(entry: dict, tool_name: str, tool_input=None) -> None:
    """追踪 CreatePlan / SwitchMode，供 stop 跳过 followup。

    写计划制品不得清除 awaiting；仅切到 agent 或出现非计划制品代码编辑时才清除。
    """
    blob = tool_input if isinstance(tool_input, dict) else {}
    name = unwrap_tool_name((tool_name or "").strip(), {"tool_input": blob, "toolName": tool_name})
    if not name:
        return
    key = name.lower().replace("_", "")
    if key in _WRAPPER_TOOLS:
        return
    entry["last_tool"] = name
    if key == "createplan":
        entry["awaiting_plan_approval"] = True
        return
    if key == "switchmode":
        data = {"tool_input": blob}
        target = switchmode_target(data)
        if target:
            entry["last_mode_target"] = target
        if target in PLAN_MODE_VALUES:
            entry["awaiting_plan_approval"] = True
        elif target in AGENT_MODE_VALUES:
            entry["awaiting_plan_approval"] = False
        return
    if key not in _EDIT_TOOL_KEYS:
        return
    paths = _edit_paths_from_input(blob)
    if paths and all(is_plan_artifact(p) for p in paths):
        return
    if not paths:
        return
    entry["awaiting_plan_approval"] = False



# ---- 方案A：清单制品 diff 差集校验（design-v2 v11.3.6）----


def _norm_path(p: str) -> str:
    p = p.strip().replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    return p


def git_dirty_set(cwd: str):
    """当前脏文件集；非 git 仓库返回 None。"""
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"], cwd=cwd or None,
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    files = set()
    for line in proc.stdout.splitlines():
        if len(line) > 3:
            rel = _norm_path(line[3:].strip().strip('"'))
            if rel.startswith(".claude/"):
                continue  # hook 自身运行时状态（清单制品等）不算变更面
            files.add(rel)
    return files


def manifest_log_path(cwd: str) -> str:
    return os.path.join(cwd or os.getcwd(), ".claude", "state", "impact-manifest.log")


def declared_impact(session_id: str, cwd: str) -> set:
    """本 session 在项目清单中声明的文件集。"""
    declared = set()
    try:
        with open(manifest_log_path(cwd), "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split("|")
                if len(parts) >= 3 and parts[0].strip() == "IMPACT" and parts[1].strip() == session_id:
                    for p in parts[2].split(","):
                        if p.strip():
                            declared.add(_norm_path(p))
    except OSError:
        pass
    return declared


def impact_diff_check(entry: dict, session_id: str, cwd: str = "") -> list:
    """Stop 门差集：当前脏集 − 会话基线集 − 声明清单 → 清单外变更列表。

    skip（返回 []）：无基线（非git/未记录）、无编辑、或 git 不可用。
    """
    baseline = entry.get("git_baseline")
    if not isinstance(baseline, list) or not baseline:
        return []
    if not counted_edit_items(entry):
        return []
    current = git_dirty_set(cwd)
    if current is None:
        return []
    base = {_norm_path(p) for p in baseline}
    declared = declared_impact(session_id, cwd)
    extra = current - base - declared
    if extra:
        # 宽容匹配：清单声明为目录（以/结尾）或为某额外路径的后缀/前缀时不算清单外
        relaxed = set()
        for cur in extra:
            for dec in declared:
                if dec.endswith("/") and cur.startswith(dec):
                    relaxed.add(cur)
                elif cur.endswith(dec) or dec.endswith(cur):
                    relaxed.add(cur)
        extra -= relaxed
    return sorted(extra)
