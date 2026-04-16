# 规范索引

> 本文件是 CLAUDE.md 的详细索引，提供规则、Skill、Agent、Hooks 的快速查找
>
> **CLAUDE.md** 是全局规范入口，核心规则和流程定义在此

---

## 规则速查

### 核心规则（RULES_CORE.md）

| # | 规则 | 说明 |
|---|------|------|
| R1 | 任务未完成禁止停止 | 验证通过才算完成 |
| R2 | 修改后必须重新读取确认 | Read → Edit → Read |
| R3 | Bug修复：Grep全项目 → 全部修复 → 再Grep确认 | 零遗漏 |
| R4 | 配置变更：Grep所有引用方 → 全部同步 | |
| R5 | 失败后分析根因，同一方案失败 ≤ 2次 | |
| R6 | 非简单任务：头脑风暴 → 计划 → 执行 → 验证 | |
| R7 | 任何"已完成"前必须交叉验证 | |
| R8 | 高危操作必须用户确认 | |
| R9 | 禁止 cd + 重定向 / powershell -Command | |
| R10 | 简洁优先，最小代码解决 | 拒绝过度设计 |
| R11 | 安全默认，输入验证、最小权限、无硬编码 | |

### 语言规则

| 规则 | 适用 | 说明 |
|------|------|------|
| `RULES_PYTHON.md` | Python开发 | PEP 8、类型注解、异步 |
| `RULES_TYPESCRIPT.md` | TypeScript开发 | 严格类型、接口泛型 |
| `RULES_GO.md` | Go开发 | 错误处理、并发、CSP |
| `RULES_RUST.md` | Rust开发 | 所有权、借用、Result |
| `RULES_CSHARP.md` | C#开发 | LINQ、异步、依赖注入 |
| `RULES_DART.md` | Flutter/Dart | 空安全、Widget、状态管理 |
| `RULES_MOBILE.md` | 移动开发 | Flutter/React Native/原生 |

### 领域规则

| 规则 | 适用 | 说明 |
|------|------|------|
| `RULES_BACKEND.md` | 后端API开发 | RESTful、Express/FastAPI |
| `RULES_FRONTEND.md` | 前端UI开发 | React/Vue、组件规范 |
| `RULES_DATABASE.md` | 数据库操作 | 表设计、查询规范、Migration |
| `RULES_SECURITY.md` | 安全相关 | OWASP Top 10、密钥管理 |
| `RULES_TESTING.md` | 测试编写 | 单元/集成/E2E、Mock |
| `RULES_DEVOPS.md` | CI/CD/部署 | Docker/K8s/监控 |
| `RULES_GIT.md` | Git操作 | 分支策略、Commit规范 |
| `RULES_WORKFLOW.md` | 工作流/流程 | Phase工作流、任务分解、上下文腐败治理 |

---

## Skill 速查

### P0 强制Skill（不可跳过）

| Skill | 触发词 | 位置 | 功能 |
|-------|--------|------|------|
| `brainstorming` | 头脑风暴、方案设计、技术选型、架构决策 | `skills/brainstorming/` | 发散≥3方案 → 六帽评估 → 收敛确认 |
| `verification-before-completion` | 完成、声称完成、验收 | `skills/verification-before-completion/` | 交叉验证清单，铁律 |
| `systematic-debugging` | 调试、报错、bug、异常、崩溃 | `skills/systematic-debugging/` | 四阶段：信息→假设→验证→根因 |
| `using-superpowers` | 开始对话、不确定技能、有什么技能 | `skills/using-superpowers/` | 技能发现规则 |

### P1 推荐Skill

