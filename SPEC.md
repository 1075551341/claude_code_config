# 规范索引

> CLAUDE.md 的详细索引，提供规则、Skill、Agent、Hooks 的快速查找
> CLAUDE.md 定义原则和规则（宪法），本文件提供完整索引和细节（法典）

---

## 规则速查

> 铁律 R1–R11 完整定义见 `CLAUDE.md → 铁律 R1–R11`

### 语言规则

| 规则                  | 适用         | 说明                             |
| --------------------- | ------------ | -------------------------------- |
| `RULES_PYTHON.md`     | Python       | PEP 8、类型注解、异步            |
| `RULES_TYPESCRIPT.md` | TypeScript   | 严格类型、接口泛型               |
| `RULES_GO.md`         | Go           | 错误处理、并发、CSP              |
| `RULES_RUST.md`       | Rust         | 所有权、借用、Result             |
| `RULES_CSHARP.md`     | C#           | LINQ、异步、依赖注入             |
| `RULES_DART.md`       | Flutter/Dart | 空安全、Widget、状态管理         |
| `RULES_JAVA.md`       | Java/Spring  | Spring Boot 约定、并发、Optional |
| `RULES_RUBY.md`       | Ruby/Rails   | Rails 约定、安全、Service Object |
| `RULES_MOBILE.md`     | 移动端       | Flutter/React Native/原生        |

### 领域规则

| 规则                | 适用     | 说明                             |
| ------------------- | -------- | -------------------------------- |
| `RULES_BACKEND.md`  | 后端 API | RESTful、Express/FastAPI         |
| `RULES_FRONTEND.md` | 前端 UI  | React/Vue、组件规范              |
| `RULES_DATABASE.md` | 数据库   | 表设计、查询规范、Migration      |
| `RULES_SECURITY.md` | 安全     | OWASP Top 10、密钥管理           |
| `RULES_TESTING.md`  | 测试     | 单元/集成/E2E、Mock              |
| `RULES_DEVOPS.md`   | CI/CD    | Docker/K8s/监控                  |
| `RULES_GIT.md`      | Git      | 分支策略、Commit 规范            |
| `RULES_WORKFLOW.md` | 工作流   | Phase 工作流、上下文腐败治理     |
| `RULES_MCP.md`      | MCP 配置 | 单一权威源、分组派生、一致性验证 |
| `RULES_AI.md`       | AI/LLM   | Prompt 工程、模型选择            |

---

## Skill 速查

### P0 强制 Skill

| Skill                            | 触发词                                 | 功能                               |
| -------------------------------- | -------------------------------------- | ---------------------------------- |
| `brainstorming`                  | 头脑风暴、方案设计、技术选型、架构决策 | 发散 ≥3 方案 → 六帽评估 → 收敛确认 |
| `verification-before-completion` | 完成、声称完成、验收                   | 交叉验证清单                       |
| `systematic-debugging`           | 调试、报错、bug、异常、崩溃            | 四阶段：信息 → 假设 → 验证 → 根因  |
| `using-superpowers`              | 开始对话、不确定技能、有什么技能       | 技能发现规则                       |

### P1 推荐 Skill

| Skill                         | 触发词                            | 功能                         |
| ----------------------------- | --------------------------------- | ---------------------------- |
| `test-driven-development`     | TDD、测试驱动、RED-GREEN-REFACTOR | RED→GREEN→REFACTOR 循环      |
| `writing-plans`               | 写计划、实施计划、任务分解        | 详细实施计划编写             |
| `executing-plans`             | 执行计划、实施任务                | 计划执行与进度跟踪           |
| `code-review`                 | 代码审查、PR 审查                 | 全流程代码审查               |
| `subagent-driven-development` | 并行 Agent、多任务、子代理        | 子代理调度与协调             |
| `orchestration-workflow`      | 编排工作流、任务编排              | 拆解 → 调度 → 整合 → 验证    |
| `context-engineering`         | 上下文工程、token 优化            | 上下文腐败治理+Token 优化    |
| `context-rot-guard`           | 上下文腐败、上下文退化            | 上下文腐败检测与治理         |
| `quality-gate`                | 质量门禁、质量检查                | 质量门禁检查与阻断           |
| `progress-tracking`           | 进度追踪、长任务进度、checkbox    | 长任务可视化进度追踪         |
| `memory-compression`          | 记忆压缩、上下文压缩、记忆持久化  | 跨会话记忆压缩与持久化       |
| `spec-validation`             | 规格验证、spec 验证               | 规格可执行验证               |
| `meta-prompting`              | 元提示、prompt 优化               | 元提示工程                   |
| `design-reasoning`            | 设计推理、UI 推理、设计决策       | UI/UX 设计推理与设计系统生成 |
| `eval-driven-dev`             | 评估驱动、盲比较、基准测试        | 评估驱动开发，量化验证方案   |

