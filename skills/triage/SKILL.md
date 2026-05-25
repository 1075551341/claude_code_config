---
name: triage
description: 问题分诊，Bug报告/Issue的第一道分类关卡，判断类型、严重度、指派方向
triggers: [问题分诊, bug分类, issue分类, triage, 问题报告, 用户反馈]
layer: supplement
source: mattpocock/skills
---

# 问题分诊

收到问题报告后，先分类再路由，禁止跳过分类直接修。

## 分诊流程

1. **复现判断** — 能复现吗？有最小复现步骤吗？
2. **范围评估** — 影响面多大？涉及哪些模块？
3. **分类** — bug / feature / 疑问 / 技术债
4. **严重度** — P0(阻断) / P1(严重) / P2(一般) / P3(低)
5. **指派方向** — 哪个领域/谁处理

## 输出格式

```
## 分诊报告
- 分类: [bug/feature/疑问/技术债]
- 严重度: [P0/P1/P2/P3]
- 影响范围: [模块/文件]
- 建议下一步: [skill/systematic-debugging | skill/brainstorming | 追问用户]
- 预估工时: [小/中/大]
```

## 路由规则

| 分类 | 路由 |
|------|------|
| bug + 可复现 | → skill/systematic-debugging |
| feature 请求 | → skill/brainstorming |
| 疑问 | → 直接回答或追问 |
| 技术债 | → skill/improve-codebase-architecture |

## 边界

- triage 只做分类，不做修复
- 不确定分类时标注"待确认"并追问用户
- 与 systematic-debugging 的边界：triage 回答"这是什么问题"，debugging 回答"为什么发生"
