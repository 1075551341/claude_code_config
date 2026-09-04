"""R15：按语言选标准包管理器 + 按 OS 选稳定 CLI（Claude/Cursor SessionStart 共用）。"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys

LANG_PM = {
    "javascript": ("pnpm", "npm"),
    "python": ("uv", "pip"),
    "go": ("go", ""),
    "rust": ("cargo", ""),
    "dotnet": ("dotnet", ""),
    "java": ("mvn", "gradle"),
    "php": ("composer", ""),
    "ruby": ("bundle", "gem"),
}


def detect_project_language(cwd: str) -> str | None:
    def has(*names: str) -> bool:
        return any(os.path.isfile(os.path.join(cwd, n)) for n in names)

    if has("package.json", "pnpm-lock.yaml", "package-lock.json", "yarn.lock", "bun.lock", "bun.lockb"):
        return "javascript"
    if has("pyproject.toml", "requirements.txt", "uv.lock", "Pipfile"):
        return "python"
    if has("go.mod"):
        return "go"
    if has("Cargo.toml"):
        return "rust"
    if has("composer.json"):
        return "php"
    if has("Gemfile"):
        return "ruby"
    if has("pom.xml", "build.gradle", "build.gradle.kts"):
        return "java"
    try:
        names = os.listdir(cwd)
    except OSError as exc:
        print(f"⚠️ {exc}", file=sys.stderr)
        names = []
    if any(n.endswith(".csproj") or n.endswith(".sln") or n == "Directory.Packages.props" for n in names):
        return "dotnet"
    return None


def _tool_available(name: str) -> bool:
    return shutil.which(name) is not None


def detect_package_manager(cwd: str) -> str:
    lang = detect_project_language(cwd)
    if not lang:
        return "unknown"
    standard, fallback = LANG_PM[lang]
    if _tool_available(standard):
        return standard
    if fallback and _tool_available(fallback):
        return fallback
    return standard


def format_r15_lang(cwd: str) -> str | None:
    lang = detect_project_language(cwd)
    if not lang:
        return None
    standard, fallback = LANG_PM[lang]
    if _tool_available(standard):
        return f"R15 lang: {lang} → {standard}"
    if fallback and _tool_available(fallback):
        return f"R15 lang: {lang} → {fallback} (标准 {standard} 不可用，已兜底)"
    return f"R15 lang: {lang} → {standard}（PATH 未检测到；仍优先标准）"


def _run(args: list[str], timeout: int = 5) -> str:
    kwargs: dict = {"capture_output": True, "text": True, "timeout": timeout}
    if sys.platform == "win32":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        proc = subprocess.run(args, **kwargs)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"⚠️ r15_detect: {exc}", file=sys.stderr)
        return ""
    return (proc.stdout or "").strip()


def _pwsh_version(exe: str) -> tuple[int, int] | None:
    out = _run(
        [exe, "-NoProfile", "-Command", "$v=$PSVersionTable.PSVersion; '{0}.{1}' -f $v.Major,$v.Minor"]
    )
    match = re.search(r"(\d+)\.(\d+)", out)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def _bash_major(exe: str) -> int | None:
    out = _run([exe, "-c", "printf %s \"${BASH_VERSINFO[0]}\""])
    if out.isdigit():
        return int(out)
    return None


def detect_r15_os() -> str:
    plat = sys.platform
    if plat == "win32":
        exe = shutil.which("pwsh")
        if not exe:
            return "R15 OS: windows → pwsh 7.5+ 未安装（禁止 powershell.exe 5.1）"
        ver = _pwsh_version(exe)
        if ver is None:
            return "R15 OS: windows → pwsh（版本未知，目标 ≥7.5）"
        major, minor = ver
        label = f"{major}.{minor}"
        if (major, minor) >= (7, 5):
            return f"R15 OS: windows → pwsh {label}"
        if major >= 7:
            return f"R15 OS: windows → pwsh {label}（请升级到 7.5+；禁止回落 PS5.1）"
        return f"R15 OS: windows → pwsh {label}（低于 7；禁止 powershell.exe 5.1）"
    if plat == "darwin":
        if shutil.which("zsh"):
            brew = " + Homebrew" if shutil.which("brew") else "（Homebrew 不可用）"
            return f"R15 OS: macos → zsh{brew}"
        bash = shutil.which("bash")
        if bash:
            major = _bash_major(bash)
            extra = "（bash 5+ 兜底）" if major is not None and major >= 5 else "（bash 未达 5，请装 zsh/Homebrew）"
            return f"R15 OS: macos → bash{extra}"
        return "R15 OS: macos → unknown（请安装 zsh + Homebrew）"
    bash = shutil.which("bash")
    if bash:
        major = _bash_major(bash)
        if major is not None and major >= 5:
            return f"R15 OS: linux → bash {major}"
        if major is not None:
            return f"R15 OS: linux → bash {major}（请升级到 bash 5+）"
        return "R15 OS: linux → bash（版本未知，目标 5+）"
    return "R15 OS: linux → sh（bash 不可用）"
