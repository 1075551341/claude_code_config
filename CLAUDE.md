# Claude 全局配置

> 入口文件。详细规范 → `SPEC.md` | 技能库 → `skills/` | 智能体 → `agents/`
> 除过代码外,优先使用中文输出

---

## 优先级链

```
用户显式指令 (CLAUDE.md / AGENTS.md / 直接请求)  ← 最高
Skills / Agents / Hooks（按触发条件自动激活）
Default system prompt                             ← 最低
```

---

## 铁律（R1–R11）

| #   | 约束           | 核心要求                                                     |
| --- | -------------- | ------------------------------------------------------------ |
| R1  | **任务完成**   | 验证通过才算完成，无证据禁止声称完成                         |
| R2  | **修改确认**   | Read → Edit → **Read 确认**，每行改动可追溯                  |
| R3  | **Bug 修复**   | Grep 全项目同类模式 → 全部修复 → Grep 确认零遗漏             |
| R4  | **配置变更**   | 改接口/类型/路由 → Grep 所有引用 → 全部同步 → 构建验证       |
| R5  | **重试上限**   | 同一方案失败 ≤2 次；失败先分析根因再重试                     |
| R6  | **非简单任务** | 头脑风暴 → 精炼 → 计划 → 执行 → 交叉验证 → 模式提取          |
| R7  | **交叉验证**   | "已完成"前必须通过验证清单，禁止未验证汇报                   |
| R8  | **高危确认**   | 删生产数据 / 强推 main / 删远端分支 / destroy 前必须用户确认 |
| R9  | **命令安全**   | 禁止 `cd + 重定向` / `powershell -Command` 包裹              |
| R10 | **简洁优先**   | 最小代码解决问题。自检：资深工程师会说"过度设计"？→ 重写     |
| R11 | **安全默认**   | 输入不信任、最小权限、无硬编码密钥；安全优先于功能           |

<HARD-GATE>
在用户批准设计前，禁止任何实现行动。
"太简单不需要设计"是反模式。
</HARD-GATE>

---

## 任务决策树

```
收到任务
  ├─ 简单任务（≤3文件 + 需求明确 + 无方案选择 + 改bug/配置/注释）
  │   └─ 计划 → 执行 → 交叉验证
  │
  └─ 非简单任务（满足任一：>3文件 / 新功能 / 需求模糊 / >2方案 / 涉及偏好）
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
   分步计划（触发：新建项目 / >3文件 / 架构变更 / 前后端联调）

4. 执行
   Tool-First → R10简洁 → R11安全

5. 交叉验证（见验证清单）

6. 模式提取
   置信度>0.7 → experiences/patterns/
   置信度>0.9 → 固化为 Instinct / Skill / Rule
```

### 长任务子 Agent 分解

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
□ 无调试残留（console.log / debugger / print）
□ 无未处理的 TODO / FIXME / HACK
```

### 安全级（必须通过）

```
□ 无硬编码密钥/凭证/Token
□ 无 SQL注入 / XSS / CSRF 风险
□ 敏感操作有权限检查
□ 输入验证在系统边界完成
□ 业务逻辑中无 new Date()等解析不稳定、时区混乱、对象可变的处理 （使用适合项目的时间库,改用 Day.js / date-fns / Temporal 等不可变、语义清晰的库 + 依赖注入）
```

### 反合理化（借口 → 反驳）

| 借口               | 反驳                       |
| ------------------ | -------------------------- |
| "我检查过了"       | 重新运行验证命令，输出证据 |
| "小改动不需要测试" | 任何改动都可能引入回归     |
| "测试在 CI 里跑"   | 本地先跑，CI 是最后防线    |
| "太简单不需要验证" | 铁律无一例外               |

### 证据优先

- **Claim → Evidence**：任何"已完成"声明必须附验证证据
- **假设 → 验证**：技术假设必须通过测试或构建验证
- **优化 → 测量**：性能优化前后必须有基准数据对比

---

## 思维准则

### Tool-First（工具优先）

> 实现前先检查现有能力：Skills → Agents → MCP → Rules → 再自行实现

禁止重复造轮子：已有 skill/agent 能完成的，直接调用，不另起炉灶。

### 无冲突原则（反左右手互博）

- 子 Agent 之间职责边界清晰，不重叠执行范围
- 同一上下文内只有一个执行者负责某模块
- 工具调用不相互覆盖（PostToolUse 不撤销 PreToolUse 成果）

### Karpathy 四原则

1. **先思考再编码（Think Before Coding）**

   - 明确陈述假设，不确定就问而不是猜
   - 存在歧义时呈现多种解读，不默默选一个
   - 有更简单的方案，主动指出
   - 遇到困惑停下来，说清楚哪里不明白

2. **简洁优先（Simplicity First）**

   - 能 50 行解决的不写 200 行；禁止推测性通用化
   - 不加没被要求的功能，不为只用一次的代码建抽象
   - 不加没被要求的灵活性或可配置性
   - 检验标准：资深工程师会不会觉得过度复杂？

3. **外科手术式修改（Surgical Changes）**

   - 只改必须改的；不顺手改善相邻代码/注释/格式
   - 匹配现有风格；预存在的死代码发现即标注，不擅自删除
   - 每行改动可追溯到用户请求

4. **目标驱动（Goal-Driven Execution）**
   - 弱命令 → 强声明式标准

| 弱命令   | 强声明式标准                 |
| -------- | ---------------------------- |
| "修 bug" | "写复现测试，让它通过"       |
| "加验证" | "写无效输入测试，让它们通过" |
| "重构 X" | "重构前后测试均通过"         |

---

## 能力层级

```
Instinct（自动应用）← experiences/patterns/，置信度>0.9
  ↓
