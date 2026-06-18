---
name: triage
description: Bug分类分诊（L2）。触发词：bug报告 | issue分类 | 问题分诊 | 故障排查 | 什么错误 | 出错了 | 报错了 | triage
triggers: [问题分诊, bug分类, issue分类, triage, 问题报告, 用户反馈]
layer: supplement
source: mattpocock/skills
disable-model-invocation: true
loading_tier: L3
---

# 问题分诊

收到问题报告后，先分类再路由，禁止跳过分类直接修。

## 分诊流程

1. **复现判断** — 能复现吗？有最小复现步骤吗？
2. **范围评估** — 影响面多大？涉及哪些模块？
3. **分类** — bug / feature / 疑问 / 技术债
4. **严重度** — P0(阻断) / P1(严重) / P2(一般) / P3(低)
5. **指派方向** — 哪个领域/谁处理

## 状态机模型（mattpocock 源设计）

```
问题报告 → needs-triage (待分诊)
  ├─ 信息不足 → needs-info (生成追问模板，等待回复)
  ├─ 已确认 → ready-for-agent (自动路由)
  ├─ 需人工 → ready-for-human (标注理由 + 建议处理人)
  └─ 无效 → wontfix (记录原因，存档)

会话恢复时:
  needs-info → 检查是否有新回复 → needs-triage (重新分诊)
  ready-for-agent → 检查是否已修复 → 更新状态
```

## 输出格式

```
## 分诊报告
- 分类: [bug/feature/疑问/技术债]
- 严重度: [P0/P1/P2/P3]
- 状态: [needs-triage/needs-info/ready-for-agent/ready-for-human/wontfix]
- 影响范围: [模块/文件]
- 建议下一步: [skill/systematic-debugging | skill/brainstorming | 追问用户]
- 预估工时: [小(<1h)/中(1-4h)/大(>4h)]
```

## 路由规则

| 分类 | 状态 | 路由 |
|------|------|------|
| bug + 可复现 | ready-for-agent | → skill/systematic-debugging |
| feature 请求 | ready-for-agent | → skill/brainstorming |
| 疑问 | — | → 直接回答或追问 |
| 技术债 | ready-for-agent | → skill/improve-codebase-architecture |
| 信息不足 | needs-info | → 生成追问模板 |
| 需人工 | ready-for-human | → 标注理由 |

## 边界

- triage 只做分类，不做修复
- 不确定分类时标注 needs-info 并追问用户
- 与 systematic-debugging 的边界：triage 回答"这是什么问题"，debugging 回答"为什么发生"
