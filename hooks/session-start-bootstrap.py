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
from graph_freshness import ensure_both, format_status, format_ui_banner, load_cfg, resolve_cwd  # noqa: E402

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


def load_p0_gate() -> str | None:
    """读取门控 SSOT 的 P0 分类门段。"""
    from gate_reader import load_gate

    return load_gate("p0")


def main():
    try:
        # 读取 stdin（显式 UTF-8：Claude Code 传入 UTF-8 JSON，Windows 默认 cp936 会乱码）
        try:
            raw = sys.stdin.buffer.read().decode("utf-8", errors="replace") if hasattr(sys.stdin, "buffer") else sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        cwd = resolve_cwd(data)

        # 按当前模型同步 autoCompactWindow（封顶，不超出模型最大上下文）
        try:
            sync_result = sync_settings_compact_window(write=True)
        except Exception as sync_err:
            sync_result = {"updated": False, "error": str(sync_err)}
            print(f"session-start-bootstrap: compact window sync failed: {sync_err}", file=sys.stderr)

        # 检测包管理器
        package_manager = detect_package_manager(cwd)

        session_id = str(data.get("session_id") or data.get("conversation_id") or "")
        cfg = load_cfg()
        graph_result = ensure_both(
            cwd,
            int(cfg.get("session_ensure_timeout_sec", 120)),
            session_id=session_id,
        )
        codegraph_status = format_status(graph_result) if not (
            graph_result.get("skipped") and not graph_result.get("eligible")
        ) else None

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

        p0_gate = load_p0_gate()
        if p0_gate:
            parts.append(p0_gate)

        bootstrap_info = "\n".join(parts)

        result = {
            "systemMessage": format_ui_banner(graph_result, action="ensure"),
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
