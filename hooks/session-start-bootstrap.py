#!/usr/bin/env python3
"""
SessionStart Hook: Session Bootstrap
会话启动时加载上下文、检测包管理器

exit 0 = 正常结束
"""
# source: obra/superpowers
import json
import sys
import io
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "_lib"))
from context_thresholds import sync_settings_compact_window  # noqa: E402

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception as e:
    print(f"⚠️ {e}", file=sys.stderr)


def detect_package_manager(cwd: str) -> str:
    """检测项目使用的包管理器"""
    # 检查锁文件
    lock_files = {
        "package-lock.json": "npm",
        "yarn.lock": "yarn",
        "pnpm-lock.yaml": "pnpm",
        "bun.lockb": "bun",
    }
    
    for lock_file, pm in lock_files.items():
        if os.path.exists(os.path.join(cwd, lock_file)):
            return pm
    
    # 检查 Python 项目
    if os.path.exists(os.path.join(cwd, "pyproject.toml")):
        return "pip"
    if os.path.exists(os.path.join(cwd, "requirements.txt")):
        return "pip"
    
    # 检查 Go 项目
    if os.path.exists(os.path.join(cwd, "go.mod")):
        return "go"
    
    return "unknown"


def load_previous_context(cwd: str) -> dict:
    """加载之前的上下文信息"""
    context = {}
    
    # 尝试读取项目特定的上下文文件
    context_files = [
        ".claude/context.json",
        ".claude/session-context.json",
        "CLAUDE.md",
    ]
    
    for context_file in context_files:
        file_path = os.path.join(cwd, context_file)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    if context_file.endswith(".json"):
                        context.update(json.load(f))
                    else:
                        context["project_notes"] = f.read()[:1000]
                break
            except Exception as e:
                print(f"⚠️ {e}", file=sys.stderr)
    
    return context


def detect_codegraph(cwd: str) -> str | None:
    """检测 codegraph 索引状态"""
    is_git = os.path.exists(os.path.join(cwd, ".git"))
    has_codegraph = os.path.exists(os.path.join(cwd, ".codegraph"))

    if not is_git:
        return None  # 非 git 项目，跳过

    if has_codegraph:
        return (
            "✅ CodeGraph 已索引 — 优先使用 codegraph_search/explore/impact "
            "代替 grep 探索代码（47% token 减少, 58% 调用减少）"
        )
    else:
        # 有 .git 但没有 .codegraph → 提示初始化
        file_count = sum(1 for _ in os.walk(cwd)) if os.path.isdir(cwd) else 0
        return (
            f"⚠️ 项目有 .git 但未初始化 CodeGraph 索引。\n"
            f"   → 运行 codegraph init -i 可节省 ~47% token 和 ~58% 工具调用\n"
            f"   → 索引后自动同步，无需手动维护"
        )


def main():
    try:
        # 读取 stdin
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        cwd = data.get("cwd", os.getcwd())

        # 按当前模型同步 autoCompactWindow（封顶，不超出模型最大上下文）
        try:
            sync_result = sync_settings_compact_window(write=True)
        except Exception as sync_err:
            sync_result = {"updated": False, "error": str(sync_err)}
            print(f"session-start-bootstrap: compact window sync failed: {sync_err}", file=sys.stderr)

        # 检测包管理器
        package_manager = detect_package_manager(cwd)

        # 检测 codegraph 索引
        codegraph_status = detect_codegraph(cwd)

        # 加载上下文
        context = load_previous_context(cwd)

        # 输出启动信息
        parts = [f"🚀 Session Bootstrap:", f"  • 项目路径: {cwd}"]
        if sync_result.get("updated"):
            parts.append(
                f"  • 上下文窗口已同步: autoCompactWindow={sync_result.get('resolved_window')} "
                f"({sync_result.get('model')})"
            )
        if package_manager != "unknown":
            parts.append(f"  • 包管理器: {package_manager}")
        if codegraph_status:
            parts.append(f"  • {codegraph_status}")
        if context:
            parts.append(f"  • 已加载上下文: {list(context.keys())}")

        bootstrap_info = "\n".join(parts)

        result = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": bootstrap_info,
            }
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    except SystemExit:
        raise
    except Exception as e:
        print(f"⚠️ {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
