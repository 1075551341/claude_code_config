# Skills 技能库

适配 Claude、Cursor、Windsurf、Trae、Qoder 等主流 AI 编辑器的技能包集合。
以 Claude 标准为优先，按「最小 Token 消耗、最大上下文价值」原则设计。

---

## 目录结构

```
skills/
├── README.md              # 本文件
│
├── 后端开发
│   ├── api-development/   # RESTful API 设计与实现
│   ├── api-mock/          # Mock 数据生成
│   ├── db-migration/      # 数据库迁移
│   ├── middleware/        # Express 中间件
│   ├── mcp-builder/       # MCP 服务器开发
│   ├── nodejs-backend/    # Node.js 后端
│   ├── python-backend/    # Python 后端
│   ├── scheduled-task/    # 定时任务
│   ├── socket-event/      # Socket.io 事件
│   └── sql-database/      # SQL 数据库
│
├── 前端开发
│   ├── frontend-design/   # 生产级 UI 界面设计
│   ├── icon-search/       # 图标搜索
│   ├── react-component/   # React 组件
│   ├── theme-config/      # 主题配置
│   ├── typescript/        # TypeScript 类型
│   ├── uniapp-development/# UniApp 跨平台
│   ├── vue-development/   # Vue 3 开发
│   └── web-artifacts-builder/ # 复杂 Web 制品
│
├── 测试与质量
│   ├── code-review/       # 代码审查
│   ├── code-refactor/     # 代码重构
│   ├── code-standards/    # 代码规范
│   ├── error-handling/    # 错误处理
│   ├── performance-optimization/ # 性能优化
│   ├── regex-helper/      # 正则表达式
│   ├── security-best-practices/ # 安全实践
│   ├── testing-standards/ # 测试规范
│   └── web-testing/       # Playwright 测试
│
├── 运维部署
│   ├── deploy-script/     # 部署脚本
│   ├── docker-devops/     # Docker 容器化
│   └── nginx-config/      # Nginx 配置
│
├── 文档办公
│   ├── doc-coauthoring/   # 协同文档写作
│   ├── docx/              # Word 文档
│   ├── pdf/               # PDF 处理
│   ├── pptx/              # PPT 演示
│   ├── report-generator/  # 报告生成
│   └── xlsx/              # Excel 表格
│
├── 创意设计
│   ├── algorithmic-art/   # p5.js 算法艺术
│   ├── canvas-design/     # 视觉设计
│   ├── slack-gif-creator/ # Slack GIF
│   └── theme-factory/     # 主题样式
│
└── 工具与工作流
    ├── git-workflow/      # Git 工作流
    └── skill-creator/     # 技能创建
```

---

## 技能速查表

### 后端开发

| 技能 | 触发场景 | 核心能力 |
|------|----------|----------|
| **api-development** | 构建 REST API、设计端点、实现后端服务 | URL 规范、统一响应格式、入参验证、安全基线、分页设计 |
| **api-mock** | 生成 Mock 数据、模拟服务响应 | Mock.js、Faker.js、MSW 模拟服务 |
| **db-migration** | 数据库结构变更、Migration 脚本 | Knex.js、Prisma、TypeORM 迁移 |
| **middleware** | Express 中间件开发 | 认证、日志、限流、错误处理 |
| **mcp-builder** | 构建 MCP 服务器、集成外部 API | FastMCP(Python) / MCP SDK(TS) 实现、工具命名规范、错误设计 |
| **nodejs-backend** | Node.js 后端开发 | Express/Koa/Fastify/NestJS 最佳实践 |
| **python-backend** | Python 后端开发 | FastAPI/Flask/Django 最佳实践 |
| **scheduled-task** | 定时任务、周期作业 | node-cron、node-schedule、Bull 队列 |
| **socket-event** | WebSocket 实时通信 | Socket.io 事件定义、房间管理 |
| **sql-database** | SQL 数据库开发优化 | MySQL/PostgreSQL/SQLite 查询优化、索引设计 |

### 前端开发

| 技能 | 触发场景 | 核心能力 |
|------|----------|----------|
| **frontend-design** | 构建 Web 组件、落地页、仪表板、UI 样式美化 | 生产级界面、避免 AI 审美、大胆设计方向 |
| **icon-search** | 查找和导入图标 | Iconify、IconPark、FontAwesome |
| **react-component** | React 组件开发 | Hooks、状态管理、性能优化、TypeScript |
| **theme-config** | 主题配置与切换 | Ant Design、Element Plus、Tailwind CSS |
| **typescript** | 处理 TS 类型定义、类型安全问题、高级类型 | 辨别联合、条件类型、infer、工具类型速查、常见陷阱 |
| **uniapp-development** | UniApp 跨平台开发 | Vue 3 语法、多端适配、原生插件 |
| **vue-development** | 开发 Vue 3 组件或应用 | SFC 模板、Composable、Pinia、性能优化 |
| **web-artifacts-builder** | 构建需要状态管理或路由的复杂多组件制品 | React + Tailwind + shadcn/ui、Vite 打包 |

