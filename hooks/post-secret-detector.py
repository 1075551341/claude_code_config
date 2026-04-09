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
import json
import sys
import io
import os
import re

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

SECRET_PATTERNS = [
    # Anthropic
    (r"sk-ant-[A-Za-z0-9_\-]{20,}",             "Anthropic API Key",          "critical"),
    # OpenAI
    (r"sk-[A-Za-z0-9]{48}",                      "OpenAI API Key",             "critical"),
    (r"sk-proj-[A-Za-z0-9_\-]{40,}",             "OpenAI Project API Key",     "critical"),
    # AWS
    (r"AKIA[0-9A-Z]{16}",                         "AWS Access Key ID",          "critical"),
    (r"(?i)aws[_\-]?secret[_\-]?(?:access[_\-]?)?key\s*[=:]\s*[\"']([A-Za-z0-9/+=]{40})[\"']",
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
    (r"(?i)(?:api[_\-]?key|apikey)\s*[=:]\s*[\"']([A-Za-z0-9_\-]{20,})[\"']",
     "API Key 硬编码",                                                           "high"),
    (r"(?i)(?:access[_\-]?token|auth[_\-]?token|bearer[_\-]?token)\s*[=:]\s*[\"']([A-Za-z0-9_\-\.]{20,})[\"']",
     "Token 硬编码",                                                             "high"),
    (r"(?i)(?:secret[_\-]?key|client[_\-]?secret)\s*[=:]\s*[\"']([A-Za-z0-9_\-\.+/=]{16,})[\"']",
     "Secret Key 硬编码",                                                        "high"),
    # 密码
    (r"(?i)(?:password|passwd|pwd)\s*[=:]\s*[\"']([^\"\\']{8,})[\"']",
     "密码硬编码",                                                               "medium"),
    # JWT Secret
    (r"(?i)jwt[_\-]?secret\s*[=:]\s*[\"']([^\"\\']{10,})[\"']",
     "JWT Secret 硬编码",                                                        "high"),
    # 私钥
    (r"-----BEGIN\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE KEY-----",
     "私钥内容",                                                                  "critical"),
    # 数据库连接串含密码
    (r"(?i)(?:mysql|postgresql|postgres|mongodb|redis|mssql|oracle)://[^:@\s]+:([^@\s\"\']{8,})@",
     "数据库连接串含密码",                                                        "high"),
    # 微信/支付宝
    (r"(?i)(?:wx|wechat|wxpay)[_\-]?(?:secret|key|appsecret)\s*[=:]\s*[\"']([A-Za-z0-9]{16,})[\"']",
     "微信密钥硬编码",                                                            "high"),
]

SAFE_CONTEXTS = [
    r"\.test\.",         r"\.spec\.",      r"__test__",      r"_test\.py",
    r"\bexample\b",      r"\bsample\b",    r"\bmock\b",      r"\bfixture\b",
    r"\bfake\b",         r"\bdummy\b",     r"placeholder",
    r"your[_\-]?",       r"xxx+",          r"yyy+",          r"zzz+",
    r"\$\{",             r"process\.env\.", r"os\.environ",   r"os\.getenv",
    r"import\.meta\.env",r"env\[",
    r"<YOUR_",           r"<your_",        r"YOUR_API",       r"your-api",
    r"\*{4,}",           r"<REPLACE>",     r"CHANGEME",       r"TODO:",
]

SAFE_FILE_PATTERNS = [
    r"\.example$", r"\.sample$", r"\.template$",
    r"example\.",  r"sample\.",  r"mock\.",
    r"\.test\.",   r"\.spec\.",  r"_test\.",
    r"\.md$",
]


def is_safe_context(line: str, surrounding: str) -> bool:
    combined = (line + " " + surrounding).lower()
    return any(re.search(p, combined, re.IGNORECASE) for p in SAFE_CONTEXTS)


def scan_file(file_path: str) -> list[dict]:
    issues = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return issues

    lines = content.splitlines()

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(("#", "//", "*", "<!--", "/*")) or not stripped:
            continue

        ctx_start = max(0, line_num - 3)
        ctx_end   = min(len(lines), line_num + 2)
        surrounding = "\n".join(lines[ctx_start:ctx_end])

        for pattern, desc, severity in SECRET_PATTERNS:
            try:
                for m in re.finditer(pattern, line):
                    matched_str = m.group(0)
                    if not is_safe_context(matched_str, surrounding):
                        issues.append({
                            "line":     line_num,
                            "desc":     desc,
                            "severity": severity,
                            "content":  line.strip()[:100],
                        })
                        break
            except re.error:
                continue

        if len(issues) >= 10:
            break

    return issues


def main():
    try:
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name  = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        if tool_name not in ("Write", "Edit", "MultiEdit"):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            sys.exit(0)

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in (
            ".ts", ".tsx", ".js", ".jsx", ".py", ".go",
            ".java", ".rs", ".php", ".rb", ".cs",
            ".env", ".yaml", ".yml", ".toml", ".json", ".sh", ".bash",
            ".conf", ".config", ".ini", ".properties",
        ):
            sys.exit(0)

        basename = os.path.basename(file_path).lower()
        if any(re.search(p, basename) for p in SAFE_FILE_PATTERNS):
            sys.exit(0)

        issues = scan_file(file_path)
        if not issues:
            sys.exit(0)

        severity_order = {"critical": 0, "high": 1, "medium": 2}
        issues.sort(key=lambda x: severity_order.get(x["severity"], 9))

        severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "💡"}
        issue_lines = []
        for issue in issues:
            emoji = severity_emoji.get(issue["severity"], "⚠️")
            issue_lines.append(
                f"  {emoji} 第 {issue['line']} 行 [{issue['desc']}]：\n"
                f"     `{issue['content']}`"
            )

        feedback = (
            f"🔐 密钥泄露检测：{os.path.basename(file_path)} 发现 {len(issues)} 处风险\n\n"
            + "\n".join(issue_lines)
            + "\n\n**请立即修复**：\n"
            "1. 将硬编码值移至 `.env` 文件\n"
            "2. 代码改为 `process.env.KEY_NAME` 或 `os.environ.get('KEY_NAME')`\n"
            "3. 确认 `.env` 已加入 `.gitignore`\n"
            "4. 若已提交到 git，需 rotate 密钥（历史提交无法撤销泄露）"
        )

        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": feedback,
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
