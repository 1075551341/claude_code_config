#!/usr/bin/env python3
"""
Stop Hook: 完成验证硬门（v11.4.12）— 吸收 stop-quality-gate 全部职责并升级为硬阻断。
有代码/配置改动即双审：eng-reviewer 一次找齐；修改走 change-implementer 按完整清单集中改。每轮独立审查必须全新开审（禁止 resume）。干净 PASS 即停；禁止边审边改耗轮次（日常最多 3 轮（单任务覆盖须用户显式声明））。apply_review_verdict 同步 PASS（须已有 reviews；PASS 夹带须同步视为不干净）。
计划未批准 / 仅计划制品跳过完成门。本会话有代码编辑时强制核查：①变更范围轻量自动检查 ②测试/验证命令证据 ③预期符合性（scope）
④有代码文件即 eng-reviewer 委派 ⑤工作树交叉核查 ⑥非功能变更回归证据 ⑦会话终验 R20（反空模板，含纯文档）。
R20 检测 SSOT：hooks/_lib/r20_replay.py。缺任一 → exit 2 回灌；上限 max_blocks 次后放行并标 DONE_WITH_CONCERNS。
另保留 R16 裸 except 扫描（exit 1）与活跃 plan 提醒（仅提示）。

v10.17 新增两项拦截，均针对「改完影响其他功能」：
- ⑤ `git status --porcelain` 与 edited_files 交叉核查：MCP / Shell 重定向写入此前完全绕过
  追踪器，edited_files 为空时 Stop 门直接放行 = 回归漏网。只统计会话开始后 mtime 变化的
  文件，避免仓库里会话前就存在的未提交改动造成误阻断。
- ⑥ 非功能变更回归证据：变更集不含测试文件且仓库有测试设施时，要求存在测试运行记录
  （lint/类型检查不足以证明原功能未变）。

配置 SSOT：~/.claude/config/quality_gates.json → verification_gate。
"""
import glob as globmod
import json
import os
import re
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

from issue_state import claude_home  # noqa: E402  与追踪器共用同一 CLAUDE_HOME 解析
from r20_replay import (  # noqa: E402
    apply_review_verdict,
    counted_edit_items,
    dual_pass_phase,
    impact_diff_check,
    is_awaiting_plan,
    is_plan_artifact,
    replay_ok,
    review_verdict_ok,
)
from crg_track import has_crg_since  # noqa: E402
from graph_freshness import (  # noqa: E402
    ensure_both,
    load_cfg as load_graph_cfg,
    refresh_incremental,
    resolve_cwd,
    run_sync_ps1_if_verified,
    take_ui_slot,
)

CLAUDE_HOME = str(claude_home())
STATE_DIR = os.path.join(CLAUDE_HOME, ".state")
STATE_FILE = os.path.join(STATE_DIR, "verification-gate.json")
CONFIG_FILE = os.path.join(CLAUDE_HOME, "config", "quality_gates.json")
STALE_SECONDS = 7 * 24 * 3600

DEFAULT_CFG = {
    "enabled": True,
    "max_blocks": 3,
    "auto_check_timeout_sec": 25,
    "skip_keywords": ["跳过验证", "不用验证", "skip verify"],
    "require_reviewer_min_files": 1,
    "require_requirements_replay": True,
    "doc_only_extensions": [".md", ".txt", ".rst", ".markdown"],
    "requirement_fingerprint": True,
    "require_review_verdict": True,
    "verdict_trigger_min_blocks": 2,
    "require_crg_when_graph": True,
    "review_max_rounds": 3,
    "require_dual_graph_before_review": True,
    "parallel_review": {
        "enabled": True,
        "when_all": ["reviewers_readonly", "disjoint_concerns", "model_inherit_only"],
        "forbid_multiplier_models": True,
        "require_model": "inherit",
        "max_parallel": 3,
    },
}

CODE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte",
    ".go", ".rs", ".java", ".kt", ".c", ".cpp", ".h", ".hpp", ".cs", ".rb",
    ".php", ".swift", ".scala", ".dart", ".sh", ".ps1", ".sql",
}


