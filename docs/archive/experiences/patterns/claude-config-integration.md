---
name: claude-config-integration-pattern
description: 多仓库整合到 .claude/ 的模式和流程
metadata:
  type: pattern
  confidence: 0.9
  source: manual-integration
---

## 场景

将 20+ GitHub 仓库的能力整合到 Claude Code 配置（`.claude/`）中，保持架构一致、功能不互博。

## 模式

### 1. 五柱骨架法

先确定骨架仓库（方法论文档），再填充其他仓库的能力：

1. **骨架**（methodology）：确定 5 个核心仓库作为架构支柱
2. **结构**（structure）：目录结构、格式规范、规则模板
3. **工具**（tooling）：性能优化、CI、MCP 服务器
4. **参考**（reference）：社区索引、代码片段、编排模式

### 2. Concern→Owner 映射

每个功能点必须映射为 MANIFEST.yaml 中的一个 concern，且只能有一个 owner：

- Owner 可以是 `skill/xxx`, `agent/xxx`, `hook/xxx`, `plugin/xxx`, `rules/xxx`
- 用 `excludes:` 标记明确不归谁管（防互博）
- 用 `note:` 记录边界和例外

### 3. 三层文档

- **CLAUDE.md** — 路由层（≤500 行），仅含优先级链、任务决策树、命令速查
- **SPEC.md** — 索引+溯源层，含 22 仓库映射、组件清单、规模约束
- **rules/** — 规则层，alwaysApply/lazy 两级，CORE.md 为骨架

### 4. 同步策略

- 主环境为 Claude Code
- CLAUDE.md + AGENTS.md + skills/ + agents/ → 软链接到其他编辑器
- rules/ → 格式转换复制（Cursor .mdc / Windsurf .md / Trae .md）
- hooks/commands/MCP → 不同步（编辑器专用）

## 验证

```bash
python scripts/validate_config.py  # 9 项检查
powershell scripts/sync.ps1 -DryRun  # 同步预演
```

## 反模式

- 一个 concern 有多个 owner → 左右手互博
- 重复定义 MCP 服务器在 settings.json 和 .mcp.json → 配置漂移
- skill 做 hook 的事 / hook 做 skill 的事 → 上下文混乱
