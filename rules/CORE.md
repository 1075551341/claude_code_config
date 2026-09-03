---
trigger: always_on
alwaysApply: true
layer: skeleton
description: 代码开发时始终启用 — 骨架层：编码规范 + 铁律 + 三横切 + 阈值 + 阶段定义
---

# CORE — 机器执行层骨架

> SSOT: 三横切、阈值、编码规范、铁律R1-R20、变更彻底性门控
> 引用: P0路由集/加载等级/五阶段流程 → `CLAUDE.md`（v11: ROUTER 已并入） | 治理详情(R14/R15/R16适用范围/注释模板/变更三阶段/最佳实践详参) → `rules/GOVERNANCE.md`

## 三横切基础设施

```
L1 治理 — ECC(MANIFEST防互博+hook分级+loop防护) + deer-flow 2.0(LangGraph编排,四模式)
L2 优化 — RTK(shell压缩,60-90%) + caveman(输出压缩,~75%) + 三级阈值(上下文治理)
L3 洞察 — codegraph(R17 常驻) + Firecrawl/Exa(外部搜索)  # UA removed v10.5；codebase-memory 已禁用（全盘索引爆 CPU/内存，见 R17）

所有阶段自动注入 L1/L2/L3。柱驱动阶段，横切保障执行。
```

## 上下文腐烂三级阈值

⛔ **铁律: 绝不允许上下文达到 100%。违者任务无效。**

| 使用率 | Cursor                                | Claude Code                     |
| ------ | ------------------------------------- | ------------------------------- |
| <70%   | 正常工作                              | 正常工作                        |
| 70%    | ⚠️ 择机 `/summarize` 或「压缩上下文」 | ⚠️ 择机 `/compact`              |
| 90%    | 🔴 强制 `/summarize` 或新子 Agent     | 🔴 强制 `/compact` 或新子 Agent |

⛔ 绝不允许达到 100%。子 Agent：无依赖并行 | 有依赖串行 | 同制品路径禁止并行写入。

**GSD 逻辑断点（70%）**：到达时完成当前原子任务、切换子 Agent 或写入制品；**非**强制压缩（压缩仍按上表 70%/90%）。

**每完成原子任务 → 评估上下文% → 达阈值按平台压缩**

## 五阶段状态机与门控

> 完整流程 + 状态机 + 门控全部 → `CLAUDE.md` 五阶段流程（SSOT）。

### 错误升级路径

Agent 异常 → 主 Agent 判断：**重试**（瞬态，≤R5 上限2次）→ **降级**（非核心能力不可用，标 DONE_WITH_CONCERNS 继续）→ **需确认**（权限/冲突/数据风险，暴露详情等决策）→ **硬阻断**（安全/不可逆，立即停止+报告）。

**原则**: 不静默吞错（R16），不无限重试（R5），不确定时升级而非猜测。

## 优先级

1. **简单至上** — 最小可行方案，拒绝过度设计
2. **精准响应** — 直击要点，无废话
3. **最佳实践** — 干净代码 + 语义化 + 安全规范
4. **主动确认** — 需求模糊时先问，不盲目执行
5. **第一性原理** — 优先解决本质问题；长期可维护 > 临时运行；代码服务业务目标而非展示技术

## 代码规范

- DRY + 单一职责；不可变优先（新对象/展开/map/filter，不原地修改）
- 未指定语言 → 沿用当前项目技术栈；未指定框架 → 最轻量够用方案
- 安全防御 → `rules/SECURITY.md`；错误处理：每层显式处理，禁止静默吞错，异步必 try/catch
- 输入验证：系统边界验证所有外部输入；内部信任类型系统
- 文件组织：多小文件优于少大文件（典型 200-400 行，上限 800），单一职责
- 性能：热路径测量→优化→验证；I/O 批量，避免 N+1
- 注释：独立组件/完整功能/复杂逻辑/对外 API 时写头部 docstring（模板 → `rules/GOVERNANCE.md`）
- 测试：新功能必覆盖；Bug 修复先写复现测试；命名 `should_x_when_y`；不跳过测试

## 文件编码与写入约束（防乱码 v11.4.2）

- 默认 UTF-8 无 BOM；保留目标文件既有编码/BOM/EOL 风格，禁止全文件重写时改变行尾（机械防护 → `hooks/pre-encoding-snapshot.py` + `post-encoding-check.py`）
- **文件内容写入一律用 Edit/Write 工具**，禁止 `echo >/>></tee/Set-Content/Out-File/heredoc` 等 shell 重定向写内容（PS5.1 默认 ANSI 是乱码重灾区；命令级警告 → `hooks/pre-bash-guard.py` 编码误用组）
- Windows 一律 `pwsh` 禁 `powershell -Command`（R9）；含中文输出的命令先确保 `[Console]::OutputEncoding=UTF8`
- 检测到乱码（U+FFFD/GBK 特征串/非法 UTF-8）立即回滚本次修改并精准恢复原片段，**禁止在损坏内容上继续叠加修改**；二进制/非文本文件禁 Read/Edit

