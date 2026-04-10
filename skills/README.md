# Skills 技能库

适配 Claude、Cursor、Windsurf、Trae、Qoder 等主流 AI 编辑器的技能包集合。
以 Claude 标准为优先，按「最小 Token 消耗、最大上下文价值」原则设计。

---

## 统计概览

| 分类         | 数量    |
| ------------ | ------- |
| 开发流程     | 13      |
| 后端开发     | 14      |
| 前端开发     | 10      |
| 移动端开发   | 13      |
| 桌面应用开发 | 2       |
| 测试与质量   | 12      |
| 运维部署     | 9       |
| 安全与取证   | 4       |
| 数据与分析   | 6       |
| 文档办公     | 8       |
| 创意设计     | 7       |
| 基础组件     | 12      |
| AI与开发     | 4       |
| 自动化工具   | 6       |
| 效率与生活   | 8       |
| 工具与工作流 | 11      |
| 内容创作     | 5       |
| 协作工作流   | 3       |
| **总计**     | **157** |

---

## 目录结构

```
skills/
├── 开发流程
│   ├── design-brainstorming/   # 设计头脑风暴
│   ├── implementation-planning/ # 实施计划编写
│   ├── executing-plans/        # 计划执行跟踪
│   ├── requirement-refinement/ # 需求细化与确认
│   ├── test-driven-development/ # 测试驱动开发
│   ├── systematic-debugging/   # 系统化调试
│   ├── verification-checklist/ # 完成验证清单
│   ├── collision-zone-thinking/ # 碰撞区思维
│   ├── inversion-exercise/     # 反转练习
│   ├── meta-pattern-recognition/ # 元模式识别
│   ├── scale-game/              # 尺度游戏
│   ├── simplification-cascades/ # 简化级联
│   └── when-stuck/             # 卡住时分派
│
├── 后端开发
│   ├── api-development/   # RESTful API 设计
│   ├── api-mock/          # Mock 数据生成
│   ├── db-migration/      # 数据库迁移
│   ├── database-design/   # 数据库架构设计
│   ├── message-queue/     # 消息队列
│   ├── middleware/        # Express 中间件
│   ├── mcp-builder/       # MCP 服务器开发
│   ├── nodejs-backend/    # Node.js 后端
│   ├── python-backend/    # Python 后端
│   ├── scheduled-task/    # 定时任务
│   ├── socket-event/      # Socket.io 事件
│   ├── sql-database/      # SQL 数据库
│   ├── websocket-realtime/# WebSocket 实时通信
│   └── clickhouse-analytics/ # ClickHouse 大数据分析
│
├── 前端开发
│   ├── frontend-design/   # 生产级 UI 界面
│   ├── i18n-support/      # 前端国际化
│   ├── icon-search/       # 图标搜索
│   ├── js-code-snippets/  # JavaScript 代码片段
│   ├── react-component/   # React 组件
│   ├── state-management/  # 状态管理
│   ├── theme-config/      # 主题配置
│   ├── typescript/        # TypeScript 类型
│   ├── uniapp-development/# UniApp 跨平台
│   ├── vue-development/   # Vue 3 开发
│   └── web-artifacts-builder/ # Web 制品构建
│
├── 移动端开发
│   ├── flutter-development/  # Flutter 跨平台
│   ├── react-native/         # React Native
│   ├── android-development/  # Android 原生开发
│   ├── kotlin-android/       # Kotlin Android
│   ├── ios-native-dev/       # iOS 原生开发
│   ├── swift-ui/             # SwiftUI 界面
│   ├── ios-simulator/        # iOS 模拟器
│   ├── mini-program/         # 小程序开发
│   ├── ionic-app/            # Ionic 混合应用
│   ├── capacitor-app/        # Capacitor 原生桥接
│   ├── mobile-ui/            # 移动端 UI
│   ├── mobile-performance/   # 移动性能优化
│   └── mobile-deployment/    # 应用发布上架
│
├── 桌面应用开发
│   ├── electron-app/     # Electron 桌面应用
│   └── desktop-app/      # 桌面应用通用
│
├── 测试与质量
│   ├── code-review/       # 代码审查
│   ├── code-review-workflow/ # 审查工作流
│   ├── code-refactor/     # 代码重构
│   ├── code-standards/    # 代码规范
│   ├── error-handling/    # 错误处理
│   ├── performance-optimization/ # 性能优化
│   ├── regex-helper/      # 正则表达式
│   ├── security-best-practices/ # 安全实践
│   ├── testing-standards/ # 测试规范
│   ├── api-testing/       # API 接口测试
│   └── webapp-testing/    # Web 应用测试
│
├── 运维部署
│   ├── aws-cloud/         # AWS 云服务
│   ├── cicd-pipeline/     # CI/CD 流水线
│   ├── deploy-script/     # 部署脚本
│   ├── docker-devops/     # Docker 容器化
│   ├── nginx-config/      # Nginx 配置
│   ├── n8n-automation/    # n8n 工作流
│   ├── kubernetes/        # K8s 容器编排
│   ├── prometheus-monitoring/ # Prometheus 监控
│   └── ffuf-fuzzing/      # Web 安全测试
│
├── 安全与取证
│   ├── security-forensics/# 安全取证
│   ├── threat-hunting/    # 威胁狩猎
│   ├── metadata-extraction/ # 元数据提取
│   └── secure-deletion/   # 安全删除
│
├── 数据与分析
│   ├── data-analysis/     # 数据分析
│   ├── deep-research/     # 深度研究
│   ├── content-research/  # 内容研究
│   ├── market-research/   # 市场调研
│   ├── competitive-analysis/ # 竞品分析
│   └── tracing-knowledge-lineages/ # 知识谱系追踪
│
├── 文档办公
│   ├── changelog-generator/ # 变更日志
│   ├── doc-coauthoring/   # 文档协作
│   ├── docx/              # Word 文档
│   ├── pdf/               # PDF 处理
│   ├── pptx/              # PPT 演示
│   ├── report-generator/  # 报告生成
│   ├── xlsx/              # Excel 表格
│   └── invoice-organizer/ # 发票整理
│
├── 创意设计
│   ├── algorithmic-art/   # 算法艺术
│   ├── brand-guidelines/  # 品牌指南
│   ├── canvas-design/     # 视觉设计
│   ├── d3-visualization/  # D3 数据可视化
│   ├── slack-gif-creator/ # Slack GIF
│   ├── social-media-optimizer/ # 社交媒体优化
│   └── theme-factory/     # 主题工厂
│
├── 基础组件
│   ├── caching-strategy/  # 缓存策略
│   ├── data-validation/   # 数据校验
│   ├── env-config/        # 环境配置
│   ├── file-upload/       # 文件上传
│   ├── fullstack-auth/    # 全栈认证
│   ├── google-workspace/  # Google 集成
│   ├── logging-monitoring/# 日志监控
│   ├── mongodb/           # MongoDB 数据库
│   ├── redis-cache/       # Redis 缓存
│   ├── monorepo-management/# Monorepo
│   ├── rate-limiting/     # API 限流
│   └── search-engine/     # 全文搜索
│
├── AI与开发
│   ├── claude-api-integration/ # Claude API
│   ├── prompt-engineering/ # Prompt 工程
│   ├── software-architecture/ # 软件架构
│   ├── mcp-matcher/       # MCP 工具智能匹配
│   └── imagen/            # AI 图像生成
│
├── 自动化工具
│   ├── web-scraping/      # 网络爬虫
│   ├── python-automation/ # Python 自动化
│   ├── rpa-automation/    # RPA 流程自动化
│   ├── video-processing/  # 视频处理
│   ├── audio-processing/  # 音频处理
│   ├── image-enhancement/ # 图片增强
│   └── youtube-tools/     # YouTube 工具
│
├── 效率与生活
│   ├── file-organization/  # 文件整理
│   ├── note-management/    # 笔记管理
│   ├── time-management/    # 时间管理
│   ├── meeting-productivity/ # 会议效率
│   ├── learning-resources/ # 学习资源
│   ├── health-tracking/    # 健康追踪
│   ├── personal-finance/   # 个人理财
│   └── kaizen-improvement/ # 持续改进
│
├── 工具与工作流
│   ├── git-workflow/      # Git 工作流
│   ├── git-worktrees/     # Git Worktrees
│   ├── resume-generator/  # 简历生成
│   ├── internal-communication/ # 内部沟通
│   ├── skill-creator/     # 技能创建
│   └── notion-integration/ # Notion 集成
│
└── 内容创作
    ├── article-writing/     # 文章写作
    ├── domain-brainstorm/   # 域名创意
    ├── investor-materials/  # 投资者材料
    ├── root-cause-analysis/ # 根因分析
    ├── lead-research-assistant/ # 潜在客户研究
    └── competitive-ads-extractor/ # 竞争广告分析

├── 协作工作流
│   ├── parallel-agents/     # 并行Agent调度
│   ├── branch-finishing/    # 分支完成工作流
│   ├── meeting-insights-analyzer/ # 会议洞察分析
│   └── preserving-productive-tensions/ # 保持建设性张力
```

