#!/usr/bin/env python3
"""
PreToolUse Hook: 依赖安全检查
npm install / pip install 前检查包是否存在已知风险

修复记录：
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: BaseException 捕获避免 sys.exit 传播问题
- FIX: sys.stdout.flush() 确保输出缓冲刷新
- FIX: 扩展 typosquatting 列表（Vite、shadcn、Radix、tanstack 等）
- FIX: 支持 bun add 命令解析
"""
import json
import sys
import io
import re

try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# ── 常见拼写攻击目标 ──────────────────────────────────────────────────────────
TYPOSQUATTING_PAIRS = {
    # React 生态
    "recat": "react",        "raect": "react",       "reacct": "react",
    "reactt": "react",       "rect": "react",
    "recat-dom": "react-dom","react-doms": "react-dom","reactdom": "react-dom",
    # 网络请求
    "axois": "axios",        "axio": "axios",         "acios": "axios",
    # Express
    "expresss": "express",   "expres": "express",
    # 数据库 ORM
    "monggose": "mongoose",  "mongooose": "mongoose", "moongose": "mongoose",
    "primsa": "prisma",      "primas": "prisma",      "prism": "prisma",
    "sequlize": "sequelize", "sequaliz": "sequelize",
    # 构建工具
    "webapck": "webpack",    "viet": "vite",          "vtes": "vite",
    "vittes": "vite",        "vitte": "vite",
    # Next.js / Nuxt
    "next-js": "next",       "nextjs": "next",
    "nuxtjs": "nuxt",        "nuxt-js": "nuxt",
    # TypeScript
    "typescirpt": "typescript","typscript": "typescript","typescrpit": "typescript",
    "tyescript": "typescript",
    # 常用工具
    "noodemon": "nodemon",   "noodmon": "nodemon",
    "tailiwnd": "tailwindcss","tailwnid": "tailwindcss","taliwindcss": "tailwindcss",
    "tailwndcss": "tailwindcss",
    "zustan": "zustand",     "zustnad": "zustand",
    "jotia": "jotai",        "recoill": "recoil",
    # shadcn / Radix
    "shadcn-ui": "shadcn",   "shad-cn": "shadcn",
    "radix-ui": "@radix-ui", "radixui": "@radix-ui",
    # Tanstack
    "tanstack-query": "@tanstack/react-query",
    "react-queery": "@tanstack/react-query",
    "reactquery": "@tanstack/react-query",
    # ESLint / Prettier
    "eslinet": "eslint",     "eslnt": "eslint",
    "pretter": "prettier",   "prettierr": "prettier",
    # Python 生态
    "requets": "requests",   "requestes": "requests", "rqeuests": "requests",
    "nmupy": "numpy",        "nunpy": "numpy",         "nimpy": "numpy",
    "panads": "pandas",      "pands": "pandas",        "pandsa": "pandas",
    "scikitlearn": "scikit-learn","sklean": "scikit-learn",
    "flasck": "flask",       "falsk": "flask",
    "dajngo": "django",      "djagno": "django",       "djangoo": "django",
    "fastap": "fastapi",     "fastaip": "fastapi",     "fatapi": "fastapi",
    "pydatnic": "pydantic",  "pytdantic": "pydantic",  "pydantics": "pydantic",
    "sqlachemy": "sqlalchemy","sqlalchmey": "sqlalchemy","sqlaclhemy": "sqlalchemy",
    "beautifulsoup": "beautifulsoup4","beatifulsoup": "beautifulsoup4",
    "matplotib": "matplotlib","matploltib": "matplotlib",
    "tensorlfow": "tensorflow","tensoflow": "tensorflow",
    "pytoch": "torch",       "ptroch": "torch",         "pytoch": "torch",
    "openai-python": "openai","opneai": "openai",
    "anthropics": "anthropic","antrhopic": "anthropic",
    # 其他常用
    "loding": "lodash",      "lodahs": "lodash",
    "momentjs": "moment",    "momnet": "moment",
    "d3js": "d3",            "recharts-js": "recharts",
}

