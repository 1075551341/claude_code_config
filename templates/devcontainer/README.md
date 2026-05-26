# Devcontainer 隔离工作流

> **source**: [trailofbits/claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer)

## 何时使用

- 不可信代码库 / 开源贡献
- 需要 `--dangerously-skip-permissions` 等价能力但要求主机隔离

## 步骤

1. Clone [trailofbits/claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer)
2. 在 devcontainer 内运行 Claude Code
3. 叠加本仓库 `settings.json` deny 规则 + 每会话 `/sandbox`

## 与 ~/.claude 关系

- hooks/settings **不同步**到编辑器（见 SYNC_GUIDE.md）
- devcontainer 内可挂载 `~/.claude` 只读或项目级 `.claude/settings.json`