def load_config() -> dict:
    cfg = json.loads(json.dumps(DEFAULT_CFG))
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f).get("verification_gate", {})
            for key in list(cfg):
                if key not in user_cfg:
                    continue
                if isinstance(cfg[key], dict) and isinstance(user_cfg[key], dict):
                    merged = dict(cfg[key])
                    merged.update(user_cfg[key])
                    cfg[key] = merged
                else:
                    cfg[key] = user_cfg[key]
    except (OSError, json.JSONDecodeError) as e:
        print(f"stop-verification-gate: config read failed: {e}", file=sys.stderr)
    return cfg


def load_impact_gate() -> dict:
    """方案A 灰度开关（design-v2）：quality_gates.impact_manifest_gate。"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("quality_gates", {}).get("impact_manifest_gate", {})
    except (OSError, json.JSONDecodeError) as e:
        print(f"stop-verification-gate: gate config read failed: {e}", file=sys.stderr)
    return {}


def load_state() -> dict:
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"stop-verification-gate: state read failed: {e}", file=sys.stderr)
    return {}


def save_state(state: dict) -> None:
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        now = time.time()
        state = {k: v for k, v in state.items() if now - v.get("ts", 0) < STALE_SECONDS}
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)
    except OSError as e:
        print(f"stop-verification-gate: state write failed: {e}", file=sys.stderr)


def last_user_message(transcript_path: str) -> str:
    if not transcript_path or not os.path.exists(transcript_path):
        return ""
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"stop-verification-gate: transcript read failed: {e}", file=sys.stderr)
        return ""
    for line in reversed(lines[-80:]):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") != "user":
            continue
        content = (obj.get("message") or {}).get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
            return "\n".join(p for p in parts if p)
    return ""


def last_assistant_message(transcript_path: str) -> str:
    """读取 transcript 中最后一条 assistant 文本（用于 R20 会话终验标记检测）。"""
    if not transcript_path or not os.path.exists(transcript_path):
        return ""
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"stop-verification-gate: transcript read failed: {e}", file=sys.stderr)
        return ""
    for line in reversed(lines[-120:]):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") != "assistant":
            continue
        content = (obj.get("message") or {}).get("content")
        text = ""
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            parts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
            text = "\n".join(p for p in parts if p)
        if text.strip():
            return text
    return ""


def has_requirements_replay(transcript_path: str, requirements: dict | None = None) -> bool:
    """R20：最后一条 assistant 须为合格终验（反空模板；v11.4 可选需求指纹实质比对）。"""
    text = last_assistant_message(transcript_path)
    return replay_ok(text, requirements)


def unique_code_files(edited_files: list, doc_exts: list) -> list:
    seen = {}
    for item in edited_files:
        path = item.get("path", "")
        if is_plan_artifact(path):
            continue
        ext = os.path.splitext(path)[1].lower()
        if ext in doc_exts or ext not in CODE_EXTENSIONS:
            continue
        prev = seen.get(path)
        if prev is None or item.get("ts", 0) > prev.get("ts", 0):
            seen[path] = item
    return list(seen.values())


def git_changed_code_files(cwd: str, doc_exts: list, timeout_sec: int) -> tuple:
    """`git status --porcelain` 得到的工作树实际变更代码文件（绝对路径）。

    返回 (files, warning)。非 git 仓库/git 不可用时返回空列表 + 警告，不阻断。
    """
    if not cwd or not shutil.which("git"):
        return [], ""
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            capture_output=True, text=True, timeout=timeout_sec, cwd=cwd,
        )
    except subprocess.TimeoutExpired:
        return [], f"git status 超时（{timeout_sec}s），跳过工作树交叉核查"
    except OSError as e:
        return [], f"git status 执行失败: {e}"
    if proc.returncode != 0:
        return [], ""

    root = cwd
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=timeout_sec, cwd=cwd,
        )
        if top.returncode == 0 and top.stdout.strip():
            root = top.stdout.strip()
    except (subprocess.TimeoutExpired, OSError) as e:
        # 拿不到仓库根就退回 cwd 拼路径；不影响判定，但按 R16 必须显式报出
        print(f"stop-verification-gate: git rev-parse failed, fallback to cwd: {e}", file=sys.stderr)

    files = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        rel = line[3:].strip().strip('"')
        # 重命名/复制形如 "old -> new"，取目标路径
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1].strip()
        if rel.endswith("/"):
            continue
        ext = os.path.splitext(rel)[1].lower()
        if ext in doc_exts or ext not in CODE_EXTENSIONS:
            continue
        files.append(os.path.normpath(os.path.join(root, rel)))
    return files, ""


def session_start_ts(entry: dict, transcript_path: str = "") -> float:
    """本会话最早一次被 hook 记录的事件时间；用于排除会话前就存在的工作树脏改动。

    追踪器一次都没被触发时（例如全程只用 MCP/Shell 写文件），entry 为空，此时退回
    transcript 文件的创建时间近似会话起点 —— 否则交叉核查会因为拿不到起点而整个跳过，
    正好在最需要它的场景失效。两者都拿不到才返回 0（保守跳过，不误阻断）。
    """
    ts = entry.get("started_ts")
    if ts:
        return float(ts)
    candidates = [
        item.get("ts", 0)
        for key in ("edited_files", "verify_commands", "reviews")
        for item in entry.get(key, [])
    ]
    candidates = [c for c in candidates if c]
    if candidates:
        return min(candidates)
    if transcript_path and os.path.exists(transcript_path):
        try:
            return os.path.getctime(transcript_path)
        except OSError as e:
            print(f"stop-verification-gate: transcript ctime failed: {e}", file=sys.stderr)
    return 0.0


def untracked_by_hook(git_files: list, entry: dict, transcript_path: str = "") -> list:
    """工作树里有、但本会话 hook 未追踪到的代码变更。

    覆盖 MCP 写工具与 Shell 重定向两条绕过验证追踪链的通道：edited_files 为空时
    Stop 门原本直接放行，等于回归漏网。
    只统计**会话开始之后被修改**的文件（按 mtime），否则仓库里会话前就存在的未提交
    改动会导致每次 Stop 都误阻断。
    """
    start = session_start_ts(entry, transcript_path)
    if not start:
        return []
    tracked = {
        os.path.normpath(item.get("path", "")).lower()
        for item in entry.get("edited_files", [])
    }
    out = []
    for path in git_files:
        if path.lower() in tracked:
            continue
        try:
            if os.path.getmtime(path) < start - 5:
                continue
        except OSError:
            continue
        out.append(path)
    return out


def run_auto_checks(code_files: list, cwd: str, timeout_sec: int) -> tuple:
    failures = []
    warnings = []
    py_files = [f["path"] for f in code_files if f["path"].lower().endswith(".py") and os.path.exists(f["path"])]
    ts_files = [
        f["path"] for f in code_files
        if os.path.splitext(f["path"])[1].lower() in (".ts", ".tsx", ".js", ".jsx", ".mts", ".cts")
        and os.path.exists(f["path"])
    ]

    if py_files and shutil.which("ruff"):
        try:
            proc = subprocess.run(
                ["ruff", "check", "--no-cache"] + py_files,
                capture_output=True, text=True, timeout=timeout_sec, cwd=cwd or None,
            )
            if proc.returncode != 0:
                out = (proc.stdout + proc.stderr).strip()[:1500]
                failures.append(f"ruff check 失败（{len(py_files)} 个变更文件）:\n{out}")
        except subprocess.TimeoutExpired:
            warnings.append(f"ruff check 超时（{timeout_sec}s），降级为提醒")
        except OSError as e:
            warnings.append(f"ruff 执行失败: {e}")

    if ts_files and cwd:
        tsc_bin = os.path.join(cwd, "node_modules", ".bin", "tsc")
        if not os.path.exists(tsc_bin) and shutil.which("tsc"):
            tsc_bin = "tsc"
        if os.path.exists(os.path.join(cwd, "tsconfig.json")) and tsc_bin:
            try:
                proc = subprocess.run(
                    [tsc_bin, "--noEmit"], capture_output=True, text=True,
                    timeout=timeout_sec, cwd=cwd,
                )
                if proc.returncode != 0:
                    out = (proc.stdout + proc.stderr).strip()[:1500]
                    failures.append(f"tsc --noEmit 失败:\n{out}")
            except subprocess.TimeoutExpired:
                warnings.append(f"tsc --noEmit 超时（{timeout_sec}s），降级为提醒")
            except OSError as e:
                warnings.append(f"tsc 执行失败: {e}")
    return failures, warnings


def find_project_roots(code_files: list, cwd: str) -> list:
    roots = set()
    if cwd:
        roots.add(cwd)
    for item in code_files:
        path = item.get("path", "")
        if path:
            roots.add(os.path.dirname(os.path.abspath(path)))
    return sorted(roots)


def crg_refresh_and_flag(roots: list, timeout_sec: int, session_id: str = "") -> tuple:
    """Stop 增量刷新双图（codegraph sync + CRG update）。返回 (has_crg, warnings, aggregate)。"""
    gcfg = load_graph_cfg()
    tmo = min(int(timeout_sec), int(gcfg.get("stop_refresh_timeout_sec", 30)))
    return refresh_incremental(roots, tmo, session_id=session_id)


def ensure_dual_graph_before_review(roots: list, session_id: str = "") -> str:
    """独立开审前再 ensure 双图（非 SessionStart 那一次）。失败返回阻断文案。"""
    gcfg = load_graph_cfg()
    tmo = min(45, int(gcfg.get("pretool_ensure_timeout_sec", 90)))
    missing = []
    for root in roots:
        result = ensure_both(root, tmo, session_id=session_id)
        if not result.get("eligible"):
            continue
        if result.get("blocked") or not result.get("ok"):
            missing.append(os.path.basename(os.path.normpath(root)) or root)
            continue
        if gcfg.get("require_both_graphs", True) and not (
            result.get("codegraph") and result.get("crg")
        ):
            missing.append(os.path.basename(os.path.normpath(root)) or root)
    if not missing:
        return ""
    shown = ", ".join(missing[:6])
    more = f" 等 {len(missing)} 个" if len(missing) > 6 else ""
    return (
        "独立审前双图 ensure 未就绪（codegraph + code-review-graph）："
        f"{shown}{more}。禁止开审；先执行 codegraph init|sync 与 "
        "code-review-graph build|update"
    )


TEST_FILE_MARKERS = ("test_", "_test.", ".test.", ".spec.", "conftest.py")
TEST_DIR_MARKERS = (os.sep + "tests" + os.sep, os.sep + "test" + os.sep, os.sep + "__tests__" + os.sep)
TEST_COMMAND_PATTERNS = (
    "pytest", "vitest", "jest", "npm test", "pnpm test", "yarn test",
    "npm run test", "cargo test", "go test", "unittest", "test-cursor-guard-hooks",
    "hooks/tests", "run_tests",
)
TEST_INFRA_MARKERS = ("tests", "test", "__tests__", "pytest.ini", "tox.ini", "conftest.py", "vitest.config.ts", "jest.config.js")


def is_test_path(path: str) -> bool:
    lowered = os.path.normpath(path).lower()
    if any(m in lowered for m in TEST_DIR_MARKERS):
        return True
    return any(m in os.path.basename(lowered) for m in TEST_FILE_MARKERS)


def repo_has_test_infra(roots: list) -> bool:
    """仓库是否存在可运行的测试设施；没有测试的仓库不应被要求「跑测试」。"""
    for root in roots:
        probe = root
        for _ in range(6):
            if any(os.path.exists(os.path.join(probe, m)) for m in TEST_INFRA_MARKERS):
                return True
            parent = os.path.dirname(probe)
            if parent == probe:
                break
            probe = parent
    return False


def has_test_evidence(entry: dict, since_ts: float) -> bool:
    for item in entry.get("verify_commands", []):
        if item.get("ts", 0) < since_ts - 1:
            continue
        cmd = str(item.get("command", "")).lower()
        if any(pat in cmd for pat in TEST_COMMAND_PATTERNS):
            return True
    return False


def plan_artifact_active(cwd: str) -> bool:
    plan_cache = os.path.expanduser("~/.claude/plan_cache.json")
    try:
        if os.path.exists(plan_cache):
            with open(plan_cache, "r", encoding="utf-8") as f:
                if json.load(f):
                    return True
    except (OSError, json.JSONDecodeError) as e:
        print(f"stop-verification-gate: plan_cache read failed: {e}", file=sys.stderr)
    if cwd:
        for root, dirs, _files in os.walk(os.path.join(cwd, "openspec", "changes")):
            if "archive" in root:
                continue
            if "tasks.md" in _files:
                return True
            if len(dirs) > 20:
                break
        if os.path.isdir(os.path.join(cwd, ".planning", "phases")):
            return True
    return False


def build_block_message(reasons: list, crg: bool, blocks: int, max_blocks: int) -> str:
    only_r20 = reasons and all(("R20" in r or "会话终验" in r) for r in reasons)
    lines = [
        "【门控 · 完成验证硬门（R1/R20）— 已阻止停止】",
        "本会话存在修改，但验证证据不完整：" if not only_r20 else "本会话有编辑，但未完成会话终验（R20）：",
    ]
    lines.extend(f"  {i}. {r}" for i, r in enumerate(reasons, 1))
    if not only_r20:
        lines.append("补齐观察输出（测试/lint/构建）；有 CRG 则调 get_impact_radius。")
        if any("eng-reviewer" in r for r in reasons):
            lines.append("委派 eng-reviewer 只读审，回贴 PASS 或 NEEDS-CHANGES。")
        if any("预期符合性" in r for r in reasons):
            lines.append("对照 plan/spec tasks，禁止静默缩范围。")
    if any("R20" in r or "会话终验" in r for r in reasons):
        lines.append("输出短 R20：满足/遗漏/错改/漏改/原功能/影响范围（漏改含文档；原功能含证据）。")
    lines.append(f"（第 {blocks}/{max_blocks} 次；达上限放行 DONE_WITH_CONCERNS；跳过请说「跳过验证」）")
    return "\n".join(lines)


def check_bare_except() -> list:
    issues = []
    hooks_dir = os.path.expanduser("~/.claude/hooks")
    pattern = re.compile(r"except(?:\s+[A-Za-z]\w*(?:\s*,\s*[A-Za-z]\w*)*)?\s*:\s*pass\s*(?:#.*)?$", re.MULTILINE)
    for pyfile in globmod.glob(os.path.join(hooks_dir, "*.py")):
        basename = os.path.basename(pyfile)
        if pyfile.endswith("__init__.py") or "_archive" in pyfile or "_optional" in pyfile or "_deprecated" in pyfile:
            continue
        if basename == "stop-verification-gate.py":
            continue
        try:
            with open(pyfile, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            matches = pattern.findall(content)
            if matches:
                issues.append(f"🚫 R16违规 {basename}: 发现{len(matches)}处裸except:pass")
        except (OSError, UnicodeDecodeError) as e:
            issues.append(f"⚠️ 扫描{basename}失败: {e}")
    return issues


def check_plan_reminder() -> list:
    plan_cache = os.path.expanduser("~/.claude/plan_cache.json")
    try:
        if os.path.exists(plan_cache):
            with open(plan_cache, "r", encoding="utf-8") as f:
                if json.load(f):
                    return ["ℹ️ 存在活跃计划，建议在ship前执行/verify交叉验证"]
    except (OSError, json.JSONDecodeError) as e:
        return [f"⚠️ plan_cache读取失败: {e}"]
    return []


def check_schema_drift(code_files: list) -> list:
    """启发式：ORM/model 文件变更但无 migration 文件变更 → 警告"""
    orm_patterns = ("model", "orm", "schema", "entity", "migration", "migrate")
    has_orm = any(
        any(p in f.get("path", "").lower() for p in orm_patterns if p not in ("migration", "migrate"))
        for f in code_files
    )
    has_migration = any(
        "migration" in f.get("path", "").lower() or "migrate" in f.get("path", "").lower()
        for f in code_files
    )
    if has_orm and not has_migration:
        return ["⚠️ Schema Drift: ORM/model 文件变更但未检测到 migration 文件变更，请确认是否需要生成 migration"]
    return []


def check_security_anchor(code_files: list) -> list:
    """启发式：auth 相关文件变更 → 提醒绑定威胁模型"""
    auth_patterns = ("auth", "login", "session", "permission", "token", "password", "credential")
    has_auth = any(
        any(p in f.get("path", "").lower() for p in auth_patterns)
        for f in code_files
    )
    if has_auth:
        return ["⚠️ Security Anchor: 检测到 auth/安全相关文件变更，请确认验证逻辑已绑定威胁模型（STRIDE/OWASP）"]
    return []


def _emit_graph_ui(session_id: str, aggregate: dict | None) -> None:
    """Stop 把双图刷新成败写到 systemMessage（会话界面，非 stderr 日志）。"""
    if not aggregate:
        return
    banner = str(aggregate.get("ui") or "").strip()
    if not banner:
        return
    show_fail = bool(aggregate.get("blocked") or not aggregate.get("ok"))
    if not show_fail and not take_ui_slot(session_id, "refresh"):
        return
    try:
        sys.stdout.write(json.dumps({"systemMessage": banner}, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    except OSError as exc:
        print(f"stop-verification-gate: ui write failed: {exc}", file=sys.stderr)


def mark_issues_resolved(session_id: str) -> None:
    """验证全部通过 → 把本会话触碰过的问题指纹标记已解决（issue-tracker 轻提示分支）。

    v10.16 只写入 resolved=False 却无人置 true，轻提示分支是死代码；此处补上唯一写点。
    """
    try:
        from issue_state import mark_session_resolved

        marked = mark_session_resolved(session_id)
        if marked:
            print(f"✅ 验证通过：已标记 {marked} 个问题指纹为已解决", file=sys.stderr)
    except Exception as e:
        print(f"stop-verification-gate: mark resolved failed: {e}", file=sys.stderr)


def main():
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        print(f"stop-verification-gate: stdin parse failed: {e}", file=sys.stderr)
        data = {}

    cfg = load_config()
    session_id = str(data.get("session_id") or data.get("conversation_id") or "unknown")
    cwd = str(data.get("cwd") or "")
    transcript_path = str(data.get("transcript_path") or "")
    code_files = []
    graph_refresh = None

    if cfg["enabled"]:
        state = load_state()
        entry = state.get(session_id) or {}
        awaiting = is_awaiting_plan(entry, data)
        if awaiting:
            print("stop-verification-gate: 计划未批准，跳过完成门（仅刷新图谱）", file=sys.stderr)
        edited = [] if awaiting else counted_edit_items(entry)
        code_files = unique_code_files(edited, cfg["doc_only_extensions"])

        # 工作树交叉核查：抓 MCP / Shell 重定向等绕过 hook 追踪的写入
        worktree_cwd = entry.get("cwd") or cwd
        if awaiting:
            git_files, git_warn = [], ""
            untracked = []
        else:
            git_files, git_warn = git_changed_code_files(
                worktree_cwd, cfg["doc_only_extensions"], min(10, int(cfg["auto_check_timeout_sec"]))
            )
            if git_warn:
                print(f"⚠️ {git_warn}", file=sys.stderr)
            untracked = untracked_by_hook(git_files, entry, transcript_path)

        if edited and not code_files and not untracked:
            print("ℹ️ 本会话仅文档类编辑：请重读修改内容确认无误后再声称完成", file=sys.stderr)

        has_any_edit = bool(edited) or bool(untracked)
        if has_any_edit:
            blocks = int(entry.get("blocks", 0))
            skip_msg = last_user_message(transcript_path).lower()
            user_skipped = any(k.lower() in skip_msg for k in cfg["skip_keywords"])
            project_cwd = entry.get("cwd") or cwd
            checkable = code_files + [{"path": p, "ts": 0} for p in untracked]
            refresh_roots = find_project_roots(checkable, project_cwd)
            if not refresh_roots and project_cwd:
                refresh_roots = [project_cwd]
            crg = False
            crg_warnings = []
            if refresh_roots:
                crg, crg_warnings, graph_refresh = crg_refresh_and_flag(
                    refresh_roots,
                    int(load_graph_cfg().get("stop_refresh_timeout_sec", 30)),
                    session_id=session_id,
                )
                for w in crg_warnings:
                    print(f"⚠️ {w}", file=sys.stderr)

            if user_skipped:
                print("⚠️ 用户显式跳过验证 — 本次放行，完成声明按 DONE_WITH_CONCERNS 处理", file=sys.stderr)
            elif blocks >= int(cfg["max_blocks"]):
                print(
                    f"⚠️ 验证硬门已达上限（{blocks} 次）— 放行并标 DONE_WITH_CONCERNS："
                    "验证证据仍不完整，请用户人工复核",
                    file=sys.stderr,
                )
            else:
                check_warnings = []
                reasons = []
                if code_files or untracked:
                    # 未追踪变更也纳入 lint/类型检查范围，否则 MCP 写入的文件永远查不到
                    roots = refresh_roots
                    failures, check_warnings = run_auto_checks(checkable, project_cwd, int(cfg["auto_check_timeout_sec"]))

                    reasons = list(failures)
                    if untracked:
                        shown = ", ".join(os.path.basename(p) for p in untracked[:8])
                        more = f" 等 {len(untracked)} 个" if len(untracked) > 8 else ""
                        reasons.append(
                            f"工作树存在 hook 未追踪的代码变更（MCP/Shell 写入）：{shown}{more}。"
                            "这些文件未进入本会话验证范围，须逐一确认影响面并纳入验证后再声称完成"
                        )
                    edit_ts = [f.get("ts", 0) for f in code_files]
                    last_edit_ts = max(edit_ts) if edit_ts else session_start_ts(entry, transcript_path)
                    verified = any(c.get("ts", 0) >= last_edit_ts - 1 for c in entry.get("verify_commands", []))
                    if not verified:
                        reasons.append("最后一次代码编辑之后未检测到任何测试/lint/构建验证命令运行记录")
                    if cfg.get("require_crg_when_graph", True) and crg and not has_crg_since(entry, last_edit_ts):
                        reasons.append(
                            "项目已建 .code-review-graph/ 但最后一次代码编辑后未调用 CRG"
                            "（get_minimal_context / get_impact_radius / detect_changes / get_review_context）"
                        )
                    total_changed = len({f["path"] for f in code_files} | set(untracked))
                    verdict_cfg_on = cfg.get("require_review_verdict", True)
                    last_msg = last_assistant_message(transcript_path)
                    verdict_ok = review_verdict_ok(last_msg) if verdict_cfg_on else True
                    if apply_review_verdict(entry, last_msg):
                        entry["ts"] = time.time()
                        state[session_id] = entry
                        save_state(state)
                    max_rounds = int(cfg.get("review_max_rounds", 3))
                    rounds = int(entry.get("review_rounds") or 0)
                    phase = dual_pass_phase(entry, cfg)
                    if phase == "capped":
                        print(
                            f"⚠️ 修改→审查已 {rounds}/{max_rounds} 轮仍未符合预期 — 放行并标 DONE_WITH_CONCERNS",
                            file=sys.stderr,
                        )
                    elif phase == "modify":
                        reasons.append(
                            "有改动双审：审查已给出完整清单后，须派 change-implementer 按清单集中改齐并跑验证，再全新开审"
                            f"（第 {rounds + 1}/{max_rounds} 轮）。禁止 resume 上一轮审查者、禁止边审边改、禁止审查者改文件、禁止只连审不改。"
                        )
                    elif phase == "verify":
                        pass
                    elif phase == "review":
                        if cfg.get("require_dual_graph_before_review", True) and refresh_roots:
                            graph_reason = ensure_dual_graph_before_review(
                                refresh_roots, session_id
                            )
                            if graph_reason:
                                reasons.append(graph_reason)
                        pr = cfg.get("parallel_review") or {}
                        if pr.get("forbid_multiplier_models") or (
                            str((pr.get("require_model") or "")).strip().lower() == "inherit"
                        ):
                            viol = entry.get("review_model_violations") or []
                            if viol:
                                shown = ", ".join(
                                    f"{v.get('agent')}={v.get('model')}" for v in viol[:6]
                                )
                                reasons.append(
                                    "独立审查子代理须 Task model=inherit（禁止倍率档）；"
                                    f"检测到非 inherit：{shown}"
                                )
                        reasons.append(
                            "有改动双审：须委派全新 eng-reviewer 对照原始要求一次找齐全部问题（禁止 resume 上一轮审查者、禁止改文件、禁止发现一条就停审），"
                            f"回贴完整清单与 PASS 或 NEEDS-CHANGES（第 {rounds + 1}/{max_rounds} 轮；干净 PASS 即停）。"
                            " 并行审查仅当只读+维度不重叠+Task model=inherit（禁止倍率档）；否则串行。"
                        )
                    elif (
                        verdict_cfg_on
                        and not verdict_ok
                        and blocks >= int(cfg.get("verdict_trigger_min_blocks", 2))
                    ):
                        reasons.append(
                            f"验证已连续阻断 {blocks} 次仍未过：须委派 eng-reviewer 只读复核本轮 diff，"
                            "并在回复中回贴结论 PASS 或 NEEDS-CHANGES（v11.4 持续处理升档）"
                        )
                    # 非功能变更回归保持：改了代码但没碰任何测试文件时，必须有测试运行证据
                    changed_paths = [f["path"] for f in code_files] + list(untracked)
                    if (
                        changed_paths
                        and not any(is_test_path(p) for p in changed_paths)
                        and repo_has_test_infra(roots)
                        and not has_test_evidence(entry, last_edit_ts)
                    ):
                        reasons.append(
                            "非功能变更回归保持：本次变更未新增/修改任何测试文件，且最后一次编辑后无测试运行记录"
                            "（lint/类型检查不足以证明原功能未变）。请运行既有测试并贴出输出，"
                            "或说明该仓库无相关测试覆盖"
                        )
                    if plan_artifact_active(project_cwd) and not entry.get("scope_nudged"):
                        reasons.append("预期符合性：存在活跃 plan/spec 制品，须对照 tasks 清单确认全部修改满足预期要求")

                # 方案A：清单制品差集校验（v11.3.6）— 当前脏集−基线集 ⊄ 声明清单 → 错改/漏改硬证据
                igate = load_impact_gate()
                if igate.get("enabled") and entry.get("git_baseline"):
                    extras = impact_diff_check(entry, session_id, project_cwd)
                    if extras:
                        shown = ", ".join(extras[:8])
                        more = f" 等 {len(extras)} 个" if len(extras) > 8 else ""
                        reasons.append(
                            f"清单差集校验：以下文件已变更但不在 change-impact 声明清单内：{shown}{more}。"
                            "逐个确认：范围外变更=错改，回滚或向用户说明；清单漏项=补登记至 "
                            ".claude/state/impact-manifest.log（IMPACT|<session>|<路径,...>）"
                        )

                if cfg.get("require_requirements_replay", True):
                    reqs = entry.get("requirements") if cfg.get("requirement_fingerprint", True) else None
                    if not has_requirements_replay(transcript_path, reqs):
                        hint = (
                            "「满足」行未覆盖需求指纹关键词（v11.4 实质比对）"
                            if reqs
                            else "未按原始要求逐条回放输出满足/遗漏/错改/漏改/原功能/影响范围"
                        )
                        reasons.append(
                            f"R20 会话终验：{hint}"
                            "（禁止空模板：漏改须含文档或无文档影响，原功能须含证据/测试/冒烟；"
                            "验证命令不能代替本项）"
                        )

                if reasons:
                    entry["blocks"] = blocks + 1
                    entry["scope_nudged"] = True
                    entry["ts"] = time.time()
                    state[session_id] = entry
                    save_state(state)
                    for w in check_warnings:
                        print(f"⚠️ {w}", file=sys.stderr)
                    print(build_block_message(reasons, crg, blocks + 1, int(cfg["max_blocks"])), file=sys.stderr)
                    _emit_graph_ui(session_id, graph_refresh)
                    sys.exit(2)

                mark_issues_resolved(session_id)
                _ok_sync, sync_msg = run_sync_ps1_if_verified(has_edits=True, verified_green=True)
                print(f"graph_freshness: {sync_msg}", file=sys.stderr)
        else:
            refresh_root = resolve_cwd(data) or entry.get("cwd") or cwd
            if refresh_root:
                _crg, crg_warnings, graph_refresh = crg_refresh_and_flag(
                    [refresh_root],
                    int(load_graph_cfg().get("stop_refresh_timeout_sec", 30)),
                    session_id=session_id,
                )
                for w in crg_warnings:
                    print(f"⚠️ {w}", file=sys.stderr)

    issues = (
        check_schema_drift(code_files)
        + check_security_anchor(code_files)
        + check_plan_reminder()
        + check_bare_except()
    )
    for issue in issues:
        print(issue, file=sys.stderr)
    _emit_graph_ui(session_id, graph_refresh if cfg["enabled"] else None)
    if any("🚫" in i for i in issues):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
