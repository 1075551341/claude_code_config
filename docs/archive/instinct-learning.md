# 历史资料：instinct-learning

> 2026-11-15 移出技能发现路径。仅用于了解旧设计，文中命令与组件不构成当前可执行配置。
> 旧版源归属保留；当前策略及来源核查见本轮研究记录。


# Instinct Learning v2

> **历史变体（v14）**：本文依赖的 `/instinct-*`、`/evolve`、Stop hook 与 MANIFEST 已移除；仅作历史参考，不按文中命令执行。

## 触发
- Stop hook 自动提取
- `/instinct-status` 查看学习结果
- `/instinct-import <file>` 导入
- `/instinct-export` 导出
- `/evolve` 聚类成 skill

## Instinct 结构
```yaml
name: pattern-name
confidence: 0.85  # 0-1，使用后递增
evidence: 3        # 成功使用次数
source: session    # session/import/evolve
created: 2026-05-23
actions: [...]
examples: [...]
```

## 置信度机制
- 初始 0.5
- 每次成功使用 +0.1（上限 1.0）
- 每次失败使用 -0.2
- <0.3 自动淘汰
- 30天未使用衰减 -0.05/周

## 进化
相关 instinct 聚类 → 生成新 skill → 进入 catalog

## ⑤ 持久化：/learn ↔ claude-mem 管道

学习产物写入可用记忆工具（如 claude-mem），实现**跨会话复用**（R14 记忆优先的供给侧）；无记忆工具则写入项目文档（R9）。

| 来源 | 触发 | 写入 claude-mem |
|------|------|-----------------|
| brainstorming 决策 | 设计批准 | observation（决策 + 理由 + 替代方案） |
| design-shotgun 品味 | taste_memory concern | observation（品味偏好 + 来源归属） |
| bug 修复模式 | systematic-debugging 收尾 | experiences/patterns/ + observation |
| 项目模式 | 会话结束/交付后 | observation（模式 + 适用条件） |

**observation 写入规范**（token 克制）：
- `title` ≤ 60 字，一句话概括模式
- `tags`：领域 + 模式类型（如 `[python, error-handling, retry]`）
- `body` ≤ 200 字：模式 + 适用条件 + 反例
- 高置信度（≥0.7、evidence≥3）才写入，避免噪声污染记忆库
- 写入前先 `claude-mem search` 去重；命中则更新 evidence，不新建

**检索闭环**：下次任务 R14 先查可用记忆工具（如 `claude-mem search`）→ 命中即复用，跳过重复分析（见 `skills/memory-compression`）。

## 与 stop-pattern-extraction 的关系

- **v1 自动提取**：`hook/stop-pattern-extraction`（Stop 时写入 experiences/patterns/）
- **v2 置信度进化**：本 skill（/instinct-*、/evolve），不替代 hook
- MANIFEST：`instinct_v2` excludes `stop-pattern-extraction` 的重复存储逻辑
