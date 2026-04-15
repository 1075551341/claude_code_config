# Agents 智能体库

> 整合自 [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)、[obra/superpowers](https://github.com/obra/superpowers)

---

## 设计原则

### 1. 精确上下文构造

子代理应该从不继承会话历史，精确构造所需上下文。

### 2. 单一职责

每个 Agent 专注于特定领域或任务类型。

### 3. 模型选择策略

| 任务类型       | 模型选择     | 原因                         |
| -------------- | ------------ | ---------------------------- |
| 机械实现任务   | 快速便宜模型 | 孤立函数、清晰规格、1-2文件  |
| 集成和判断任务 | 标准模型     | 多文件协调、模式匹配、调试   |
| 架构设计和审查 | 最强模型     | 需要设计判断或广泛代码库理解 |

### 4. 状态处理

```
DONE              → 继续 spec 合规性审查
DONE_WITH_CONCERNS → 阅读担忧后决定
NEEDS_CONTEXT     → 提供缺失上下文并重新派遣
BLOCKED           → 评估阻止因素并重新派遣
```

---

## 标准 Agent 格式

````markdown
---
name: agent-name
description: |
  Use this agent when [specific triggering conditions]...
model: inherit
color: blue
tools:
  - Read
  - Write
  - Edit
  - Bash
---

# Agent Name

## 角色定位

[一句话说明Agent职责]

## 核心能力

1. **能力1**: 描述
2. **能力2**: 描述

## 工作流程

### 1. [步骤名]

[说明]

### 2. [步骤名]

[说明]

## 输出格式

```markdown
[输出模板]
```
````

## 注意事项

- 注意点1
- 注意点2

```

---

## Frontmatter 字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | **是** | 唯一标识符 |
| `description` | **是** | 触发条件描述 |
| `model` | 否 | 指定模型，默认 inherit |
| `color` | 否 | UI颜色标识 |
| `tools` | 否 | 可用工具列表 |

---

## Agent 分类（64个）

### 架构与设计（1个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `architect` | 系统设计、架构决策 | Read, Write, Grep |

### 前端开发（8个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `frontend-developer` | 前端开发 | Read, Write, Edit |
| `react-reviewer` | React代码审查 | Read, Grep |
| `ux-design-expert` | UI/UX设计 | Read, Write, Edit |
| `typescript-pro` | TypeScript专家 | Read, Write, Grep |
| `snippet-expert` | 代码片段 | Read, Write |
| `accessibility-expert` | 无障碍专家 | Read, Grep |
| `web-artifacts-builder` | Web构件 | Read, Write |
| `mermaid-expert` | 图表绘制 | Read, Write |

### 后端开发（6个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `backend-developer` | 后端开发 | Read, Write, Bash |
| `nodejs-reviewer` | Node.js审查 | Read, Grep |
| `python-pro` | Python专家 | Read, Write, Grep |
| `python-reviewer` | Python审查 | Read, Grep |
| `api-versioner` | API版本管理 | Read, Write, Grep |
| `websocket-server` | WebSocket开发 | Read, Write, Bash |

### 数据（2个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `database-expert` | 数据库设计/优化 | Read, Grep, Bash |
| `data-engineer` | 数据工程 | Read, Bash, Grep |

### 测试与质量（3个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `qa-engineer` | 测试策略/自动化 | Read, Write, Bash |
| `code-review-workflow` | 代码审查全流程 | Read, Grep |
| `tdd-guide` | TDD指导 | Read, Write |

### 安全（2个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `security-reviewer` | 安全审查 | Read, Grep |
| `compliance-checker` | 合规检查 | Read, Grep |

### DevOps（4个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `devops-engineer` | CI/CD、容器化 | Read, Bash |
| `observability-engineer` | 监控/可观测性 | Read, Bash, Grep |
| `incident-responder` | 故障响应 | Read, Bash |
| `cloud-cost-optimizer` | 云成本优化 | Read, Bash |

### 文档与沟通（5个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `docs-expert` | 文档生成 | Read, Write |
| `changelog-generator` | 变更日志 | Read, Write |
| `business-writing` | 商务写作 | Read, Write |
| `ppt-creator` | PPT创建 | Read, Write |
| `canvas-design` | 画布设计 | Read, Write |

### 工程效能（3个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `git-expert` | Git工作流 | Bash, Read |
| `refactoring-expert` | 重构 | Read, Write, Edit |
| `build-error-resolver` | 构建错误 | Read, Bash |

### AI与数据（5个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `ai-engineer` | AI/LLM应用 | Read, Write, Bash |
| `agentic-orchestrator` | 多Agent编排 | Read, Write |
| `ml-engineer` | 机器学习 | Read, Write, Bash |
| `mcp-builder` | MCP服务器开发 | Read, Write, Bash |
| `workflow-automation` | 工作流自动化 | Read, Write, Bash |

### 垂直领域（2个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `payment-integration` | 支付集成 | Read, Write |
| `game-developer` | 游戏开发 | Read, Write |

### 语言专项（11个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `go-reviewer` | Go审查 | Read, Grep |
| `rust-reviewer` | Rust审查 | Read, Grep |
| `kotlin-reviewer` | Kotlin审查 | Read, Grep |
| `swift-reviewer` | Swift审查 | Read, Grep |
| `csharp-reviewer` | C#审查 | Read, Grep |
| `flutter-reviewer` | Flutter审查 | Read, Grep |
| `typescript-reviewer` | TypeScript审查 | Read, Grep |
| `cpp-reviewer` | C++审查 | Read, Grep |
| `embedded-engineer` | 嵌入式 | Read, Write, Bash |
| `react-reviewer` | React审查 | Read, Grep |
| `nodejs-reviewer` | Node.js审查 | Read, Grep |

### 管理与流程（4个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `planning-expert` | 规划管理 | Read, Write |
| `context-manager` | 上下文管理 | Read, Write |
| `verification-checker` | 验证检查 | Read, Grep |
| `brainstorming` | 头脑风暴 | Read, Write |

### 效率与创意（2个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `file-organizer` | 文件整理 | Read, Bash |
| `snippet-expert` | 代码片段 | Read, Write |

### 移动开发（1个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `mobile-developer` | 移动开发 | Read, Write, Bash |

### 其他（5个）
| Agent | 场景 | 工具 |
|-------|------|------|
| `performance-analyzer` | 性能分析 | Read, Bash, Grep |
| `security-reviewer` | 安全审查 | Read, Grep |
| `claude-code-optimizer` | Claude Code优化 | Read, Write |
| `skill-learning-system` | 技能学习 | Read, Write |
| `deep-researcher` | 深度研究 | Read, Write, WebSearch |

---

## 使用方式

### 直接调用
```

使用 [agent-name] agent 来 [任务描述]

````

### 示例
```bash
# AI 开发
使用 ai-engineer agent 集成 OpenAI API 实现智能客服

# 前端开发
使用 frontend-developer agent 创建用户管理仪表板

# 代码审查
使用 code-review-workflow agent 审查这个 PR

# 数据库设计
使用 database-expert agent 设计电商订单系统数据库

# 规划
使用 planning-expert agent 制定项目实施计划
````

---

## Agent 模型选择指南

### 按任务复杂度

| 复杂度    | Agent                                 | 推荐模型 |
| --------- | ------------------------------------- | -------- |
| 简单/机械 | snippet-expert, file-organizer        | haiku    |
| 标准/协调 | frontend-developer, backend-developer | sonnet   |
| 复杂/架构 | architect, security-reviewer          | opus     |

### 按任务类型

| 类型   | Agent                        | 推荐模型    |
| ------ | ---------------------------- | ----------- |
| 实现类 | _\_developer, _\_engineer    | sonnet      |
| 审查类 | \*\_reviewer                 | sonnet/opus |
| 架构类 | architect                    | opus        |
| 研究类 | deep-researcher, ai-engineer | opus        |

---

## 双阶段审查模式（来自 superpowers）

```
Implementer → Spec Reviewer → Code Quality Reviewer → Task Complete
     ↓              ↓                ↓
   [FIX]         [FIX]            [FIX]
     ↓              ↓                ↓
   [REVIEW]      [REVIEW]         [REVIEW]
```

---

## PR Review 协议（来自 awesome-claude-code）

```
FETCH → CONTEXT → REVIEW → VALIDATE → DECIDE → REPORT → PUBLISH → OUTPUT
```

### 多角色审查

1. Product Manager Review → 商业价值/用户体验
2. Developer Review → 代码质量/性能
3. Quality Engineer Review → 测试覆盖/边缘case
4. Security Engineer Review → 漏洞/数据保护
5. DevOps Review → CI/CD/基础设施
6. UI/UX Designer Review → 视觉/可用性

---

## Phase 工作流（来自 get-shit-done）

```
Phase 1: Minimum Viable — 最小可工作切片
Phase 2: Core Experience — 完整快乐路径
Phase 3: Edge Cases — 错误处理、边界情况、打磨
Phase 4: Optimization — 性能、监控
```

---

## 来源

- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - 48个专业Agent
- [obra/superpowers](https://github.com/obra/superpowers) - 工作流系统
- [anthropics/skills](https://github.com/anthropics/skills) - 技能标准

---

## 统计

| 分类       | 数量   |
| ---------- | ------ |
| 架构与设计 | 1      |
| 前端开发   | 8      |
| 后端开发   | 6      |
| 数据       | 2      |
| 测试与质量 | 3      |
| 安全       | 2      |
| DevOps     | 4      |
| 文档与沟通 | 5      |
| 工程效能   | 3      |
| AI与数据   | 5      |
| 垂直领域   | 2      |
| 语言专项   | 11     |
| 管理与流程 | 4      |
| 效率与创意 | 2      |
| 移动开发   | 1      |
| 其他       | 5      |
| **总计**   | **64** |
