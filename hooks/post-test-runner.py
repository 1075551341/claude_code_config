#!/usr/bin/env python3
"""
PostToolUse Hook: 自动测试运行器
检测到测试文件或被测文件修改后，自动运行对应的测试
将测试结果反馈给 Claude，让其自动修复失败的测试
"""
import json
import sys
import io
import os
import re
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GLOBAL_CLAUDE_DIR = os.path.normpath(os.path.join(os.path.expanduser("~"), ".claude"))


def run(cmd: str, cwd: str = None) -> tuple:
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=120, cwd=cwd,
        )
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return -1, "测试执行超时（120 秒）"
    except Exception as e:
        return -1, str(e)


def find_project_root(file_path: str) -> tuple:
    """向上查找项目根目录，返回 (root, type)"""
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
    return None, None


def find_test_command(project_root: str, project_type: str, file_path: str) -> str:
    """根据项目类型和文件路径确定测试命令"""
    basename = os.path.basename(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    if project_type == "node":
        pkg_path = os.path.join(project_root, "package.json")
        try:
            with open(pkg_path, encoding="utf-8") as f:
                pkg = json.load(f)
            scripts = pkg.get("scripts", {})
        except Exception:
            scripts = {}

        is_test_file = any(p in basename for p in [".test.", ".spec.", "__tests__"])

        if is_test_file:
            rel_path = os.path.relpath(file_path, project_root).replace("\\", "/")
            if os.path.exists(os.path.join(project_root, "node_modules", ".bin", "vitest")):
                return f'npx vitest run "{rel_path}" --reporter=verbose'
            if os.path.exists(os.path.join(project_root, "node_modules", ".bin", "jest")):
                return f'npx jest "{rel_path}" --verbose --no-coverage'

        if "test" in scripts:
            return "npm test -- --passWithNoTests"
        if "test:unit" in scripts:
            return "npm run test:unit -- --passWithNoTests"

    elif project_type == "python":
        is_test_file = basename.startswith("test_") or basename.endswith("_test.py")
        if is_test_file:
            rel_path = os.path.relpath(file_path, project_root).replace("\\", "/")
            return f'python -m pytest "{rel_path}" -v --tb=short'
        return "python -m pytest --tb=short -q"

    elif project_type == "go":
        dir_path = os.path.dirname(os.path.relpath(file_path, project_root))
        return f"go test ./{dir_path}/... -v -count=1"

    return ""


TEST_THRESHOLD = 5


def get_counter_file(project_root: str) -> str:
    """计数器存放在项目的 .claude/ 目录下"""
    return os.path.join(project_root, ".claude", "test_counter.json")


def load_counter(session_id: str, project_root: str) -> dict:
    counter_file = get_counter_file(project_root)
    try:
        if os.path.exists(counter_file):
            with open(counter_file, encoding="utf-8") as f:
                data = json.load(f)
            return data.get(session_id, {"count": 0})
    except Exception:
        pass
    return {"count": 0}


def save_counter(session_id: str, counter: dict, project_root: str):
    counter_file = get_counter_file(project_root)
    try:
        os.makedirs(os.path.dirname(counter_file), exist_ok=True)
        data = {}
        if os.path.exists(counter_file):
            with open(counter_file, encoding="utf-8") as f:
                data = json.load(f)
        data[session_id] = counter
        if len(data) > 20:
            oldest = list(data.keys())[0]
            del data[oldest]
        with open(counter_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    session_id = data.get("session_id", "unknown")

    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path or not os.path.exists(file_path):
        sys.exit(0)

    ext = os.path.splitext(file_path)[1].lower()
    code_exts = {".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java"}
    if ext not in code_exts:
        sys.exit(0)

    skip_patterns = [
        r"\.claude/", r"node_modules/", r"__pycache__/",
        r"dist/", r"build/", r"\.config\.", r"\.d\.ts$",
    ]
    if any(re.search(p, file_path) for p in skip_patterns):
        sys.exit(0)

    project_root, project_type = find_project_root(file_path)
    if not project_root or not project_type:
        sys.exit(0)

    if os.path.normpath(project_root) == GLOBAL_CLAUDE_DIR:
        sys.exit(0)

    basename = os.path.basename(file_path)
    is_test_file = any(p in basename for p in [".test.", ".spec.", "test_", "_test."])

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

    if is_test_file or code != 0:
        save_counter(session_id, {"count": 0}, project_root)

    if code != 0:
        lines = output.splitlines()[-30:]
        truncated = "\n".join(lines)
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"测试失败，请自动修复：\n"
                    f"命令：`{test_cmd}`\n"
                    f"输出（最后 30 行）：\n```\n{truncated}\n```"
                )
            }
        }
        print(json.dumps(result, ensure_ascii=False))

    sys.exit(0)


if __name__ == "__main__":
    main()
