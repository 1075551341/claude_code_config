# Hook 测试夹具

> **source**: [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) + [trailofbits/claude-code-config](https://github.com/trailofbits/claude-code-config)

## 用法

```powershell
Get-Content hooks/tests/fixtures/bash_rm_rf_blocked.json | python hooks/pre-bash-guard.py
# 预期: exit 2

# strict 扩展扫描脚本（pre-userprompt-secret-scan.py）v11 起随 _archive/ 删除，
# 如需测试请先从 git 历史恢复该脚本，再:
# Get-Content hooks/tests/fixtures/secret_paste_blocked.json | python <恢复路径>/pre-userprompt-secret-scan.py
# 预期: exit 2 (strict profile)
```

## 夹具

| 文件 | 测试目标 | 预期 | source |
|------|----------|------|--------|
| bash_rm_rf_blocked.json | pre-bash-guard | exit 2（`rm -rf /` 命中危险模式） | trailofbits |
| bash_rm_rf_allowed.json | pre-bash-guard | exit 0（`rm -rf node_modules` 按设计放行） | v10.17 |
| bash_git_push_main_blocked.json | pre-bash-guard | exit 2 | trailofbits |
| bash_git_checkout_b_blocked.json | pre-bash-guard R19 | exit 2（`git checkout -b`） | v11.4.13 |
| bash_git_switch_c_blocked.json | pre-bash-guard R19 | exit 2（`git switch -c`） | v11.4.13 |
| bash_git_checkout_file_allowed.json | pre-bash-guard R19 | exit 0（`git checkout -- file` 路径还原） | v11.4.13 |
| secret_paste_blocked.json | pre-userprompt-secret-scan（脚本已随 \_archive/ 删除，git 历史可恢复） | exit 2（strict profile） | dwarvesf |
| issue_first_no_inject.json | pre-userprompt-issue-tracker（首次无注入） | exit 0 无输出 | v10.15 |
| issue_repeat_inject.json | pre-userprompt-issue-tracker（重复有注入） | exit 0 有注入 | v10.15 |
| mcp_serena_edit_tracked.json | post-edit-verify-tracker（MCP 写工具被追踪） | 状态文件记录该文件 | v10.17 |
| stop_untracked_change_blocked.json | stop-verification-gate（工作树未追踪变更） | exit 2 | v10.17 |

```powershell
# issue-tracker 手测（隔离状态目录，按顺序连跑两次同 fixture 即覆盖两个场景）
# 注意：Windows 上 $env:HOME 对 Python 的 Path.home() 无效，必须用 CLAUDE_HOME
$env:CLAUDE_HOME = "$env:TEMP\issue-tracker-test"
Get-Content hooks/tests/fixtures/issue_first_no_inject.json | python hooks/pre-userprompt-issue-tracker.py
# 预期: 无输出，exit 0
Get-Content hooks/tests/fixtures/issue_repeat_inject.json | python hooks/pre-userprompt-issue-tracker.py
# 预期: 输出 hookSpecificOutput.additionalContext 注入，exit 0
Remove-Item Env:\CLAUDE_HOME
```

```powershell
# v10.17 新增：MCP 写工具是否进入验证追踪（此前 serena/fs 完全绕过追踪器）
$env:CLAUDE_HOME = "$env:TEMP\verify-tracker-test"
Get-Content hooks/tests/fixtures/mcp_serena_edit_tracked.json | python hooks/post-edit-verify-tracker.py
Get-Content "$env:TEMP\verify-tracker-test\.state\verification-gate.json"
# 预期: edited_files 含 fixture 中的 relative_path
Remove-Item Env:\CLAUDE_HOME
```

```powershell
# v10.17 新增：工作树未追踪变更是否被 Stop 门阻断
# 在一次性 git 仓库里测，避免污染真实工作树
$repo = "$env:TEMP\stopgate-repo"
Remove-Item -Recurse -Force $repo -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $repo | Out-Null; Push-Location $repo
git init -q; "def ok(): return 1" | Set-Content app.py; git add -A
git -c user.email=t@t -c user.name=t commit -qm init
"def sneaky(): return 2" | Add-Content app.py        # 模拟 MCP/Shell 绕过 hook 的写入

$env:CLAUDE_HOME = "$env:TEMP\stop-gate-test"
New-Item -ItemType Directory -Force "$env:CLAUDE_HOME\.state" | Out-Null
# started_ts 必须是「刚刚」：交叉核查只统计会话开始后 mtime 变化的文件
$start = [int][double]::Parse((Get-Date -UFormat %s)) - 60
$state = @{ "fixture-untracked-change" = @{ ts=$start; started_ts=$start; cwd=$repo;
  edited_files=@(); verify_commands=@(); reviews=@(); blocks=0 } } | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText("$env:CLAUDE_HOME\.state\verification-gate.json", $state)
(@{ session_id="fixture-untracked-change"; cwd=$repo; transcript_path="" } | ConvertTo-Json) |
  python $HOME\.claude\hooks\stop-verification-gate.py
# 预期: exit 2，stderr 含「工作树存在 hook 未追踪的代码变更（MCP/Shell 写入）：app.py」
# 变体：session_id 换成状态文件里不存在的值 + 传入真实 transcript_path，应同样 exit 2
#       （追踪器一次都没触发的场景，退回 transcript 创建时间作为会话起点）
Pop-Location; Remove-Item Env:\CLAUDE_HOME
```