### P2 领域 Skill

#### 开发流程

`iterative-refinement` `collision-zone-thinking` `writing-skills` `skill-creator` `fix-skills` `must-execute-tools` `spec-first` `error-recovery` `incremental-arch`

#### 后端开发

`api-development` `api-mock` `api-documentation` `api-gateway` `api-testing` `db-migration` `database-design` `message-queue` `middleware` `nodejs-backend` `python-backend` `sql-database` `supabase-backend` `websocket-server` `scheduled-task`

#### 前端开发

`frontend-design` `react-component` `vue-development` `typescript` `state-management` `i18n-support` `theme-config` `web-artifacts-builder` `d3-visualization`

#### 移动开发

`flutter-development` `react-native` `android-development` `ios-native-dev` `ios-simulator` `capacitor-app` `mini-program` `uniapp-development` `mobile-deployment` `mobile-performance` `mobile-ui`

#### 测试与质量

`webapp-testing` `code-refactor` `code-standards` `error-handling` `performance-optimization` `regex-helper` `snippet-expert` `accessibility-audit`

#### 运维部署

`docker-devops` `kubernetes` `aws-cloud` `cloud-deployment` `nginx-config` `deploy-script` `logging-monitoring` `vercel-deploy`

#### 安全与取证

`security-best-practices` `security-forensics` `secure-deletion` `ffuf-fuzzing` `prompt-guard`

#### 数据与分析

`data-analysis` `data-validation` `deep-research` `content-research` `market-research` `lead-research-assistant` `financial-analysis` `clickhouse-analytics` `exa-search`

#### 文档办公

`docx` `pdf` `pptx` `xlsx` `office-docs` `changelog-generator` `doc-coauthoring` `report-generator` `metadata-extraction` `article-extractor`

#### 创意设计

`canvas-design` `theme-factory` `image-enhancement` `image-generation` `video-processing` `audio-processing`

#### 基础组件

`fullstack-auth` `env-config` `file-upload` `file-organization` `caching-strategy` `rate-limiting` `redis-cache` `mongodb` `search-engine` `monorepo-management` `linear-integration` `notion-integration` `slack-integration` `google-workspace`

#### AI 与开发

`prompt-engineering` `software-architecture` `architecture-diagrams` `mcp-builder` `agent-browser`

#### 自动化工具

`python-automation` `web-scraping` `rpa-automation`

#### 效率与生活

`life-assistant` `invoice-organizer` `meeting-insights-analyzer` `academic-paper-review` `daily-standup`

---

## Agent 速查

### 架构与设计

`architect` — 系统设计、架构决策

### 前端开发

`frontend-developer` `react-reviewer` `ux-design-expert`

### 后端开发

`backend-developer` `nodejs-reviewer` `python-reviewer` `python-pro` `typescript-pro` `typescript-reviewer`

### 数据

`database-expert` `data-engineer`

### 测试与质量

`qa-engineer`

### 安全

`security-reviewer` `compliance-checker`

### DevOps

`devops-engineer` `observability-engineer` `incident-responder` `cloud-cost-optimizer`

### 文档与沟通

`docs-expert` `changelog-generator` `business-writing`

### 工程效能

`git-expert` `refactoring-expert` `build-error-resolver` `file-organizer` `finishing-a-development-branch`

### AI 与数据