## 工程原则

- KISS：优先简单直接实现，不为消除少量重复而做过度抽象
- SOLID 思想：职责清晰、降低模块耦合（不展开五原则全文）
- YAGNI：不为假设的未来需求提前设计；不做未经验证的架构设计；从最小可工作版本演进
- 删除过时代码优先于加兼容层/fallback/临时迁移逻辑
- 依赖克制：优先成熟稳定第三方库；用已有依赖前不随意新增；引入新方案前先查已有代码/依赖/文档/能力
- 简单方案已满足则不主动升级复杂方案；避免为“看起来更优雅”增加实际复杂度
- 详参 → `rules/GOVERNANCE.md` 最佳实践详参章

## 禁用规则

业务逻辑禁止 `new Date()` / `Date.now()` / `datetime.now()` — 用时区库 + Clock 接口依赖注入（TS/JS: dayjs；Python: pendulum；Go/Rust/C# 同理）。CLI 一次性脚本、纯 UI 展示除外。推荐库表 → `rules/GOVERNANCE.md`。

## 铁律 R1–R20

> 一行表 = 操作要点 + 机械门。R15/R19 短小节见下。详情 R14/R15/R16 → `rules/GOVERNANCE.md`；R19 命令表 → `rules/GIT.md`。L0 一行表 → `CLAUDE.md`。

| #   | 约束          | 操作要点                                                                                          | 机械门                                              |
| --- | ------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| R1  | 任务完成      | 验证通过才算完成；须跑 verification 并贴命令/测试/文件证据                                        | verification skill + `r20_replay` + Stop/Guard      |
| R2  | 修改确认      | 每文件 Read→Edit→Read                                                                             | `pre-read-before-edit`                              |
| R3  | Bug 修复      | 全关联修齐；Grep 残留 = 0                                                                         | CRG + `codegraph_explore` + Grep                    |
| R4  | 配置变更      | 引用同步 + 构建/校验；INDEX/MANIFEST 同改                                                         | MANIFEST `depends_on` + `validate_config`           |
| R5  | 重试上限      | 同方案 ≤2；第 3 次换方案或上报                                                                    | issue-tracker                                       |
| R6  | 非简单        | ①→⑤ 全流程；禁跳 grill                                                                            | task-triage + 分类门                                |
| R7  | 交叉验证      | 完成前对照清单，不止 lint                                                                         | verification skill                                  |
| R8  | 高危确认      | 删数据 / 强推 main / DROP 前确认                                                                  | bash-guard 危险命令                                 |
| R9  | 命令安全      | Windows 优先 pwsh；禁 `powershell -Command`；禁 shell 重定向写内容                                | encoding 守卫 + `pre-bash-guard`                    |
| R10 | 简洁优先      | KISS/YAGNI；最小改动集                                                                            | CORE 工程原则                                       |
| R11 | 安全默认      | 不信任输入、无硬编码密钥                                                                          | SECURITY + `post-secret-detector`                   |
| R12 | 子 Agent 隔离 | fresh context + 结构化制品通信，禁止共享可变状态                                                  | `rules/AGENTS.md`                                   |
| R13 | 制品存活      | PROJECT/REQUIREMENTS/ROADMAP/STATE/CONTEXT 跨会话持久化                                           | CONTEXT + `pre-compact-state`                       |
| R14 | 版本克制      | 非必要不升 major；优先 patch/minor；major 需明确收益或用户确认                                    | GOVERNANCE R14                                      |
| R15 | 包管理器      | 先认锁文件；按语言选隔离+锁文件工具；禁幻影依赖/幻觉包/混用                                       | bash-guard/Guard **警告**；矩阵 → GOVERNANCE        |
| R16 | 错误暴漏      | 禁止裸 `except:pass`，异常必须传播或显式处理并报告                                                | `validate_config` V17                               |
| R17 | 代码探索优先  | 严格：codegraph → claude-mem；codebase-memory **已禁用**；禁止跳级                                | 图谱保鲜 deny                                       |
| R18 | 记忆优先      | 「为什么/约定/偏好」查 claude-mem；禁止塞入 codegraph/cbm                                         | issue-tracker + claude-mem                          |
| R19 | Git 禁令      | 禁自动 stash/commit/非 dry-run push；**禁自动新建或切换分支**（仅用户本条消息显式要求）           | Claude bash-guard **deny**；Cursor Guard **ask**    |
| R20 | 会话终验      | 改前优先成熟方案；完成后逐条回放满足/遗漏/错改/漏改/原功能/影响范围；配置/文档/注释必须同步；独立审查一次找齐且每轮全新开审；修改走 `change-implementer` | verification skill + `r20_replay`；Claude Stop exit 2；Cursor 无完成门 followup |

