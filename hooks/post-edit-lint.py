#!/usr/bin/env python3
"""
PostToolUse Hook: Lint + 类型检查
编辑代码文件后自动运行 Lint 和类型检查

修复记录：
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: BaseException/SystemExit 分离捕获
- FIX: sys.stdout.flush() 确保输出缓冲刷新
- FIX: subprocess.TimeoutExpired 显式捕获，超时不报错
- FIX: shutil.which 检查工具可用性，避免命令未安装时报错
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

MAX_LINES = 30


def run(cmd: list | str, cwd=None) -> tuple[int, str]:
    try:
        if isinstance(cmd, str):
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60, cwd=cwd)
        else:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=cwd)
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, "（检查超时，请手动运行）"
    except FileNotFoundError:
        return 127, ""
    except Exception:
        return -1, ""


def find_project_root(file_path: str) -> str | None:
    try:
        directory = os.path.dirname(os.path.abspath(file_path))
        for _ in range(10):
            if os.path.exists(os.path.join(directory, "package.json")):
                return directory
            parent = os.path.dirname(directory)
            if parent == directory:
                break
            directory = parent
    except Exception:
        pass
    return None


def find_python_project_root(file_path: str) -> str | None:
    try:
        directory = os.path.dirname(os.path.abspath(file_path))
        for _ in range(10):
            for marker in ("pyproject.toml", "setup.py", "setup.cfg", ".git"):
                if os.path.exists(os.path.join(directory, marker)):
                    return directory
            parent = os.path.dirname(directory)
            if parent == directory:
                break
            directory = parent
    except Exception:
        pass
    return None


def find_local_bin(project_root: str, name: str) -> str | None:
    if not project_root:
        return None
    for suffix in ("", ".cmd"):
        candidate = os.path.join(project_root, "node_modules", ".bin", name + suffix)
        if os.path.exists(candidate):
            return candidate
    return None


def truncate(output: str, max_lines: int = MAX_LINES) -> str:
    lines = output.splitlines()
    if len(lines) <= max_lines:
        return output
    return "\n".join(lines[:max_lines]) + f"\n... （已截断，共 {len(lines)} 行）"


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
        issues = []

        # ── TypeScript / JavaScript ──────────────────────────────────────────
        if ext in (".ts", ".tsx", ".js", ".jsx"):
            project_root = find_project_root(file_path)
            if not project_root:
                sys.exit(0)

            eslint = find_local_bin(project_root, "eslint") or shutil.which("eslint")
            if eslint:
                code, output = run(
                    [eslint, file_path, "--max-warnings", "0", "--format", "compact"],
                    cwd=project_root,
                )
                if code not in (0, 127) and output.strip():
                    issues.append(f"ESLint 问题：\n{truncate(output)}")

            if ext in (".ts", ".tsx"):
                tsconfig = os.path.join(project_root, "tsconfig.json")
                if os.path.exists(tsconfig):
                    tsc = find_local_bin(project_root, "tsc") or shutil.which("tsc")
                    if tsc:
                        code, output = run(
                            [tsc, "--noEmit", "--pretty", "false"],
                            cwd=project_root,
                        )
                        if code not in (0, 127) and output.strip():
                            issues.append(f"TypeScript 类型错误：\n{truncate(output)}")

        # ── Python ──────────────────────────────────────────────────────────
        elif ext == ".py":
            py_root = find_python_project_root(file_path)
            cwd = py_root or os.path.dirname(os.path.abspath(file_path))

            if shutil.which("ruff"):
                code, output = run(
                    ["ruff", "check", file_path, "--output-format=text"],
                    cwd=cwd,
                )
                if code not in (0, 127) and output.strip():
                    issues.append(f"Ruff 问题：\n{truncate(output)}")

            if shutil.which("mypy"):
                code, output = run(
                    ["mypy", file_path, "--ignore-missing-imports", "--no-error-summary"],
                    cwd=cwd,
                )
                if code not in (0, 127) and output.strip():
                    issues.append(f"Mypy 类型错误：\n{truncate(output)}")

        if issues:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        "⚠️ 代码质量检查发现以下问题，请自动修复：\n\n"
                        + "\n\n".join(issues)
                    ),
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
