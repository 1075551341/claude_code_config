---
name: task-triage
description: 任务分类（简单/非简单两大类+使用类型细分，严格判定）。触发词：任务分诊 | 复杂度判定 | 简单还是复杂 | 五维判定 | 是否访谈
triggers: [任务分诊, 复杂度判定, 简单还是复杂, 五维判定, 是否访谈]
layer: skeleton
source: internal
loading_tier: L1
---

# 任务分类 task-triage

> P0 路由集（L1 常驻）。本 skill 是「简单/非简单」判定的**唯一 SSOT**；CLAUDE.md / gate_messages / using-superpowers 一律引用本文件，禁止各处复制矩阵正文。

## 分类树（两大类 → 使用类型）

```
任务
├── 简单（必须同时满足：单文件 + 白名单 + 五维全低）
│   ├── 文档类：拼写/格式/注释/文档补写
│   ├── 实现类：单一纯函数实现（无接口变更）
│   ├── 配置值类：配置值修改（非结构）
│   └── Bug类：可复现 + 根因明确 + 单文件
└── 非简单（任一条件不满足）
    ├── Bug类：多文件/根因不明/需复现 → triage(P0-P3) → systematic-debugging
    ├── 功能类：新功能/多文件实现 → grill → brainstorming → 五阶段全链
    ├── 架构类：架构/重构/跨模块设计 → grill → brainstorming
    ├── 配置类：配置结构/hook/rule/skill/agent/MANIFEST/依赖升级/数据迁移 → grill → brainstorming
    ├── 删除类：删除/移动/重命名文件 → grill 确认不可逆性
    └── 调研类：技术选型/深度调研 → deep-research（L3 双源）
```

## 五维判定矩阵（唯一 SSOT）

| 维度 | 低(1) | 中(2) | 高(3) |
|------|-------|-------|-------|
| ①文件数 | **=1** | 2–5 | >5 |
| ②变更风险 | 纯文本/格式/注释 | 单模块逻辑/配置值 | 配置结构/hook/rule/skill/agent/依赖升级/DB/API签名 |
| ③跨模块影响 | 无共享符号 | 局部共享 | 改接口/类型/MANIFEST depends_on 目标/多模块调用链 |
| ④需求歧义度 | 明确可复现 | 部分模糊 | 多义/缺成功标准/需用户决策 |
| ⑤不可逆性 | 可回退(增改) | git 可回滚 | 删除/覆盖/强推/数据迁移 |

## 判定顺序（严格收窄）

1. **文件数前置**：改动文件 ≠ 1 → 直接非简单（禁止 ≤3 放宽）
2. **黑名单命中 → 非简单**：删除/移动/重命名文件；改 hook/rule/skill/agent/MANIFEST/配置结构；依赖升级/数据迁移；改共享接口/类型签名；跨模块调用链
3. **白名单命中（单文件前提下）→ 简单**：文档类(拼写/格式/注释)；实现类(单一纯函数，无接口变更)；配置值类(非结构)；Bug类(可复现+根因明确)
4. **其余 → 五维计分**：任一维"高"→非简单；全"低"→简单；含"中"→grill 兜底
5. **无法判定 → 默认非简单**（兜底 grill）

**简单 = 单文件 + 白名单 + 五维全低，缺一不可。**

## Grill（非简单任务执行前必做）

非简单任务在 Read 任何实现类 skill 之前，必须先访谈用户（一次一问 + 推荐答案，沿用 brainstorming relentless interview 纪律）：

1. 需求目标与验收标准是什么？
2. 范围边界：可改什么、不可改什么？
3. 风险与不可逆点：哪些操作不可回退？
4. 优先级与约束：时间/兼容/性能限制？
5. 期望输出形态？

≤5 问收敛；grill 确认后仍需设计 → Read skills/brainstorming/SKILL.md（HARD-GATE：用户批准设计前禁止实现）。

## 路由（按使用类型）

| 大类 | 使用类型 | 路由 |
|------|----------|------|
| 简单 | 文档/实现/配置值/Bug(单文件可复现) | Read skills/change-impact-analysis → 执行 → 轻量验证 |
| 非简单 | Bug（多文件/根因不明） | Read skills/triage（P0-P3 分级，L3）→ Read skills/systematic-debugging |
| 非简单 | 功能/架构/配置/删除 | **grill 访谈** → Read skills/brainstorming → 五阶段全链 |
| 非简单 | 调研 | Read skills/deep-research（L3 双源） |

## 边界

- task-triage = 任务复杂度判定 + 需求级访谈（grill）；triage = Bug P0-P3 分级。互补不重叠。
- brainstorming = 设计级访谈（HARD-GATE 批准方案）；grill 只做需求澄清，不重复设计访谈。
- catalog/skills/grill-with-docs = 文档对齐拷问，与需求访谈语义不同。