### R15 包管理器（防幻影依赖）

1. **先认项目**：锁文件 / `packageManager` / wrapper 已声明则必须用该工具，禁止混用（双 lock、pnpm 仓跑 `npm i`）。
2. **无声明时**按语言选「隔离 + 锁文件」的稳定工具（JS/TS→pnpm；Python→uv；Rust→cargo；Go→go mod；其余 → GOVERNANCE 矩阵）。
3. **禁止**：为未在清单/锁文件中的包写 import；编造 registry 包名；把 npm 扁平化「能 import」当成已声明依赖。
4. 与 R14 对齐：不追最新 major。机械门：`pre-bash-guard` / Cursor Guard 对 pnpm 仓 `npm install`、uv/poetry 仓裸 `pip install` / `python -m pip` **警告不阻断**。

### R19 Git 禁令（含分支）

禁止自动 `git stash` / `git commit` / 非 dry-run `git push` / **新建或切换分支**。仅用户**本条消息**显式要求「提交 / 建分支 / 切分支 / 开 PR 且必须新分支」时才允许。路径还原 `git checkout -- <path>` / `git checkout .` / `git restore` 与只读 `status` / `diff` / `log` / `branch -a` 放行。复合命令与包装（`bash -c` / `eval` / `timeout` / `nice` / 子 shell）中的建切分支同样拦截。机械门：Claude `pre-bash-guard` deny；Cursor Guard ask（`forbid_auto_branch`）。命令表 → `rules/GIT.md`。

### R20 会话终验

**改前**：优先成熟方案或已有全局通用处理（禁止为单编辑器发明特例）。**完成后**：逐条回放满足/遗漏/错改/漏改/原功能/影响范围；核对范围=影响面全部相关项（非仅已编辑文件）；**配置/修改必须与文档、注释、版本戳同步**（不一致计入漏改且不得声称完成）。独立审查者只找问题（是否符合预期），禁止改文件，**必须一次找齐全部未满足项**；**每轮必须全新开审**（禁止 `resume` 上一轮审查者；对照原始要求全量重扫，上轮清单不得限定范围）。修改必须另派 `change-implementer` 按完整清单集中改齐。禁止边审边改耗轮次。验证与独立审查结论不一致（含 PASS 夹带必须修项）→ 清单齐后再派修改者，禁止只汇报等用户。原功能须测试或冒烟证据；影响范围须对照 CRG `get_impact_radius` 或 IMPACT 清单。「满足」行须覆盖会话需求指纹的 strong 关键词（v11.4 `req_fingerprint` 机械比对）。**验证证据须为观察输出（命令/测试/文件），不信 agent 叙述**。模板与检测 SSOT → `skills/verification-before-completion/SKILL.md`。未输出不得声称完成。

### R17-R18 代码理解工具优先级（严格递进，禁止跳级）

```
1. 结构/局部（调用链、依赖、影响面、「怎么运作」）
   → 仅 codegraph_explore；禁止直接 Grep/Read
2. codebase-memory：**已禁用**（全盘索引爆内存）— 勿调用；原升级场景（语义/跨服务/ADR）一律用 codegraph
3. 「为什么这么做」「约定是什么」「用户偏好」（代码推不出）
   → 查 claude-mem；决策原因存 memory
```

| 需求                        | 首选                                                    | 次选                          | 禁止                                 |
| --------------------------- | ------------------------------------------------------- | ----------------------------- | ------------------------------------ |
| 函数/类/调用链/「怎么运作」 | codegraph_explore（blast-radius）                       | —（双图就绪后 Grep 定点残留） | 跳过 codegraph 直接 Grep/Read        |
| 语义模糊 / 跨服务 / ADR     | codegraph_explore                                       | docs/ADR/ 手写                | 启用/调用 codebase-memory（已禁用）  |
| 为什么/约定/偏好/决策原因   | claude-mem search→get_observations                      | —                             | 往 codegraph 塞偏好；重复 Read       |
| 精准上下文 / 变更影响面     | CRG `get_minimal_context` + `get_impact_radius`（有图） | codegraph blast-radius + Grep | 只靠直觉估范围；用 serena 探索       |
| 风险门禁 / 审查 / 开 PR     | CRG `detect_changes` + `get_review_context`             | eng-reviewer                  | 用 codegraph 做 test-gap（无此能力） |

