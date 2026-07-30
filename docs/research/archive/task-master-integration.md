# Task Master MCP 集成参考

> 来源: eyaltoledano/claude-task-master (27K stars) | 按需启用，非默认加载

---

## 概述

Task Master 是一个 AI 驱动的任务管理系统，通过 MCP 与 Claude Code 集成。支持 PRD 解析 → 结构化任务 → 复杂度分析 → 进度追踪。

## 安装

```bash
# 推荐: core 模式（7 工具，~5K tokens）
claude mcp add task-master-ai --scope user \
  --env TASK_MASTER_TOOLS="core" \
  -- npx -y task-master-ai

# 标准模式（15 工具，~10K tokens）
claude mcp add task-master-ai --scope user \
  --env TASK_MASTER_TOOLS="standard" \
  -- npx -y task-master-ai

# 自定义工具
claude mcp add task-master-ai --scope user \
  --env TASK_MASTER_TOOLS="get_tasks,next_task,set_task_status" \
  -- npx -y task-master-ai
```

## 三级加载

| 模式 | 工具数 | Token 占用 | 适用场景 |
|------|--------|-----------|----------|
| `core` | 7 | ~5K | 日常开发任务追踪 |
| `standard` | 15 | ~10K | 完整任务管理 |
| `all` | 36 | ~21K | 全功能（含研究/标签/依赖） |

**Core 工具**: `get_tasks`, `next_task`, `get_task`, `set_task_status`, `update_subtask`, `parse_prd`, `expand_task`

## Claude Code 模式优势

- 无需额外 API Key（使用本地 Claude 实例）
- 模型: `claude-code/opus` 和 `claude-code/sonnet`

## 使用方式

在 Claude Code 中通过自然语言交互：

```
"Initialize taskmaster-ai in my project"
"Parse the PRD and generate tasks"
"Show me the next task to work on"
"Mark task #3 as completed"
```

## 与 writing-plans skill 的关系

| 维度 | writing-plans (superpowers) | task-master |
|------|---------------------------|-------------|
| 定位 | 原子任务生成（2-5min/task） | 项目级任务追踪 |
| 粒度 | 细粒度代码任务 | 中粗粒度功能任务 |
| 输出 | 文件路径 + 代码 + 验证步骤 | 任务列表 + 状态 + 依赖 |
| 阶段 | ②规格 → ③执行 | 全阶段追踪 |
| 互斥 | — | 互补，非替代 |

**建议**: writing-plans 用于生成原子实施任务，task-master 用于项目级任务状态追踪。两者互补。
