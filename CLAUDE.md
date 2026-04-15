# Claude Code 全局配置

> 跨编辑器共享配置：Claude Code / Cursor / Windsurf / Trae / VS Code
>
> 本文件是所有配置的入口，详细的分类索引请查看 `SPEC.md`
>
> 继承自：
> - [anthropics/skills](https://github.com/anthropics/skills) - 官方技能标准
> - [obra/superpowers](https://github.com/obra/superpowers) - 工作流系统
> - [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - 配置集合
> - [zilliztech/claude-context](https://github.com/zilliztech/claude-context) - 上下文管理
> - [bytedance/deer-flow](https://github.com/bytedance/deer-flow) - 任务规划
> - [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) - 极简工作流
> - [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) - 技能集合

---

## 优先级定义

```
User explicit instructions (CLAUDE.md, AGENTS.md, direct requests) — 最高优先级
Superpowers Skills (brainstorming, tdd, verification, etc.) — 次高优先级
Default system prompt — 最低优先级
```

---

## 核心规则

### R1: 任务完成铁律
**任务未完成（需确认或高危操作除外）禁止停止，直到验证通过**
- 验证通过才算完成
- "看起来完成了" ≠ "验证通过了"
- 无新鲜验证证据，不声称完成

### R2: 修改确认铁律
**修改文件后必须重新读取确认生效**
- Read → Edit/Write → Read 确认
- 每行改动可追溯到用户请求

### R3: Bug修复铁律
**Bug修复必须Grep全项目同类模式，全部修复，再Grep确认零遗漏**
```
1. Grep 全项目相同模式 → 列出所有同类问题文件
2. 逐个修复 → 每文件修后重新读取确认
3. Grep 再次确认零遗漏
```

### R4: 配置变更铁律
**配置/接口/类型变更必须Grep所有引用方，全部同步，构建验证**
```
改了路由 → Grep路由路径 → 找到所有页面/组件
改了环境变量 → Grep变量名 → 找到所有读取代码
改了类型定义 → Grep类型名 → 找到所有import文件
改了API接口 → Grep接口URL/方法名 → 找到所有调用方
```

### R5: 重试限制
**失败后分析根因再重试，同一方案失败 ≤ 2 次**

### R6: 非简单任务必须流程
**头脑风暴 → 迭代精炼 → 计划 → 执行 → 交叉验证 → 学习提取**
```
触发条件（满足任一）：
- 涉及 >3 文件
- 新功能
- 需求 <20 字
- >2 种方案
- 涉及偏好选择
```

### R7: 交叉验证铁律
**任何"已完成"前必须通过交叉验证，禁止未验证汇报**

### R8: 高危操作确认
**高危操作前必须用户确认**
- 删生产数据
- 强推 main/master
- 删远端分支
- terraform destroy

### R9: 命令安全
**禁止 `cd + 重定向` / `powershell -Command` 包裹**

### R10: 简洁优先
**最小代码解决问题，禁止未请求的功能/抽象/灵活性/冗余错误处理**
- 能 50 行解决的不写 200 行
- 禁止：单次使用的封装 / 未请求的配置项 / 不可能场景的错误处理
- 自检：资深工程师会说"过度设计"？→ 重写

### R11: 安全默认
**输入不信任、最小权限、无硬编码密钥；安全问题优先于功能**

---

## 思维准则

### 声明假设，不静默选择
- 不确定时停下来，指出困惑点再问
- 不猜测，不悄悄选一个解释
- 多种解释存在时并列呈现
- 更简单方案存在时说出来
- 显式标注约束：`假设：X；若不符请纠正`

### 简洁优先原则（Karpathy 原则）
- 能 50 行解决的不写 200 行
- 不加"以后可能用到"的抽象
- 禁止：单次使用的封装 / 未请求的配置项 / 不可能场景的错误处理 / 推测性功能
- 自检：资深工程师会说"过度设计"？→ 重写

### 外科手术式修改
- 只改必须改的（修改彻底性）
- 不顺手改善相邻代码/注释/格式
- 匹配现有风格
- 自己改动造成的孤儿代码才删
- 预存在的死代码：发现即标注，不擅自删除

### 目标驱动执行（成功标准驱动）
| 命令式（弱） | 声明式成功标准（强） |
|---|---|
| "修 bug" | "写复现测试，让它通过" |
| "加验证" | "写无效输入测试，让它们通过" |
| "重构 X" | "重构前后测试均通过" |

---

## 标准工作流

### 简单任务流程（改bug/配置/注释/格式化）
跳过 1-2-6，3-5 不可跳过：
```
3. 计划先行 → 5. 交叉验证
```

### 非简单任务流程（>3文件/新功能/需求模糊/多方案）

```
1. 头脑风暴（强制）
   ├─ 发散 ≥3 方案
   ├─ 六帽思考/决策矩阵评估
   ├─ 收敛选最优
   └─ 与用户确认后执行

2. 迭代精炼
   ├─ 草案 v1
   ├─ 反问确认
   ├─ v2 达成一致
   └─ 锁定（不一致继续发散）

3. 计划先行
   输出分步计划
   （满足任一：新建项目 / >3文件 / 架构/DB/API / 前后端联调）

4. 执行
   遵循 R10 简洁优先 + R11 安全默认

5. 交叉验证（见下节）

6. 学习提取
   提取模式 → 固化为 instinct/skill/rule → 存入 experiences/
```

### 长任务子Agent分解

```
1. 分解为独立子目标，每个子目标有明确成功标准
2. 按依赖顺序排列；无依赖的子任务可并行
3. 每个子目标完成后独立验证，再进入下一个
4. 子目标失败时隔离问题，不污染其他子目标
```

---

## 交叉验证清单

### 代码级验证（必须通过）
```
□ 构建通过（零错误、零警告）
□ 类型检查通过（tsc --noEmit / mypy / cargo check）
□ Lint 通过（eslint / ruff / clippy）
□ 所有修改文件已重新读取确认修改生效
□ 无 console.log / debugger / print() 调试残留
□ 无 TODO / FIXME / HACK 遗漏（或已记录为 Issue）
```

### 测试级验证（必须通过）
```
□ 单元测试全部通过
□ 修改相关测试已同步更新
□ 新功能有对应测试覆盖
□ 无跳过/禁用的测试
```

### 功能级验证（必须通过）
```
□ 核心功能端到端可运行
□ 错误路径正确处理（非仅 happy path）
□ 边界情况已考虑
□ 性能无明显退化
```

### 安全级验证（必须通过）
```
□ 无硬编码密钥/凭证/Token
□ 无 SQL 注入 / XSS / CSRF 风险
□ 敏感操作有权限检查
□ 输入验证在系统边界完成
```

### 交叉验证（非简单任务必须）
```
□ 换个视角审视：如果我是代码审查者，会提出什么问题？
□ 反向验证：尝试构造让方案失败的场景
□ 需求回溯：方案是否完整覆盖了原始需求？有无偏离？
□ 一致性检查：修改是否与项目现有风格/模式一致？
□ 遗漏扫描：是否有同类文件/同类问题未同步修改？
□ [Bug] Grep再次搜索相同模式 → 确认零遗漏
□ [配置] 构建/类型检查 → 确认零新错误
□ 输出"已修改文件列表"供用户核对
```

### 反合理化检查
| 合理化借口 | 反驳 |
|------------|------|
| "我检查过了" | 重新运行验证命令，输出证据 |
| "小改动不需要测试" | 任何改动都可能引入回归 |
| "测试在 CI 里跑" | 本地先跑，CI 是最后防线 |
| "太简单不需要验证" | 铁律无一例外 |

---

## 修改彻底性

### 场景A — Bug修复
```
1. Grep 全项目相同模式 → 列出所有同类问题文件
2. 逐个修复 → 每文件修后重新读取确认
3. Grep 再次确认零遗漏
```

### 场景B — 配置/接口/类型变更
```
1. Grep 识别影响面：
   ├─ 路由配置   → 所有使用该路由的页面/组件
   ├─ 环境变量   → 所有读取该变量的代码
   ├─ 类型定义   → 所有 import 该类型的文件
   ├─ API 接口   → 所有调用该接口的前后端代码
   └─ 组件 Props → 所有使用该组件的地方
2. 逐个同步 → 每文件修后重新读取确认
3. 构建验证 → 确认无新错误
```

---

## Skill 系统

### P0 强制Skill（不可跳过）

| Skill | 触发词 | 功能 |
|-------|--------|------|
| `brainstorming` | 头脑风暴、方案设计、技术选型、架构决策 | 强制设计先行，发散→收敛→确认 |
| `verification-before-completion` | 完成、声称完成、验收、确认完成 | 交叉验证清单，铁律 |
| `systematic-debugging` | 调试、报错、bug、异常、崩溃 | 四阶段调试，信息→假设→验证→根因 |
| `using-superpowers` | 开始对话、不确定技能、有什么技能 | 技能发现规则 |

### P1 推荐Skill

| Skill | 触发词 | 功能 |
|-------|--------|------|
| `test-driven-development` | TDD、测试驱动、RED-GREEN-REFACTOR | 测试先行开发循环 |
| `writing-plans` | 写计划、实施计划、任务分解 | 详细实施计划编写 |
| `code-review` | 代码审查、PR审查、审查反馈 | 全流程代码审查 |
| `subagent-driven-development` | 并行Agent、多任务、子代理 | 子代理调度与协调 |
| `finishing-a-development-branch` | 分支完成、合并PR | 分支收尾流程 |
| `receiving-code-review` | 接收审查、审查反馈 | 处理审查意见 |

### Skill调用原则
1. **不跳过**：技能存在就必须完整执行，不走捷径
2. **不替代**：不用自己的逻辑替代技能定义的工作流
3. **不省略**：技能的每个步骤都必须执行
4. **铁律优先**：技能中的 Iron Law / 铁律不可违反

### 强制技能前摄
> If you think there is even a 1% chance a skill might apply, you ABSOLUTELY MUST invoke the skill. THIS IS NOT NEGOTIABLE.

---

## Agent 系统

### 调用方式
```
使用 [agent-name] agent 来 [任务描述]
```

### 核心Agent索引

| 领域 | Agent | 场景 |
|------|-------|------|
| **架构** | `architect` | 系统设计、架构决策 |
| **前端** | `frontend-developer` | 前端开发 |
| **前端** | `react-reviewer` | React代码审查 |
| **前端** | `ux-design-expert` | UI/UX设计 |
| **后端** | `backend-developer` | 后端开发 |
| **后端** | `nodejs-reviewer` | Node.js审查 |
| **后端** | `python-reviewer` | Python审查 |
| **数据** | `database-expert` | 数据库设计/优化 |
| **数据** | `data-engineer` | 数据工程 |
| **测试** | `qa-engineer` | 测试策略/自动化 |
| **安全** | `security-reviewer` | 安全审查 |
| **安全** | `compliance-checker` | 合规检查 |
| **DevOps** | `devops-engineer` | CI/CD、容器化 |
| **DevOps** | `observability-engineer` | 监控/可观测性 |
| **DevOps** | `incident-responder` | 故障响应 |
| **架构** | `cloud-cost-optimizer` | 云成本优化 |
| **文档** | `docs-expert` | 文档生成 |
| **文档** | `changelog-generator` | 变更日志 |
| **工程** | `git-expert` | Git工作流 |
| **工程** | `refactoring-expert` | 重构 |
| **工程** | `build-error-resolver` | 构建错误 |
| **AI** | `ai-engineer` | AI/LLM应用 |
| **AI** | `agentic-orchestrator` | 多Agent编排 |
| **AI** | `ml-engineer` | 机器学习 |
| **AI** | `mcp-builder` | MCP服务器开发 |
| **垂直** | `payment-integration` | 支付集成 |
| **垂直** | `game-developer` | 游戏开发 |
| **垂直** | `embedded-engineer` | 嵌入式 |
| **语言** | `go-reviewer` | Go审查 |
| **语言** | `rust-reviewer` | Rust审查 |
| **语言** | `kotlin-reviewer` | Kotlin审查 |
| **语言** | `swift-reviewer` | Swift审查 |
| **语言** | `csharp-reviewer` | C#审查 |
| **语言** | `flutter-reviewer` | Flutter审查 |
| **语言** | `typescript-reviewer` | TypeScript审查 |
| **流程** | `planning-expert` | 规划管理 |
| **流程** | `context-manager` | 上下文管理 |
| **流程** | `verification-checker` | 验证检查 |
| **流程** | `brainstorming` | 头脑风暴 |
| **效率** | `file-organizer` | 文件整理 |
| **创意** | `canvas-design` | 画布设计 |
| **创意** | `ppt-creator` | PPT创建 |
| **图表** | `mermaid-expert` | 图表绘制 |

---

## Hook 系统

> Claude Code 专用，其他编辑器通过 launcher 跳过

### PreToolUse Hooks
| Hook | 功能 | 触发 |
|------|------|------|
| `pre-context-injector` | 上下文注入 | Task/Write/Edit |
| `pre-task-planner` | 任务规划 | Task/Bash/Write |
| `pre-bash-guard` | Bash危险命令拦截 | Bash |
| `pre-dep-checker` | 依赖安全检查 | Bash |
| `pre-config-protection` | 配置文件保护 | Write/Edit |
| `pre-token-budget` | Token预算检查 | 全局 |
| `pre-git-hook-bypass-block` | 阻止git --no-verify | Bash |
| `pre-commit-quality` | 提交前质量检查 | Bash |
| `pre-dev-server-blocker` | 阻止tmux外运行dev server | Bash |
| `pre-git-push-reminder` | push前提醒 | Bash |
| `pre-doc-file-warning` | 文档文件警告 | Write |
| `pre-mcp-health-check` | MCP健康检查 | Bash |
| `pre-compact-state` | 压缩前状态保存 | PreCompact |
| `pre-tool-matcher` | 工具匹配 | 全局 |
| `pre-observe-tool` | 工具执行观察 | 全局 |
| `pre-suggest-compact` | 建议压缩 | 全局 |

### PostToolUse Hooks
| Hook | 功能 | 触发 |
|------|------|------|
| `post-edit-format` | 代码格式化 | Edit/Write |
| `post-edit-lint` | Lint+类型检查 | Edit/Write |
| `post-secret-detector` | 密钥泄露检测 | Edit/Write |
| `post-test-runner` | 自动测试运行 | Bash |
| `post-operation-log` | 操作日志 | 全局 |
| `post-auto-commit` | 自动提交格式 | Bash |
| `post-build-analysis` | 构建分析 | Bash |
| `post-command-log-audit` | 命令日志审计 | Bash |
| `post-cost-tracker` | 成本追踪 | Stop |
| `post-dependency-audit` | 依赖审计 | Bash |
| `post-doc-reminder` | 文档更新提醒 | Stop |
| `post-edit-console-warn` | console.log警告 | Edit |
| `post-governance-capture` | 治理捕获 | Stop |
| `post-observe-result` | 结果观察 | PostToolUse |
| `post-pr-logger` | PR日志 | Bash |
| `post-record-js-edits` | JS编辑记录 | Edit |
| `post-batch-format-typecheck` | 批量格式化检查 | Stop |

### Stop Hooks
| Hook | 功能 |
|------|------|
| `stop-notify` | 桌面通知 |
| `stop-daily-summary` | 每日总结 |
| `stop-readme-updater` | README更新 |
| `stop-debug-checker` | Debug检查 |
| `stop-session-summary` | 会话摘要 |
| `stop-session-end-marker` | 会话结束标记 |
| `stop-pattern-extraction` | 模式提取 |
| `stop-persist-session` | 会话持久化 |
| `stop-cost-tracker` | 成本追踪 |
| `stop-evaluate-patterns` | 模式评估 |

### SessionStart Hooks
| Hook | 功能 |
|------|------|
| `session-start-bootstrap` | 会话启动引导 |

---

## Token 管理

### 上下文健康
- **Spec驱动**：复杂任务用 `specs/TASK_NAME.md` 记录需求+验收标准
- **压缩检查点**：长任务每完成一个子目标，输出"当前状态摘要"
- **CLAUDE.md精简**：本文件只存规则和流程；业务上下文 → `specs/`

### Token预算
- 上下文超 70%：主动压缩历史消息
- 压缩策略：摘要 → 保留关键决策点 → 丢弃重复
- 大文件处理：只读相关章节

---

## 上下文管理策略

### 分层上下文
```
顶层：CLAUDE.md（全局规则）
中层：SPEC.md（规范索引）
底层：skills/agents（执行能力）
```

### 上下文注入原则（来自 superpowers）
- SessionStart 时注入 using-superpowers
- 子代理精确构造：从不继承会话历史

### 上下文压缩（来自 claude-context）
- AST感知分块：语义保持的上下文压缩
- Merkle DAG增量同步：变更检测而非全量重索引
- 向量+BM25混合检索：双路召回RRF融合

---

## 安全规范

### OWASP Top 10 防护
```
1. 注入攻击 → 参数化查询/ORM
2. 失效认证 → JWT短有效期/Refresh Token
3. 敏感泄露 → 过滤敏感字段/日志脱敏
4. XXE → XML解析器安全配置
5. 访问控制 → 资源归属检查
6. 安全配置 → 禁用目录列表/安全Headers
7. XSS → textContent优先/DOMPurify
8. 反序列化 → JSON优先/禁止pickle不可信数据
9. 组件漏洞 → 定期npm audit/及时更新
10. 日志监控 → 记录异常登录/接口异常
```

### Git安全禁止
```
push --force origin main
push --force origin master
git branch -D <branch>
git push origin --delete <branch>
```

---

## 规则自动加载

| 规则 | alwaysApply | 触发条件 |
|------|-------------|----------|
| `RULES_CORE.md` | true | 始终启用 |
| `RULES_GIT.md` | false | Git操作 |
| `RULES_SECURITY.md` | false | 安全相关 |
| `RULES_TESTING.md` | false | 测试编写 |
| `RULES_BACKEND.md` | false | 后端API开发 |
| `RULES_FRONTEND.md` | false | 前端UI开发 |
| `RULES_DATABASE.md` | false | 数据库操作 |
| `RULES_DEVOPS.md` | false | CI/CD/部署 |
| `RULES_PYTHON.md` | false | Python开发 |
| `RULES_TYPESCRIPT.md` | false | TypeScript开发 |
| `RULES_GO.md` | false | Go开发 |
| `RULES_RUST.md` | false | Rust开发 |
| `RULES_CSHARP.md` | false | C#开发 |
| `RULES_DART.md` | false | Flutter/Dart |
| `RULES_MOBILE.md` | false | 移动开发 |

---

## 自迭代更新

- 新发现模式 → 提取为 skill/rule（置信度 >0.7）→ `experiences/patterns/`
- 工具变更 → `sync.ps1` 同步到编辑器
- 同步范围：`rules/` + `agents/` + `skills/` + `CLAUDE.md`

---

## 多编辑器兼容性

通过 `sync.ps1` 同步到：Cursor / Windsurf / Trae / VS Code

### 编辑器适配
| 平台 | 配置目录 | 说明 |
|------|---------|------|
| Claude Code | `.claude/` | 主平台 |
| Cursor | `.cursor/` | 镜像配置 |
| Windsurf | `.windsurf/` | 镜像配置 |
| Trae | `.trae/` | 镜像配置 |
| VS Code | `.vscode/` | 镜像配置 |

### 同步原则
Treat the root `.claude/` as source of truth, then mirror shipped changes to other editors only where the feature actually exists.

---

## 设计原则（来自 30-seconds-of-code）

### "30秒"约束
每个技能/指南设计为30秒内可读完/理解

### 渐进披露
```
metadata → SKILL.md → references/
```

### 示例驱动
具体输入输出示例优先于抽象描述

---

## 经验库（experiences）

### 置信度标准
| 分数 | 含义 |
|------|------|
| 0.9+ | 多次验证，几乎总是有效 |
| 0.7-0.9 | 多次出现，通常有效 |
| 0.5-0.7 | 偶尔出现，需更多验证 |
| <0.5 | 不稳定，存入 rejected |

### 模式提取流程
1. **识别**：从任务/hooks/agents中发现模式
2. **评估**：置信度 >0.7 → 提取
3. **固化**：存入 `experiences/patterns/` + 创建 skill/rule
4. **验证**：在后续任务中验证

---

## TDD 工作流（来自多个仓库）

```
RED (写失败测试) → GREEN (最小代码) → REFACTOR (清理)

原则：
- 测试必须在实现之前编写
- 目标 80%+ 覆盖率（金融/认证 100%）
- 写最小代码使测试通过
```

---

## PR Review 工作流（来自 awesome-claude-code）

```
FETCH → CONTEXT → REVIEW → VALIDATE → DECIDE → REPORT → PUBLISH → OUTPUT

多角色审查：
1. Product Manager Review → 商业价值/用户体验
2. Developer Review → 代码质量/性能
3. Quality Engineer Review → 测试覆盖/边缘case
4. Security Engineer Review → 漏洞/数据保护
5. DevOps Review → CI/CD/基础设施
6. UI/UX Designer Review → 视觉/可用性
```

---

## Phase 工作流（来自 get-shit-done）

```
/gsd-new-project → /gsd-discuss-phase → /gsd-ui-phase → /gsd-plan-phase → /gsd-execute-phase → /gsd-verify-work → /gsd-ship

阶段特点：
- 最小可工作切片优先
- 每阶段可独立合并
- 降低大PR的review难度
```

---

## 附录：文件索引

```
.claude/
├── CLAUDE.md           # 本文件：全局规范入口
├── SPEC.md             # 规范索引：规则/Skill/Agent速查
├── agents/             # 64个Agent定义
├── skills/             # 148个Skill定义
├── rules/              # 16个规则文件
├── hooks/              # 47个Hooks
├── specs/              # 任务规范目录
├── experiences/        # 经验库
│   └── patterns/        # 已验证模式
└── mcp/                # MCP服务器配置
```
