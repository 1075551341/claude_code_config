#!/usr/bin/env python3
"""
PostToolUse Hook: 自动测试运行器
检测到测试文件或被测文件修改后，自动运行对应的测试

修复记录：
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: BaseException/SystemExit 分离捕获
- FIX: sys.stdout.flush() 确保输出缓冲刷新
- FIX: subprocess 列表参数 + TimeoutExpired 显式捕获
- FIX: shutil.which 检测工具可用性
"""
import json
import sys
import io
import os
import re
import shutil
import subprocess

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

GLOBAL_CLAUDE_DIR = os.path.normpath(os.path.join(os.path.expanduser("~"), ".claude"))
TEST_THRESHOLD = 5


def run(cmd: list | str, cwd: str = None) -> tuple[int, str]:
    try:
        if isinstance(cmd, str):
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120, cwd=cwd)
        else:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=cwd)
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, "测试执行超时（120 秒），请手动运行"
    except FileNotFoundError:
        return 127, ""
    except Exception as e:
        return -1, str(e)


def find_project_root(file_path: str) -> tuple[str | None, str | None]:
    try:
        directory = os.path.dirname(os.path.abspath(file_path))
        for _ in range(10):
            if os.path.exists(os.path.join(directory, "package.json")):
                return directory, "node"
            if os.path.exists(os.path.join(directory, "pyproject.toml")):
                return directory, "python"
            if os.path.exists(os.path.join(directory, "setup.py")):
                return directory, "python"
            if os.path.exists(os.path.join(directory, "go.mod")):
                return directory, "go"
            parent = os.path.dirname(directory)
            if parent == directory:
                break
            directory = parent
    except Exception:
        pass
    return None, None


def find_local_bin(project_root: str, name: str) -> str | None:
    for suffix in ("", ".cmd"):
        candidate = os.path.join(project_root, "node_modules", ".bin", name + suffix)
        if os.path.exists(candidate):
            return candidate
    return None


def find_test_command(project_root: str, project_type: str, file_path: str) -> str:
    try:
        basename = os.path.basename(file_path)
        rel_path = os.path.relpath(file_path, project_root).replace("\\", "/")
        is_test = any(p in basename for p in (".test.", ".spec.", "test_", "_test."))

        if project_type == "node":
            try:
                with open(os.path.join(project_root, "package.json"), encoding="utf-8") as f:
                    pkg = json.load(f)
                scripts = pkg.get("scripts", {})
            except Exception:
                scripts = {}

            if is_test:
                vitest = find_local_bin(project_root, "vitest")
                if vitest:
                    return f'"{vitest}" run "{rel_path}" --reporter=verbose'
                jest = find_local_bin(project_root, "jest")
                if jest:
                    return f'"{jest}" "{rel_path}" --verbose --no-coverage'
                # npx fallback
                has_vitest = os.path.exists(os.path.join(project_root, "vitest.config.ts")) or \
                             os.path.exists(os.path.join(project_root, "vitest.config.js")) or \
                             os.path.exists(os.path.join(project_root, "vitest.config.mts"))
                if has_vitest:
                    return f'npx vitest run "{rel_path}" --reporter=verbose'
                return f'npx jest "{rel_path}" --verbose --no-coverage'
            else:
                for key in ("test", "test:unit", "test:all"):
                    if key in scripts:
                        return f"npm run {key} -- --passWithNoTests"

        elif project_type == "python":
            if shutil.which("pytest"):
                if is_test:
                    return f'python -m pytest "{rel_path}" -v --tb=short'
                return "python -m pytest --tb=short -q"

        elif project_type == "go":
            dir_path = os.path.dirname(
                os.path.relpath(file_path, project_root)
            ).replace("\\", "/") or "."
            return f"go test ./{dir_path}/... -v -count=1 -timeout 60s"

    except Exception:
        pass
    return ""


def get_counter_file(project_root: str) -> str:
    return os.path.join(project_root, ".claude", "test_counter.json")


def load_counter(session_id: str, project_root: str) -> dict:
    try:
        cf = get_counter_file(project_root)
        if os.path.exists(cf):
            with open(cf, encoding="utf-8") as f:
                data = json.load(f)
            return data.get(session_id, {"count": 0})
    except Exception:
        pass
    return {"count": 0}


def save_counter(session_id: str, counter: dict, project_root: str):
    try:
        cf = get_counter_file(project_root)
        os.makedirs(os.path.dirname(cf), exist_ok=True)
        data = {}
        if os.path.exists(cf):
            with open(cf, encoding="utf-8") as f:
                data = json.load(f)
        data[session_id] = counter
        if len(data) > 20:
            for k in list(data.keys())[: len(data) - 20]:
                del data[k]
        with open(cf, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def main():
    try:
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name  = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        session_id = data.get("session_id", "unknown")

        if tool_name not in ("Edit", "Write", "MultiEdit"):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            sys.exit(0)

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in {".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java"}:
            sys.exit(0)

        skip_patterns = [
            r"\.claude[\\/]", r"node_modules[\\/]", r"__pycache__[\\/]",
            r"dist[\\/]", r"build[\\/]", r"\.d\.ts$", r"\.min\.", r"vendor[\\/]",
        ]
        if any(re.search(p, file_path, re.IGNORECASE) for p in skip_patterns):
            sys.exit(0)

        project_root, project_type = find_project_root(file_path)
        if not project_root or not project_type:
            sys.exit(0)

        if os.path.normpath(project_root) == GLOBAL_CLAUDE_DIR:
            sys.exit(0)

        basename = os.path.basename(file_path)
        is_test_file = any(p in basename for p in (".test.", ".spec.", "test_", "_test."))

        if not is_test_file:
            counter = load_counter(session_id, project_root)
            counter["count"] += 1
            save_counter(session_id, counter, project_root)
            if counter["count"] < TEST_THRESHOLD:
                sys.exit(0)

        test_cmd = find_test_command(project_root, project_type, file_path)
        if not test_cmd:
            sys.exit(0)

        code, output = run(test_cmd, cwd=project_root)

        if is_test_file or code == 0:
            save_counter(session_id, {"count": 0}, project_root)

        if code not in (0, 127):
            lines = output.splitlines()
            truncated = "\n".join(lines[-30:])
            if len(lines) > 30:
                truncated = f"... （前 {len(lines)-30} 行已省略）\n" + truncated

            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        f"❌ 测试失败，请自动修复：\n"
                        f"命令：`{test_cmd}`\n\n"
                        f"```\n{truncated}\n```"
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