SUSPICIOUS_PATTERNS = [
    r"^eval\-", r"\-eval$", r"^exec\-",
    r"cryptominer", r"stealer", r"keylogger",
    r"^node-(?:fetch|http)-v\d",
]

LOCK_VERSION_PKGS = {
    "next", "react", "react-dom", "vue", "nuxt", "svelte",
    "express", "fastapi", "django", "flask",
    "prisma", "typeorm", "sequelize",
}


def normalize_pkg(name: str) -> str:
    return name.lower().replace("-", "").replace("_", "").replace(".", "")


def extract_packages(command: str) -> list[tuple[str, str]]:
    packages = []
    # npm / yarn / pnpm / bun install/add
    m = re.match(
        r"(?:npm\s+(?:install|i|add)|pnpm\s+add|yarn\s+add|bun\s+add)\s+(.+)",
        command, re.IGNORECASE,
    )
    if m:
        for arg in m.group(1).split():
            if not arg.startswith("-"):
                pkg = re.sub(r"@[\d\.\^~>=<*].*$", "", arg)
                if pkg:
                    packages.append(("npm", pkg))

    # pip install
    pm = re.match(r"pip(?:3(?:\.\d+)?)?\s+install\s+(.+)", command, re.IGNORECASE)
    if pm:
        for arg in pm.group(1).split():
            if arg.startswith("-"):
                continue
            pkg = re.sub(r"[><=!~;@\[].*$", "", arg)
            if pkg:
                packages.append(("pip", pkg))

    return packages


def main():
    try:
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except Exception:
            sys.exit(0)

        tool_name  = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        if tool_name != "Bash":
            sys.exit(0)

        command = tool_input.get("command", "").strip()

        if not re.match(
            r"(?:npm\s+(?:install|i|add)|pnpm\s+add|yarn\s+add|bun\s+add|pip(?:3(?:\.\d+)?)?\s+install)",
            command, re.IGNORECASE,
        ):
            sys.exit(0)

        packages = extract_packages(command)
        if not packages:
            sys.exit(0)

        blockers, warnings = [], []

        for pkg_type, pkg_name in packages:
            if pkg_name.startswith("@") and "/" in pkg_name:
                continue  # 跳过合法 scope 包

            # 拼写攻击检测
            norm = normalize_pkg(pkg_name)
            real_pkg = None
            for typo, real in TYPOSQUATTING_PAIRS.items():
                if norm == normalize_pkg(typo):
                    real_pkg = real
                    break
            if real_pkg:
                blockers.append(f"🚨 [{pkg_name}] 疑似拼写攻击！你是否想安装 [{real_pkg}]？")
                continue

            # 可疑包名
            if any(re.search(p, pkg_name, re.IGNORECASE) for p in SUSPICIOUS_PATTERNS):
                blockers.append(f"🚨 [{pkg_name}] 包名包含可疑关键词，请确认来源")
                continue

            # 重要包建议锁定版本
            clean = pkg_name.lstrip("@").split("/")[-1].lower()
            if clean in LOCK_VERSION_PKGS:
                if pkg_type == "npm" and "--save-exact" not in command:
                    warnings.append(f"💡 [{pkg_name}] 生产依赖建议使用 --save-exact 锁定版本")
                elif pkg_type == "pip" and "==" not in command:
                    warnings.append(f"💡 [{pkg_name}] 建议使用 ==x.y.z 精确版本")

        if blockers:
            msg = "依赖安全检查发现风险，已阻止安装：\n\n" + "\n".join(blockers)
            msg += "\n\n请确认包名是否正确后重新安装。"
            sys.stderr.write(msg + "\n")
            sys.stderr.flush()
            sys.exit(2)

        if warnings:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": "⚠️ 依赖安全提醒：\n" + "\n".join(warnings),
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
