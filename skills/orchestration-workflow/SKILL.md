---
name: orchestration-workflow
description: 编排工作流 - 拆解→调度→整合→验证四阶段复杂任务编排
triggers:
  - 编排工作流
  - 任务编排
  - Agent协调
  - 多Agent编排
  - 复杂任务编排
do_not_trigger:
  - 单一文件修改
  - 简单bug修复
---

# 编排工作流

## Iron Law

- 子Agent不共享可变状态，通过消息传递协调
- 每个子Agent完成后必须输出结构化结果
- 失败子Agent最多重试2次，仍失败则隔离并报告

## 工作流

### Phase 1: 拆解（Decompose）

1. 分析任务，识别独立子目标与依赖关系
2. 为每个子目标指定最合适的 Agent
3. 为每个子目标定义明确的成功标准
4. 输出 DAG 任务图（含依赖关系和并行机会）

### Phase 2: 调度（Dispatch）

1. 无依赖子目标 → 并行派发子Agent（`dispatching-parallel-agents`）
2. 有依赖子目标 → 等待前置完成后派发
3. 每个子Agent注入精确上下文：不继承会话历史，只注入必要状态
4. 子Agent模型选择：简单任务用轻量模型，复杂任务用强模型

### Phase 3: 整合（Integrate）

1. 收集所有子Agent结果
2. 冲突检测：识别不同子Agent对同一文件的修改冲突
3. 冲突解决：按优先级合并或人工确认
4. 合并为最终交付物

### Phase 4: 验证（Validate）

1. 每个子目标独立验证（成功标准检查）
2. 整体集成验证（构建/类型/lint/测试）
3. 交叉验证清单全通过（见 CLAUDE.md）
4. 输出验证报告

## 输出格式

```json
{
  "task_id": "xxx",
  "phase": "integrate",
  "sub_agents": [
    { "name": "agent-1", "status": "completed", "result": "..." },
    { "name": "agent-2", "status": "completed", "result": "..." }
  ],
  "conflicts": [],
  "validation": { "build": "pass", "lint": "pass", "test": "pass" }
}
```
