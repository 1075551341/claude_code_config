# Agents 智能体

64 个专业化智能体，覆盖软件开发全流程。

基于以下开源项目优化整合：

- [anthropics/skills](https://github.com/anthropics/skills) - Anthropic 官方技能标准
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - 性能优化系统
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) - 实用技能集合
- [obra/superpowers](https://github.com/obra/superpowers) - 结构化开发工作流
- [Chalarangelo/30-seconds-of-code](https://github.com/Chalarangelo/30-seconds-of-code) - 代码片段集合

---

## 快速索引

| 领域         | 智能体                                                                                                                                                                                    |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **前端**     | `frontend-developer`, `mobile-developer`, `react-reviewer`, `typescript-reviewer`, `ux-design-expert`, `typescript-pro`, `accessibility-expert`, `snippet-expert`                          |
| **后端**     | `backend-developer`, `nodejs-reviewer`, `python-pro`, `python-reviewer`, `api-versioner`, `claude-code-optimizer`                                                                         |
| **数据**     | `database-expert`, `data-engineer`                                                                                                                                                        |
| **测试**     | `qa-engineer`, `code-review-workflow`, `tdd-guide`                                                                                                                                        |
| **安全**     | `security-reviewer`, `compliance-checker`                                                                                                                                                 |
| **性能**     | `performance-analyzer`                                                                                                                                                                    |
| **架构**     | `architect`                                                                                                                                                                               |
| **运维**     | `devops-engineer`, `observability-engineer`, `incident-responder`, `cloud-cost-optimizer`                                                                                                 |
| **工程**     | `git-expert`, `refactoring-expert`, `build-error-resolver`                                                                                                                                |
| **AI/数据**  | `ai-engineer`, `agentic-orchestrator`, `ml-engineer`, `workflow-automation`, `mcp-builder`                                                                                                |
| **文档**     | `docs-expert`, `changelog-generator`, `ppt-creator`, `business-writing`, `canvas-design`                                                                                                  |
| **支付**     | `payment-integration`                                                                                                                                                                     |
| **管理**     | `planning-expert`, `context-manager`                                                                                                                                                      |
| **图表**     | `mermaid-expert`                                                                                                                                                                          |
| **调试**     | `systematic-debugging`                                                                                                                                                                    |
| **游戏**     | `game-developer`                                                                                                                                                                          |
| **嵌入式**   | `embedded-engineer`                                                                                                                                                                       |
| **工作流**   | `brainstorming`, `skill-learning-system`, `finishing-a-development-branch`, `verification-checker`                                                                                        |
| **文件管理** | `file-organizer`                                                                                                                                                                          |
| **语言专项** | `go-reviewer`, `cpp-reviewer`, `rust-reviewer`, `kotlin-reviewer`, `swift-reviewer`, `csharp-reviewer`, `flutter-reviewer`, `typescript-reviewer`, `python-reviewer`, `nodejs-reviewer`, `react-reviewer` |

---

## 合并记录

以下智能体已合并（保留核心能力，消除重复）：

| 合并后名称 | 原智能体 | 合并原因 |
|-----------|---------|---------|
| `code-review-workflow` | code-reviewer + requesting-code-review + receiving-code-review | 代码审查全生命周期 |
| `database-expert` | database-architect + database-reviewer + sql-pro + migration-planner | 数据库全栈能力 |
| `planning-expert` | execution-planner + spec-writer + project-manager | 规划全链路 |
| `docs-expert` | doc-generator + docs-lookup | 文档生成+查找 |
| `business-writing` | email-writer + meeting-notes + weekly-report | 商务写作 |
| `ux-design-expert` | ui-designer + ux-researcher | UX设计+研究 |
| `skill-learning-system` | continuous-learning-v2 + skill-creator | 学习→创建连续流程 |
| `build-error-resolver` | + java-build-resolver | Java是构建子集 |
| `git-expert` | + using-git-worktrees | Worktree是Git子功能 |
| `agentic-orchestrator` | + subagent-driven-development | 核心编排能力重叠 |
| `claude-code-optimizer` | + harness-optimizer + tool-matcher | 工具/配置优化子能力 |
| `ai-engineer` | + prompt-engineer + langsmith-fetch | Prompt工程是AI核心子能力 |
| `devops-engineer` | + terraform-specialist | Terraform是DevOps IaC子领域 |
| `qa-engineer` | + e2e-runner | E2E是QA子领域 |

---

## 使用方式

### 直接调用（Claude Code）

```
使用 [agent-name] agent 来 [任务描述]
```

### 使用示例

```
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
```

---

## 统计

| 类别          | 数量   |
| ------------- | ------ |
| 前端开发      | 8      |
| 后端开发      | 6      |
| 数据          | 2      |
| 测试与质量    | 3      |
| 安全          | 2      |
| 性能          | 1      |
| 架构          | 1      |
| 运维与 DevOps | 4      |
| 工程效能      | 3      |
| AI/数据       | 5      |
| 文档与沟通    | 5      |
| 专项领域      | 2      |
| 管理          | 2      |
| 图表          | 1      |
| 调试          | 1      |
| 游戏          | 1      |
| 嵌入式        | 1      |
| 工作流        | 4      |
| 文件管理      | 1      |
| 语言专项      | 11     |
| **总计**      | **64** |
