#!/usr/bin/env python3
"""
PreToolUse Hook: Git 提交质量检查
在 git commit 前执行质量检查：lint staged files、验证 commit message、检测 console.log/debugger/secrets

exit 0 = 允许提交
exit 2 = 阻止提交（stderr 内容会发送给 Claude）
"""
import json
import sys
import io
import os
import re
import subprocess
from typing import List, Tuple

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass


def get_staged_files() -> List[str]:
    """获取暂存区的文件列表"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        pass
    return []


def get_commit_message() -> str:
    """获取 commit message（从 .git/COMMIT_EDITMSG 或环境变量）"""
    # 优先从环境变量读取
    msg = os.environ.get("GIT_COMMIT_MESSAGE", "")
    if msg:
        return msg
    
    # 尝试读取 .git/COMMIT_EDITMSG
    try:
        git_dir = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False
        )
        if git_dir.returncode == 0:
            editmsg_path = os.path.join(git_dir.stdout.strip(), "COMMIT_EDITMSG")
            if os.path.exists(editmsg_path):
                with open(editmsg_path, encoding="utf-8", errors="ignore") as f:
                    return f.read()
    except Exception:
        pass
    
    return ""


def validate_commit_message(msg: str) -> Tuple[bool, List[str]]:
    """验证 commit message 格式"""
    errors = []
    
    if not msg.strip():
        errors.append("Commit message 为空")
        return False, errors
    
    lines = msg.strip().split("\n")
    first_line = lines[0]
    
    # 检查标题行长度
    if len(first_line) > 72:
        errors.append(f"标题行过长 ({len(first_line)} > 72 字符)")
    
    # 检查标题行是否以大写字母开头（可选）
    if first_line and not first_line[0].isupper() and not first_line.startswith("fixup!"):
        errors.append("建议标题行以大写字母开头")
    
    # 检查是否包含空行分隔标题和正文
    if len(lines) > 1 and lines[1].strip():
        errors.append("标题和正文之间应有一个空行")
    
    return len(errors) == 0, errors


def check_console_log(file_path: str) -> List[str]:
    """检测文件中的 console.log/debugger"""
    issues = []
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith(("//", "#", "*", "<!--", "/*")):
                continue
            
            if re.search(r"console\.(log|warn|error|debug|info)", line):
                issues.append(f"第 {i} 行: console.{line.split('console.')[1].split('(')[0]}")
            elif "debugger" in line and not stripped.startswith("//"):
                issues.append(f"第 {i} 行: debugger 语句")
    except Exception:
        pass
    
    return issues


def check_secrets_in_file(file_path: str) -> List[str]:
    """简单检测文件中的敏感信息"""
    issues = []
    secret_patterns = [
        (r"sk-ant-[A-Za-z0-9_\-]{20,}", "Anthropic API Key"),
        (r"sk-[A-Za-z0-9]{48}", "OpenAI API Key"),
        (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
        (r"gh[pousr]_[A-Za-z0-9]{36,}", "GitHub Token"),
        (r"sk_live_[A-Za-z0-9]{24,}", "Stripe Key"),
        (r"AIza[0-9A-Za-z\-_]{35}", "Google API Key"),
    ]
    
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        for pattern, desc in secret_patterns:
            if re.search(pattern, content):
                issues.append(f"疑似包含 {desc}")
                break
    except Exception:
        pass
    
    return issues


def run_linter(file_path: str) -> Tuple[bool, str]:
    """根据文件类型运行相应的 linter"""
    ext = os.path.splitext(file_path)[1].lower()
    
    # JS/TS - ESLint
    if ext in [".js", ".jsx", ".ts", ".tsx"]:
        try:
            result = subprocess.run(
                ["eslint", file_path],
                capture_output=True,
                text=True,
                timeout=15,
                check=False
            )
            if result.returncode != 0:
                return False, result.stdout or result.stderr
        except FileNotFoundError:
            pass  # ESLint 未安装
    
    # Python - Flake8 / Pylint
    elif ext == ".py":
        for linter in ["flake8", "pylint"]:
            try:
                result = subprocess.run(
                    [linter, file_path],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    check=False
                )
                if result.returncode != 0:
                    return False, result.stdout or result.stderr
            except FileNotFoundError:
                continue
    
    # Go - gofmt
    elif ext == ".go":
        try:
            result = subprocess.run(
                ["gofmt", "-l", file_path],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )
            if result.stdout.strip():
                return False, "文件需要 gofmt 格式化"
        except FileNotFoundError:
            pass
    
    return True, ""


def main():
    try:
        # 读取 stdin
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        # 仅处理 git commit 命令
        if tool_name != "Bash":
            sys.exit(0)

        command = tool_input.get("command", "").strip()
        if not re.match(r"git\s+commit", command, re.IGNORECASE):
            sys.exit(0)

        # 如果有 --no-verify 标志，放行（由 pre-bash-guard 处理拦截）
        if "--no-verify" in command:
            sys.exit(0)

        all_errors = []
        all_warnings = []

        # 1. 验证 commit message
        commit_msg = get_commit_message()
        msg_valid, msg_errors = validate_commit_message(commit_msg)
        if not msg_valid:
            all_errors.extend(["Commit message 问题:"] + msg_errors)

        # 2. 检查暂存文件
        staged_files = get_staged_files()
        if not staged_files:
            sys.exit(0)  # 无暂存文件，放行

        code_files = [f for f in staged_files if f.endswith((".js", ".jsx", ".ts", ".tsx", ".py", ".go"))]
        
        for file_path in code_files:
            # 检测 console.log
            console_issues = check_console_log(file_path)
            if console_issues:
                all_warnings.append(f"\n{file_path} 包含 console.log/debugger:")
                all_warnings.extend(console_issues)
            
            # 检测敏感信息
            secret_issues = check_secrets_in_file(file_path)
            if secret_issues:
                all_errors.append(f"\n{file_path} 可能包含敏感信息:")
                all_errors.extend(secret_issues)
            
            # 运行 linter
            lint_ok, lint_output = run_linter(file_path)
            if not lint_ok:
                all_errors.append(f"\n{file_path} Lint 失败:")
                all_errors.append(lint_output[:500])  # 限制长度

        # 输出结果
        if all_errors:
            error_msg = "❌ 提交质量检查失败：\n\n" + "\n".join(all_errors)
            error_msg += "\n\n请修复上述问题后重新提交。"
            sys.stderr.write(error_msg + "\n")
            sys.stderr.flush()
            sys.exit(2)
        
        if all_warnings:
            warn_msg = "⚠️ 提交质量警告：\n\n" + "\n".join(all_warnings)
            warn_msg += "\n\n建议在合并 PR 前清理这些问题。"
            
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": warn_msg,
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
