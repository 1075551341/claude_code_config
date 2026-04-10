# Agents 智能体

99 个专业化智能体，覆盖软件开发全流程。

基于以下开源项目优化整合：

- [anthropics/skills](https://github.com/anthropics/skills) - Anthropic 官方技能标准
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - 性能优化系统
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) - 实用技能集合
- [obra/superpowers](https://github.com/obra/superpowers) - 结构化开发工作流
- [Chalarangelo/30-seconds-of-code](https://github.com/Chalarangelo/30-seconds-of-code) - 代码片段集合

---

## 快速索引

| 领域         | 智能体                                                                                                                                                                                                                                                                                                                                  |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **前端**     | `frontend-developer`, `mobile-developer`, `react-reviewer`, `typescript-reviewer`, `ui-designer`, `typescript-pro`, `accessibility-expert`, `snippet-expert`                                                                                                                                                                            |
| **后端**     | `backend-developer`, `nodejs-reviewer`, `python-pro`, `python-reviewer`, `api-versioner`, `api-developer`, `claude-code-optimizer`                                                                                                                                                                                                      |
| **数据**     | `database-architect`, `data-engineer`, `sql-pro`, `migration-planner`, `database-reviewer`                                                                                                                                                                                                                                              |
| **测试**     | `qa-engineer`, `api-tester`, `code-quality-checker`, `code-reviewer`, `e2e-runner`, `tdd-guide`, `web-tester`                                                                                                                                                                                                                           |
| **安全**     | `security-scanner`, `security-reviewer`, `compliance-checker`                                                                                                                                                                                                                                                                           |
| **性能**     | `performance-analyzer`, `llm-optimizer`                                                                                                                                                                                                                                                                                                 |
| **架构**     | `software-architect`, `component-architect`, `microservice-architect`                                                                                                                                                                                                                                                                   |
| **运维**     | `devops-engineer`, `observability-engineer`, `terraform-specialist`, `incident-responder`, `cloud-cost-optimizer`, `cloud-architect`, `build-validator`                                                                                                                                                                                 |
| **工程**     | `git-expert`, `refactoring-expert`, `legacy-modernizer`, `git-workflow`, `build-error-resolver`                                                                                                                                                                                                                                         |
| **AI/数据**  | `ai-engineer`, `prompt-engineer`, `business-analyst`, `agentic-orchestrator`, `ml-engineer`, `workflow-automation`, `mcp-builder`, `harness-optimizer`                                                                                                                                                                                  |
| **文档**     | `doc-generator`, `doc-updater`, `docs-lookup`, `changelog-generator`, `meeting-notes`, `ppt-creator`, `email-writer`, `weekly-report`, `spec-writer`                                                                                                                                                                                    |
| **支付**     | `payment-integration`                                                                                                                                                                                                                                                                                                                   |
| **管理**     | `project-manager`, `context-manager`                                                                                                                                                                                                                                                                                                    |
| **图表**     | `mermaid-expert`                                                                                                                                                                                                                                                                                                                        |
| **调试**     | `systematic-debugging`                                                                                                                                                                                                                                                                                                                  |
| **用户体验** | `ux-researcher`, `context-manager`                                                                                                                                                                                                                                                                                                      |
| **游戏**     | `game-developer`                                                                                                                                                                                                                                                                                                                        |
| **嵌入式**   | `embedded-engineer`                                                                                                                                                                                                                                                                                                                     |
| **工作流**   | `brainstorming`, `subagent-driven-development`, `design-brainstorming`, `skill-creator`, `using-git-worktrees`, `finishing-a-development-branch`, `requesting-code-review`, `receiving-code-review`, `writing-plans`, `continuous-learning-v2`, `plankton-code-quality`, `execution-planner`, `verification-checker`, `parallel-agents` |
| **文件管理** | `file-organizer`                                                                                                                                                                                                                                                                                                                        |
| **业务分析** | `meeting-insights-analyzer`                                                                                                                                                                                                                                                                                                             |
| **语言专项** | `go-reviewer`, `java-build-resolver`, `cpp-reviewer`, `rust-reviewer`, `kotlin-reviewer`, `swift-reviewer`, `typescript-reviewer`, `python-reviewer`, `nodejs-reviewer`, `react-reviewer`                                                                                                                                               |

---

## 智能体详情

### AI 与数据

| 智能体                 | 职责           | 典型场景                                            |
| ---------------------- | -------------- | --------------------------------------------------- |
| `ai-engineer`          | AI 开发工程师  | LLM API 集成、RAG 系统、Prompt 工程、AI Agent 开发  |
| `prompt-engineer`      | Prompt 工程师  | 高质量 Prompt 设计、Few-shot 示例、系统提示词优化   |
| `business-analyst`     | 业务分析师     | 业务数据分析、KPI 指标计算、运营日报/周报、竞品分析 |
| `data-engineer`        | 数据工程师     | ETL 数据管道、数据仓库、BI 报表、Kafka 实时流处理   |
| `llm-optimizer`        | LLM 成本优化师 | Token 优化、成本分析、Prompt 压缩、API 调用效率提升 |
| `agentic-orchestrator` | Agent 编排师   | 多 Agent 协调、任务分解、Agent 工作流设计           |
| `mcp-builder`          | MCP 构建师     | MCP 服务器开发、工具集成、协议实现                  |
| `harness-optimizer`    | Harness 优化师 | Claude Code 配置优化、模型选择、工具权限配置        |

### 前端开发

| 智能体                 | 职责                | 典型场景                                                  |
| ---------------------- | ------------------- | --------------------------------------------------------- |
| `frontend-developer`   | 前端开发工程师      | Vue/React 组件、UI 界面、响应式布局、状态管理、动画效果   |
| `mobile-developer`     | 移动端开发工程师    | React Native、Flutter、UniApp、微信小程序、H5 移动页面    |
| `react-reviewer`       | React 审查专家      | React 组件审查、Hooks 规范、性能优化、TypeScript 代码评审 |
| `typescript-reviewer`  | TypeScript 审查专家 | TS/JS 代码审查、类型安全、异步正确性、安全性检查          |
| `ui-designer`          | UI/UX 设计师        | 界面设计、交互设计、设计规范、色彩方案、无障碍设计        |
| `typescript-pro`       | TypeScript 专家     | 复杂类型、泛型、tsconfig、类型安全 API、迁移与重构        |
| `accessibility-expert` | 无障碍设计专家      | WCAG 合规、屏幕阅读器适配、键盘导航、ARIA 优化            |

### 后端开发

| 智能体              | 职责             | 典型场景                                                             |
| ------------------- | ---------------- | -------------------------------------------------------------------- |
| `backend-developer` | 后端开发工程师   | REST API、数据库模型、认证授权、WebSocket、消息队列、定时任务        |
| `nodejs-reviewer`   | Node.js 审查专家 | Node.js/TypeScript 后端审查、Express/Koa/NestJS 代码质量、安全性检查 |
| `python-pro`        | Python 全栈专家  | Python 脚本、算法实现、CLI 工具、爬虫、自动化脚本、异步编程          |
| `python-reviewer`   | Python 审查专家  | Python/FastAPI/Flask/Django 代码审查、PEP8 规范、SQLAlchemy 操作     |
| `api-versioner`     | API 版本管理师   | API 版本策略、兼容性设计、版本迁移、废弃 API 管理                    |

### 数据库

| 智能体               | 职责           | 典型场景                                                      |
| -------------------- | -------------- | ------------------------------------------------------------- |
| `database-architect` | 数据库架构师   | 数据库架构设计、表结构、索引策略、分库分表、数据迁移          |
| `sql-pro`            | SQL 查询专家   | 复杂 SQL 查询、慢查询优化、窗口函数、存储过程、数据库迁移脚本 |
| `migration-planner`  | 数据迁移规划师 | 零停机迁移、迁移策略、数据一致性、回滚机制                    |
| `database-reviewer`  | 数据库审查专家 | 数据库设计审查、SQL查询优化、索引策略、数据一致性检查         |

### 测试与质量

| 智能体                 | 职责           | 典型场景                                                 |
| ---------------------- | -------------- | -------------------------------------------------------- |
| `qa-engineer`          | 测试工程师     | 测试用例编写、自动化测试、单元测试、E2E 测试、测试覆盖率 |
| `api-tester`           | API 测试专家   | API 接口测试、验证响应、冒烟测试、回归测试、性能测试     |
| `code-quality-checker` | 代码质量检查员 | 代码规范审查、命名规范、可读性分析、圈复杂度、代码坏味道 |
| `code-reviewer`        | 代码审查专家   | 综合代码审查、PR 评审、代码质量、安全性、性能、可维护性  |
| `tdd-guide`            | TDD 指导专家   | 测试驱动开发、RED-GREEN-REFACTOR 循环、测试先行开发      |
| `web-tester`           | Web 测试专家   | 前端功能测试、Playwright 自动化、UI 验证、交互测试       |

### 安全与性能

| 智能体                 | 职责         | 典型场景                                                        |
| ---------------------- | ------------ | --------------------------------------------------------------- |
| `security-scanner`     | 安全扫描专家 | 安全漏洞扫描、OWASP 检查、SQL 注入检测、XSS/CSRF 防护、安全审计 |
| `compliance-checker`   | 合规检查专家 | GDPR/HIPAA 合规、数据保护、隐私合规、合规审计                   |
| `performance-analyzer` | 性能分析师   | 性能瓶颈分析、内存泄漏排查、慢查询优化、Bundle 分析、渲染优化   |

### 架构与设计

| 智能体                   | 职责         | 典型场景                                                     |
| ------------------------ | ------------ | ------------------------------------------------------------ |
| `software-architect`     | 软件架构师   | 系统架构设计、技术选型、微服务拆分、数据库架构、技术规范制定 |
| `component-architect`    | 组件架构师   | 组件设计审查、耦合度分析、组件拆分、状态管理设计、Props 优化 |
| `microservice-architect` | 微服务架构师 | DDD 领域划分、服务边界设计、服务通信、服务治理               |

### 运维与 DevOps

| 智能体                   | 职责           | 典型场景                                                        |
| ------------------------ | -------------- | --------------------------------------------------------------- |
| `devops-engineer`        | DevOps 工程师  | CI/CD 流水线、Docker 配置、K8s 部署、GitHub Actions、Nginx 配置 |
| `observability-engineer` | 可观测性工程师 | 监控告警、Prometheus+Grafana、链路追踪、日志采集、APM           |
| `terraform-specialist`   | Terraform 专家 | Terraform 配置、云资源编排、VPC/ECS/RDS、IaC 架构、多环境管理   |
| `incident-responder`     | 故障响应专家   | 生产故障处理、服务宕机、性能下降、安全事件、应急响应            |
| `cloud-cost-optimizer`   | 云成本优化师   | AWS/Azure/GCP 成本分析、资源优化、预算控制                      |

### 工程效能

| 智能体                 | 职责               | 典型场景                                                           |
| ---------------------- | ------------------ | ------------------------------------------------------------------ |
| `git-expert`           | Git 专家           | 合并冲突处理、分支策略、commit 规范、代码回滚、rebase、cherry-pick |
| `refactoring-expert`   | 重构专家           | 代码重构、消除坏味道、拆解大函数、消除重复代码、提取公共逻辑       |
| `legacy-modernizer`    | 遗留代码现代化专家 | JS 升级 TS、CommonJS 转 ES Module、类组件迁移 Hooks、框架升级      |
| `git-workflow`         | Git 工作流专家     | 分支管理、提交规范、Git 冲突、版本控制、Git 提交、代码合并         |
| `build-error-resolver` | 构建错误解决专家   | Maven/Gradle构建错误、依赖冲突、编译问题修复                       |

### 文档与沟通

| 智能体                | 职责             | 典型场景                                                 |
| --------------------- | ---------------- | -------------------------------------------------------- |
| `doc-generator`       | 技术文档工程师   | API 文档、README、JSDoc/docstring、接口文档、部署文档    |
| `doc-updater`         | 文档更新专家     | 文档与代码同步、API文档更新、README维护、注释完善        |
| `docs-lookup`         | 文档查找专家     | API 文档查找、库文档查询、技术文档检索、代码示例获取     |
| `changelog-generator` | 变更日志生成专家 | Git 提交转变更日志、用户友好的发布说明、版本更新记录     |
| `meeting-notes`       | 会议记录员       | 会议纪要整理、行动项梳理、会议决议文档                   |
| `ppt-creator`         | 演示文稿专家     | PPT 大纲、项目汇报、技术方案演示、培训课件、年终总结     |
| `email-writer`        | 商务邮件 writer  | 工作邮件、商务信函、会议邀请、需求确认、问题升级、感谢信 |
| `weekly-report`       | 周报月报 writer  | 工作周报、月报、个人总结、成果提炼、述职报告             |
| `spec-writer`         | 规格文档编写专家 | 技术规格、实施计划、设计文档、功能规格文档               |

### 专项领域

| 智能体                 | 职责           | 典型场景                                                      |
| ---------------------- | -------------- | ------------------------------------------------------------- |
| `payment-integration`  | 支付集成专家   | 微信支付、支付宝、Stripe 集成、支付回调、退款功能、分账系统   |
| `project-manager`      | 项目经理       | 项目计划、任务拆分、需求分析、里程碑、风险评估、技术路线图    |
| `context-manager`      | 上下文管理师   | 会话状态持久化、跨会话恢复、上下文压缩、信息传递              |
| `mermaid-expert`       | 技术图表专家   | 流程图、时序图、架构图、ER 图、甘特图、状态图、类图、思维导图 |
| `systematic-debugging` | 系统化调试专家 | 四阶段系统化调试、根因分析、问题定位、故障诊断                |
| `execution-planner`    | 计划执行专家   | 实施计划制定、任务分解、开发排期、里程碑规划                  |
| `verification-checker` | 验证清单专家   | 提交前检查、合并验证、发布前验收、质量门禁                    |
| `parallel-agents`      | 并行Agent专家  | 批量任务分发、多Agent并发执行、任务依赖调度                   |

### 用户体验

| 智能体          | 职责        | 典型场景                                           |
| --------------- | ----------- | -------------------------------------------------- |
| `ux-researcher` | UX 研究专家 | 用户调研、可用性测试、用户访谈、旅程设计、体验度量 |

### 游戏开发

| 智能体           | 职责           | 典型场景                                              |
| ---------------- | -------------- | ----------------------------------------------------- |
| `game-developer` | 游戏开发工程师 | Unity/Unreal/Godot 开发、游戏逻辑、物理引擎、渲染优化 |

### 嵌入式开发

| 智能体              | 职责         | 典型场景                                     |
| ------------------- | ------------ | -------------------------------------------- |
| `embedded-engineer` | 嵌入式工程师 | ESP32/STM32 开发、物联网、传感器、固件、RTOS |

### 语言专项

| 智能体                | 职责                | 典型场景                                                         |
| --------------------- | ------------------- | ---------------------------------------------------------------- |
| `go-reviewer`         | Go 代码审查专家     | Go 语言特性、goroutine、channel、并发安全审查                    |
| `java-build-resolver` | Java 构建解决专家   | Maven/Gradle 构建错误、依赖冲突、编译问题修复                    |
| `cpp-reviewer`        | C++ 代码审查专家    | C++ 现代特性、内存安全、RAII、并发、性能优化审查                 |
| `rust-reviewer`       | Rust 代码审查专家   | Rust 所有权、借用检查、生命周期、并发安全审查                    |
| `kotlin-reviewer`     | Kotlin 代码审查专家 | Kotlin 惯用法、空安全、协程、Android/KMP 最佳实践审查            |
| `swift-reviewer`      | Swift 代码审查专家  | Swift 惯用法、Optionals、SwiftUI、Swift 并发审查                 |
| `typescript-reviewer` | TS 审查专家         | TypeScript 类型安全、异步正确性、泛型、高级类型审查              |
| `python-reviewer`     | Python 审查专家     | Python/FastAPI/Flask/Django 代码审查、PEP8 规范、SQLAlchemy 操作 |
| `nodejs-reviewer`     | Node.js 审查专家    | Node.js/TypeScript 后端审查、Express/Koa/NestJS 代码质量         |
| `react-reviewer`      | React 审查专家      | React 组件审查、Hooks 规范、性能优化、TypeScript 代码评审        |

---

## 使用方式

### 直接调用（Claude Code）

```
使用 [agent-name] agent 来 [任务描述]
```

### 编辑器配置

#### Cursor

```bash
# 创建 .cursorrules 合并多个agent
cat ~/.claude/agents/ai-engineer.md \
    ~/.claude/agents/frontend-developer.md > .cursorrules
```

Settings → Rules for AI → 粘贴 agent.md 内容

#### Windsurf

```bash
# 创建 .windsurfrules
cp ~/.claude/agents/ai-engineer.md .windsurfrules
```

Settings → Cascade → System Prompt

#### Trae / Qoder

```bash
mkdir -p .trae
cp ~/.claude/agents/ai-engineer.md .trae/system-prompt.md
```

### 使用示例

```bash
# AI 开发
使用 ai-engineer agent 集成 OpenAI API 实现智能客服

# 前端开发
使用 frontend-developer agent 创建用户管理仪表板

# 后端开发
使用 backend-developer agent 设计用户认证 API

# 代码审查
使用 code-reviewer agent 审查这个 PR

# 故障排查
使用 systematic-debugging agent 排查接口 500 错误

# 数据库设计
使用 database-architect agent 设计电商订单系统数据库
```

---

## 统计

| 类别          | 数量   |
| ------------- | ------ |
| AI 与数据     | 8      |
| 前端开发      | 7      |
| 后端开发      | 5      |
| 数据库        | 4      |
| 测试与质量    | 6      |
| 安全与性能    | 3      |
| 架构与设计    | 3      |
| 运维与 DevOps | 5      |
| 工程效能      | 4      |
| 文档与沟通    | 8      |
| 专项领域      | 8      |
| 用户体验      | 1      |
| 游戏          | 1      |
| 嵌入式        | 1      |
| 工作流        | 14     |
| 文件管理      | 1      |
| 业务分析      | 1      |
| 语言专项      | 10     |
| **总计**      | **78** |
