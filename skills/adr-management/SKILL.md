---
name: adr-management
description: 架构决策记录（ADR）管理。触发词：ADR | 架构决策 | 技术决策 | /adr
triggers: [架构决策, 技术选型, ADR, 为什么用]
layer: supplement
source: open-gsd/gsd-core
disable-model-invocation: true
loading_tier: L3
---

# ADR 架构决策记录

防止重复讨论已决定的技术选型。位置：`docs/ADR/YYYY-MM-DD-<kebab-title>.md`

## 触发

- 架构变更、技术选型、重大重构
- 讨论「为什么用 X 不用 Y」前 → 先 `/adr search`

## 格式

```markdown
# ADR-NNNN: <标题>

状态: [提议 | 已采纳 | 已废弃]
日期: YYYY-MM-DD

## 背景
为什么需要做这个决策

## 决策
我们决定...

## 后果
正面 / 负面影响

## 替代方案
考虑过的其他选项及拒绝理由
```

## 命令

| 命令 | 作用 |
|------|------|
| `/adr new <title>` | 创建新 ADR（自动编号+日期前缀） |
| `/adr list` | 列出 `docs/ADR/` 全部 ADR |
| `/adr search <query>` | Grep docs/ADR 防重复讨论 |

## 与 OpenSpec

- OpenSpec `design.md` → 功能级设计
- ADR → 跨功能、长期有效的架构决策
- 重大 ADR 应在 brainstorming HARD-GATE 后记录