`ai-engineer` `agentic-orchestrator` `ml-engineer` `mcp-builder` `prompt-engineer`

### 上下文管理

`context-manager` `context-rot-monitor` `context-compressor` `spec-reviewer`

### 垂直领域

`payment-integration` `game-developer` `embedded-engineer` `mobile-developer` `performance-analyzer` `api-versioner`

### 语言专项

`go-reviewer` `rust-reviewer` `kotlin-reviewer` `swift-reviewer` `csharp-reviewer` `cpp-reviewer` `flutter-reviewer` `java-reviewer` `ruby-reviewer`

### 管理与流程

`planning-expert` `claude-code-optimizer` `connect` `artifacts-builder`

---

## Hooks 速查

### PreToolUse（18 个）

| Hook                        | 功能                    | 优先级 |
| --------------------------- | ----------------------- | ------ |
| `pre-context-injector`      | 上下文注入              | HIGH   |
| `pre-task-planner`          | 任务规划                | HIGH   |
| `pre-bash-guard`            | 危险命令拦截            | HIGH   |
| `pre-dep-checker`           | 依赖安全检查            | HIGH   |
| `pre-git-hook-bypass-block` | 阻止 git --no-verify    | HIGH   |
| `pre-prompt-guard`          | Prompt 安全防护         | HIGH   |
| `pre-config-protection`     | 配置文件保护            | MEDIUM |
| `pre-token-budget`          | Token 预算检查          | MEDIUM |
| `pre-commit-quality`        | 提交前质量检查          | MEDIUM |
| `pre-compact-state`         | 压缩前状态保存          | MEDIUM |
| `pre-tool-matcher`          | 工具匹配                | MEDIUM |
| `pre-workflow-guard`        | 工作流守卫              | MEDIUM |
| `pre-dev-server-blocker`    | 阻止 tmux 外 dev server | LOW    |
| `pre-git-push-reminder`     | push 前提醒             | LOW    |
| `pre-doc-file-warning`      | 文档文件警告            | LOW    |
| `pre-mcp-health-check`      | MCP 健康检查            | LOW    |
| `pre-observe-tool`          | 工具执行观察            | LOW    |
| `pre-suggest-compact`       | 建议压缩                | LOW    |

### PostToolUse（17 个）

| Hook                          | 功能             | 优先级 |
| ----------------------------- | ---------------- | ------ |
| `post-edit-format`            | 代码格式化       | HIGH   |
| `post-edit-lint`              | Lint+类型检查    | HIGH   |
| `post-secret-detector`        | 密钥泄露检测     | HIGH   |
| `post-test-runner`            | 自动测试运行     | HIGH   |
| `post-operation-log`          | 操作日志         | MEDIUM |
| `post-auto-commit`            | 自动提交格式     | MEDIUM |
| `post-edit-console-warn`      | console.log 警告 | MEDIUM |
| `post-batch-format-typecheck` | 批量格式化检查   | MEDIUM |
| `post-doc-reminder`           | 文档更新提醒     | LOW    |
| `post-build-analysis`         | 构建分析         | LOW    |
| `post-command-log-audit`      | 命令日志审计     | LOW    |
| `post-cost-tracker`           | 成本追踪         | LOW    |
| `post-dependency-audit`       | 依赖审计         | LOW    |
| `post-governance-capture`     | 治理捕获         | LOW    |
| `post-observe-result`         | 结果观察         | LOW    |
| `post-pr-logger`              | PR 日志          | LOW    |
| `post-record-js-edits`        | JS 编辑记录      | LOW    |

### Stop（12 个）

| Hook                          | 功能         | 优先级 |
| ----------------------------- | ------------ | ------ |
| `stop-daily-summary`          | 每日总结     | HIGH   |
| `stop-quality-gate`           | 质量门禁     | HIGH   |
| `stop-notify`                 | 桌面通知     | MEDIUM |
| `stop-debug-checker`          | Debug 检查   | MEDIUM |
| `stop-session-summary`        | 会话摘要     | MEDIUM |
| `stop-pattern-extraction`     | 模式提取     | MEDIUM |
| `stop-batch-format-typecheck` | 批量格式检查 | MEDIUM |
| `stop-readme-updater`         | README 更新  | LOW    |
| `stop-session-end-marker`     | 会话结束标记 | LOW    |
| `stop-persist-session`        | 会话持久化   | LOW    |
| `stop-cost-tracker`           | 成本追踪     | LOW    |
| `stop-evaluate-patterns`      | 模式评估     | LOW    |

