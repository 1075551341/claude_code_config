---
name: claude-config-optimization-pattern
date: 2026-04-21
confidence: 0.9
source: task
tags: [claude-code, configuration, sync, optimization]
---

# Claude Code 配置优化模式

## 背景

在维护 `.claude` 文件夹配置时，需要定期整合社区优秀仓库的优点，同时保持配置的可维护性和同步兼容性。

## 模式

### 1. 参考仓库分析流程

```text
收到优化请求
├─ 列出所有参考仓库
├─ 并行搜索各仓库核心贡献
├─ 对比当前配置，识别缺口
└─ 按优先级排序：CLAUDE.md > rules > skills/agents > hooks > mcp
```

### 2. 整合原则

- **去重**：已有功能不重复添加
- **溯源**：每个新增点标注来源仓库
- **兼容**：修改后验证 sync.ps1 同步脚本
- **简洁**：遵循 R10，不过度设计

### 3. 关键整合点

| 来源仓库 | 核心贡献 | 整合位置 |
| --- | --- | --- |
| superpowers | 证据优先、Iron Law | CLAUDE.md 交叉验证 |
| get-shit-done | Phase工作流、命令规范 | RULES_WORKFLOW.md |
| deer-flow | 子Agent状态机 | RULES_WORKFLOW.md |
| claude-mem | 记忆持久化 | CLAUDE.md 上下文管理 |
| everything-claude-code | Instinct系统、持续学习 | CLAUDE.md + experiences/ |
| github-mcp-server | Toolset分组 | mcp/servers.json |
| 30-seconds-of-code | "30秒"约束 | CLAUDE.md 设计原则 |
| karpathy-skills | 四原则 | CLAUDE.md 思维准则 |

### 4. 同步验证

修改后必须执行：

```powershell
~/.claude/scripts/sync.ps1 -DryRun
```

确认：

- skills/agents 链接正确
- CLAUDE.md 能正常写入
- rules 格式转换无报错
- MCP 配置同步正常

## 验证

本次优化验证通过：

- 修改 7 个文件
- sync.ps1 DryRun 成功
- 无 lint 错误

## 提取决策

- 置信度: 0.9
- 提取为: skill
- 原因: 配置优化是周期性需求，此模式可复用
