#!/usr/bin/env python3
"""
PreToolUse Hook: 依赖安全检查
npm install / pip install 前检查包是否存在已知风险
- 检测包名拼写攻击（typosquatting）
- 检查是否安装了可疑的小众包
- 提示使用 --save-exact 锁定版本
"""
import json
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 常见拼写攻击目标（热门包的易错拼写）
TYPOSQUATTING_PAIRS = {
    # npm
    "expresss":    "express",
    "requst":      "request",
    "lodahs":      "lodash",
    "recat":       "react",
    "raect":       "react",
    "reacct":      "react",
    "axois":       "axios",
    "axio":        "axios",
    "monggose":    "mongoose",
    "mongooose":   "mongoose",
    "moongose":    "mongoose",
    "typescirpt":  "typescript",
    "typscript":   "typescript",
    "nodemon":     "nodemon",   # 合法，但常被仿冒
    "noodemon":    "nodemon",
    "primsa":      "prisma",
    "primas":      "prisma",
    "sequlize":    "sequelize",
    "sequaliz":    "sequelize",
    "webapck":     "webpack",
    "viet":        "vite",
    # pip
    "requets":     "requests",
    "requestes":   "requests",
    "nmupy":       "numpy",
    "nunpy":       "numpy",
    "panads":      "pandas",
    "pands":       "pandas",
    "scikitlearn": "scikit-learn",
    "flasck":      "flask",
    "dajngo":      "django",
    "djagno":      "django",
    "fastap":      "fastapi",
    "pydatnic":    "pydantic",
}

# 高风险标志（包名包含这些词时提醒）
SUSPICIOUS_PATTERNS = [
    r"^eval\-",
    r"\-eval$",
    r"^exec\-",
    r"cryptominer",
    r"stealer",
    r"keylogger",
]

def extract_packages(command):
    """从安装命令中提取包名列表"""
    packages = []

    # npm install xxx / npm i xxx
    npm_match = re.match(
        r"npm\s+(?:install|i|add)\s+(.+)", command, re.IGNORECASE
    )
    if npm_match:
        args = npm_match.group(1).split()
        for arg in args:
            # 跳过 flags 和 scope（-D, --save-dev, @types/...）
            if not arg.startswith("-"):
                # 去掉版本号
                pkg = re.sub(r"@[\d\.\^~>=<*]+$", "", arg)
                if pkg:
                    packages.append(("npm", pkg))

    # pnpm add / yarn add
    pm_match = re.match(
        r"(?:pnpm|yarn)\s+add\s+(.+)", command, re.IGNORECASE
    )
    if pm_match:
        args = pm_match.group(1).split()
        for arg in args:
            if not arg.startswith("-"):
                pkg = re.sub(r"@[\d\.\^~>=<*]+$", "", arg)
                if pkg:
                    packages.append(("npm", pkg))

    # pip install xxx
    pip_match = re.match(
        r"pip(?:3)?\s+install\s+(.+)", command, re.IGNORECASE
    )
    if pip_match:
        args = pip_match.group(1).split()
        for arg in args:
            if not arg.startswith("-") and arg != "-r":
                pkg = re.sub(r"[><=!~]+.*$", "", arg)
                if pkg and not arg.startswith("-r"):
                    packages.append(("pip", pkg))

    return packages

def check_typosquatting(pkg_name):
    """检查是否是常见包的错误拼写"""
    lower = pkg_name.lower().replace("-", "").replace("_", "")
    for typo, real in TYPOSQUATTING_PAIRS.items():
        typo_clean = typo.replace("-", "").replace("_", "")
        if lower == typo_clean:
            return real
    return None

def check_suspicious(pkg_name):
    """检查是否包含可疑模式"""
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, pkg_name, re.IGNORECASE):
            return True
    return False

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name  = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name != "Bash":
        sys.exit(0)

    command = tool_input.get("command", "").strip()

    # 只处理安装命令
    if not re.match(
        r"(?:npm\s+(?:install|i|add)|pnpm\s+add|yarn\s+add|pip(?:3)?\s+install)",
        command, re.IGNORECASE
    ):
        sys.exit(0)

    packages = extract_packages(command)
    if not packages:
        sys.exit(0)

    warnings = []
    blockers = []

    for pkg_type, pkg_name in packages:
        # 跳过明显合法的包（有 scope 的 @org/pkg）
        if pkg_name.startswith("@") and "/" in pkg_name:
            continue

        # 拼写攻击检测
        real_pkg = check_typosquatting(pkg_name)
        if real_pkg:
            blockers.append(
                f"🚨 [{pkg_name}] 疑似拼写攻击！你是否想安装 [{real_pkg}]？"
            )

        # 可疑包名
        elif check_suspicious(pkg_name):
            blockers.append(
                f"🚨 [{pkg_name}] 包名包含可疑关键词，请确认来源"
            )

    # 有阻断问题则拒绝
    if blockers:
        msg = "依赖安全检查发现问题，已阻止安装：\n\n"
        msg += "\n".join(blockers)
        msg += "\n\n请确认包名是否正确后再安装。"
        print(msg, file=sys.stderr)
        sys.exit(2)

    # 有警告但不阻断
    if warnings:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": "⚠️ 依赖安全提醒：\n" + "\n".join(warnings)
            }
        }
        print(json.dumps(result, ensure_ascii=False))

    sys.exit(0)

if __name__ == "__main__":
    main()
