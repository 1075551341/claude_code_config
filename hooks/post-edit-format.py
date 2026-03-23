#!/usr/bin/env python3
"""
PostToolUse Hook: 自动代码格式化
文件编辑/写入后自动运行格式化工具
支持：TypeScript/JavaScript (Prettier)、Python (Black/Ruff)
"""
import json
import sys
import subprocess
import os

def run(cmd, cwd=None):
    """运行命令，静默失败"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=30, cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception:
        return False, "", ""

def find_project_root(file_path):
    """向上查找项目根目录（包含 package.json 或 pyproject.toml）"""
    directory = os.path.dirname(os.path.abspath(file_path))
    for _ in range(10):
        if os.path.exists(os.path.join(directory, "package.json")):
            return directory, "node"
        if os.path.exists(os.path.join(directory, "pyproject.toml")):
            return directory, "python"
        if os.path.exists(os.path.join(directory, "setup.py")):
            return directory, "python"
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None, None

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path or not os.path.exists(file_path):
        sys.exit(0)

    ext = os.path.splitext(file_path)[1].lower()
    project_root, project_type = find_project_root(file_path)

    # ── TypeScript / JavaScript / CSS / JSON ──────────────────
    if ext in (".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".json", ".md"):
        formatted = False

        # 优先使用项目本地 prettier
        if project_root:
            local_prettier = os.path.join(project_root, "node_modules", ".bin", "prettier")
            if os.path.exists(local_prettier):
                ok, _, _ = run(f'"{local_prettier}" --write "{file_path}"')
                formatted = ok

        # 降级使用全局 prettier
        if not formatted:
            ok, _, _ = run(f'npx prettier --write "{file_path}"')

    # ── Python ────────────────────────────────────────────────
    elif ext == ".py":
        # 优先 ruff（更快）
        ok, _, _ = run(f'ruff format "{file_path}"')
        if not ok:
            # 降级使用 black
            run(f'black "{file_path}"')

    sys.exit(0)

if __name__ == "__main__":
    main()
