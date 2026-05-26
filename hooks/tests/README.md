# Hook 测试夹具

> **source**: [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) + [trailofbits/claude-code-config](https://github.com/trailofbits/claude-code-config)

## 用法

```powershell
Get-Content hooks/tests/fixtures/bash_rm_rf_blocked.json | python hooks/pre-bash-guard.py
# 预期: exit 2

Get-Content hooks/tests/fixtures/secret_paste_blocked.json | python hooks/_optional/pre-userprompt-secret-scan.py
# 预期: exit 2 (strict profile)
```

## 夹具

| 文件 | 测试目标 | source |
|------|----------|--------|
| bash_rm_rf_blocked.json | pre-bash-guard | trailofbits |
| bash_git_push_main_blocked.json | pre-bash-guard | trailofbits |
| secret_paste_blocked.json | pre-userprompt-secret-scan | dwarvesf |