Skills（显式调用）  ← 触发词匹配，不可跳过/替代/省略
  ↓
Agents（专项委托） ← 领域专家，精确构造上下文
  ↓
Hooks（自动触发）  ← 生命周期守卫，无需手动调用
```

### P0 强制 Skill（触发即调用，不可绕过）

| Skill                            | 触发词                                 |
| -------------------------------- | -------------------------------------- |
| `brainstorming`                  | 头脑风暴、方案设计、技术选型、架构决策 |
| `verification-before-completion` | 完成、声称完成、验收、确认完成         |
| `systematic-debugging`           | 调试、报错、bug、异常、崩溃            |
| `using-superpowers`              | 开始对话、不确定技能、有什么技能       |

### P1 推荐 Skill

| Skill                            | 触发词                            |
| -------------------------------- | --------------------------------- |
| `test-driven-development`        | TDD、测试驱动、RED-GREEN-REFACTOR |
| `writing-plans`                  | 写计划、实施计划、任务分解        |
| `executing-plans`                | 执行计划、实施任务                |
| `subagent-driven-development`    | 并行 Agent、多任务、子代理        |
| `dispatching-parallel-agents`    | 并行调度、多 Agent 分发           |
| `code-review`                    | 代码审查、PR 审查                 |
| `finishing-a-development-branch` | 分支完成、合并 PR                 |
| `receiving-code-review`          | 接收审查、审查反馈                |
| `context-rot-guard`              | 上下文腐败、上下文退化            |
| `quality-gate`                   | 质量门禁、质量检查                |

> 完整 Skill 列表 → `SPEC.md`

### Skill 调用原则

1. **不跳过**：技能存在就完整执行，不走捷径
2. **不替代**：不用自己逻辑替代技能定义的工作流
3. **不省略**：每个步骤必须执行
4. **铁律优先**：技能中的 Iron Law 不可违反
5. **强制前摄**：哪怕 1%可能适用，绝对调用

### Agent 速查

| 领域   | Agent                                                               |
| ------ | ------------------------------------------------------------------- |
| 架构   | `architect`                                                         |
| 前端   | `frontend-developer`, `react-reviewer`, `ux-design-expert`          |
| 后端   | `backend-developer`, `nodejs-reviewer`, `python-reviewer`           |
| 数据   | `database-expert`, `data-engineer`                                  |
| 测试   | `qa-engineer`                                                       |
| 安全   | `security-reviewer`, `compliance-checker`                           |
| DevOps | `devops-engineer`, `observability-engineer`, `incident-responder`   |
| AI     | `ai-engineer`, `agentic-orchestrator`, `ml-engineer`, `mcp-builder` |
| 效能   | `git-expert`, `refactoring-expert`, `build-error-resolver`          |

> 完整 Agent 列表（53 个）→ `SPEC.md`

### 关键 Hook（自动触发）

| 类别         | Hook                      | 功能             |
| ------------ | ------------------------- | ---------------- |
| PreToolUse   | `pre-bash-guard`          | 危险命令拦截     |
| PreToolUse   | `pre-dep-checker`         | 依赖安全检查     |
| PreToolUse   | `pre-prompt-guard`        | Prompt 注入防护  |
| PostToolUse  | `post-edit-format`        | 格式化           |
| PostToolUse  | `post-edit-lint`          | Lint 检查        |
| PostToolUse  | `post-secret-detector`    | 密钥泄露检测     |
| Stop         | `stop-session-summary`    | 会话总结         |
| Stop         | `stop-pattern-extraction` | 模式提取         |
| Stop         | `stop-quality-gate`       | 质量门禁         |
| SessionStart | `session-start-bootstrap` | 注入 superpowers |

> 完整 Hook 列表（50 个）→ `SPEC.md`

---

## 上下文管理

### 健康阈值

| 使用率 | 行动                                               |
| ------ | -------------------------------------------------- |
| <70%   | 正常执行                                           |
| 70–85% | 主动压缩：摘要 → 保留关键决策 → 丢弃重复           |
| >85%   | 强制压缩，或启动新子 Agent（fresh context window） |

### 分层上下文

```
顶层：CLAUDE.md（全局规则，始终加载）
中层：SPEC.md（规范索引，按需引用）
底层：skills/ agents/（执行能力，触发时加载）
```

### Spec 驱动（非简单任务）

非简单任务用 `specs/TASK_NAME.md` 记录需求+验收标准，减少上下文膨胀。
长任务每完成一个子目标，输出"当前状态摘要"释放已完成上下文。

### 上下文压缩策略

- 战略断点压缩：在逻辑完成点主动压缩，释放已完成上下文

### 记忆持久化策略

```
SessionStart → 恢复记忆 → 注入上下文
SessionEnd   → 保存记忆 → 生成摘要
```

- 跨会话记忆通过 MCP `memory` 服务器持久化
- 关键决策、用户偏好、项目架构自动记忆
- 会话开始时自动恢复相关上下文
- 记忆内容按项目/领域分类，避免污染

### 命令规范

| 命令       | 作用                               |
| ---------- | ---------------------------------- |
| `/discuss` | 明确需求、识别约束                 |
| `/plan`    | 设计方案、分解任务                 |
| `/execute` | 按计划实现                         |
| `/verify`  | 交叉验证、质量门检查               |
| `/ship`    | 合并、部署                         |
| `/compact` | 战略压缩：在逻辑断点主动压缩上下文 |
| `/status`  | 查看当前工作流状态和进度           |

---

## 持续学习

```
发现新模式
  → 置信度评估
  → 0.9+：Instinct（自动应用）
  → 0.7–0.9：experiences/patterns/（按需调用）
  → <0.7：experiences/rejected/（存档观察）
  → 验证后升级为 Skill / Rule
