---
name: claude-mem-maintenance
description: claude-mem 记忆维护。触发词：记忆维护 | mem维护 | 清理记忆 | 记忆去重
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

## 三层查询（R18 检索侧）

```
1. search 索引 → 识别关键 IDs
2. get_observations 详情
3. 避免重复 Read 已分析文件
```

## /learn ↔ mem 写入管道（供给侧）

R18 的另一半：学习产物**写入** observation 由 [`instinct-learning`](../instinct-learning/SKILL.md) §⑤ 持久化 定义。

- 写入规范：title ≤60 字 / tags 领域+类型 / body ≤200 字 / 高置信度才入库
- **写入前先 search 去重**：命中则更新 evidence，不新建（防记忆库膨胀）
- 来源：brainstorming 决策 · design-shotgun 品味 · bug 修复模式 · /learn 项目模式
- 闭环：写入（instinct-learning）→ 检索（本 skill R18）→ 复用 → 跳过重复分析

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