**codegraph vs code-review-graph 分工（v11.4.6）**：

- **codegraph = R17 探索主位**（符号/调用链/「怎么运作」；无 CRG 图时的 blast-radius）
- **code-review-graph = 精准上下文 + 变更影响 + 风险门禁 + 审查 + 开 PR**（`get_minimal_context` / `get_impact_radius` / `get_affected_flows` / `detect_changes` / `get_review_context`）
- 禁止用 CRG 替代 R17「怎么运作」日常探索；禁止用 codegraph 做 test-gap。eligible git 仓须先有双图（SessionStart/PreToolUse hook 自动 init/update）；无图 **deny**，禁止 Grep/编辑/查询 MCP，不得 Grep 兜底。

**索引刷新**：codegraph v1.5 MCP watcher 管日常改动；**会话开始** hook 再 `codegraph sync` + CRG update/init；**Stop** 增量刷新。不恢复每次编辑 kg sync hook。

### R17 反模式检测

| 行为                                             | 判定     | 后果                              |
| ------------------------------------------------ | -------- | --------------------------------- |
| 改文件前未查 blast-radius（`codegraph_explore`） | 违反 R17 | 变更范围不可信                    |
| 跳过 codegraph 直接 Grep 搜函数                  | 违反 R17 | ~47% token / ~58% 工具调用浪费    |
| 结构问题未用 codegraph 就上 cbm                  | 违反 R17 | cbm 已禁用；标 DONE_WITH_CONCERNS |
| 启用/调用 codebase-memory                        | 禁止     | 全盘索引爆内存；用 codegraph      |
| codegraph 已返回结果仍 Read 同文件               | 违反 R17 | 重复 token 消耗                   |
| 探索前未确认 codegraph init                      | 违反硬门 | 无图 deny，禁止后续探索/编辑      |

**codegraph_explore 返回的源码视为已读取，禁止重复 Read/Grep。**（F1 默认工具集与 impact env 启用细节 → `rules/GOVERNANCE.md`）

## 变更彻底性保障（R3/R4 强制执行）

**⛔ 改任何文件前必须先查影响面：有 `.code-review-graph/` 时 CRG `get_minimal_context` + `get_impact_radius`（有 git diff 再 `detect_changes`），并叠加 `codegraph_explore` blast-radius + Grep — 违反者变更视为不可信。**

> 改任何文件/函数/类型/配置 → 先分析影响范围 → 全关联文件修改 → 残留引用检测（三阶段详情 → `rules/GOVERNANCE.md`）

### 强制触发条件

| 变更类型                   | 必须执行                                                    |
| -------------------------- | ----------------------------------------------------------- |
| 改函数签名/接口/类型定义   | CRG impact（有图）+ `codegraph_explore` blast-radius + Grep |
| 改配置文件/规则/Skill      | MANIFEST `depends_on` 遍历                                  |
| 重命名/删除/移动文件       | Grep 全项目残留引用                                         |
| 改 agent/hook/MCP 定义     | 同步更新 INDEX.md + MANIFEST.yaml                           |
| 调研/分析任务              | 先 `codegraph_explore` blast-radius 确定范围，再逐文件深读  |
| 风险/审查/开 PR / test-gap | CRG `detect_changes` + `get_review_context`（有图）+ 测试   |

### 反模式（禁止）

| 禁止                                       | 原因                          |
| ------------------------------------------ | ----------------------------- |
| 只改指定文件不改关联文件；只验当前编辑文件 | 造成不一致/死代码；五问题复发 |
| "看起来差不多" 跳过 Grep                   | 遗漏隐藏引用                  |
| 手动估计影响范围                           | codegraph 比人准              |
| 残留引用 > 0 声称完成                      | 违反 R1（验证通过才算完成）   |

## 工作原则与项目约定

> Tool-First 路由、五柱边界、失败报告 → `CLAUDE.md`

- 自动维护 `README.md`；最小改动集；环境配置走 `.env`，禁止硬编码
- 沟通语言：中文；代码仅在明确要求或上下文需要时输出完整代码块
- Windows 终端：优先 `pwsh`（PowerShell 7+ 稳定版，避免 PS5.1 异常）；脚本注释示例统一 pwsh 化（编辑器 MCP 启动包装 `python-mcp.ps1` 等用 powershell.exe，详见 GOVERNANCE）
- Git 规范 → `rules/GIT.md`；提交/PR → `skills/git-workflow`、`skills/pr-workflow`
- Karpathy 四原则 → `skills/karpathy-guidelines/SKILL.md`（L3 按需）
