#!/usr/bin/env python3
"""
PostToolUse Hook: 密钥泄露检测器
文件写入后扫描是否包含硬编码的密钥、Token、密码

修复记录：
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: BaseException/SystemExit 分离捕获
- FIX: sys.stdout.flush() 确保输出缓冲刷新
- FIX: 补充 Vercel/Clerk/Resend/PlanetScale 等新兴平台密钥
- FIX: 改进 JWT 检测（减少 base64 误报）
"""
# source: shanraisshan/claude-code-best-practice
import json
import sys
import io
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_lib"))

from tool_paths import extract_edit_paths, is_edit_tool  # noqa: E402

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    print("密钥检查输出初始化未完成。", file=sys.stderr)

SECRET_PATTERNS = [
    # Anthropic
    (r"sk-ant-[A-Za-z0-9_\-]{20,}",             "Anthropic API Key",          "critical"),
    # OpenAI
    (r"sk-[A-Za-z0-9]{48}",                      "OpenAI API Key",             "critical"),
    (r"sk-proj-[A-Za-z0-9_\-]{40,}",             "OpenAI Project API Key",     "critical"),
    # AWS
    (r"AKIA[0-9A-Z]{16}",                         "AWS Access Key ID",          "critical"),
    (r"(?i)(?<![\w-])[\"']?aws[_\-]?secret[_\-]?(?:access[_\-]?)?key(?![\w-])[\"']?\s*[=:]\s*[\"']([A-Za-z0-9/+=]{40})[\"']",
     "AWS Secret Key",                                                           "critical"),
    # GitHub
    (r"gh[pousr]_[A-Za-z0-9]{36,}",              "GitHub Token",               "critical"),
    (r"github_pat_[A-Za-z0-9_]{82}",             "GitHub Fine-grained PAT",    "critical"),
    # Stripe
    (r"sk_live_[A-Za-z0-9]{24,}",               "Stripe Live Secret Key",     "critical"),
    (r"rk_live_[A-Za-z0-9]{24,}",               "Stripe Restricted Key",      "critical"),
    # Firebase / GCP
    (r"AIza[0-9A-Za-z\-_]{35}",                 "Google/Firebase API Key",    "high"),
    # Supabase Service Role
    (r"(?i)supabase[^=\n]{0,30}[=:]\s*[\"'](eyJ[A-Za-z0-9_\-]{50,})",
     "Supabase Service Role Key",                                               "critical"),
    # Vercel
    (r"vercel_[A-Za-z0-9_]{24,}",               "Vercel Token",               "high"),
    # Clerk
    (r"sk_(?:live|test)_[A-Za-z0-9_]{32,}",     "Clerk Secret Key",           "critical"),
    # Resend
    (r"re_[A-Za-z0-9_]{32,}",                    "Resend API Key",             "high"),
    # Slack
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}",          "Slack Token",                "high"),
    # Twilio
    (r"SK[a-f0-9]{32}",                          "Twilio API Key SID",         "high"),
    # SendGrid
    (r"SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}",
     "SendGrid API Key",                                                         "critical"),
    # 通用 API Key / Token / Secret
    (r"(?i)(?<![\w-])[\"']?(?:api[_\-]?key|apikey)(?![\w-])[\"']?\s*[=:]\s*[\"']([A-Za-z0-9_\-]{20,})[\"']",
     "API Key 硬编码",                                                           "high"),
    (r"(?i)(?<![\w-])[\"']?(?:access[_\-]?token|auth[_\-]?token|bearer[_\-]?token)(?![\w-])[\"']?\s*[=:]\s*[\"']([A-Za-z0-9_\-\.]{20,})[\"']",
     "Token 硬编码",                                                             "high"),
    (r"(?i)(?<![\w-])[\"']?(?:secret[_\-]?key|client[_\-]?secret)(?![\w-])[\"']?\s*[=:]\s*[\"']([A-Za-z0-9_\-\.+/=]{16,})[\"']",
     "Secret Key 硬编码",                                                        "high"),
    # 密码
    (r"(?i)(?<![\w-])[\"']?(?:password|passwd|pwd)(?![\w-])[\"']?\s*[=:]\s*[\"']([^\"\\']{8,})[\"']",
     "密码硬编码",                                                               "medium"),
    # .env 常见无引号 KEY=VALUE
    (r"(?i)^\s*(?:export\s+)?(?!\w*(?:_HEADER|_EXPIRY|_TTL|_URL|_PATH|_NAME|_LENGTH)\s*=)[A-Z0-9_]*(?:PASSWORD|PASSWD|SECRET|TOKEN|API_KEY|PRIVATE_KEY|ACCESS_KEY)[A-Z0-9_]*\s*=\s*([^\s#]{8,})",
     "硬编码密码/密钥（无引号）",                                                  "high"),
    # JWT Secret
    (r"(?i)(?<![\w-])[\"']?jwt[_\-]?secret(?![\w-])[\"']?\s*[=:]\s*[\"']([^\"\\']{10,})[\"']",
     "JWT Secret 硬编码",                                                        "high"),
    # 私钥
    (r"-----BEGIN\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE KEY-----",
     "私钥内容",                                                                  "critical"),
    # 数据库连接串含密码
    (r"(?i)(?:mysql|postgresql|postgres|mongodb|redis|mssql|oracle)://[^:@\s]+:([^@\s\"\']{8,})@",
     "数据库连接串含密码",                                                        "high"),
    # 微信/支付宝
    (r"(?i)(?<![\w-])[\"']?(?:wx|wechat|wxpay)[_\-]?(?:secret|key|appsecret)(?![\w-])[\"']?\s*[=:]\s*[\"']([A-Za-z0-9]{16,})[\"']",
     "微信密钥硬编码",                                                            "high"),
]

