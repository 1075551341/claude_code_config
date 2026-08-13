# Catalog INDEX — 变体库一页式清单

> **权威 vs 变体**：`skills/` `agents/` `rules/` 是权威实现，会被路由加载；
> 本目录是**变体库**，不参与全局加载，只在 `migrate-from-legacy.py --skill|--agent|--rule`
> 复制到项目 `.claude/` 时使用。同名项一律以顶层权威版为准。

规模：skills 107 / agents 48 / rules 15

## 同名项消歧（权威在顶层，此处为变体，勿加载）

| 类型 | 同名项 |
| ---- | ------ |
| skills | `deep-research`, `git-workflow` |
| agents | `ceo-reviewer`, `designer`, `eng-reviewer`, `qa`, `security-reviewer` |
| rules | （无） |

## Skills（107）

| 名称 | 说明 |
| ---- | ---- |
| `accessibility-audit` | 无障碍审计，检查 WCAG 合规性并生成修复建议 |
| `android-development` | Android原生应用开发、Kotlin/Java编程、Jetpack组件使用 |
| `api-development` | 设计RESTful API、实现API端点、编写后端接口 |
| `api-documentation` | API文档编写规范，编写清晰、完整的RESTful API文档 |
| `api-gateway` | API网关配置与管理 |
| `api-mock` | 生成Mock数据、模拟API响应、创建测试数据、使用Faker.js/Mock.js |
| `api-testing` | 测试API接口、执行接口测试、验证API响应 |
| `article-extractor` | 从网页提取完整文章内容和元数据 |
| `aws-cloud` | 部署AWS云服务、配置AWS资源、编写CloudFormation/IAM策略、使用AWS CLI/SDK |
| `browser-qa` | 浏览器QA测试，真实浏览器点击验证，发现bug并原子提交修复。 |
| `caching-strategy` | 设计缓存策略、使用Redis缓存、配置CDN缓存、解决缓存穿透/雪崩/击穿问题 |
| `capacitor-app` | 开发混合移动应用、使用Capacitor/Ionic框架、将Web应用打包为移动应用 |
| `changelog-generator` | 生成变更日志 |
| `cicd-pipeline` | 配置CI/CD流水线、设置GitHub Actions/GitLab CI、实现自动化构建部署 |
| `claude-api` | Claude API / Anthropic SDK 开发指南。触发：使用 Claude API、Anthropic SDK、构建 AI 应用、Managed Agents |
| `claude-to-deerflow` | deer-flow 外部编排引擎桥接。触发词：deer-flow | 外部编排 | LangGraph | 长时任务 | /deer-flow |
| `code-refactor` | 重构代码 |
| `code-standards` | 制定代码规范 |
| `command-reference` | 常用CLI命令速查表 |
| `content-research` | 提取文章内容 |
| `d3-visualization` | 创建D3.js数据可视化图表 |
| `data-analysis` | 分析CSV/Excel数据、统计计算、数据可视化、生成数据报告、汇总数据洞察 |
| `data-validation` | 验证输入数据、校验请求参数、使用Zod/Joi/Pydantic进行数据校验 |
| `database-design` | 设计数据库表结构 |
| `db-migration` | 编写数据库迁移脚本、执行数据库结构变更、使用Prisma/TypeORM/Knex迁移 |
| `deep-research` ⚠️变体 | 系统化深度研究方法论。触发：深度研究 |
| `deploy-script` | 编写部署脚本、配置PM2/systemd服务、实现应用部署 |
| `desktop-app` | 开发桌面应用程序 |
| `diagnose` | 深度诊断循环（reproduce→minimize→hypothesize→instrument→fix→regression-test）。触发：顽固 bug、性能问题、P0  |
| `doc-coauthoring` | 结构化文档协作撰写。触发：写文档 |
| `docker-devops` | 编写Dockerfile |
| `docx` | 创建Word文档 |
| `env-config` | 管理环境变量 |
| `error-recovery` | 错误恢复与故障处理策略，包括重试、降级、熔断、补偿 |
| `exa-search` | 使用 Exa AI 进行语义搜索和智能检索 |
| `figma-design` | Figma 设计工具集成与设计稿转代码 |
| `file-upload` | 实现文件上传功能 |
| `flutter-development` | 开发Flutter跨平台移动应用、编写Dart代码、实现iOS/Android双端应用 |
| `frontend-design` | 设计前端UI界面、创建落地页仪表板、实现高质量Web界面 |
| `fullstack-auth` | 实现用户认证授权 |
| `git-workflow` ⚠️变体 | 管理Git分支 |
| `git-worktrees` | 并行开发多个功能 |
| `github` | 使用gh命令管理GitHub仓库的Issue、PR、CI/CD等 |
| `google-workspace` | Google Workspace集成（CLI+API），统一管理Gmail |
| `grill-with-docs` | 对照 CONTEXT.md/ADR 拷问计划，逐条消解术语与决策并 inline 更新文档。触发：计划需对齐领域语言、stress-test 设计。excludes skill |
| `handoff` | 将当前会话压缩为 handoff 文档，供新会话或子 agent 续作。触发：/clear 前、子 agent 切换、长任务断点。excludes claude-mem SSO |
| `i18n-support` | 实现前端国际化 |
| `incremental-arch` | 增量架构同步，基于 AST 感知分块和 Merkle DAG 实现高效上下文更新 |
| `instinct-learning` | 本能学习（Ω-提示词优化器）。触发词：instinct learning | 本能学习 | 提示词优化 | 自我改进 |
| `internal-communication` | 编写内部沟通邮件 |
| `invoice-organizer` | 整理发票 |
| `ios-native-dev` | 开发iOS原生应用、使用Swift/Objective-C开发iPhone/iPad应用、实现iOS UI界面 |
| `ios-simulator` | 测试iOS应用、使用iOS模拟器、调试iOS界面、测试iPhone/iPad应用 |
| `kubernetes` | 部署Kubernetes集群、编写K8s配置文件、管理容器编排、配置Pod/Service/Deployment |
| `lead-research-assistant` | 识别和筛选高质量潜在客户 |
| `linear-integration` | 集成 Linear 项目管理和 Issue 跟踪 |
| `logging-monitoring` | 可观测性系统搭建，包括日志 |
| `market-research` | 进行市场调研 |
| `mcp-builder` | 开发MCP服务器 |
| `meeting-insights-analyzer` | 分析会议转录发现行为模式 |
| `message-queue` | 实现消息队列、处理异步任务、使用BullMQ/RabbitMQ/Kafka |
| `metadata-extraction` | 提取文件元数据 |
| `middleware` | 编写Express中间件 |
| `mini-program` | 开发微信小程序 |
| `mobile-deployment` | 发布移动应用 |
| `mobile-performance` | 优化移动端应用性能 |
| `mobile-ui` | 开发移动端UI界面 |
| `mongodb` | 操作MongoDB数据库 |
| `monorepo-management` | 管理Monorepo项目、使用Turborepo/Nx/pnpm workspace、配置多包仓库 |
| `nginx-config` | 配置Nginx服务器 |
| `nodejs-backend` | 开发Node.js后端应用、使用Express/Koa/NestJS框架、编写后端API服务 |
| `notion-integration` | 使用Notion API |
| `office-docs` | 办公文档处理。触发：写报告 |
| `office-hours` | 六问产品框架。触发词：office hours | 六问框架 | 产品分析 | 需求深挖 | /office-hours |
| `onboarding-guide` | 新人 onboarding 引导。触发词：onboarding | 新人引导 | 项目入门 | 快速上手 |
| `pdf` | 处理PDF文件、提取PDF文本、合并拆分PDF、填写PDF表单 |
| `performance-optimization` | 优化系统性能 |
| `pptx` | 创建PPT演示文稿、编辑pptx文件，制作幻灯片 |
| `prompt-engineering` | 设计Prompt |
| `python-automation` | 编写Python自动化脚本 |
| `python-backend` | 开发Python后端应用、使用FastAPI/Flask/Django框架、编写Python API服务 |
| `rate-limiting` | 实现API限流 |
| `react-component` | 开发React组件 |
| `react-native` | 开发React Native跨平台移动应用、使用JavaScript/TypeScript开发移动端 |
| `redis-cache` | 使用Redis缓存 |
| `regex-helper` | 编写正则表达式 |
| `report-generator` | 生成报告文档、制作分析报告、输出Markdown/PDF/Word/Excel报告 |
| `scheduled-task` | 定时任务 |
| `search-engine` | 实现全文搜索功能、集成Elasticsearch/MeiliSearch搜索引擎、配置站内搜索 |
| `security-best-practices` | 进行安全开发 |
| `slack-integration` | 集成 Slack 消息发送 |
| `software-architecture` | 进行系统架构设计 |
| `sql-database` | 编写SQL查询、优化数据库性能、设计SQL索引、使用MySQL/PostgreSQL |
| `state-management` | 管理前端状态、使用Redux/Pinia/Zustand、设计全局状态存储 |
| `supabase-backend` | 使用 Supabase 构建 BaaS 后端服务 |
| `taste-memory` | 品味记忆学习（UI 偏好跨会话）。触发词：taste memory | 品味记忆 | UI偏好 | 设计偏好学习 |
| `theme-config` | 配置主题样式、设计暗色模式、配置Ant Design/Element Plus主题 |
| `typescript` | 编写TypeScript类型、解决类型错误、使用泛型/高级类型、实现类型安全 |
| `ui-ux-pro-max` | UI/UX设计知识库，67风格+161色板+99UX指南，CSV数据驱动设计决策。触发词：UI设计、UX、设计系统、landing、dashboard。 |
| `uniapp-development` | 开发UniApp跨平台应用 |
| `vercel-deploy` | Vercel 部署和托管配置 |
| `vibe-coding-cn` | 中文 vibe 编码模式 — 道/法/术/器框架 + α/Ω 元技能 + 五步协作流程 |
| `vue-development` | 开发Vue组件 |
| `web-scraping` | 爬取网页数据 |
| `webapp-testing` | 用于 Web 应用自动化测试，使用 Playwright 进行端到端测试。测试 Web 应用 |
| `websocket-server` | WebSocket 服务端开发与实时通信 |
| `xlsx` | 处理Excel表格、操作xlsx文件、处理CSV数据 |

