#!/usr/bin/env python3
"""
SessionStart Hook: Session Bootstrap
会话启动时加载上下文、检测包管理器

exit 0 = 正常结束
"""
import json
import sys
import io
import os
import subprocess

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


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
            except Exception:
                pass
    
    return context


def main():
    try:
        # 读取 stdin
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        cwd = data.get("cwd", os.getcwd())
        
        # 检测包管理器
        package_manager = detect_package_manager(cwd)
        
        # 加载上下文
        context = load_previous_context(cwd)
        
        # 输出启动信息
        if package_manager != "unknown":
            bootstrap_info = (
                f"🚀 Session Bootstrap:\n"
                f"  • 检测到包管理器: {package_manager}\n"
                f"  • 项目路径: {cwd}"
            )
            
            if context:
                bootstrap_info += f"\n  • 已加载上下文: {list(context.keys())}"
            
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
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
