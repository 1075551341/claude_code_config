---
name: instinct-learning
description: 本能学习（Ω-提示词优化器）。触发词：instinct learning | 本能学习 | 提示词优化 | 自我改进
layer: supplement
source: affaan-m/ECC
disable-model-invocation: true
loading_tier: L3
---

# Instinct Learning v2

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

学习产物必须写入 claude-mem，实现**跨会话复用**（R18 记忆优先的供给侧）。

| 来源 | 触发 | 写入 claude-mem |
|------|------|-----------------|
| brainstorming 决策 | 设计批准 | observation（决策 + 理由 + 替代方案） |
| design-shotgun 品味 | taste_memory concern | observation（品味偏好 + 来源归属） |
| bug 修复模式 | systematic-debugging 收尾 | experiences/patterns/ + observation |
| /learn 项目模式 | ⑤ 学习阶段 | observation（模式 + 适用条件） |

**observation 写入规范**（token 克制）：
- `title` ≤ 60 字，一句话概括模式
- `tags`：领域 + 模式类型（如 `[python, error-handling, retry]`）
- `body` ≤ 200 字：模式 + 适用条件 + 反例
- 高置信度（≥0.7、evidence≥3）才写入，避免噪声污染记忆库
- 写入前先 `claude-mem search` 去重；命中则更新 evidence，不新建

**检索闭环**：下次任务 R18 先 `claude-mem search` → 命中即复用，跳过重复分析（见 `skills/claude-mem-maintenance`）。

## 与 stop-pattern-extraction 的关系

- **v1 自动提取**：`hook/stop-pattern-extraction`（Stop 时写入 experiences/patterns/）
- **v2 置信度进化**：本 skill（/instinct-*、/evolve），不替代 hook
- MANIFEST：`instinct_v2` excludes `stop-pattern-extraction` 的重复存储逻辑