SAFE_FILE_PATTERNS = [
    r"\.example$", r"\.sample$", r"\.template$",
    r"example\.",  r"sample\.",  r"mock\.",
    r"\.test\.",   r"\.spec\.",  r"_test\.",
    r"^test_.*\.py$",
    r"\.md$",
]


def is_safe_value(value: str) -> bool:
    """Exempt only an explicit placeholder or complete environment reference value."""
    value = value.strip().strip("\"'")
    placeholders = (
        r"(?:x{3,}|y{3,}|z{3,}|\*{4,})",
        r"(?:your|replace|placeholder|changeme|change_me)(?:[_ -][a-z0-9_-]+)?",
        r"<(?:your[_ -]?[a-z0-9_-]*|replace|placeholder)>",
    )
    references = (
        r"\$\{[A-Za-z_][A-Za-z0-9_]*(?::[-?][^}]*)?\}",
        r"\$[A-Za-z_][A-Za-z0-9_]*",
        r"\$env:[A-Za-z_][A-Za-z0-9_]*",
        r"%[A-Za-z_][A-Za-z0-9_]*%",
        r"(?:process\.env\.|import\.meta\.env\.)[A-Za-z_][A-Za-z0-9_]*",
        r"(?:os\.environ|process\.env|env)\[['\"][A-Za-z_][A-Za-z0-9_]*['\"]\]",
        r"os\.(?:getenv|environ\.get)\(['\"][A-Za-z_][A-Za-z0-9_]*['\"]\)",
    )
    return any(re.fullmatch(pattern, value, re.IGNORECASE) for pattern in (*placeholders, *references))


def scan_file(file_path: str) -> list[dict]:
    issues = []
    with open(file_path, "r", encoding="utf-8") as stream:
        content = stream.read()

    lines = content.splitlines()

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(("#", "//", "*", "<!--", "/*")) or not stripped:
            continue

        for pattern, desc, severity in SECRET_PATTERNS:
            try:
                matches = [
                    m.group(0)
                    for m in re.finditer(pattern, line)
                    if not is_safe_value(m.group(1) if m.lastindex else m.group(0))
                ]
                if matches:
                    issues.append({
                        "line":     line_num,
                        "desc":     desc,
                        "severity": severity,
                    })
            except re.error:
                continue

        if len(issues) >= 10:
            break

    return issues


def incomplete_notice(file_index: int | None = None) -> None:
    where = f"（编辑文件{file_index}）" if file_index is not None else ""
    print(f"密钥检查未完成{where}；请检查输入和文件可读性。本提示未包含输入或文件内容。", file=sys.stderr)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        if not isinstance(data, dict):
            raise ValueError("expected object")
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        cwd = data.get("cwd") or ""
        if not isinstance(tool_name, str) or not isinstance(tool_input, dict) or not isinstance(cwd, str):
            raise ValueError("invalid payload")
        if not is_edit_tool(tool_name, tool_input):
            return
        file_paths = extract_edit_paths(tool_input, cwd)
        allowed_ext = {
            ".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".java", ".rs", ".php", ".rb", ".cs",
            ".yaml", ".yml", ".toml", ".json", ".sh", ".bash", ".conf", ".config", ".ini", ".properties", ".ipynb",
        }
        issues = []
        for index, file_path in enumerate(file_paths, 1):
            basename = os.path.basename(file_path).lower()
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in allowed_ext and not basename.startswith(".env"):
                continue
            if any(re.search(pattern, basename) for pattern in SAFE_FILE_PATTERNS):
                continue
            try:
                for issue in scan_file(file_path):
                    issue["file_index"] = index
                    issues.append(issue)
            except (OSError, UnicodeError):
                incomplete_notice(index)
        if not issues:
            return
        severity_order = {"critical": 0, "high": 1, "medium": 2}
        issues.sort(key=lambda issue: severity_order.get(issue["severity"], 9))
        issue_lines = [f"编辑文件{issue['file_index']}，行{issue['line']}：{issue['desc']}（{issue['severity']}）" for issue in issues]
        feedback = (
            f"密钥模式检查：发现 {len(issues)} 处风险\n" + "\n".join(issue_lines)
            + "\n请核实并改用环境变量或凭据管理；若已泄露，请轮换密钥。此检查仅覆盖已知模式，不能替代完整安全审查。"
        )
        result = {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": feedback}}
        sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        sys.stdout.flush()
    except Exception:
        # Nonblocking and visible, without exception details, source fragments or paths.
        incomplete_notice()


if __name__ == "__main__":
    main()
