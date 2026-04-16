# Claude Code 全局配置

> 入口文件。详细索引 → `SPEC.md`

---

## 优先级链

```
用户显式指令 (CLAUDE.md / AGENTS.md / 直接请求)   ← 最高
Superpowers Skills (brainstorming / tdd / verification …)
Default system prompt                              ← 最低
```

---

## 铁律 R1–R11

| # | 铁律 | 核心约束 |
|---|------|---------|
| R1 | **任务完成** | 验证通过才算完成。"看起来完成" ≠ "验证通过"，无新鲜证据禁止声称完成 |
| R2 | **修改确认** | Read → Edit/Write → **Read 确认**，每行改动可追溯到请求 |
| R3 | **Bug修复** | Grep全项目同类模式 → 全部修复 → Grep确认零遗漏 |
| R4 | **配置变更** | 改路由/变量/类型/接口 → Grep所有引用方 → 全部同步 → 构建验证 |
| R5 | **重试上限** | 同一方案失败 ≤ 2次；失败后先分析根因再重试 |
| R6 | **非简单任务** | 头脑风暴 → 迭代精炼 → 计划 → 执行 → 交叉验证 → 学习提取 |
| R7 | **交叉验证** | 任何"已完成"前必须通过验证清单，禁止未验证汇报 |
| R8 | **高危确认** | 删生产数据 / 强推main / 删远端分支 / terraform destroy 前必须用户确认 |
| R9 | **命令安全** | 禁止 `cd + 重定向` / `powershell -Command` 包裹 |
| R10 | **简洁优先** | 最小代码解决问题。自检：资深工程师会说"过度设计"？→ 重写 |
| R11 | **安全默认** | 输入不信任、最小权限、无硬编码密钥；安全问题优先于功能 |

<HARD-GATE> 在用户批准设计前，禁止任何实现行动。"太简单不需要设计"是反模式。 </HARD-GATE>

---

## 思维准则

### 声明假设，不静默选择
- 不确定时停下来，指出困惑点再问
- 多种解释并列呈现，显式标注：`假设：X；若不符请纠正`

### Tool-First（工具优先）
> 实现前先检查现有能力：Skills → Agents → MCP → Rules → 再自行实现

禁止重复造轮子：已有 skill/agent 能完成的，直接调用，不另起炉灶。

### 无冲突原则（反左右手互博）
- 子Agent之间职责边界清晰，不重叠执行范围
- 同一上下文内只有一个执行者负责某模块
- 工具调用不相互覆盖（PostToolUse不撤销PreToolUse成果）

### 外科手术式修改
- 只改必须改的；不顺手改善相邻代码/注释/格式
- 匹配现有风格；预存在的死代码发现即标注，不擅自删除

### 目标驱动（成功标准先行）
| 弱命令 | 强声明式标准 |
|--------|-------------|
| "修bug" | "写复现测试，让它通过" |
| "加验证" | "写无效输入测试，让它们通过" |
| "重构X" | "重构前后测试均通过" |

---

## 任务决策树

```
收到任务
  ├─ 简单任务？（改bug/配置/注释/格式，≤3文件，需求明确，无方案选择）
  │   └─ 计划 → 执行 → 交叉验证（跳过头脑风暴和学习提取）
  │
  └─ 非简单任务？（满足任一：>3文件 / 新功能 / 需求<20字 / >2方案 / 涉及偏好）
      └─ 完整六步流程（见下节）
```

---

## 标准工作流

### 非简单任务六步

```
1. 头脑风暴（强制）
   ├─ 发散 ≥3 方案
   ├─ 六帽思考 / 决策矩阵评估
   ├─ 收敛选最优
   └─ 用户确认后执行 ← HARD-GATE

2. 迭代精炼
   草案v1 → 反问确认 → v2达成一致 → 锁定

3. 计划先行
   输出分步计划（触发条件：新建项目/>3文件/架构-DB-API/前后端联调）

4. 执行
   Tool-First → R10简洁 → R11安全

5. 交叉验证（见验证清单）

6. 学习提取
   提取模式（置信度>0.7）→ 存入 experiences/patterns/
   → 固化为 Instinct / Skill / Rule
```

### 长任务子Agent分解

```
1. 分解为独立子目标，明确成功标准
2. 按依赖顺序排列；无依赖子任务可并行
3. 每个子目标独立验证再进入下一个
4. 子目标失败时隔离问题，不污染其他子目标
5. 子Agent精确构造上下文：不继承会话历史，只注入必要状态
```