---

## 技能速查表

### 开发流程

| 技能                        | 触发词                                                           |
| --------------------------- | ---------------------------------------------------------------- |
| design-brainstorming        | 新功能、设计组件、架构设计、方案讨论                             |
| implementation-planning     | 实施计划、开发计划、任务分解                                     |
| executing-plans             | 执行计划、实现步骤、进度跟踪                                     |
| requirement-refinement      | 拷问、需求细化、需求确认、需求澄清、反问需求、明确需求、需求对齐、细化需求、澄清需求、确认理解、细化方案 |
| test-driven-development     | TDD、测试驱动、RED-GREEN-REFACTOR                                |
| systematic-debugging        | 报错、调试、bug、异常、崩溃                                      |
| verification-checklist      | 完成验证、提交前检查、验收检查                                   |
| collision-zone-thinking     | 碰撞思维、概念结合、跨界创新、强制联想                             |
| inversion-exercise          | 反转假设、逆向思维、假设翻转、约束发现                             |
| meta-pattern-recognition    | 元模式、跨领域模式、通用原则、模式识别                             |
| scale-game                  | 尺度游戏、极端测试、边界测试、规模测试                             |
| simplification-cascades     | 简化级联、组件消除、简化洞察、去复杂化                           |
| when-stuck                  | 卡住、陷入困境、问题解决、技术选择                               |