| Skill | 触发词 | 位置 | 功能 |
|-------|--------|------|------|
| `test-driven-development` | TDD、测试驱动、RED-GREEN-REFACTOR | `skills/test-driven-development/` | RED→GREEN→REFACTOR循环 |
| `writing-plans` | 写计划、实施计划、任务分解 | `skills/writing-plans/` | 详细实施计划编写 |
| `executing-plans` | 执行计划、实施任务 | `skills/executing-plans/` | 计划执行与进度跟踪 |
| `code-review` | 代码审查、PR审查、审查反馈 | `skills/code-review/` | 全流程代码审查 |
| `subagent-driven-development` | 并行Agent、多任务、子代理 | `skills/subagent-driven-development/` | 子代理调度与协调 |
| `dispatching-parallel-agents` | 并行调度、多Agent分发 | `skills/dispatching-parallel-agents/` | 并行Agent任务分发 |
| `finishing-a-development-branch` | 分支完成、合并PR | `skills/finishing-a-development-branch/` | 分支收尾流程 |
| `receiving-code-review` | 接收审查、审查反馈 | `skills/receiving-code-review/` | 处理审查意见 |
| `requesting-code-review` | 请求审查、PR审查 | `skills/requesting-code-review/` | 发起审查流程 |
| `context-rot-guard` | 上下文腐败、上下文退化 | `skills/context-rot-guard/` | 上下文腐败检测与治理 |
| `quality-gate` | 质量门禁、质量检查 | `skills/quality-gate/` | 质量门禁检查与阻断 |
| `prompt-guard` | Prompt安全、Prompt注入 | `skills/prompt-guard/` | Prompt安全防护 |

### P2 领域Skill

#### 开发流程
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `iterative-refinement` | 迭代精炼、持续改进 | `skills/iterative-refinement/` |
| `collision-zone-thinking` | 碰撞区思考、反转假设 | `skills/collision-zone-thinking/` |
| `inversion-exercise` | 反转练习、约束探索 | `skills/inversion-exercise/` |
| `meta-pattern-recognition` | 元模式、跨领域模式 | `skills/meta-pattern-recognition/` |
| `writing-skills` | 编写技能、技能开发 | `skills/writing-skills/` |

#### 后端开发
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `api-development` | API开发、RESTful | `skills/api-development/` |
| `api-mock` | Mock、API模拟 | `skills/api-mock/` |
| `db-migration` | 数据库迁移 | `skills/db-migration/` |
| `database-design` | 数据库设计 | `skills/database-design/` |
| `message-queue` | 消息队列、MQ | `skills/message-queue/` |
| `nodejs-backend` | Node.js后端 | `skills/nodejs-backend/` |
| `python-backend` | Python后端 | `skills/python-backend/` |
| `sql-database` | SQL查询 | `skills/sql-database/` |
| `websocket-server` | WebSocket开发 | `skills/websocket-server/` |

#### 前端开发
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `frontend-design` | 前端设计、UI开发 | `skills/frontend-design/` |
| `react-component` | React组件 | `skills/react-component/` |
| `vue-development` | Vue开发 | `skills/vue-development/` |
| `typescript` | TypeScript类型 | `skills/typescript/` |
| `state-management` | 状态管理 | `skills/state-management/` |
| `i18n-support` | 国际化 | `skills/i18n-support/` |
| `theme-config` | 主题配置 | `skills/theme-config/` |
| `web-artifacts-builder` | Web构件构建 | `skills/web-artifacts-builder/` |
| `d3-visualization` | D3可视化 | `skills/d3-visualization/` |

#### 移动开发
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `flutter-development` | Flutter开发 | `skills/flutter-development/` |
| `react-native` | React Native | `skills/react-native/` |
| `android-development` | Android开发 | `skills/android-development/` |
| `ios-native-dev` | iOS开发 | `skills/ios-native-dev/` |
| `capacitor-app` | Capacitor跨平台 | `skills/capacitor-app/` |
| `mini-program` | 微信小程序 | `skills/mini-program/` |
| `uniapp-development` | UniApp开发 | `skills/uniapp-development/` |

#### 测试与质量
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `testing-standards` | 测试标准 | `skills/testing-standards/` |
| `api-testing` | API测试 | `skills/api-testing/` |
| `webapp-testing` | Web应用测试 | `skills/webapp-testing/` |
| `code-refactor` | 代码重构 | `skills/code-refactor/` |
| `code-standards` | 代码规范 | `skills/code-standards/` |
| `error-handling` | 错误处理 | `skills/error-handling/` |
| `performance-optimization` | 性能优化 | `skills/performance-optimization/` |
| `regex-helper` | 正则表达式 | `skills/regex-helper/` |