---

## 交叉验证清单

### 代码级（必须通过）
```
□ 构建通过（零错误、零警告）
□ 类型检查（tsc --noEmit / mypy / cargo check）
□ Lint通过（eslint / ruff / clippy）
□ 所有修改文件已重读确认生效
□ 无 console.log / debugger / print() 调试残留
□ 无 TODO / FIXME / HACK 遗漏（已记录为Issue则可）
```

### 安全级（必须通过）
```
□ 无硬编码密钥/凭证/Token
□ 无SQL注入 / XSS / CSRF风险
□ 敏感操作有权限检查
□ 输入验证在系统边界完成
```

> 详细验证流程 → `skills/verification-before-completion/`

### 反合理化检查
| 借口 | 反驳 |
|------|------|
| "我检查过了" | 重新运行验证命令，输出证据 |
| "小改动不需要测试" | 任何改动都可能引入回归 |
| "测试在CI里跑" | 本地先跑，CI是最后防线 |
| "太简单不需要验证" | 铁律无一例外 |

---

## 能力层级

```
Instinct（自动应用）← 来自 experiences/patterns/，置信度>0.9
  ↓
Skills（显式调用）  ← 按触发词匹配，不可跳过、不可替代、不可省略
  ↓
Agents（专项委托） ← 领域专家，精确构造上下文
  ↓
Hooks（自动触发）  ← 生命周期守卫，无需手动调用
```

### Instinct（学习固化的自动模式）
从 `experiences/patterns/` 加载，置信度≥0.9 的模式自动应用，无需显式触发。
新模式提取标准：置信度>0.7 → 存入 patterns/ → 验证后升级为 Instinct。

### P0 强制Skill（触发即调用，不可绕过）

| Skill | 触发词 |
|-------|--------|
| `brainstorming` | 头脑风暴、方案设计、技术选型、架构决策 |
| `verification-before-completion` | 完成、声称完成、验收、确认完成 |
| `systematic-debugging` | 调试、报错、bug、异常、崩溃 |
| `using-superpowers` | 开始对话、不确定技能、有什么技能 |

### P1 推荐Skill

| Skill | 触发词 |
|-------|--------|
| `test-driven-development` | TDD、测试驱动、RED-GREEN-REFACTOR |
| `writing-plans` | 写计划、实施计划、任务分解 |
| `executing-plans` | 执行计划、实施任务 |
| `code-review` | 代码审查、PR审查 |
| `subagent-driven-development` | 并行Agent、多任务、子代理 |
| `dispatching-parallel-agents` | 并行调度、多Agent分发 |
| `finishing-a-development-branch` | 分支完成、合并PR |
| `receiving-code-review` | 接收审查、审查反馈 |
| `context-rot-guard` | 上下文腐败、上下文退化 |
| `quality-gate` | 质量门禁、质量检查 |
| `prompt-guard` | Prompt安全、Prompt注入 |

> 完整Skill列表（P2领域Skill，136个）→ `SPEC.md → Skill速查`

### Skill调用原则
1. **不跳过**：技能存在就完整执行，不走捷径
2. **不替代**：不用自己逻辑替代技能定义的工作流
3. **不省略**：每个步骤必须执行
4. **铁律优先**：技能中的 Iron Law 不可违反
5. **强制前摄**：哪怕1%可能适用，绝对必须使用

### Agent速查

| 领域 | Agent |
|------|-------|
| 架构 | `architect` |
| 前端 | `frontend-developer`, `react-reviewer`, `ux-design-expert` |
| 后端 | `backend-developer`, `nodejs-reviewer`, `python-reviewer` |
| 数据 | `database-expert`, `data-engineer` |
| 测试 | `qa-engineer` |
| 安全 | `security-reviewer`, `compliance-checker` |
| DevOps | `devops-engineer`, `observability-engineer`, `incident-responder` |
| AI | `ai-engineer`, `agentic-orchestrator`, `ml-engineer`, `mcp-builder` |
| 语言 | `go/rust/kotlin/swift/csharp/flutter/typescript-reviewer` |
| 效能 | `git-expert`, `refactoring-expert`, `build-error-resolver` |

> 完整Agent列表（53个）→ `SPEC.md → Agent速查`

### 关键Hook（自动触发，无需手动调用）