### 后端开发

| 技能                 | 触发词                                 |
| -------------------- | -------------------------------------- |
| api-development      | REST API、接口设计、端点实现           |
| api-mock             | Mock数据、模拟服务、Faker.js           |
| db-migration         | 数据库迁移、Migration、Prisma          |
| database-design      | 数据库设计、表结构、索引策略           |
| message-queue        | 消息队列、BullMQ、Kafka                |
| middleware           | Express中间件、认证、限流              |
| mcp-builder          | MCP服务器、Claude集成                  |
| nodejs-backend       | Node.js、Express、Koa、NestJS          |
| python-backend       | Python、FastAPI、Flask、Django         |
| scheduled-task       | 定时任务、cron、周期作业               |
| socket-event         | Socket.io、WebSocket事件               |
| sql-database         | SQL、MySQL、PostgreSQL优化             |
| websocket-realtime   | WebSocket、实时通信、SSE               |
| clickhouse-analytics | ClickHouse、大数据分析、OLAP、实时分析 |

### 前端开发

| 技能                  | 触发词                          |
| --------------------- | ------------------------------- |
| frontend-design       | UI界面、落地页、仪表板          |
| i18n-support          | 国际化、多语言、i18next         |
| icon-search           | 图标查找、Iconify、FontAwesome  |
| js-code-snippets      | JS片段、ES6技巧、代码模式       |
| react-component       | React、Hooks、组件开发          |
| state-management      | 状态管理、Redux、Pinia、Zustand |
| theme-config          | 主题配置、暗色模式、Tailwind    |
| typescript            | TypeScript、类型定义、泛型      |
| uniapp-development    | UniApp、跨平台、小程序          |
| vue-development       | Vue 3、Composable、Pinia        |
| web-artifacts-builder | Web制品、React+Tailwind         |

### 移动端开发

| 技能                | 触发词                                         |
| ------------------- | ---------------------------------------------- |
| flutter-development | Flutter、Dart、跨平台移动                      |
| react-native        | React Native、RN、移动应用                     |
| android-development | Android开发、Android原生、Gradle               |
| kotlin-android      | Kotlin Android、Kotlin协程、Jetpack Compose    |
| ios-native-dev      | iOS开发、Swift、UIKit、Cocoa                   |
| swift-ui            | SwiftUI、声明式UI、Swift UI组件                |
| ios-simulator       | iOS模拟器、iPhone测试、Xcode调试               |
| mini-program        | 小程序、微信小程序、支付宝小程序、UniApp小程序 |
| ionic-app           | Ionic、混合应用、Ionic Angular/React/Vue       |
| capacitor-app       | Capacitor、原生桥接、混合应用原生功能          |
| mobile-ui           | 移动端UI、Vant Mobile、Ant Design Mobile       |
| mobile-performance  | 移动性能、App优化、启动优化、包体积            |
| mobile-deployment   | 应用发布、App Store、Google Play、应用签名     |

