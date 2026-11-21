#!/usr/bin/env python3
"""
PreToolUse Hook: 安全拦截器
在 Bash / PowerShell / shell 命令执行前拦截明显危险操作（尽力而为，不替代原生权限）

exit 0 = 允许执行
exit 2 = 阻止执行（stderr 内容会发送给 Claude）

修复记录：
- FIX: 整体 BaseException 捕获，防止 sys.exit() 被误拦截
- FIX: json.loads 替代 json.load(sys.stdin) 避免 stdin 流问题
- FIX: sys.stdout.flush() 确保输出刷新
- FIX: 补充更多危险命令模式（curl/eval、生产环境 db 操作等）
- FIX: 改进敏感文件写入检测范围
"""
# source: shanraisshan/claude-code-best-practice
import json
import sys
import io
import re
import os

# ── stdout 安全包装 ───────────────────────────────────────────────────────────
try:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
except Exception as e:
    print(f"pre-bash-guard: stdout wrap failed ({type(e).__name__})", file=sys.stderr)

# ── Git 命令选项前缀（防 -C/--git-dir/--work-tree/-c 变体绕过；支持空格/等号分隔）─
_GIT_OPTS = r"(?:(?:-C|-c|--git-dir|--work-tree)(?:\s+|=)\S+(?:\s+|))*"