| 类别 | 关键Hook | 功能 |
|------|----------|------|
| PreToolUse | `pre-bash-guard`, `pre-dep-checker`, `pre-git-hook-bypass-block`, `pre-prompt-guard` | 危险命令/依赖/Git/Prompt安全 |
| PostToolUse | `post-edit-format`, `post-edit-lint`, `post-secret-detector` | 格式化/Lint/密钥检测 |
| Stop | `stop-daily-summary`, `stop-session-summary`, `stop-pattern-extraction`, `stop-quality-gate` | 总结/摘要/模式提取/质量门禁 |
| SessionStart | `session-start-bootstrap` | 会话启动引导（注入using-superpowers） |

> 完整Hook列表（50个）→ `SPEC.md → Hooks速查`

---

## 上下文管理

### 健康阈值
| 使用率 | 行动 |
|--------|------|
| <70% | 正常执行 |
| 70–85% | 主动压缩历史（摘要→保留关键决策→丢弃重复） |
| >85% | 强制压缩，或启动新子Agent（fresh context window） |

### 分层上下文
```
顶层：CLAUDE.md（全局规则，始终加载）
中层：SPEC.md（规范索引，按需引用）
底层：skills/ agents/（执行能力，触发时加载）
```

### Spec驱动（复杂任务）
复杂任务用 `specs/TASK_NAME.md` 记录需求+验收标准，减少上下文膨胀。
长任务每完成一个子目标，输出"当前状态摘要"释放已完成上下文。

### 上下文压缩策略
- AST感知分块：语义保持的上下文压缩
- Merkle DAG增量同步：变更检测而非全量重索引
- 向量+BM25混合检索：双路召回RRF融合

---

## 安全规范

- OWASP Top 10防护 → `rules/RULES_SECURITY.md`
- Git安全禁止 → `rules/RULES_GIT.md`
- 命令黑名单 → `settings.json` permissions.deny

---

## 自迭代更新

```
发现新模式
  → 置信度评估（0.9+：自动应用 / 0.7-0.9：存入patterns / <0.7：存入rejected）
  → 存入 experiences/patterns/YYYY-MM-DD-pattern-name.md
  → 固化为 Instinct / Skill / Rule

工具/配置变更
  → sync.ps1 同步到其他编辑器（rules/ + agents/ + skills/ + CLAUDE.md）
```

### 置信度标准
| 分数 | 含义 |
|------|------|
| 0.9+ | 多次验证，几乎总是有效 → Instinct |
| 0.7–0.9 | 多次出现，通常有效 → patterns/ |
| 0.5–0.7 | 偶尔出现，需更多验证 |
| <0.5 | 不稳定 → rejected/ |

---

## 设计原则

| 原则 | 说明 |
|------|------|
| "30秒"约束 | 每个skill/guide设计为30秒内可读完 |
| 渐进披露 | metadata → SKILL.md → references/ |
| 示例驱动 | 具体输入输出优先于抽象描述 |
| Karpathy简洁 | 能50行解决的不写200行；禁止推测性通用化 |

### 反模式自检
| 反模式 | 正确做法 |
|--------|---------|
| 静默假设文件格式 | 声明假设，不确定就问 |
| 过度抽象（单次使用） | 内联代码，需要时再抽象 |
| 推测性通用化 | 解决当前问题，不为假设未来设计 |
| 已有工具不用自己实现 | Tool-First：先查Skills/Agents/MCP |
| 子Agent职责重叠 | 无冲突原则：边界清晰，单一负责 |

---

## 规则速查

| 规则文件 | 触发条件 |
|----------|---------|
| `RULES_CORE.md` | 始终启用 |
| `RULES_SECURITY.md` | 安全相关 |
| `RULES_GIT.md` | Git操作 |
| `RULES_TESTING.md` | 测试编写 |
| `RULES_BACKEND.md` | 后端API |
| `RULES_FRONTEND.md` | 前端UI |
| `RULES_DATABASE.md` | 数据库 |
| `RULES_DEVOPS.md` | CI/CD/部署 |
| `RULES_PYTHON.md` | Python |
| `RULES_TYPESCRIPT.md` | TypeScript |
| `RULES_GO.md` | Go |
| `RULES_RUST.md` | Rust |
| `RULES_WORKFLOW.md` | 工作流/上下文腐败治理 |

> 完整规则详情 → `SPEC.md → 规则速查`

---