#### 运维部署
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `docker-devops` | Docker容器化 | `skills/docker-devops/` |
| `kubernetes` | K8s部署 | `skills/kubernetes/` |
| `aws-cloud` | AWS云服务 | `skills/aws-cloud/` |
| `cicd-pipeline` | CI/CD配置 | `skills/cicd-pipeline/` |
| `nginx-config` | Nginx配置 | `skills/nginx-config/` |
| `deploy-script` | 部署脚本 | `skills/deploy-script/` |
| `logging-monitoring` | 日志监控 | `skills/logging-monitoring/` |

#### 安全与取证
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `security-best-practices` | 安全最佳实践 | `skills/security-best-practices/` |
| `security-forensics` | 安全取证 | `skills/security-forensics/` |
| `secure-deletion` | 安全删除 | `skills/secure-deletion/` |
| `ffuf-fuzzing` | Web安全测试 | `skills/ffuf-fuzzing/` |

#### 数据与分析
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `data-analysis` | 数据分析 | `skills/data-analysis/` |
| `deep-research` | 深度研究 | `skills/deep-research/` |
| `content-research` | 内容研究 | `skills/content-research/` |
| `market-research` | 市场调研 | `skills/market-research/` |
| `clickhouse-analytics` | ClickHouse分析 | `skills/clickhouse-analytics/` |

#### 文档办公
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `docx` | Word文档 | `skills/docx/` |
| `pdf` | PDF处理 | `skills/pdf/` |
| `pptx` | PPT创建 | `skills/pptx/` |
| `xlsx` | Excel处理 | `skills/xlsx/` |
| `changelog-generator` | 变更日志 | `skills/changelog-generator/` |
| `doc-coauthoring` | 文档协作 | `skills/doc-coauthoring/` |
| `report-generator` | 报告生成 | `skills/report-generator/` |

#### 创意设计
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `canvas-design` | 画布设计 | `skills/canvas-design/` |
| `brand-guidelines` | 品牌指南 | `skills/brand-guidelines/` |
| `algorithmic-art` | 算法艺术 | `skills/algorithmic-art/` |
| `theme-factory` | 主题工厂 | `skills/theme-factory/` |
| `image-generation` | 图像生成 | `skills/image-generation/` |

#### 基础组件
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `fullstack-auth` | 全栈认证 | `skills/fullstack-auth/` |
| `env-config` | 环境配置 | `skills/env-config/` |
| `data-validation` | 数据验证 | `skills/data-validation/` |
| `file-upload` | 文件上传 | `skills/file-upload/` |
| `caching-strategy` | 缓存策略 | `skills/caching-strategy/` |
| `rate-limiting` | 限流 | `skills/rate-limiting/` |
| `redis-cache` | Redis缓存 | `skills/redis-cache/` |
| `mongodb` | MongoDB | `skills/mongodb/` |
| `search-engine` | 搜索引擎 | `skills/search-engine/` |
| `monorepo-management` | Monorepo管理 | `skills/monorepo-management/` |

#### AI与开发
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `claude-api` | Claude API | `skills/claude-api/` |
| `prompt-engineering` | Prompt工程 | `skills/prompt-engineering/` |
| `software-architecture` | 软件架构 | `skills/software-architecture/` |
| `mcp-builder` | MCP服务器 | `skills/mcp-builder/` |

#### 自动化工具
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `python-automation` | Python自动化 | `skills/python-automation/` |
| `web-scraping` | 网页爬取 | `skills/web-scraping/` |
| `rpa-automation` | RPA自动化 | `skills/rpa-automation/` |
| `video-processing` | 视频处理 | `skills/video-processing/` |
| `audio-processing` | 音频处理 | `skills/audio-processing/` |
| `image-enhancement` | 图像增强 | `skills/image-enhancement/` |

