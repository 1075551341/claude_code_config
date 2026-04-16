---
name: dispatching-parallel-agents
description: 并行Agent调度，将独立子任务分配给多个Agent并行执行
triggers:
  - 并行执行
  - 多Agent
  - 并行调度
  - 子Agent分配
priority: P1
---
# 并行Agent调度

## 流程
1. 识别可并行的独立子任务
2. 为每个子任务构造精确的Agent上下文（不继承会话历史）
3. 并行启动子Agent
4. 收集结果，验证每个子Agent输出
5. 合并结果，处理冲突

## 原则
- 子Agent从不继承会话历史（避免上下文污染）
- 每个子Agent有明确的输入/输出契约
- 子Agent失败时隔离问题，不影响其他子Agent
- 合并时检测冲突，按优先级解决
