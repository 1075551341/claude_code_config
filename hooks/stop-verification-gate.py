#!/usr/bin/env python3
"""
Stop Hook: 完成验证硬门（v11.3.3）— 吸收 stop-quality-gate 全部职责并升级为硬阻断。
本会话有代码编辑时强制核查：①变更范围轻量自动检查 ②测试/验证命令证据 ③预期符合性（scope）
④≥3 文件 eng-reviewer 委派 ⑤工作树交叉核查 ⑥非功能变更回归证据 ⑦会话终验 R20（含纯文档）。
缺任一 → exit 2 回灌（阻止停止）；上限 max_blocks 次后放行并标 DONE_WITH_CONCERNS。
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
    "require_reviewer_min_files": 3,
    "require_requirements_replay": True,
    "doc_only_extensions": [".md", ".txt", ".rst", ".markdown"],
}

CODE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte",
    ".go", ".rs", ".java", ".kt", ".c", ".cpp", ".h", ".hpp", ".cs", ".rb",
    ".php", ".swift", ".scala", ".dart", ".sh", ".ps1", ".sql",
}


def load_config() -> dict:
    cfg = dict(DEFAULT_CFG)
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f).get("verification_gate", {})
            for key in cfg:
                if key in user_cfg:
                    cfg[key] = user_cfg[key]
    except (OSError, json.JSONDecodeError) as e:
        print(f"stop-verification-gate: config read failed: {e}", file=sys.stderr)
    return cfg


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


def has_requirements_replay(transcript_path: str) -> bool:
    """R20：最后一条 assistant 须含会话终验标记 + 遗漏 + 错改 + 漏改 + 原功能。"""
    text = last_assistant_message(transcript_path)
    if not text:
        return False
    has_header = ("会话终验" in text) or ("R20" in text)
    return (
        has_header
        and ("遗漏" in text)
        and ("错改" in text)
        and ("漏改" in text)
        and ("原功能" in text)
    )


def unique_code_files(edited_files: list, doc_exts: list) -> list:
    seen = {}
    for item in edited_files:
        path = item.get("path", "")
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


def crg_refresh_and_flag(roots: list, timeout_sec: int) -> tuple:
    has_graph = False
    warnings = []
    for root in roots:
        probe = root
        found = ""
        for _ in range(6):
            if os.path.isdir(os.path.join(probe, ".code-review-graph")):
                found = probe
                break
            parent = os.path.dirname(probe)
            if parent == probe:
                break
            probe = parent
        if not found:
            continue
        has_graph = True
        if shutil.which("code-review-graph"):
            try:
                proc = subprocess.run(
                    ["code-review-graph", "update"], capture_output=True, text=True,
                    timeout=timeout_sec, cwd=found,
                )
                if proc.returncode != 0:
                    warnings.append(f"CRG update 非零退出（{found}）: {(proc.stderr or proc.stdout).strip()[:300]}")
            except subprocess.TimeoutExpired:
                warnings.append(f"CRG update 超时（{timeout_sec}s），图可能过时")
            except OSError as e:
                warnings.append(f"CRG update 执行失败: {e}")
    return has_graph, warnings


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
    lines.append("必须执行（全部完成后再次结束）：")
    if not only_r20:
        lines.append("  ① 实际运行测试/lint/构建/功能核验命令，贴出输出证据（禁止\"应该没问题\"）")
        if crg:
            lines.append("  ② 项目已建 code-review-graph：调用 detect_changes_tool 检查 test-gap 与高风险函数")
        if any("eng-reviewer" in r for r in reasons):
            lines.append("  ③ 委派 eng-reviewer（只读审查本轮 diff）获取 PASS/NEEDS-CHANGES 结论")
        if any("预期符合性" in r for r in reasons):
            lines.append("  ④ 对照 plan/spec 的 tasks 清单逐项确认：无静默缩范围、无遗漏需求")
    if any("R20" in r or "会话终验" in r for r in reasons):
        lines.append("  ⑤ 会话终验（R20）：按原始要求逐条回放，输出满足/遗漏/错改/漏改/原功能（禁止把实现重做一遍；漏改含文档/备注与文件/配置一致；非功能变更必须证明原功能保持）")
    lines.append("跳过验证的完成声明视为无效（R1，先证据后断言）。")
    lines.append(f"（第 {blocks}/{max_blocks} 次阻断；达上限后放行并标 DONE_WITH_CONCERNS；确需跳过请用户显式说「跳过验证」）")
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

    if cfg["enabled"]:
        state = load_state()
        entry = state.get(session_id) or {}
        edited = entry.get("edited_files", [])
        code_files = unique_code_files(edited, cfg["doc_only_extensions"])

        # 工作树交叉核查：抓 MCP / Shell 重定向等绕过 hook 追踪的写入
        worktree_cwd = entry.get("cwd") or cwd
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

            if user_skipped:
                print("⚠️ 用户显式跳过验证 — 本次放行，完成声明按 DONE_WITH_CONCERNS 处理", file=sys.stderr)
            elif blocks >= int(cfg["max_blocks"]):
                print(
                    f"⚠️ 验证硬门已达上限（{blocks} 次）— 放行并标 DONE_WITH_CONCERNS："
                    "验证证据仍不完整，请用户人工复核",
                    file=sys.stderr,
                )
            else:
                project_cwd = entry.get("cwd") or cwd
                crg = False
                crg_warnings = []
                check_warnings = []
                reasons = []
                if code_files or untracked:
                    # 未追踪变更也纳入 lint/类型检查范围，否则 MCP 写入的文件永远查不到
                    checkable = code_files + [{"path": p, "ts": 0} for p in untracked]
                    roots = find_project_roots(checkable, project_cwd)
                    crg, crg_warnings = crg_refresh_and_flag(roots, min(15, int(cfg["auto_check_timeout_sec"])))
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
                    total_changed = len({f["path"] for f in code_files} | set(untracked))
                    if total_changed >= int(cfg["require_reviewer_min_files"]):
                        reviewed = any(r.get("ts", 0) >= last_edit_ts - 1 for r in entry.get("reviews", []))
                        if not reviewed:
                            reasons.append(
                                f"会话内 {total_changed} 个代码文件变更（≥{cfg['require_reviewer_min_files']}）"
                                "但无 eng-reviewer 审查委派记录"
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

                if cfg.get("require_requirements_replay", True) and not has_requirements_replay(transcript_path):
                    reasons.append(
                        "R20 会话终验：未按原始要求逐条回放输出满足/遗漏/错改/漏改/原功能"
                        "（禁止把实现重做一遍；漏改含文档/备注与文件/配置一致；"
                        "非功能变更必须证明原功能保持；验证命令不能代替本项）"
                    )

                if reasons:
                    entry["blocks"] = blocks + 1
                    entry["scope_nudged"] = True
                    entry["ts"] = time.time()
                    state[session_id] = entry
                    save_state(state)
                    for w in crg_warnings + check_warnings:
                        print(f"⚠️ {w}", file=sys.stderr)
                    print(build_block_message(reasons, crg, blocks + 1, int(cfg["max_blocks"])), file=sys.stderr)
                    sys.exit(2)

                mark_issues_resolved(session_id)

    issues = (
        check_schema_drift(code_files)
        + check_security_anchor(code_files)
        + check_plan_reminder()
        + check_bare_except()
    )
    for issue in issues:
        print(issue, file=sys.stderr)
    if any("🚫" in i for i in issues):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