### 桌面应用开发

| 技能         | 触发词                          |
| ------------ | ------------------------------- |
| electron-app | Electron、桌面应用、Windows应用 |
| desktop-app  | 桌面软件、Tauri、Qt、WPF        |

### 测试与质量

| 技能                     | 触发词                           |
| ------------------------ | -------------------------------- |
| code-review              | 代码审查、PR审查、代码质量       |
| code-review-workflow     | PR流程、审查请求、合并流程       |
| code-refactor            | 重构、代码优化、设计模式         |
| code-standards           | 代码规范、命名规范、代码风格     |
| error-handling           | 错误处理、异常捕获、日志         |
| performance-optimization | 性能优化、前端渲染、慢查询       |
| regex-helper             | 正则表达式、模式匹配             |
| security-best-practices  | 安全实践、OWASP、XSS防护         |
| testing-standards        | 测试规范、单元测试、E2E          |
| api-testing              | API测试、Postman、curl测试       |
| webapp-testing           | Web应用测试、E2E测试、自动化测试 |

### 运维部署

| 技能                  | 触发词                        |
| --------------------- | ----------------------------- |
| aws-cloud             | AWS、EC2、S3、Lambda          |
| cicd-pipeline         | CI/CD、GitHub Actions、流水线 |
| deploy-script         | 部署脚本、PM2、Docker部署     |
| docker-devops         | Docker、容器化、Compose       |
| nginx-config          | Nginx、反向代理、负载均衡     |
| n8n-automation        | n8n、工作流自动化             |
| kubernetes            | K8s、容器编排、kubectl        |
| prometheus-monitoring | Prometheus、Grafana、监控告警 |
| ffuf-fuzzing          | Web安全、目录扫描、渗透测试   |

### 安全与取证

| 技能                | 触发词                       |
| ------------------- | ---------------------------- |
| security-forensics  | 安全取证、入侵检测、日志分析 |
| threat-hunting      | 威胁狩猎、Sigma规则、APT     |
| metadata-extraction | 元数据、Exif、文件属性       |
| secure-deletion     | 安全删除、数据擦除           |

### 数据与分析

| 技能                 | 触发词                                 |
| -------------------- | -------------------------------------- |
| data-analysis        | 数据分析、CSV分析、统计计算            |
| deep-research        | 深度研究、竞品分析、技术调研           |
| content-research     | 文章提取、素材收集、内容分析           |
| market-research      | 市场调研、竞品分析、行业研究、市场分析 |
| competitive-analysis | 竞品分析、竞争对手、竞争格局、竞品对比 |
| tracing-knowledge-lineages | 知识谱系、思想演变、追溯源头、知识追踪 |

### 文档办公

| 技能                | 触发词                                 |
| ------------------- | -------------------------------------- |
| changelog-generator | 变更日志、CHANGELOG、版本说明          |
| doc-coauthoring     | 文档协作、提案编写、PRD                |
| docx                | Word文档、docx处理                     |
| pdf                 | PDF处理、文本提取、合并拆分            |
| pptx                | PPT、演示文稿、幻灯片                  |
| report-generator    | 报告生成、Markdown报告                 |
| xlsx                | Excel、电子表格、数据分析              |
| invoice-organizer   | 发票整理、收据管理、报销整理、票据管理 |

### 创意设计

| 技能                   | 触发词                          |
| ---------------------- | ------------------------------- |
| algorithmic-art        | 算法艺术、p5.js、生成艺术       |
| brand-guidelines       | 品牌指南、设计规范、视觉系统    |
| canvas-design          | 海报设计、平面设计、视觉作品    |
| d3-visualization       | D3.js、数据可视化、交互图表     |
| slack-gif-creator      | Slack GIF、动画表情             |
| social-media-optimizer | 社交媒体、Twitter优化、内容策略 |
| theme-factory          | 主题样式、颜色方案              |

### 基础组件

