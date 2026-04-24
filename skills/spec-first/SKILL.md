---
name: spec-first
priority: P2
triggers: [规格优先, spec-first, 规格驱动, spec driven, OpenSpec]
description: Spec 驱动开发，先写规格再实现，确保需求可执行验证
---

# 规格优先开发

## 核心流程

```
需求 → spec.md → design.md → tasks.md → 实现 → 验证
```

## 工作步骤

### 1. 编写 spec.md
- 定义"做什么"（What），禁止"怎么做"（How）
- 使用 EARS 格式：When [event], the [system] shall [response]
- 每条需求附带验收条件

### 2. 编写 design.md
- 定义"怎么做"（How）
- 架构图、接口设计、数据模型
- 与 spec.md 严格分离

### 3. 生成 tasks.md
- 从 design.md 派生实现任务
- 每个任务有明确验收标准
- 按依赖顺序排列

### 4. 实现与验证
- 按 tasks.md 逐步实现
- 每步完成后对照 spec.md 验收条件验证
- 全部通过才算完成

## 约束

- spec.md 禁止包含设计细节
- 未写 spec 禁止开始实现
- 验收条件必须可执行验证
