#!/usr/bin/env python3
"""
PostToolUse Hook: 自动代码格式化
文件编辑/写入后自动运行格式化工具
支持：TS/JS (Prettier)、Python (Ruff/Black)、Go (gofmt)、Rust (rustfmt)

修复记录：
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: BaseException/SystemExit 分离捕获
- FIX: subprocess 统一超时 + TimeoutExpired 捕获
- FIX: find_prettier 使用 shutil.which 跨平台查找
"""
import json
import sys
import io
import subprocess
import os
import shutil

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def run(cmd: list | str, cwd=None) -> bool:
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=cwd)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=cwd)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except FileNotFoundError:
        return False
    except Exception:
        return False


def find_prettier(project_root: str) -> str | None:
    if not project_root:
        return None
    for name in ("prettier", "prettier.cmd"):
        candidate = os.path.join(project_root, "node_modules", ".bin", name)
        if os.path.exists(candidate):
            return candidate
    return None


def find_project_root(file_path: str) -> tuple[str | None, str | None]:
    try:
        directory = os.path.dirname(os.path.abspath(file_path))
        markers = {
            "package.json": "node",
            "pyproject.toml": "python",
            "setup.py": "python",
            "go.mod": "go",
            "Cargo.toml": "rust",
        }
        for _ in range(10):
            for marker, proj_type in markers.items():
                if os.path.exists(os.path.join(directory, marker)):
                    return directory, proj_type
            parent = os.path.dirname(directory)
            if parent == directory:
                break
            directory = parent
    except Exception:
        pass
    return None, None


def main():
    try:
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name  = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        if tool_name not in ("Edit", "Write", "MultiEdit"):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            sys.exit(0)

        ext = os.path.splitext(file_path)[1].lower()
        project_root, _ = find_project_root(file_path)

        # TypeScript / JavaScript / CSS / JSON / Markdown / HTML
        if ext in (".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".json", ".md", ".html", ".yaml", ".yml"):
            local_prettier = find_prettier(project_root)
            if local_prettier:
                run([local_prettier, "--write", file_path])
            elif shutil.which("prettier"):
                run(["prettier", "--write", file_path])
            else:
                run(f'npx --yes prettier --write "{file_path}"')

        elif ext == ".py":
            if shutil.which("ruff"):
                run(["ruff", "format", file_path])
            elif shutil.which("black"):
                run(["black", file_path])

        elif ext == ".go":
            if shutil.which("gofmt"):
                run(["gofmt", "-w", file_path])

        elif ext == ".rs":
            if shutil.which("rustfmt"):
                run(["rustfmt", file_path])

        elif ext in (".java",):
            if shutil.which("google-java-format"):
                run(["google-java-format", "--replace", file_path])

    except SystemExit:
        raise
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
