# Claude Code 全局配置

> 本文件是所有配置的入口，详细的分类索引请查看 `SPEC.md`

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

<HARD-GATE> 在用户批准设计前，禁止任何实现行动。反模式："这太简单不需要设计"——每个项目都必须经过设计审批 </HARD-GATE>

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
- 禁止：单次使用的封装 / 未请求的配置项 / 不可能场景的错误处理 / 推测性功能
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

### 简洁优先（Karpathy 原则）
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

### 安全级验证（必须通过）
```
□ 无硬编码密钥/凭证/Token
□ 无 SQL 注入 / XSS / CSRF 风险
□ 敏感操作有权限检查
□ 输入验证在系统边界完成
```

> 详细验证流程（测试级/功能级/交叉验证/反合理化检查）见 `verification-before-completion` skill

### 反合理化检查
| 合理化借口 | 反驳 |
|------------|------|
| "我检查过了" | 重新运行验证命令，输出证据 |
| "小改动不需要测试" | 任何改动都可能引入回归 |
| "测试在 CI 里跑" | 本地先跑，CI 是最后防线 |
| "太简单不需要验证" | 铁律无一例外 |

---

## 修改彻底性

Bug修复遵循 R3 铁律，配置变更遵循 R4 铁律，详见对应规则

---

## Skill 系统

> 详细索引见 `SPEC.md → Skill 速查`

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
> 即使你认为某项技能有哪怕 1%的可能适用，你也绝对必须使用它。这一点没有商量的余地。

---

## Agent 系统

> 详细索引见 `SPEC.md → Agent 速查`

| 领域 | Agent | 场景 |
|------|-------|------|
| **架构** | `architect` | 系统设计、架构决策 |
| **前端** | `frontend-developer`, `react-reviewer`, `ux-design-expert` | 前端开发/审查/设计 |
| **后端** | `backend-developer`, `nodejs-reviewer`, `python-reviewer` | 后端开发/审查 |
| **数据** | `database-expert`, `data-engineer` | 数据库设计/数据工程 |
| **测试** | `qa-engineer` | 测试策略/自动化 |
| **安全** | `security-reviewer`, `compliance-checker` | 安全审查/合规 |
| **DevOps** | `devops-engineer`, `observability-engineer`, `incident-responder` | CI/CD/监控/故障响应 |
| **AI** | `ai-engineer`, `agentic-orchestrator`, `ml-engineer`, `mcp-builder` | AI/LLM应用/编排/ML |
| **语言** | `go/rust/kotlin/swift/csharp/flutter/typescript-reviewer` | 语言专项审查 |
| **效率** | `git-expert`, `refactoring-expert`, `build-error-resolver` | Git/重构/构建错误 |

---

## Hook 系统

> 详细索引见 `SPEC.md → Hooks 速查`（Claude Code 专用，其他编辑器通过 launcher 跳过）

| 类别 | 关键Hook | 功能 |
|------|----------|------|
| **PreToolUse** | `pre-bash-guard`, `pre-dep-checker`, `pre-git-hook-bypass-block` | 危险命令拦截、依赖安全、Git安全 |
| **PostToolUse** | `post-edit-format`, `post-edit-lint`, `post-secret-detector` | 格式化、Lint、密钥检测 |
| **Stop** | `stop-daily-summary`, `stop-session-summary`, `stop-pattern-extraction` | 总结、摘要、模式提取 |

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

### 上下文注入原则
- SessionStart 时注入 using-superpowers
- 子代理精确构造：从不继承会话历史

### 上下文压缩
- AST感知分块：语义保持的上下文压缩
- Merkle DAG增量同步：变更检测而非全量重索引
- 向量+BM25混合检索：双路召回RRF融合

### Context Rot 治理
- 上下文腐败度 >70%：强制压缩或启动新子Agent（fresh context window）
- 每完成一个子目标：输出状态摘要，释放已完成上下文
- 长任务（>30分钟）：拆分为独立子Agent，每个子Agent有明确成功标准

---

## 安全规范

OWASP Top 10 防护详见 `RULES_SECURITY.md`，Git安全禁止详见 `RULES_GIT.md`，命令黑名单详见 `settings.json` permissions.deny

---

## 规则自动加载

详见 `SPEC.md → 规则速查`。核心：`RULES_CORE.md` 始终启用，其余按 globs 条件按需加载。

---

## 自迭代更新

- 新发现模式 → 提取为 skill/rule（置信度 >0.7）→ `experiences/patterns/`
- 工具变更 → `sync.ps1` 同步到编辑器
- 同步范围：`rules/` + `agents/` + `skills/` + `CLAUDE.md`

---

## 设计原则

### "30秒"约束
每个技能/指南设计为30秒内可读完/理解

### 渐进披露
```
metadata → SKILL.md → references/
```

### 示例驱动
具体输入输出示例优先于抽象描述

### 反模式自检
| 反模式 | 正确做法 |
|--------|---------|
| 静默假设文件格式 | 声明假设，不确定就问 |
| 过度抽象（单次使用） | 内联代码，需要时再抽象 |
| 推测性通用化 | 解决当前问题，不为假设的未来设计 |
| 不必要的复杂性 | 自检：资深工程师会说"过度设计"？→ 重写 |

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

## 工作流引用

TDD: `test-driven-development` skill | PR Review: `code-review` skill | Phase: `writing-plans` skill