## Agents（48）

| 名称 | 说明 |
| ---- | ---- |
| `accessibility-expert` | 负责Web无障碍设计和WCAG合规。当需要实现无障碍访问、WCAG标准合规、屏幕阅读器适配、键盘导航支持、颜色对比度检查、表单可访问性、ARIA属性优化时调用此Agent。触发 |
| `ai-engineer` | 负责AI/LLM应用开发，含Prompt工程设计和LangSmith调试追踪。触发词：AI开发、LLM、RAG、Prompt工程、向量数据库、Claude API、OpenAI |
| `api-versioner` | 负责API版本管理和向后兼容策略。当需要设计API版本策略、实现版本控制、处理版本迁移、管理API生命周期、实现向后兼容、处理废弃API时调用此Agent。触发词：API版本、 |
| `backend-developer` | 负责后端API与服务开发（RESTful/GraphQL/gRPC）、数据库设计、认证授权、OpenAPI文档。触发词：后端、API、数据库、服务端、Express、FastA |
| `ceo-reviewer` ⚠️变体 | 产品决策审查（大功能/新特性时启用）。触发词：产品审查、scope审查、用户价值、ceo review。 |
| `changelog-generator` | 变更日志生成专家。当需要从 git 提交历史生成面向用户的变更日志、从技术提交转换为客户友好的发布说明时调用此 Agent。触发词：变更日志、changelog、发布说明、版本 |
| `compliance-checker` | 负责法规合规检查和数据保护审计。当需要进行GDPR合规检查、HIPAA合规、数据保护评估、隐私合规、合规审计、数据治理、监管合规检查时调用此Agent。触发词：合规、GDPR、 |
| `context-rot-monitor` | 上下文腐烂监控Agent，持续监控上下文窗口使用率并在超过阈值时触发治理措施。 |
| `cpp-reviewer` | C++ 代码审查专家。当需要审查 C++ 代码、检查现代 C++ 特性、评估内存安全、检查并发正确性、审查 C++ 性能优化时调用此 Agent。触发词：审查 C++、C++  |
| `csharp-reviewer` | C# / .NET 代码审查专家。触发：C# 代码审查、.NET 项目质量检查、ASP.NET Core 审查 |
| `data-engineer` | 负责数据工程相关任务。当需要构建ETL数据管道、设计数据仓库、处理数据清洗转换、实现数据同步方案、构建数据报表系统、处理大数据任务、设计数据湖方案、实现实时流数据处理时调用此A |
| `database-expert` | 数据库全栈专家，覆盖架构设计、审查优化、SQL编写与数据迁移。触发词：数据库设计、数据库架构、表设计、索引设计、数据建模、分库分表、数据迁移、数据库选型、PostgreSQL、 |
| `design-shotgun` | 设计探索器，生成 4-6 个 AI mockup 变体，浏览器比较板，品味记忆学习。触发词：设计方案、多方案对比、mockup、UI探索、shotgun。 |
| `designer` ⚠️变体 | UI/UX 审查（UI/交互变更时启用）。触发词：设计审查、UI审查、交互审查、design review。 |
| `devops-engineer` | DevOps/运维专家，覆盖 CI/CD、容器化、Terraform/IaC、监控告警与自动化部署。触发词：CI/CD、Docker、Kubernetes、K8s、部署、容器、 |
| `docs-expert` | 文档专家，覆盖文档生成和文档查找。当需要生成API文档、编写README文件、添加代码注释、生成JSDoc/docstring、编写接口文档、创建技术说明文档、编写开发指南、生 |
| `eng-reviewer` ⚠️变体 | 工程审查（所有变更必须通过）。触发词：eng review、代码审查、PR审查、工程评审。 |
| `flutter-reviewer` | Flutter / Dart 代码审查专家。触发：Flutter 代码审查、Dart 质量检查、Widget 性能分析 |
| `frontend-developer` | 负责前端开发任务。当需要实现前端页面、开发UI组件、创建Vue/React组件、实现响应式布局、处理前端状态管理、开发表单交互、实现动画效果、接入前端路由、调用后端API、处理 |
| `git-expert` | Git版本控制和工作流专家。负责Git分支策略设计、提交规范制定、合并冲突解决、工作流管理、版本控制最佳实践、Git Worktree并行开发。触发词：Git、合并冲突、分支策 |
| `go-reviewer` | Go代码审查专家。专注于Go语言特性、并发安全、错误处理和性能优化。当需要审查Go代码、goroutine使用、channel操作时调用此Agent。触发词：Go审查、Go代码 |
| `incident-responder` | 负责生产故障响应和处理任务。当生产环境发生故障、服务宕机、性能严重下降、数据异常、安全事件需要紧急处理时调用此Agent。触发词：生产故障、服务宕机、系统崩溃、紧急故障、P0故 |
| `ios-specialist` | iOS 专用审查 — QA测试/fix修复/design-review设计审查/clean清理/sync同步（gstack v0.19） |
| `java-reviewer` | Java/Spring代码审查专家。专注于Java语言特性、Spring Boot约定、并发安全和性能优化。触发词：Java审查、Spring审查、Java代码、Spring  |
| `kotlin-reviewer` | Kotlin 代码审查专家。当需要审查 Kotlin 代码、检查 Kotlin 惯用法、评估 Android/KMP 代码、审查协程使用、检查空安全时调用此 Agent。触发词 |
| `land-and-deploy` | 一键部署 — 从 approved PR 到 verified in production。触发词：部署、上线、land、deploy、发布到生产。 |
| `mcp-builder` | MCP 服务器开发专家。当需要开发 MCP 服务器、构建 Claude 集成工具、创建 MCP 协议服务时调用此 Agent。提供 MCP 协议实现、工具定义、资源管理和服务器 |
| `ml-engineer` | 负责机器学习模型开发与部署。触发词：ML、机器学习、深度学习、TensorFlow、PyTorch、模型训练、神经网络、推荐系统、NLP、计算机视觉。 |
| `mobile-developer` | 负责移动端开发任务。当需要开发React Native应用、Flutter应用、UniApp跨平台应用、微信小程序、H5移动页面、处理移动端适配问题、实现原生功能调用、处理移动 |
| `nodejs-reviewer` | 负责 Node.js 与 TypeScript 后端代码审查任务。当需要审查 Node.js 代码、审查 TypeScript 后端代码、检查 Express/Koa/Fast |
| `observability-engineer` | 负责系统监控和可观测性相关任务。当需要配置监控告警、搭建Prometheus+Grafana监控体系、实现分布式链路追踪、配置日志采集与分析、设计SLI/SLO指标体系、排查监 |
| `pair-agent` | 多 AI Agent 浏览器共享协作。触发词：多 Agent 协作、共享浏览器、pair、agent 互联。 |
| `performance-analyzer` | 负责代码性能分析和优化任务。当需要分析性能瓶颈、排查内存泄漏、优化数据库查询、解决页面卡顿、优化接口响应时间、分析CPU占用过高、优化前端渲染性能、解决N+1查询问题、优化缓存 |
| `performance-engineer` | 性能工程师，基准页面加载、Core Web Vitals、资源大小，PR前后对比 |
| `python-pro` | Python全栈开发专家，负责Python通用开发任务。当需要编写Python脚本、实现Python算法、开发CLI工具、处理文件操作、数据处理、爬虫开发、自动化脚本、Pyth |
| `python-reviewer` | 负责 Python 后端代码审查任务。当需要审查 Python 代码、审查 FastAPI/Flask/Django 代码、检查 Python 代码质量、评审异步 Python |
| `qa-engineer` | 负责测试相关任务，含E2E端到端测试(Playwright/Cypress)。当需要编写测试用例、制定测试策略、开发自动化测试、编写单元测试、集成测试、E2E端到端测试、搭建测 |
| `qa` ⚠️变体 | 质量保障审查（测试用例、边界、回归）。触发词：QA审查、测试审查、边界测试、回归测试。 |
| `react-reviewer` | 负责 React 组件代码审查任务。当需要审查 React 组件代码、检查 Hooks 使用规范、评审 React 性能优化、检查组件设计模式、评估 React 最佳实践合规性 |
| `refactoring-expert` | 代码重构和清理专家，识别代码坏味道、安全重构、消除死代码和重复、代码简化与精炼。当需要重构遗留代码、消除代码坏味道、清理死代码、消除重复代码、提升代码可维护性、代码简化、KIS |
| `ruby-reviewer` | Ruby/Rails代码审查专家。专注于Ruby惯用法、Rails约定、安全和性能优化。触发词：Ruby审查、Rails审查、Ruby代码、Rails。 |
| `rust-reviewer` | Rust 代码审查专家。当需要审查 Rust 代码、检查所有权规则、评估借用检查、审查 Rust 最佳实践、检查并发安全时调用此 Agent。触发词：审查 Rust、Rust  |
| `security-reviewer` ⚠️变体 | 负责安全代码审查和漏洞检测。触发词：安全审查、漏洞检测、OWASP、安全审计、代码安全。 |
| `security` | 安全深度审计（安全敏感变更时启用）。触发词：安全审计、STRIDE、威胁建模、安全评估。 |
| `swift-reviewer` | Swift 代码审查专家。当需要审查 Swift 代码、检查 Swift 惯用法、评估 iOS/macOS 代码、审查 SwiftUI、检查并发安全时调用此 Agent。触发词 |
| `typescript-pro` | TypeScript专家，负责TypeScript类型系统和高级特性相关任务。当需要设计复杂TypeScript类型、实现泛型工具类型、解决类型错误、进行TypeScript项 |
| `typescript-reviewer` | 负责 TypeScript/JavaScript 代码审查任务。当需要审查 TypeScript/JavaScript 代码、检查类型安全、审查 React/Next.js 组 |
| `ux-design-expert` | UX设计专家，覆盖UI/交互设计、设计系统、用户研究与可用性测试。触发词：UI设计、UX设计、界面设计、交互设计、设计规范、设计系统、视觉设计、色彩方案、布局设计、原型设计、设 |