| 技能                | 触发词                          |
| ------------------- | ------------------------------- |
| caching-strategy    | 缓存策略、Redis、CDN            |
| data-validation     | 数据校验、Zod、Joi、Pydantic    |
| env-config          | 环境变量、.env、配置管理        |
| file-upload         | 文件上传、分片上传、OSS         |
| fullstack-auth      | 认证授权、JWT、OAuth2           |
| google-workspace    | Gmail、Google Drive、Sheets API |
| logging-monitoring  | 日志、监控、ELK                 |
| mongodb             | MongoDB、NoSQL、Mongoose        |
| redis-cache         | Redis、缓存、分布式锁           |
| monorepo-management | Monorepo、Turborepo、pnpm       |
| rate-limiting       | 限流、防刷、令牌桶              |
| search-engine       | 全文搜索、Elasticsearch         |

### AI与开发

| 技能                   | 触发词                            |
| ---------------------- | --------------------------------- |
| claude-api-integration | Claude API、Anthropic SDK、AI应用 |
| prompt-engineering     | Prompt设计、提示词、Few-shot      |
| software-architecture  | 架构设计、设计模式、技术选型      |

### 自动化工具

| 技能              | 触发词                                               |
| ----------------- | ---------------------------------------------------- |
| web-scraping      | 爬虫、数据采集、网页抓取                             |
| python-automation | Python脚本、批量处理、自动化                         |
| rpa-automation    | RPA、流程自动化、UI自动化                            |
| video-processing  | 视频处理、FFmpeg、视频编辑                           |
| audio-processing  | 音频处理、音频编辑、降噪                             |
| image-enhancement | 图片增强、图像增强、图片修复、提升画质、超分辨率     |
| youtube-tools     | YouTube下载、YouTube字幕、视频下载、字幕提取、yt-dlp |

### 效率与生活

| 技能                 | 触发词                                 |
| -------------------- | -------------------------------------- |
| file-organization    | 文件整理、目录组织、批量重命名         |
| note-management      | 笔记管理、Obsidian、Notion             |
| time-management      | 时间管理、番茄工作法、GTD              |
| meeting-productivity | 会议效率、会议纪要、会议准备           |
| learning-resources   | 学习资源、教程推荐、学习路径           |
| health-tracking      | 健康追踪、运动记录、饮食管理、睡眠监测 |
| personal-finance     | 个人理财、财务管理、预算规划、收支记录 |
| kaizen-improvement   | 持续改进、改善、Kaizen、流程优化、PDCA |

### 工具与工作流

| 技能                   | 触发词                                             |
| ---------------------- | -------------------------------------------------- |
| git-workflow           | Git工作流、分支管理、提交规范                      |
| git-worktrees          | Worktrees、并行开发、分支隔离                      |
| resume-generator       | 简历生成、简历优化、求职简历                       |
| internal-communication | 内部邮件、团队公告、跨部门沟通                     |
| skill-creator          | 技能创建、Skill开发                                |
| notion-integration     | Notion API、Notion集成、Notion数据库、Notion自动化 |
| api-documentation      | API文档、接口文档、Swagger、文档生成               |
| architecture-diagrams  | 架构图、系统架构图、Mermaid、架构可视化            |
| command-reference      | CLI命令、命令速查、命令参考                        |
| config-management      | 配置管理、配置文件、配置规范                       |
| image-generation       | 图像生成、AI生图、图片生成                         |

### 内容创作

| 技能                | 触发词                                           |
| ------------------- | ------------------------------------------------ |
| article-writing     | 文章写作、博客撰写、技术文章、长文写作、避免AI腔 |
| domain-brainstorm   | 域名创意、域名推荐、域名命名、品牌域名、域名生成 |
| investor-materials  | 投资者材料、商业计划书、融资PPT、路演材料、BP    |
| root-cause-analysis | 根因分析、根本原因、问题追溯、根因追踪、5Why分析 |
| lead-research-assistant | 潜在客户、线索研究、客户筛选、销售线索       |
| competitive-ads-extractor | 竞争广告、广告分析、竞品广告、广告库       |

### 协作工作流

| 技能                        | 触发词                                           |
| --------------------------- | ------------------------------------------------ |
| parallel-agents             | 并行Agent、多Agent、批量处理、并行开发           |
| branch-finishing            | 分支完成、合并分支、完成开发、创建PR、分支合并   |
| meeting-insights-analyzer    | 会议分析、行为模式、会议洞察、转录分析           |
| preserving-productive-tensions | 建设性张力、保持选项、延迟决策、多方案保留     |