### SessionStart（1 个）

`session-start-bootstrap` — 会话启动引导（HIGH）

---

## 目录结构

```
.claude/
├── CLAUDE.md              # 全局规范入口（宪法）
├── SPEC.md               # 本文件：规范索引（法典）
├── .mcp.json             # MCP 服务器权威配置
├── settings.json         # Claude Code 运行时配置
├── agents/               # Agent定义（56个）
├── skills/               # Skill定义（154个）
├── rules/                # 规则文件（22个）
├── hooks/                # Hook脚本（50个）
├── mcp/                  # MCP分组视图
│   └── servers.json      # toolset分组映射
├── templates/            # 模板文件
│   └── github-actions/   # GitHub Action工作流
├── experiences/          # 经验库
│   └── patterns/         # 已验证模式
├── scripts/              # 维护脚本
│   └── sync.ps1          # 跨编辑器同步
└── spec/                 # 非简单任务规格（按项目分目录）
```

---

## 来源索引

| 仓库                                                                                                | 主要贡献                                     | 整合位置                              |
| --------------------------------------------------------------------------------------------------- | -------------------------------------------- | ------------------------------------- |
| [anthropics/skills](https://github.com/anthropics/skills)                                           | Skill 标准格式、渐进披露                     | skills/                               |
| [obra/superpowers](https://github.com/obra/superpowers)                                             | Iron Law、子代理上下文构造、证据优先         | CLAUDE.md                             |
| [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)               | 分层 Rules、Instinct 系统、持续学习          | hooks/、experiences/                  |
| [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)                                       | Spec-First、可执行规格                       | skills/spec-validation/               |
| [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)                   | GitHub Action 集成、进度追踪                 | templates/、skills/progress-tracking/ |
| [github/github-mcp-server](https://github.com/github/github-mcp-server)                             | Toolset 分组、官方 GitHub MCP                | .mcp.json                             |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)             | Skill 分类策展                               | skills/README.md                      |
| [zilliztech/claude-context](https://github.com/zilliztech/claude-context)                           | Merkle DAG 增量同步、AST 感知分块            | CLAUDE.md 上下文压缩                  |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)             | 配置集合、多角色 PR 审查                     | agents/                               |
| [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done)                               | Phase 工作流、上下文腐败治理、Meta-Prompting | rules/、skills/meta-prompting/        |
| [Chalarangelo/30-seconds-of-code](https://github.com/Chalarangelo/30-seconds-of-code)               | 30 秒约束、示例驱动                          | CLAUDE.md 设计原则                    |
| [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)       | Karpathy 四原则                              | CLAUDE.md 思维准则                    |
| [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | 概念精确区分、编排工作流                     | 全局                                  |
| [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)                                   | 跨会话记忆持久化、压缩算法                   | skills/memory-compression/            |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)     | UI/UX 推理规则、设计系统生成                 | skills/frontend-design/               |
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow)                                       | Sub-Agent 编排、无冲突原则                   | agents/、rules/                       |

---

## 版本信息

- **版本**: 1.8.0
- **更新日期**: 2026-04-24
- **整合仓库数**: 16
- **总配置项**: agents(56) + skills(154) + hooks(50) + rules(22) + mcp(22)
- **本次更新**:
  - CLAUDE.md 精炼：补缺概念精确区分原则
  - 新增 skill：`design-reasoning`、`eval-driven-dev`、`spec-first`、`incremental-arch`、`error-recovery`、`accessibility-audit`
  - 新增 agent：`java-reviewer`、`ruby-reviewer`
  - 新增 rule：`RULES_JAVA.md`、`RULES_RUBY.md`
  - SPEC.md 补缺：Phase 间验证门禁