## Rules（15）

| 名称 | 说明 |
| ---- | ---- |
| `RULES_AI` | AI/LLM 应用开发相关任务时启用 |
| `RULES_BACKEND` | 后端相关功能开发时启用 |
| `RULES_CSHARP` | C# / .NET 开发规则 |
| `RULES_DART` | Dart / Flutter 开发规则 |
| `RULES_DATABASE` | 数据库设计、查询、迁移相关任务时启用 |
| `RULES_DEVOPS` | DevOps、CI/CD、容器化、部署相关任务时启用 |
| `RULES_FRONTEND` | 前端代码开发时启用 |
| `RULES_GO` | Go 开发规则 |
| `RULES_JAVA` | Java/Spring 开发规则 |
| `RULES_MOBILE` | 移动端开发规则（Flutter/RN/UniApp/原生） |
| `RULES_PYTHON` | Python 代码开发时启用 |
| `RULES_RUBY` | Ruby/Rails 开发规则 |
| `RULES_RUST` | Rust 开发规则 |
| `RULES_TESTING` | 测试编写、测试策略、测试框架相关任务时启用 |
| `RULES_TYPESCRIPT` | TypeScript 代码开发时启用 |

---

v11.0.0 · 由 `scripts/gen-catalog-index.py` 生成，新增/删除 catalog 项后重跑该脚本