#### 效率与生活
| Skill | 触发词 | 位置 |
|-------|--------|------|
| `file-organization` | 文件整理 | `skills/file-organization/` |
| `note-management` | 笔记管理 | `skills/note-management/` |
| `time-management` | 时间管理 | `skills/time-management/` |
| `meeting-productivity` | 会议效率 | `skills/meeting-productivity/` |
| `learning-resources` | 学习资源 | `skills/learning-resources/` |
| `health-tracking` | 健康追踪 | `skills/health-tracking/` |
| `personal-finance` | 个人财务 | `skills/personal-finance/` |
| `kaizen-improvement` | 持续改进 | `skills/kaizen-improvement/` |

---

## Agent 速查

### 架构与设计
| Agent | 场景 | 工具 |
|-------|------|------|
| `architect` | 系统设计、架构决策 | Read, Write, Grep |

### 前端开发
| Agent | 场景 | 工具 |
|-------|------|------|
| `frontend-developer` | 前端开发 | Read, Write, Edit |
| `react-reviewer` | React代码审查 | Read, Grep |
| `ux-design-expert` | UI/UX设计 | Read, Write, Edit |

### 后端开发
| Agent | 场景 | 工具 |
|-------|------|------|
| `backend-developer` | 后端开发 | Read, Write, Bash |
| `nodejs-reviewer` | Node.js审查 | Read, Grep |
| `python-reviewer` | Python审查 | Read, Grep |

### 数据
| Agent | 场景 | 工具 |
|-------|------|------|
| `database-expert` | 数据库设计/优化 | Read, Grep, Bash |
| `data-engineer` | 数据工程 | Read, Bash, Grep |

### 测试与质量
| Agent | 场景 | 工具 |
|-------|------|------|
| `qa-engineer` | 测试策略/自动化 | Read, Write, Bash |

### 安全
| Agent | 场景 | 工具 |
|-------|------|------|
| `security-reviewer` | 安全审查 | Read, Grep |
| `compliance-checker` | 合规检查 | Read, Grep |

### DevOps
| Agent | 场景 | 工具 |
|-------|------|------|
| `devops-engineer` | CI/CD、容器化 | Read, Bash |
| `observability-engineer` | 监控/可观测性 | Read, Bash, Grep |
| `incident-responder` | 故障响应 | Read, Bash |
| `cloud-cost-optimizer` | 云成本优化 | Read, Bash |

### 文档与沟通
| Agent | 场景 | 工具 |
|-------|------|------|
| `docs-expert` | 文档生成 | Read, Write |
| `changelog-generator` | 变更日志 | Read, Write |
| `business-writing` | 商务写作 | Read, Write |

### 工程效能
| Agent | 场景 | 工具 |
|-------|------|------|
| `git-expert` | Git工作流 | Bash, Read |
| `refactoring-expert` | 重构 | Read, Write, Edit |
| `build-error-resolver` | 构建错误 | Read, Bash |

### AI与数据
| Agent | 场景 | 工具 |
|-------|------|------|
| `ai-engineer` | AI/LLM应用 | Read, Write, Bash |
| `agentic-orchestrator` | 多Agent编排 | Read, Write |
| `ml-engineer` | 机器学习 | Read, Write, Bash |
| `mcp-builder` | MCP服务器开发 | Read, Write, Bash |
| `prompt-engineer` | Prompt工程/优化 | Read, Write |

### 垂直领域
| Agent | 场景 | 工具 |
|-------|------|------|
| `payment-integration` | 支付集成 | Read, Write |
| `game-developer` | 游戏开发 | Read, Write |
| `embedded-engineer` | 嵌入式 | Read, Write |

### 语言专项
| Agent | 场景 | 工具 |
|-------|------|------|
| `go-reviewer` | Go审查 | Read, Grep |
| `rust-reviewer` | Rust审查 | Read, Grep |
| `kotlin-reviewer` | Kotlin审查 | Read, Grep |
| `swift-reviewer` | Swift审查 | Read, Grep |
| `csharp-reviewer` | C#审查 | Read, Grep |
| `flutter-reviewer` | Flutter审查 | Read, Grep |
| `typescript-reviewer` | TypeScript审查 | Read, Grep |

