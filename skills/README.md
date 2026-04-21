# Skills 技能库

> 整合自 [anthropics/skills](https://github.com/anthropics/skills)、[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)、[obra/superpowers](https://github.com/obra/superpowers)

---

## 设计原则（来自 anthropics/skills）

### 1. description 即触发器
通过 `description` 字段的自然语言描述实现触发，而非硬编码关键词。

### 2. 自包含
每个 skill 文件夹内含所有必要资源。

### 3. 模板起步
基于现有模板修改，不从零构建。

### 4. 黑盒脚本
复杂脚本作为工具调用，不提前阅读源码。

### 5. 外部权威
引用 live 文档而非重复内容。

### 6. 渐进披露
```
metadata → SKILL.md → references/
```

### 7. "30秒"约束
每个 skill 设计为 30 秒内可读完/理解。

---

## 标准 SKILL.md 格式

```markdown
---
name: skill-name                    # 唯一标识符，小写连字符
description: 一句话描述技能用途和使用场景
triggers: [触发词1, 触发词2]        # 可选，增强触发
---

# Skill名称

## @Examples
```
用户: "..."
Claude: /skill-name → [动作]
```

## 核心流程
[简洁流程]

## 步骤
### 1. [步骤名]
[说明]

## 输出格式
```markdown
[输出模板]
```

## Tips
- 技巧1
- 技巧2

## Common Use Cases
- 用例1
- 用例2
```

---

## Frontmatter 字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | **是** | 唯一标识符，小写连字符 |
| `description` | **是** | 触发条件描述，自然语言 |
| `triggers` | 否 | 关键词罗列，增强触发 |
| `model` | 否 | 指定模型，默认 inherit |
| `color` | 否 | UI颜色标识 |

---

## Skill 分类（148个）

### P0 强制Skill（4个）

| Skill | 触发词 | 功能 |
|-------|--------|------|
| `brainstorming/` | 头脑风暴、方案设计 | 发散→收敛→确认 |
| `verification-before-completion/` | 完成、验收 | 交叉验证清单 |
| `systematic-debugging/` | 调试、报错 | 四阶段调试 |
| `using-superpowers/` | 技能调用 | 技能发现规则 |

### P1 推荐Skill（6个）

| Skill | 触发词 | 功能 |
|-------|--------|------|
| `test-driven-development/` | TDD、RED-GREEN | 测试先行 |
| `writing-plans/` | 写计划、实施 | 任务分解 |
| `code-review/` | 代码审查、PR | 全流程审查 |
| `subagent-driven-development/` | 并行Agent | 子代理调度 |
| `finishing-a-development-branch/` | 分支完成 | 分支收尾 |
| `receiving-code-review/` | 接收审查 | 处理反馈 |

### P2 开发流程（10个）

| Skill | 触发词 | 功能 |
|-------|--------|------|
| `iterative-refinement/` | 迭代精炼 | 持续改进 |
| `collision-zone-thinking/` | 碰撞区思考 | 反转假设 |
| `inversion-exercise/` | 反转练习 | 约束探索 |
| `meta-pattern-recognition/` | 元模式 | 跨领域模式 |

### P3 后端开发（14个）

`api-development/`, `api-mock/`, `db-migration/`, `database-design/`, `message-queue/`, `middleware/`, `mcp-builder/`, `nodejs-backend/`, `python-backend/`, `scheduled-task/`, `socket-event/`, `sql-database/`, `websocket-server/`, `clickhouse-analytics/`

### P4 前端开发（9个）

`frontend-design/`, `react-component/`, `vue-development/`, `typescript/`, `state-management/`, `i18n-support/`, `theme-config/`, `web-artifacts-builder/`, `d3-visualization/`

### P5 移动开发（10个）

`flutter-development/`, `react-native/`, `android-development/`, `ios-native-dev/`, `capacitor-app/`, `mini-program/`, `mobile-ui/`, `mobile-performance/`, `mobile-deployment/`, `uniapp-development/`

### P6 测试与质量（12个）

`testing-standards/`, `test-driven-development/`, `api-testing/`, `webapp-testing/`, `code-review/`, `code-refactor/`, `code-standards/`, `error-handling/`, `performance-optimization/`, `security-best-practices/`, `regex-helper/`, `receiving-code-review/`

### P7 运维部署（8个）

`docker-devops/`, `kubernetes/`, `aws-cloud/`, `cicd-pipeline/`, `nginx-config/`, `deploy-script/`, `n8n-automation/`, `logging-monitoring/`

### P8 安全与取证（4个）

`security-best-practices/`, `security-forensics/`, `secure-deletion/`, `ffuf-fuzzing/`

### P9 数据与分析（6个）

`data-analysis/`, `deep-research/`, `content-research/`, `market-research/`, `clickhouse-analytics/`, `sql-database/`

### P10 文档办公（8个）

`docx/`, `pdf/`, `pptx/`, `xlsx/`, `changelog-generator/`, `doc-coauthoring/`, `report-generator/`, `api-documentation/`

### P11 创意设计（7个）

`canvas-design/`, `brand-guidelines/`, `algorithmic-art/`, `theme-factory/`, `image-generation/`, `d3-visualization/`, `slack-gif-creator/`

### P12 基础组件（12个）

`fullstack-auth/`, `env-config/`, `data-validation/`, `file-upload/`, `caching-strategy/`, `rate-limiting/`, `redis-cache/`, `mongodb/`, `search-engine/`, `monorepo-management/`, `google-workspace/`, `slack-integration/`

### P13 AI与开发（4个）

`claude-api/`, `prompt-engineering/`, `software-architecture/`, `mcp-builder/`

### P14 自动化工具（6个）

`python-automation/`, `web-scraping/`, `rpa-automation/`, `video-processing/`, `audio-processing/`, `image-enhancement/`

### P15 效率与生活（8个）

`file-organization/`, `note-management/`, `time-management/`, `meeting-productivity/`, `learning-resources/`, `health-tracking/`, `personal-finance/`, `kaizen-improvement/`

### P16 工具与工作流（11个）

`git-workflow/`, `git-worktrees/`, `skill-creator/`, `notion-integration/`, `linear-integration/`, `command-reference/`, `architecture-diagrams/`, `api-documentation/`, `internal-communication/`, `resume-generator/`, `lead-research-assistant/`

### P17 内容创作（5个）

`article-writing/`, `domain-brainstorm/`, `investor-materials/`, `competitive-ads-extractor/`, `content-research/`

---

## Skill 创建模板

### 简单型（纯指令型）
```
skill-name/
  SKILL.md          # 唯一文件
```

### 资源型（带辅助文件）
```
skill-name/
  SKILL.md
  templates/       # 代码模板
  scripts/         # 辅助脚本
  examples/        # 示例文件
  reference/       # 参考文档
```

### 多语言型
```
claude-api/
  SKILL.md
  python/          # 语言子目录
  typescript/
  curl/
  go/
  shared/          # 共享文档
```

---

## 使用方式

### Claude Code
自动识别 `~/.claude/skills/` 目录下的 SKILL.md

### Cursor / Windsurf / Trae
通过 `sync.ps1` 同步后，在编辑器设置中引用对应 skill 目录

### 手动调用
```
/skill-name
```

---

## 触发词设计

### 描述性触发（主要）
```yaml
description: "Use this skill when someone asks about..."
```

### 显式 TRIGGER / DO NOT TRIGGER（推荐）
```yaml
description: |
  TRIGGER when: 用户需要生成Word文档、修改docx文件、提取文档内容
  DO NOT TRIGGER when: 用户只是提及"文档"但没有具体文件操作需求；用户要求生成PDF/PPT/Excel
```

### 关键词列表
```yaml
description: "A set of resources to help me write..."
triggers: [keyword1, keyword2, keyword3]
```

### 触发词设计原则
1. **具体场景优先**：描述具体使用场景而非抽象概念
2. **正反例明确**：用 TRIGGER / DO NOT TRIGGER 减少误触发
3. **动词开头**："生成"、"分析"、"调试"等动作词提高匹配精度
4. **避免过度宽泛**："开发"、"编程"等词会导致技能冲突
5. **渐进披露**：metadata → SKILL.md → references/，按需加载避免上下文膨胀

---

## 来源

- [anthropics/skills](https://github.com/anthropics/skills) - 官方技能标准
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) - 技能集合
- [obra/superpowers](https://github.com/obra/superpowers) - 工作流系统
- [bytedance/deer-flow](https://github.com/bytedance/deer-flow) - 任务规划
- [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) - 极简工作流

---

## 统计

| 分类 | 数量 |
|------|------|
| P0 强制 | 4 |
| P1 推荐 | 6 |
| P2 开发流程 | 10 |
| P3 后端开发 | 14 |
| P4 前端开发 | 9 |
| P5 移动开发 | 10 |
| P6 测试与质量 | 12 |
| P7 运维部署 | 8 |
| P8 安全与取证 | 4 |
| P9 数据与分析 | 6 |
| P10 文档办公 | 8 |
| P11 创意设计 | 7 |
| P12 基础组件 | 12 |
| P13 AI与开发 | 4 |
| P14 自动化工具 | 6 |
| P15 效率与生活 | 8 |
| P16 工具与工作流 | 11 |
| P17 内容创作 | 5 |
| **总计** | **148** |
