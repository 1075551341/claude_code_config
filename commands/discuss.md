---
description: 需求讨论与对齐（①规划阶段入口）
---

# /discuss — 需求讨论与对齐

讨论需求、识别约束、对齐期望。非简单任务启动前必须先对齐。
访谈纪律（一次一问+推荐答案，≤5 问收敛；目标/约束/边界/优先级）SSOT → `skills/task-triage/SKILL.md`「Grill」节。

## 输出格式

```
## 需求摘要
[一句话核心目标]
## 验收标准
- [ ] 可量化标准 1
- [ ] 可量化标准 2
## 约束与边界
- 技术约束 | 时间/资源约束 | 不做的事: ...
```

<!-- spine:stage-gate -->
## 门控（派生自 config/workflow.yaml，改配置后 `python scripts/workflow.py render`，勿手改）

- 阶段：①规划 | skill：`skills/brainstorming/SKILL.md` | 角色：session
- 进入：非简单（triage 判定）
- 退出（全部满足才进入下一阶段）：
  - grill ≤5 问收敛，验收标准可量化
  - HARD-GATE：用户批准设计
<!-- /spine:stage-gate -->