### 管理与流程
| Agent | 场景 | 工具 |
|-------|------|------|
| `planning-expert` | 规划管理 | Read, Write |
| `context-manager` | 上下文管理 | Read, Write |
| `context-rot-monitor` | 上下文腐败监控 | Read, Bash |

### 效率与创意
| Agent | 场景 | 工具 |
|-------|------|------|
| `file-organizer` | 文件整理 | Read, Bash |

---

## Hooks 速查

### PreToolUse Hooks

| Hook | 功能 | 触发 | 优先级 |
|------|------|------|--------|
| `pre-context-injector` | 上下文注入 | Task/Write/Edit | HIGH |
| `pre-task-planner` | 任务规划 | Task/Bash/Write | HIGH |
| `pre-bash-guard` | Bash危险命令拦截 | Bash | HIGH |
| `pre-dep-checker` | 依赖安全检查 | Bash | HIGH |
| `pre-config-protection` | 配置文件保护 | Write/Edit | MEDIUM |
| `pre-token-budget` | Token预算检查 | 全局 | MEDIUM |
| `pre-git-hook-bypass-block` | 阻止git --no-verify | Bash | HIGH |
| `pre-commit-quality` | 提交前质量检查 | Bash | MEDIUM |
| `pre-dev-server-blocker` | 阻止tmux外运行dev server | Bash | LOW |
| `pre-git-push-reminder` | push前提醒 | Bash | LOW |
| `pre-doc-file-warning` | 文档文件警告 | Write | LOW |
| `pre-mcp-health-check` | MCP健康检查 | Bash | LOW |
| `pre-compact-state` | 压缩前状态保存 | PreCompact | MEDIUM |
| `pre-tool-matcher` | 工具匹配 | 全局 | MEDIUM |
| `pre-observe-tool` | 工具执行观察 | 全局 | LOW |
| `pre-suggest-compact` | 建议压缩 | 全局 | LOW |
| `pre-prompt-guard` | Prompt安全防护 | 全局 | HIGH |
| `pre-workflow-guard` | 工作流守卫 | Task/Write | MEDIUM |

### PostToolUse Hooks

| Hook | 功能 | 触发 | 优先级 |
|------|------|------|--------|
| `post-edit-format` | 代码格式化 | Edit/Write | HIGH |
| `post-edit-lint` | Lint+类型检查 | Edit/Write | HIGH |
| `post-secret-detector` | 密钥泄露检测 | Edit/Write | HIGH |
| `post-test-runner` | 自动测试运行 | Bash | HIGH |
| `post-operation-log` | 操作日志 | 全局 | MEDIUM |
| `post-auto-commit` | 自动提交格式 | Bash | MEDIUM |
| `post-build-analysis` | 构建分析 | Bash | LOW |
| `post-command-log-audit` | 命令日志审计 | Bash | LOW |
| `post-cost-tracker` | 成本追踪 | Stop | LOW |
| `post-dependency-audit` | 依赖审计 | Bash | LOW |
| `post-doc-reminder` | 文档更新提醒 | Stop | LOW |
| `post-edit-console-warn` | console.log警告 | Edit | MEDIUM |
| `post-governance-capture` | 治理捕获 | Stop | LOW |
| `post-observe-result` | 结果观察 | PostToolUse | LOW |
| `post-pr-logger` | PR日志 | Bash | LOW |
| `post-record-js-edits` | JS编辑记录 | Edit | LOW |
| `post-batch-format-typecheck` | 批量格式化检查 | Stop | MEDIUM |

### Stop Hooks

| Hook | 功能 | 优先级 |
|------|------|--------|
| `stop-notify` | 桌面通知 | MEDIUM |
| `stop-daily-summary` | 每日总结 | HIGH |
| `stop-readme-updater` | README更新 | LOW |
| `stop-debug-checker` | Debug检查 | MEDIUM |
| `stop-session-summary` | 会话摘要 | MEDIUM |
| `stop-session-end-marker` | 会话结束标记 | LOW |
| `stop-pattern-extraction` | 模式提取 | MEDIUM |
| `stop-persist-session` | 会话持久化 | LOW |
| `stop-cost-tracker` | 成本追踪 | LOW |
| `stop-evaluate-patterns` | 模式评估 | LOW |
| `stop-quality-gate` | 质量门禁 | HIGH |

