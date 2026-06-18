---
name: claude-mem-maintenance
description: 记忆维护（L3）。触发词：记忆管理 | claude-mem | 记忆清理 | 记忆优化 | 记忆搜索
triggers: [claude-mem, 记忆搜索, mem search, 跨会话记忆]
layer: supplement
disable-model-invocation: true
loading_tier: L3
source: user-rules-migration
---

# Claude-Mem 使用与维护

> **L3**：记忆查询或维护任务时 Read。⑤学习默认 claude-mem pattern 提取；`instinct-learning` 仅显式「提取模式」信号。

## Endless Mode（P1 评估，默认关闭）

见 [ADR-2026-06-16](../../docs/ADR/2026-06-16-v10-ua-disabled-endless-mode.md) §决策 2。

- **不**默认修改 `CLAUDE_MEM_*` 启用 Endless Mode
- 长会话：GSD 70% 逻辑断点 + `/summarize` + claude-mem 检索
- **结论**：维持默认关闭 — 详见 ADR §决策 2 评估表

## 架构速览

- **Hooks** → worker-service（Bun，端口 `37700 + uid%100`）
- **DB**：`~/.claude-mem/claude-mem.db`
- **Search**：`plugin/skills/mem-search/SKILL.md` 或 HTTP API
- **多配置**：`CLAUDE_MEM_DATA_DIR` + 可选 `CLAUDE_MEM_WORKER_PORT`

## 三层查询（R18）

```
1. search 索引 → 识别关键 IDs
2. get_observations 详情
3. 避免重复 Read 已分析文件
```

## 隐私

- `<private>...</private>` 标签在 hook 层剥离，不入库

## 日常维护（维护任务时）

1. 根目录及嵌套 `package.json` 执行 `npm outdated`
2. 升级到 latest（含 major）；`npm audit fix`
3. `npm run build-and-sync`；验证 worker 启动与测试
4. 提交更新的 lock 文件

## 构建

```bash
npm run build-and-sync
```

## 文档

- 公开：https://docs.claude-mem.ai
- 源码：`plugins/marketplaces/thedotmack/` 或已安装 marketplace 路径
