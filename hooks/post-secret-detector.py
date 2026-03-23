#!/usr/bin/env python3
"""
PostToolUse Hook: 密钥泄露检测器
文件写入后扫描是否包含硬编码的密钥、Token、密码
发现问题立即告知 Claude 自动修复
"""
import json
import sys
import io
import os
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 密钥检测规则
SECRET_PATTERNS = [
    # API Keys
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9_\-]{20,})["\']',
     "API Key 硬编码"),
    # Tokens
    (r'(?i)(token|access_token|auth_token)\s*[=:]\s*["\']([A-Za-z0-9_\-\.]{20,})["\']',
     "Token 硬编码"),
    # 密码
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^\'"]{6,})["\']',
     "密码硬编码"),
    # AWS
    (r'AKIA[0-9A-Z]{16}',
     "AWS Access Key ID"),
    (r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\']([A-Za-z0-9/+=]{40})["\']',
     "AWS Secret Key"),
    # 数据库连接串含密码
    (r'(?i)(mysql|postgresql|postgres|mongodb|redis)://[^:]+:([^@\s"\']{6,})@',
     "数据库连接串含密码"),
    # JWT Secret
    (r'(?i)jwt[_-]?secret\s*[=:]\s*["\']([^\'"]{10,})["\']',
     "JWT Secret 硬编码"),
    # 私钥开头
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE KEY-----',
     "私钥内容"),
    # 微信/支付宝密钥
    (r'(?i)(wx|wechat)[_-]?(secret|key)\s*[=:]\s*["\']([A-Za-z0-9]{16,})["\']',
     "微信密钥硬编码"),
    # GitHub Token
    (r'ghp_[A-Za-z0-9]{36}',
     "GitHub Personal Access Token"),
    # Anthropic API Key
    (r'sk-ant-[A-Za-z0-9_\-]{20,}',
     "Anthropic API Key"),
]

# 安全的忽略模式（测试/示例文件不告警）
SAFE_PATTERNS = [
    r'\.test\.',
    r'\.spec\.',
    r'example',
    r'sample',
    r'mock',
    r'fixture',
    r'your[_-]?api[_-]?key',
    r'xxx+',
    r'placeholder',
    r'\$\{',       # 环境变量引用
    r'process\.env',
    r'os\.environ',
    r'os\.getenv',
]

def is_safe_context(match_str, surrounding):
    """判断是否是安全上下文（环境变量引用、示例等）"""
    for safe in SAFE_PATTERNS:
        if re.search(safe, surrounding, re.IGNORECASE):
            return True
    return False

def scan_file(file_path):
    """扫描文件中的密钥"""
    issues = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return issues

    lines = content.splitlines()

    for line_num, line in enumerate(lines, 1):
        # 跳过注释行
        stripped = line.strip()
        if stripped.startswith(("#", "//", "*", "<!--")):
            continue

        # 获取上下文（前后各 1 行）
        start = max(0, line_num - 2)
        end   = min(len(lines), line_num + 1)
        context = "\n".join(lines[start:end])

        for pattern, desc in SECRET_PATTERNS:
            matches = re.finditer(pattern, line)
            for m in matches:
                full_match = m.group(0)
                if not is_safe_context(full_match, context):
                    issues.append({
                        "line":    line_num,
                        "desc":    desc,
                        "content": line.strip()[:80],
                        "fix":     "请将此值移至 .env 文件，代码中改用环境变量读取"
                    })

    return issues

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name  = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path or not os.path.exists(file_path):
        sys.exit(0)

    # 只扫描代码文件
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in (".ts", ".tsx", ".js", ".jsx", ".py", ".go",
                   ".java", ".rs", ".php", ".rb", ".env",
                   ".yaml", ".yml", ".toml", ".json", ".sh"):
        sys.exit(0)

    # 跳过 .env.example 等示例文件
    basename = os.path.basename(file_path).lower()
    if any(k in basename for k in ["example", "sample", "template", ".example"]):
        sys.exit(0)

    issues = scan_file(file_path)
    if not issues:
        sys.exit(0)

    # 格式化问题描述
    issue_lines = []
    for issue in issues:
        issue_lines.append(
            f"  - 第 {issue['line']} 行 [{issue['desc']}]：`{issue['content']}`\n"
            f"    → {issue['fix']}"
        )

    feedback = (
        f"⚠️  密钥泄露风险检测到 {len(issues)} 处问题（文件：{file_path}）：\n\n"
        + "\n".join(issue_lines) +
        "\n\n请立即修复：\n"
        "1. 将硬编码值移至 .env 文件\n"
        "2. 代码改为 `process.env.KEY_NAME` 或 `os.environ.get('KEY_NAME')`\n"
        "3. 确认 .env 已在 .gitignore 中"
    )

    result = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": feedback
        }
    }
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()