### SessionStart Hooks

| Hook | 功能 | 优先级 |
|------|------|--------|
| `session-start-bootstrap` | 会话启动引导 | HIGH |

---

## 目录结构

```
.claude/
├── CLAUDE.md              # 全局规范入口
├── SPEC.md               # 本文件：规范索引
├── agents/               # Agent定义
│   ├── README.md          # Agent索引
│   ├── architect.md       # 架构师
│   ├── frontend-developer.md
│   ├── backend-developer.md
│   ├── database-expert.md
│   ├── ...
│   └── *_reviewer.md      # 代码审查Agent
├── skills/               # Skill定义
│   ├── README.md          # Skill索引
│   ├── brainstorming/
│   ├── verification-before-completion/
│   ├── systematic-debugging/
│   ├── test-driven-development/
│   ├── writing-plans/
│   ├── code-review/
│   └── .../               # 136个Skill
├── rules/                 # 规则文件
│   ├── README.md          # 规则索引
│   ├── RULES_CORE.md      # 核心规则
│   ├── RULES_GIT.md       # Git规则
│   ├── RULES_SECURITY.md  # 安全规则
│   ├── RULES_TESTING.md   # 测试规则
│   ├── RULES_BACKEND.md   # 后端规则
│   ├── RULES_FRONTEND.md  # 前端规则
│   ├── RULES_DATABASE.md  # 数据库规则
│   ├── RULES_DEVOPS.md    # DevOps规则
│   ├── RULES_PYTHON.md   # Python规则
│   ├── RULES_TYPESCRIPT.md
│   ├── RULES_GO.md
│   ├── RULES_RUST.md
│   ├── RULES_CSHARP.md
│   ├── RULES_DART.md
│   ├── RULES_MOBILE.md
│   └── RULES_WORKFLOW.md
├── hooks/                 # Hook脚本
│   ├── README.md          # Hook索引
│   ├── pre/               # PreToolUse
│   ├── post/              # PostToolUse
│   ├── stop/              # Stop
│   └── _editor_hook_launcher.py  # 编辑器适配
├── specs/                 # 任务规范
│   └── README.md
├── experiences/           # 经验库
│   ├── README.md
│   └── patterns/          # 已验证模式
│       └── YYYY-MM-DD-pattern-name.md
└── mcp/                   # MCP配置
    └── servers.json
```

---

## 来源索引

| 仓库 | Stars | 主要贡献 |
|------|-------|---------|
| [anthropics/skills](https://github.com/anthropics/skills) | 117k | Skill标准格式、frontmatter规范 |
| [obra/superpowers](https://github.com/obra/superpowers) | 154k | Iron Law、优先级链、子代理上下文构造 |
| [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | 140k | 分层Rules、Profile Hooks、Instinct系统 |
| [zilliztech/claude-context](https://github.com/zilliztech/claude-context) | - | Merkle DAG增量同步、AST感知分块 |
| [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) | 7k | 多认证方式、智能模式检测 |
| [github/mcp-server](https://github.com/github/mcp-server) | 29k | Toolset分组、Header驱动配置 |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | - | Skill分类、渐进披露设计 |
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | 62k | LangGraph状态机、sub-agent编排 |
| [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) | 53k | Phase工作流、上下文腐败治理 |
| [ Chalarangelo/30-seconds-of-code](https://github.com/Chalarangelo/30-seconds-of-code) | 127k | "30秒"约束、示例驱动 |
| [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | 39k | Karpathy四大原则、插件化CLAUDE.md |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | - | 配置集合、规则工作流 |

---

## 版本信息

- **版本**: 1.2.0
- **更新日期**: 2026-04-16
- **整合仓库数**: 12
- **总配置项**: agents(53) + skills(136) + hooks(50) + rules(18)