---

## 设计原则

### Token 效率优先

每个技能只包含**模型自身不具备的知识**：特定工具的非直觉用法、项目约定、多步骤工作流顺序。

### 触发精准

`description` 字段采用动词开头的结构化描述，包含触发关键词，确保匹配精准。

### 编辑器兼容

前置元数据遵循 YAML 标准，`name` / `description` 字段为必填，兼容主流 AI 编辑器。

---

## 快速使用

### Claude Code / Claude Desktop

**方法1 - 项目级技能（推荐）**
```bash
# 将技能目录复制到项目
mkdir -p .claude/skills
cp -r ~/.claude/skills/api-development .claude/skills/

# Claude自动识别项目中的.skills目录
```

**方法2 - 全局配置**
```bash
# 编辑Claude Code配置
claude config set system_prompt "$(cat ~/.claude/skills/api-development/SKILL.md)"
```

### Cursor

**项目级配置（推荐）**
```bash
# 在项目根目录创建 .cursorrules
cat ~/.claude/skills/api-development/SKILL.md > .cursorrules

# 或合并多个技能
cat ~/.claude/skills/api-development/SKILL.md \
    ~/.claude/skills/code-review/SKILL.md > .cursorrules
```

**用户级配置**
- Cursor Settings → Rules for AI → 粘贴 SKILL.md 内容

### Windsurf

**项目级配置（推荐）**
```bash
# 在项目根目录创建 .windsurfrules
cat ~/.claude/skills/api-development/SKILL.md > .windsurfrules
```

**全局配置**
- Settings → Cascade → System Prompt → 添加 SKILL.md 内容

### Trae / Qoder

**项目级配置**
```bash
# 创建系统提示配置
mkdir -p .trae
cp ~/.claude/skills/api-development/SKILL.md .trae/system-prompt.md
```

**编辑器设置**
- Settings → AI Assistant → System Prompt → 导入 SKILL.md

### 自动匹配配置（所有编辑器通用）

**多技能自动匹配方案**
```bash
# 创建组合规则文件，包含多个技能的触发词
cat > .cursorrules << 'EOF'
## 技能触发规则

当用户提到以下关键词时，自动应用对应技能：

- API开发、接口设计 → 应用 api-development 技能
- 代码审查、PR审查 → 应用 code-review 技能  
- 调试、报错 → 应用 systematic-debugging 技能
- 测试、TDD → 应用 test-driven-development 技能
- Docker、K8s → 应用 docker-devops / kubernetes 技能
- React、Vue → 应用 react-component / vue-development 技能

## 当前激活技能
EOF

# 追加具体技能内容
cat ~/.claude/skills/design-brainstorming/SKILL.md >> .cursorrules
```

---

## 来源

整合自以下仓库精华内容：

- [anthropics/skills](https://github.com/anthropics/skills)
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
- [obra/superpowers](https://github.com/obra/superpowers)
- [Chalarangelo/30-seconds-of-code](https://github.com/Chalarangelo/30-seconds-of-code)
- [bytedance/deer-flow](https://github.com/bytedance/deer-flow)

---

## 新增技能

| 技能        | 触发词                    | 功能                |
| ----------- | ------------------------- | ------------------- |
| mcp-matcher | mcp, 工具匹配, 服务器选择 | 智能选择 MCP 服务器 |

---

## 工具匹配矩阵

当用户未明确指定工具时，按以下优先级自动匹配：

### 浏览器自动化

- **首选**: Playwright MCP (mcp6\_\*) - E2E测试、表单填写
- **备选**: Puppeteer MCP (mcp8\_\*) - PDF生成

### 搜索与信息

- **语义搜索**: Exa MCP (mcp1\_\*)
- **直接获取**: Fetch MCP (mcp2\_\*)
- **GitHub文档**: DeepWiki MCP (mcp0\_\*)

### 文件与Git

- **文件操作**: Filesystem MCP (mcp4\_\*)
- **Git操作**: Git MCP (mcp5\_\*)
- **设计稿**: Figma MCP (mcp3\_\*)

### 知识与推理

- **记忆**: Memory MCP (mcp7\_\*)
- **推理**: Sequential Thinking MCP

---
