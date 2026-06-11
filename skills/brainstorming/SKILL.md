---
name: brainstorming
description: 设计头脑风暴，HARD-GATE：批准前禁止实现。触发词：方案设计、架构、新功能、需求分析、设计决策。
triggers: [头脑风暴, 方案设计, 设计验证, brainstorming, 方案讨论, 新功能, 架构设计, 需求分析]
layer: skeleton
disable-model-invocation: true
loading_tier: L2
source: obra/superpowers
---

# 设计头脑风暴

> **HARD-GATE：用户批准设计前禁止任何实现。未经过 brainstorming 确认的方案不得进入 writing-plans。**

## 纪律

**Relentless interview（逐枝澄清）** — 对计划的每个分支 relentlessly 追问，直到与用户达成共识。沿设计树逐层解析依赖：先定边界再定方案，先定数据流再定接口。

**一次一问 + 推荐答案** — 每次只问一个问题；**每个问题附带你的推荐答案及理由**，便于用户确认或纠正，而非开放式甩锅。

**终态硬流转** — brainstorming 通过后必须 Read `writing-plans`。不可跳过规划直接实施。

## Red Flags（停下，你在跳过流程）

| 想法 | 现实 |
|------|------|
| "这只是一个简单问题" | 简单需求也有未经审视的假设 |
| "我需要先了解上下文" | 先问清楚再探索，不是相反 |
| "让我先看看代码库" | brainstorming 告诉你如何探索 |
| "让我先收集信息" | 先确认了解什么 |
| "这不需要正式流程" | 有流程的 skill 就该用它 |
| "我记得这个 skill" | skill 会更新，读当前版本 |
| "这不算真正的任务" | 动作 = 任务，检查 skill |
| "Skill 太重了" | 简单变复杂时才知道后悔 |
| "我只做这一件小事" | 先检查再做事 |

## 加载

**L2 门控**：非简单任务进入 ① 时 Read 本 skill。Cursor 靠 `disable-model-invocation` + 显式 Read。

## 规划内嵌探索（批准前完成）

| 类型 | 工具/加载 |
|------|-----------|
| 本地代码 | `codegraph_explore` / `codegraph_impact`（R17 优先） |
| 外部事实 L1 | Context7 / Exa 单次 |
| 多角度 L2 | Exa + Firecrawl 单页 |
| 深度 L3 | Read `skills/deep-research/SKILL.md` |
| 架构选型 | L3 `adr-management` → `docs/ADR/` |
| 历史 | R18 claude-mem search 先于外部调研 |

证据写入设计 doc「证据」节；不足则升级调研档位，不跳过 HARD-GATE。

## 流程

1. **探索项目上下文** — `codegraph_explore` → 必要时读文档/提交；禁止未探索大范围 Read
2. **逐问澄清** — 一次一个，理解目的/约束/成功标准
3. **2-3方案对比** — 含 trade-off 和推荐方案
4. **分段呈现设计** — 每段确认后继续
5. **写出设计文档** — 保存到 `spec/<project>/` 或 `.planning/phases/`
6. **设计自审** — 检查占位符、矛盾、歧义、范围
7. **用户审核设计文档** — 批准后进入 writing-plans

## 视觉伴侣（按需提示）

若讨论涉及 UI/布局/视觉对比，可提示："有些内容用浏览器看会更直观，需要视觉伴侣吗？(需要打开本地URL)"

## 输出

### 设计文档路径

- OpenSpec: `openspec/changes/<name>/design.md`
- GSD 多阶段: `.planning/phases/design.md`
- 轻量: `spec/<project>/design.md`

### 决策模板

```markdown
# [主题] 设计决策

## 背景
[问题背景]

## 决策
[最终方案]

## 理由
[为什么选择]

## 替代方案
[考虑过但未选的方案 + 淘汰原因]

## 后果
[决策影响 + 风险 + 缓解]
```

## 流转

```
brainstorming → 用户批准设计 → writing-plans → 执行
                ↑ 不批准则回到逐问澄清
```

禁止跳过 writing-plans 直接实施。