# ── 危险命令模式（阻止，exit 2）──────────────────────────────────────────────
DANGER_PATTERNS = [
    # 递归删除系统/用户目录
    (r"rm\s+.*-[rRfF]{1,4}\s+/$",                  "禁止删除根目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/\*",                 "禁止删除根目录所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+~\s*$",               "禁止删除用户主目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+~/?\*",               "禁止删除用户主目录所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+[\"']?C:\\\\?\*",     "禁止删除 C 盘所有文件"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/etc\b",              "禁止删除 /etc 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/usr\b",              "禁止删除 /usr 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/boot\b",             "禁止删除 /boot 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/var\b",              "禁止删除 /var 目录"),
    (r"rm\s+.*-[rRfF]{1,4}\s+/home\b",             "禁止删除 /home 目录"),
    # PowerShell removal of a filesystem root or the entire user home.
    (r"\b(?:Remove-Item|ri|del|erase)\b[^;\n]*-(?:Recurse|r)\b[^;\n]*(?:[A-Za-z]:[\\/][\"']?\s*$|\$HOME\b|\$env:USERPROFILE\b)", "禁止递归删除磁盘根或用户目录"),
    # 磁盘格式化
    (r"^format\s+[A-Za-z]:",                         "禁止格式化磁盘"),
    (r"^mkfs\b",                                      "禁止格式化分区"),
    (r"dd\s+if=.+of=/dev/[sh]d[a-z]",              "禁止 dd 写入块设备"),
    (r"dd\s+if=/dev/zero\s+of=",                    "禁止 dd 零写覆盖"),
    (r"shred\s+.*-[zun].*\s+/dev/",                "禁止 shred 覆盖设备"),
    # Git 强制推送保护（兜底，含 --dry-run 之外的所有 force 形式）
    (r"\bgit\s+" + _GIT_OPTS + r"push\s+(?!.*--dry-run).*--force(?:-with-lease)?\b",  "禁止 git push 强制推送"),
    # Git 历史重写
    (r"git\s+filter-branch\b",                      "禁止 filter-branch 重写历史（建议用 git filter-repo）"),
    (r"git\s+rebase\s+.*--root\b",                  "禁止 rebase --root 重写全部历史"),
    # Redis 危险操作
    (r"redis-cli\s+.*\bFLUSHALL\b",                "禁止清空所有 Redis 数据库"),
    (r"redis-cli\s+.*\bFLUSHDB\b",                 "禁止清空当前 Redis 数据库"),
    (r"redis-cli\s+.*CONFIG\s+SET\s+requirepass\s+[\"']{2}",
     "禁止清空 Redis 密码"),
    # 数据库危险 DDL
    (r"\bDROP\s+DATABASE\b",                        "禁止删除数据库（请手动执行）"),
    (r"\bDROP\s+TABLE\b",                           "禁止删除数据表（请手动执行）"),
    (r"\bTRUNCATE\s+TABLE\b",                       "禁止清空数据表（请手动执行）"),
    # 系统级危险命令
    (r":\(\)\{:\|:&\};:",                           "Fork Bomb 攻击，已拦截"),
    (r"chmod\s+-R\s+777\s+/",                       "禁止递归 chmod 777 根目录"),
    (r"chown\s+-R\s+\S+\s+/(?!home/\S+/\S+)",     "禁止递归修改系统目录所有权"),
    # 脚本直接管道执行
    (r"curl\s+[^|]+\|\s*(?:sudo\s+)?(?:ba)?sh\b",  "禁止 curl 管道直接执行脚本"),
    (r"wget\s+[^|]+\|\s*(?:sudo\s+)?(?:ba)?sh\b",  "禁止 wget 管道直接执行脚本"),
    (r"curl\s+[^|]+\|\s*python[23]?\b",            "禁止 curl 管道直接执行 Python 脚本"),
    # eval 执行下载内容
    (r"eval\s+[\"'`]\$\(curl",                      "禁止 eval 执行 curl 下载内容"),
    (r"eval\s+[\"'`]\$\(wget",                      "禁止 eval 执行 wget 下载内容"),
]

# ── 警告模式（不阻断，注入上下文提示）──────────────────────────────────────────
WARN_PATTERNS = [
    (r"sudo\s+rm\s+.*-[rRfF]",                     "sudo rm -rf 需谨慎，请确认目标路径"),
    (r"git\s+reset\s+--hard\b",                     "git reset --hard 会丢弃工作区修改，请确认"),
    (r"git\s+clean\s+.*-f",                         "git clean -f 会永久删除未跟踪文件"),
    (r"npm\s+run\s+(?:clean|purge|reset|nuke)\b",   "清理脚本可能删除构建产物，请确认"),
    (r"pkill\s+-9\b",                               "SIGKILL 强制终止进程，请确认目标"),
    (r"\bdropdb\b",                                  "dropdb 将永久删除整个数据库，请确认"),
    (r"mongo.*--eval.*db\.dropDatabase",            "dropDatabase 将清除整个数据库"),
    (r"git\s+stash\s+(?:drop|clear)\b",            "stash drop/clear 将永久删除暂存内容"),
    (r"docker\s+(?:system|volume|image)\s+prune\b", "docker prune 将删除未使用的资源，请确认"),
]

# ── 敏感文件写入保护 ──────────────────────────────────────────────────────────
SENSITIVE_WRITE_PATTERNS = [
    r"\.env\.(?:production|prod|staging|live)\b",
    r"(?:^|[\s/])id_rsa(?:$|[\s.])",
    r"(?:^|[\s/])id_ed25519(?:$|[\s.])",
    r"(?:^|[\s/])id_ecdsa(?:$|[\s.])",
    r"\.pem(?:$|[\s])",
    r"\.key(?:$|[\s])",
    r"\.pfx(?:$|[\s])",
    r"\.p12(?:$|[\s])",
    r"authorized_keys",
    r"(?:^|/)etc/(?:passwd|shadow|sudoers)\b",
]

WRITE_INDICATORS = [">", ">>", "tee ", " write ", "truncate "]

# ─── Encoding-misuse patterns (improper tool/command usage causing mojibake;
# warn-level injection with stable alternative guidance) ──────────────────────
ENCODING_MISUSE_PATTERNS = [
    # PS5.1 Set-Content/Out-File/Add-Content defaults to ANSI(GBK); CJK content gets mangled
    (r"\b(?:Set-Content|Add-Content|Out-File)\b",
     "shell 写文件易致编码乱码（PS5.1 默认 ANSI）— 改用 Edit/Write 工具写入内容"),
    # echo redirection: escaping/EOL/encoding all uncontrolled
    (r"\becho\b[^|;&]*>{1,2}\s*\S",
     "echo 重定向写文件易致编码/EOL 异常 — 改用 Edit/Write 工具写入内容"),
    (r"\btee\s+(?:-{1,2}\w+\s+)*(?!-)\S+",
     "tee 写文件易致编码异常 — 改用 Edit/Write 工具写入内容"),
    (r"<<\s*['\"]?\w+['\"]?\s*>?>",
     "heredoc 重定向写文件易致转义/编码异常 — 改用 Edit/Write 工具写入内容"),
    # Legacy PowerShell default encodings require explicit care.
    (r"(?:^|[;&|(]\s*)powershell(?:\.exe)?\b",
     "powershell.exe(PS5.1) 默认编码可能不同 — 使用项目支持的 shell 并明确 UTF-8"),
    # sed -i may break CRLF/BOM
    (r"\bsed\s[^|;&]*\s-i(?:\.|\b)",
     "sed -i 可能破坏 CRLF/BOM — 文件内容修改改用 Edit 工具"),
]


def _block(msg: str) -> None:
    """拦截：stderr + exit 2（PreToolUse 标准拒绝语义）。"""
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()
    sys.exit(2)


_GIT_VALUE_OPTS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env", "--exec-path"}
_WRAPPERS = {
    "sudo", "doas", "env", "command", "time", "nohup", "exec",
    "bash", "sh", "zsh", "pwsh", "powershell", "cmd",
    "timeout", "nice", "xargs", "busybox", "setsid", "stdbuf",
    "then", "do", "else", "elif", "{",
}


def _norm_token(token: str) -> str:
    base = token.replace("\"", "").replace("'", "").replace("\\", "/").lower()
    base = base.rsplit("/", 1)[-1]
    for suffix in (".exe", ".cmd", ".bat"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return base


def _expand_substitutions(command: str, tool_name: str = "Bash") -> str:
    """Inspect executable substitution bodies, preserving quoted literal text.

    PowerShell uses backticks as escapes, whereas Bash uses them for command
    substitution. This bounded inspection does not execute or fully parse a shell.
    """
    pending = command
    bodies: list[str] = []
    powershell = tool_name.lower() == "powershell"
    escape = "`" if powershell else "\\"
    pattern = r"\$\(([^()]*)\)" if powershell else r"\$\(([^()]*)\)|`([^`]*)`"
    for _ in range(3):
        visible: list[str] = []
        quote: str | None = None
        index = 0
        while index < len(pending):
            char = pending[index]
            if quote == "'":
                visible.append(" ")
                if char == "'":
                    quote = None
            elif char == escape and index + 1 < len(pending):
                visible.extend((" ", " "))
                index += 1
            elif char == "'" and quote is None:
                quote = "'"
                visible.append(" ")
            else:
                visible.append(char)
                if char == '"':
                    quote = None if quote == '"' else '"'
            index += 1
        matches = list(re.finditer(pattern, "".join(visible)))
        if not matches:
            break
        found = []
        for match in matches:
            start, end = match.span()
            offset = 2 if pending[start:start + 2] == "$(" else 1
            found.append(pending[start + offset:end - 1])
        bodies.extend(found)
        pending = "\n".join(found)
    # Separate complete bodies from their outer quoted arguments. Inline
    # replacement would hide a real substitution inside echo's quoted text.
    return command + ("\n" + "\n".join(bodies) if bodies else "")


def _split_shell_segments(command: str) -> list[str]:
    segments: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for char in command:
        if quote:
            buf.append(char)
            if char == quote:
                quote = None
            continue
        if char in "\"'`":
            quote = char
            buf.append(char)
            continue
        if char in ";&|\n":
            segments.append("".join(buf))
            buf = []
            continue
        buf.append(char)
    segments.append("".join(buf))
    return segments


def _git_segments(command: str, tool_name: str = "Bash"):
    expanded = _expand_substitutions(command, tool_name)
    for segment in _split_shell_segments(expanded):
        original = segment.replace("(", " ").replace(")", " ")
        if original.strip():
            yield original  # preserve quoted option values, e.g. git -C "path with spaces"
        normalized = re.sub(r"[\"'`]", "", original)
        if normalized != original and normalized.strip():
            yield normalized  # also inspect nested wrapper command strings


def _git_invocation(segment: str) -> tuple[str | None, list[str], dict[str, str]]:
    # Shell words can contain quotes after an equals sign, or in the middle
    # of a word. Keep quoted spaces together without treating Windows path
    # backslashes as POSIX escape characters. This is inspection, not execution.
    tokens: list[str] = []
    word: list[str] = []
    quote: str | None = None
    started = False
    for char in segment:
        if quote:
            if char == quote:
                quote = None
            else:
                word.append(char)
            started = True
        elif char in "\"'":
            quote = char
            started = True
        elif char.isspace():
            if started:
                tokens.append("".join(word))
                word = []
                started = False
        else:
            word.append(char)
            started = True
    if started:
        tokens.append("".join(word))
    if not tokens:
        return None, [], {}

    start = None
    for index, token in enumerate(tokens):
        base = _norm_token(token)
        if base == "git":
            if index == 0:
                start = index
                break
            first = _norm_token(tokens[0])
            if first in _WRAPPERS or "=" in first:
                start = index
                break
            return None, [], {}
    if start is None:
        return None, [], {}

    rest = tokens[start + 1 :]
    cursor = 0
    aliases: dict[str, str] = {}
    while cursor < len(rest):
        token = rest[cursor].replace("\"", "").replace("'", "")
        if token.startswith("-"):
            config = None
            if token == "-c" and cursor + 1 < len(rest):
                config = rest[cursor + 1]
            elif token.startswith("-c") and len(token) > 2:
                config = rest[cursor][2:].lstrip("=")
            if config and "=" in config:
                key, value = config.split("=", 1)
                if key.lower().startswith("alias."):
                    aliases[key[6:].lower()] = value
            if token in _GIT_VALUE_OPTS and "=" not in token:
                cursor += 2
            else:
                cursor += 1
            continue
        return token.lower(), rest[cursor + 1 :], aliases
    return None, [], {}


def _alias_forbidden(value: str, tool_name: str, depth: int) -> bool:
    # Git expands ordinary aliases as subcommands and ! aliases as shell programs.
    value = value.strip()
    body = value[1:] if value.startswith("!") else "git " + value
    return bool(_git_forbidden(body, tool_name, depth + 1))


def _git_forbidden(command: str, tool_name: str = "Bash", _depth: int = 0) -> str | None:
    """Inspect actual Git calls and their alias definitions; never execute input."""
    if _depth > 4:
        return "Git alias 展开超过检查上限；请用户检查后在自己的终端执行"
    for segment in _git_segments(command, tool_name):
        subcommand, args, aliases = _git_invocation(segment)
        if subcommand is None:
            continue
        if subcommand in ("commit", "stash"):
            return f"禁止 Agent 执行 git {subcommand}；请用户在自己的终端执行"
        if subcommand == "push" and not any(arg in ("--dry-run", "-n") for arg in args):
            return "禁止 Agent 执行 git push；请用户在自己的终端执行"
        for value in aliases.values():
            if _alias_forbidden(value, tool_name, _depth):
                return "禁止定义或执行含 commit/push/stash 的 git alias；请用户在自己的终端执行"
        if subcommand == "config":
            queries = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--list", "-l", "--unset", "--unset-all", "--remove-section", "--rename-section"}
            if any(arg in queries for arg in args) or (args and args[0] in {"get", "list", "unset", "remove-section", "rename-section"}):
                continue
            for index, arg in enumerate(args[:-1]):
                if arg.lower().startswith("alias.") and _alias_forbidden(args[index + 1], tool_name, _depth):
                    return "禁止定义含 commit/push/stash 的 git alias；请用户在自己的终端执行"
    return None

def main():
    try:
        # ── 读取 stdin ────────────────────────────────────────────────────
        try:
            raw = sys.stdin.read()
            data = json.loads(raw) if raw.strip() else {}
        except (ValueError, OSError) as exc:
            print(f"pre-bash-guard: invalid input ({type(exc).__name__})", file=sys.stderr)
            sys.exit(1)

        tool_name  = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        if tool_name not in {"Bash", "PowerShell", "Shell", "shell_command", "exec_command"}:
            sys.exit(0)

        command = tool_input.get("command", "").strip()
        if not command:
            command = tool_input.get("shell_command", "").strip()
        if not command:
            sys.exit(0)

        # ── Git 禁令：按命令分段解析，覆盖全局选项与管道/串联绕过 ──
        git_reason = _git_forbidden(command, tool_name)
        if git_reason:
            _block(f"[安全拦截] {git_reason}")

        # PowerShell accepts named parameters in any order. Guard the full roots,
        # while leaving ordinary workspace cleanup to the native approval layer.
        if (re.search(r"\b(?:Remove-Item|ri|rd|del|erase)\b", command, re.I)
                and re.search(r"-(?:Recurse|r)\b", command, re.I)
                and re.search(r"(?:\$HOME\b|\$env:USERPROFILE\b|[A-Za-z]:[\\/](?=[\"'\s]|$))", command, re.I)):
            _block("[安全拦截] 禁止递归删除磁盘根或用户目录")

        # ── 危险命令检测 ──────────────────────────────────────────────────
        for pattern, reason in DANGER_PATTERNS:
            try:
                if re.search(pattern, command, re.IGNORECASE | re.MULTILINE):
                    msg = f"[安全拦截] {reason}"
                    _block(msg)
            except re.error:
                continue

        # ── 敏感文件写入保护 ──────────────────────────────────────────────
        if any(ind in command for ind in WRITE_INDICATORS):
            for pat in SENSITIVE_WRITE_PATTERNS:
                try:
                    if re.search(pat, command, re.IGNORECASE):
                        msg = "[安全拦截] 禁止覆写敏感文件"
                        _block(msg)
                except re.error:
                    continue

        # ── 警告（不阻断，注入上下文）────────────────────────────────────
        warns = []
        for pattern, msg in WARN_PATTERNS:
            try:
                if re.search(pattern, command, re.IGNORECASE):
                    warns.append(f"⚠️  {msg}")
            except re.error:
                continue

        # ─── Encoding misuse (improper commands causing mojibake) ─────────
        for pattern, msg in ENCODING_MISUSE_PATTERNS:
            try:
                if re.search(pattern, command, re.IGNORECASE):
                    warns.append("[编码] " + msg)
            except re.error:
                continue

        if warns:
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": "安全警告（命令已允许执行，请确认意图）：\n" + "\n".join(warns),
                }
            }
            sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
            sys.stdout.flush()

    except SystemExit:
        raise
    except Exception as exc:
        print(f"pre-bash-guard: unable to inspect input ({type(exc).__name__})", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
