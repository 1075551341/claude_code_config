---
name: instinct-learning
description: Instinct v2 置信度学习系统，从会话提取可复用模式，带置信度评分。
layer: supplement
source: affaan-m/ECC
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

## 与 stop-pattern-extraction 的关系

- **v1 自动提取**：`hook/stop-pattern-extraction`（Stop 时写入 experiences/patterns/）
- **v2 置信度进化**：本 skill（/instinct-*、/evolve），不替代 hook
- MANIFEST：`instinct_v2` excludes `stop-pattern-extraction` 的重复存储逻辑