### 测试与质量

| 技能 | 触发场景 | 核心能力 |
|------|----------|----------|
| **code-review** | 审查 PR、代码审计、评估代码质量 | 5 维度审查（正确性/安全/性能/可维护/测试）、标准反馈格式 |
| **code-refactor** | 重构遗留代码、消除代码坏味道 | 函数提取、类重构、设计模式应用 |
| **code-standards** | 代码规范性检查 | 命名规范、目录结构、代码风格、注释规范 |
| **error-handling** | 错误处理设计 | 异常捕获、错误分类、日志记录、用户友好提示 |
| **performance-optimization** | 性能优化 | 前端渲染、后端处理、数据库查询、网络优化 |
| **regex-helper** | 正则表达式编写与调试 | 常用模式、性能优化、跨语言兼容 |
| **security-best-practices** | 安全开发实践 | OWASP、SQL 注入、XSS、CSRF 防护 |
| **testing-standards** | 测试规范与实施 | 单元测试、集成测试、E2E、测试驱动开发 |
| **web-testing** | 测试 Web 应用、调试前端、自动化浏览器 | Playwright 脚本、选择器优先级、异步等待、服务管理 |

### 运维部署

| 技能 | 触发场景 | 核心能力 |
|------|----------|----------|
| **deploy-script** | 编写部署脚本 | PM2、systemd、Docker、K8s 部署配置 |
| **docker-devops** | Docker 容器化与 DevOps | Dockerfile、Compose、CI/CD 流水线 |
| **nginx-config** | Nginx 配置生成 | 反向代理、负载均衡、SSL、缓存配置 |

### 文档办公

| 技能 | 触发场景 | 核心能力 |
|------|----------|----------|
| **doc-coauthoring** | 写文档、起草提案/规范/PRD/RFC | 三阶段工作流：上下文收集 → 精炼结构 → 读者测试 |
| **docx** | 创建/编辑 .docx 文件、处理修订追踪 | OOXML 操作、Redlining 工作流、文本提取 |
| **pdf** | PDF 文本提取、创建、合并/拆分、表单填写 | pypdf、reportlab、表单处理、批量操作 |
| **pptx** | 创建/编辑演示文稿、处理幻灯片布局 | python-pptx、XML 操作、演讲者备注 |
| **report-generator** | 生成报告文档 | Markdown、PDF、Word、HTML 格式报告 |
| **xlsx** | 创建/编辑电子表格、数据分析与可视化 | openpyxl、公式而非硬编码值、图表生成 |

### 创意设计

| 技能 | 触发场景 | 核心能力 |
|------|----------|----------|
| **algorithmic-art** | 用代码创建生成艺术、流场、粒子系统 | p5.js、种子随机、算法美学哲学 |
| **canvas-design** | 创建海报、平面设计、静态视觉作品 | 设计哲学驱动、输出 .png/.pdf |
| **slack-gif-creator** | 为 Slack 制作动画 GIF 表情或消息图 | 尺寸约束（128×128 / 480×480）、文件大小优化 |
| **theme-factory** | 为制品应用或生成视觉主题 | 10 套预设主题（颜色 + 字体）、即时生成新主题 |

### 工具与工作流

| 技能 | 触发场景 | 核心能力 |
|------|----------|----------|
| **git-workflow** | Git 工作流管理 | 分支策略、合并冲突、提交规范、版本管理 |
| **skill-creator** | 创建或更新技能包 | 文件结构规范、description 编写、内容取舍决策树 |

---

## 设计原则

### Token 效率优先
每个技能只包含**模型自身不具备的知识**：特定工具的非直觉用法、项目约定、多步骤工作流顺序。通用语言知识、标准库基础用法一律省略。

### 触发精准
`description` 字段决定技能被加载的时机，采用动词开头的结构化描述，明确"何时用"而非"能做什么"。

### 编辑器兼容
前置元数据（frontmatter）遵循 YAML 标准，`name` / `description` 字段为必填，兼容 Claude Projects、Cursor Rules、Windsurf Cascade、Trae、Qoder 等主流读取方式。

---

## 快速使用

### Claude（Projects / claude.ai）
将技能文件夹上传至项目知识库，或将 `SKILL.md` 内容添加到 Project Instructions。

### Cursor
将 `SKILL.md` 内容粘贴至 `.cursorrules` 或 Cursor Settings → Rules for AI。

### Windsurf
将 `SKILL.md` 内容添加至 `.windsurfrules` 文件（项目根目录）。

### Trae / Qoder
在编辑器设置中导入 `SKILL.md` 或配置为 System Prompt 附加内容。

---

## 统计

| 项 | 数量 |
|----|------|
| 技能总数 | 43 |
| 后端开发 | 10 |
| 前端开发 | 8 |
| 测试与质量 | 9 |
| 运维部署 | 3 |
| 文档办公 | 6 |
| 创意设计 | 4 |
| 工具与工作流 | 2 |

---

_最后更新：2026-03-20_
