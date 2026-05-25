---
name: grill-with-docs
description: 对照 CONTEXT.md/ADR 拷问计划，逐条消解术语与决策并 inline 更新文档。触发：计划需对齐领域语言、stress-test 设计。excludes skill/brainstorming（非简单任务 P0 仍走 brainstorming）。
layer: catalog
source: mattpocock/skills
excludes: [skill/brainstorming]
---

# Grill With Docs（catalog 按需）

> 来源：mattpocock/skills | 与 `skill/brainstorming` 互补：brainstorming 定方案；本 skill 用已有领域文档拷问细节。

## 何时用

- 计划已定，需与 `CONTEXT.md` / ADR 对齐
- 术语模糊（Account vs User 等）
- brownfield 变更，代码与文档可能矛盾

## 流程

1. 探索 codebase + 现有 `CONTEXT.md`、`docs/adr/`
2. **一次一问**，等反馈再继续
3. 术语冲突 → 立即指出并消解
4. 决议即写：更新 `CONTEXT.md`（仅 glossary，无实现细节）
5. 不可逆决策 → 按需写 ADR（hard to reverse + surprising + real trade-off）

## CONTEXT.md 结构

```
/
├── CONTEXT.md              # 单上下文 glossary
├── CONTEXT-MAP.md          # 多上下文时指向各 CONTEXT
└── docs/adr/               # 架构决策记录
```

模板：`~/.claude/templates/artifacts/CONTEXT.md`

## 复制到项目

```powershell
python ~/.claude/scripts/migrate-from-legacy.py --project . --skill grill-with-docs
```

## 互斥

| 用 | 不用 |
|----|------|
| 方案已定后的文档对齐 | 替代 brainstorming HARD-GATE |
| + structured-artifacts | 重复写 STATE/ROADMAP 流程 |