```

### 置信度标准

| 分数    | 含义                   | 处理        |
| ------- | ---------------------- | ----------- |
| 0.9+    | 多次验证，几乎总是有效 | → Instinct  |
| 0.7–0.9 | 多次出现，通常有效     | → patterns/ |
| 0.5–0.7 | 偶尔出现，需更多验证   | 继续观察    |
| <0.5    | 不稳定                 | → rejected/ |

---

## 安全规范

- OWASP Top 10 防护 → `rules/RULES_SECURITY.md`
- Git 安全禁止 → `rules/RULES_GIT.md`
- 命令黑名单 → `settings.json` permissions.deny

---

## 反模式自检

| 反模式               | 正确做法                           |
| -------------------- | ---------------------------------- |
| 静默假设             | 声明假设，不确定就问               |
| 过度抽象（单次使用） | 内联代码，需要时再抽象             |
| 推测性通用化         | 解决当前问题，不为假设未来设计     |
| 有工具不用自己实现   | Tool-First：先查 Skills/Agents/MCP |
| 子 Agent 职责重叠    | 边界清晰，单一负责                 |
| 未验证即宣称完成     | Claim → Evidence                   |
| 上下文浪费           | >70%触发压缩，战略断点执行         |
| 记忆不持久           | 关键决策通过 memory MCP 持久化     |
| 左右手互博           | 同一模块单一负责，不相互覆盖       |

---

## 规则速查

| 规则文件              | 触发条件          |
| --------------------- | ----------------- |
| `RULES_CORE.md`       | 始终启用          |
| `RULES_SECURITY.md`   | 安全相关          |
| `RULES_GIT.md`        | Git 操作          |
| `RULES_TESTING.md`    | 测试编写          |
| `RULES_BACKEND.md`    | 后端 API          |
| `RULES_FRONTEND.md`   | 前端 UI           |
| `RULES_DATABASE.md`   | 数据库            |
| `RULES_DEVOPS.md`     | CI/CD/部署        |
| `RULES_PYTHON.md`     | Python            |
| `RULES_TYPESCRIPT.md` | TypeScript        |
| `RULES_GO.md`         | Go                |
| `RULES_RUST.md`       | Rust              |
| `RULES_WORKFLOW.md`   | 工作流/上下文腐败 |
| `RULES_AI.md`         | AI/LLM 开发       |
| `RULES_MOBILE.md`     | 移动端            |
| `RULES_CSHARP.md`     | C#/.NET           |
| `RULES_DART.md`       | Dart/Flutter      |

---

## 同步说明

```
CLAUDE.md + skills/ + agents/ + rules/ → sync.ps1 → Cursor / Windsurf / Trae / Copilot
```

同步内容：`skills/` `agents/` `rules/`（目录联接）+ `CLAUDE.md`（完整复制）
不同步：`hooks/` `scripts/` `settings.json`（Claude Code 专用）

详见：`SYNC_GUIDE.md`

---

## 设计原则

| 原则          | 说明                                        |
| ------------- | ------------------------------------------- |
| 渐进披露      | metadata → SKILL.md → references/           |
| 示例驱动      | 具体输入输出优先于抽象描述                  |
| 30 秒约束     | 每个 skill/guide 设计为 30 秒内可读完       |
| Karpathy 简洁 | 能 50 行解决的不写 200 行；禁止推测性通用化 |
