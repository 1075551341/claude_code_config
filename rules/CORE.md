---
description: 代码开发时始终启用 — 骨架层：编码规范 + 铁律 + 三横切 + 阈值 + 阶段定义
alwaysApply: true
layer: skeleton
source: obra/superpowers + forrestchang/andrej-karpathy-skills + open-gsd/gsd-core + 2025Emma/vibe-coding-cn
---

## 三横切基础设施

```
L1 治理 — ECC(MANIFEST防互博+hook分级+loop防护) + deer-flow 2.0(LangGraph编排)
L2 优化 — RTK(shell压缩,60-90%) + caveman(输出压缩,~75%) + 三级阈值(上下文治理)
L3 洞察 — codegraph(静态索引,47%token减少) + Understand-Anything(交互知识图) + Firecrawl/Exa(外部搜索)

所有阶段自动注入 L1/L2/L3。柱驱动阶段，横切保障执行。
```

## 上下文腐烂三级阈值

| 使用率 | 行动 |
|--------|------|
| <40%   | 正常工作（主会话编排 + 子 agent 实现） |
| 50%    | 逻辑断点 `/compact`，释放已完成上下文 |
| 70%    | 强制压缩或启动新子 Agent，保留决策丢弃细节 |

子 Agent 调度: 无依赖并行派发 | 有依赖等待前置完成 | 同一制品路径禁止并行写入。

## 五阶段流程

```
① 规划(brainstorming) → ② 规格(writing-plans) → ③ 执行(executing-plans/SDD+TDD)
→ ④ 验证(verification-before-completion) → ⑤ 学习(pattern-extraction)

状态机: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
门控:
  ① 规划: HARD-GATE 用户批准设计 ✓
  ② 规格: spec-validation通过 + 任务有成功标准 + 无静默缩scope
  ③ 执行: 子任务完成 + 构建/类型/Lint通过 + 子Agent异常已处理(R16)
  ④ 验证: 质量门全通过 + 交叉验证通过
  ⑤ 学习: 模式提取完成
```

## vibe-coding-cn 道/法/术/器

```
道(原则): AI能做的不人工做 | 先结构后代码 | 上下文是第一性要素
法(策略): 接口先行实现后补 | 能抄不写不重复造轮子 | 文档即上下文
术(技巧): 明确能改什么不能改什么 | Debug给预期vs实际+最小复现
器(工具): Claude Code/Cursor/Codex CLI — 选最合适的

α-提示词(生成器): 唯一职责生成其他提示词或技能
Ω-提示词(优化器): 唯一职责优化其他提示词或技能 → skill/instinct-learning
```

## 优先级

1. **简单至上** — 最小可行方案，拒绝过度设计
2. **精准响应** — 直击要点，无废话
3. **最佳实践** — 干净代码 + 语义化 + 安全规范
4. **主动确认** — 需求模糊时先问，不盲目执行

## 快速指令前缀

| 前缀     | 行为             |
| -------- | ---------------- |
| `[方法]` | 生成具体功能代码 |
| `[方案]` | 输出技术实现规划 |
| `[解释]` | 逐步解析现有代码 |
| `[修改]` | 对项目增删改查   |
| `[审查]` | 代码质量评审     |

## 代码规范

- DRY + 单一职责
- 不可变优先：创建新对象，数组用展开/map/filter，不原地修改
- 未指定语言 → 沿用当前项目技术栈
- 未指定框架 → 选最轻量够用的方案
- 安全防御 → 详见 `rules/SECURITY.md`

## 文件组织

- 多小文件优于少大文件，典型 200-400 行，上限 800 行
- 每个文件单一职责，目录按功能域组织

## 错误处理

- 每层显式处理，永不静默吞错
- 错误信息包含上下文（操作名、输入摘要、原始错误）
- 自定义错误类携带机器可读 code
- 异步操作必须 try/catch，禁止裸 await
- 已知错误 → 业务码 + 友好提示；未知错误 → 完整日志 + 通用错误码

## 输入验证

- 系统边界验证所有外部输入（API、CLI、用户输入）
- 内部代码信任类型系统，不重复验证
- 验证失败返回具体错误，不泛化

## 性能意识

- 避免不必要的计算和内存分配
- 热路径优先优化（测量 → 优化 → 验证）
- I/O 操作批量处理，避免 N+1

## 注释规则

```
触发条件（满足任一）：
  ① 独立组件 / 模块
  ② 完整业务功能
  ③ 复杂逻辑（分支 > 3 层 或 非显而易见算法）
  ④ 对外暴露的 API / 函数签名

语言：优先中文
位置：函数/类头部（JSDoc / Python docstring）
```

**注释模板：**

```
/**
 * @描述 简述功能（一句话）
 * @参数 {类型} 名称 - 说明
 * @返回 {类型} 说明
 * @示例 简短用法（复杂场景必填）
 * @注意 副作用 / 依赖 / 边界限制
 */
```

## 测试要求

- 新功能必须有测试覆盖
- Bug 修复先写复现测试
- 测试命名描述行为：`should_x_when_y`
- 不跳过测试（无 .skip/.todo 除非附 Issue 链接）

## 禁用规则

### 禁止使用 `new Date()` / 原生时间 API 获取当前时间

原生时间 API（`new Date()` / `Date.now()` / `datetime.now()` 等）依赖系统时钟，不可控、不可测试。必须使用项目对应语言的时间库，并通过依赖注入获取当前时间。

**各语言推荐时间库**：

| 语言          | 推荐库                                       | 选型依据                                              |
| ------------- | -------------------------------------------- | ----------------------------------------------------- |
| TypeScript/JS | dayjs（首选）/ date-fns（函数式）            | 轻量、不可变、链式 API；避免 moment（已弃用、体积大） |
| Python        | pendulum（首选）/ arrow                      | 比 datetime 更好的 API 和时区支持；delorean 可选      |
| Go            | 标准库 time + Clock 接口                     | Go 标准库已足够，通过接口注入即可                     |
| Rust          | chrono / time crate                          | chrono 功能全面；time crate 更轻量                    |
| C#            | NodaTime（首选）/ 标准库 + IDateTimeProvider | NodaTime 时区处理远优于 DateTime                      |

```typescript
// ❌ 禁止
const now = new Date();
const ts = new Date().toISOString();
const formatted = new Date().toLocaleDateString();

// ✅ 使用 dayjs
import dayjs from "dayjs";
const now = dayjs();
const ts = dayjs().toISOString();
const formatted = dayjs().format("YYYY-MM-DD");

// ✅ 依赖注入（业务逻辑）
type Clock = () => dayjs.Dayjs;
const defaultClock: Clock = () => dayjs();
function createService(clock: Clock = defaultClock) {
  const now = clock(); // 测试时可注入固定时间
}
```

```python
# ❌ 禁止
from datetime import datetime
now = datetime.now()

# ✅ 使用 pendulum
import pendulum
now = pendulum.now('UTC')

# ✅ 依赖注入（业务逻辑）
from typing import Callable
import pendulum
def create_service(get_now: Callable[[], pendulum.DateTime] = lambda: pendulum.now('UTC')):
    now = get_now()  # 测试时可注入固定时间
```

```go
// ❌ 禁止
now := time.Now()

// ✅ 标准库 + Clock 接口注入
type Clock interface { Now() time.Time }
type realClock struct{}; func (realClock) Now() time.Time { return time.Now() }
type fakeClock struct{ fixed time.Time }; func (c fakeClock) Now() time.Time { return c.fixed }
func createService(clock Clock) { now := clock.Now() }
```

**适用场景**：业务逻辑、数据模型、API 响应中的时间戳
**例外**：纯 UI 展示（如页面显示当前时间）、CLI 工具的一次性脚本

## 铁律 R12–R16

> R1–R11 → `CLAUDE.md`

| #   | 约束          | 核心                                                           |
| --- | ------------- | -------------------------------------------------------------- |
| R12 | 子 Agent 隔离 | fresh context + 结构化制品通信，禁止共享可变状态               |
| R13 | 制品存活      | PROJECT/REQUIREMENTS/ROADMAP/STATE/CONTEXT 跨会话持久化        |
| R14 | 版本克制      | 非必要不升 major；优先 patch/minor；major 需明确收益或用户确认 |
| R15 | 包管理器      | Node 生态默认 `pnpm`；不可用时或项目仅 npm 时用 `npm`          |
| R16 | 错误暴漏      | 禁止裸 `except:pass`，异常必须传播或显式处理并报告             |

### R16 详细声明

- **Hook**：所有 `hooks/*.py` 禁止 `except:pass` 或 `except Exception:pass`，异常必须向上传播或 `sys.exit(1)` + 错误详情
- **Agent**：执行失败时报告错误详情 + 已尝试方案 + 建议下一步，不静默吞掉
- **子 Agent**：主 Agent 接收子 Agent 异常，决定重试/报告/中止，不丢弃
- **配置验证**：`validate_config.py` 失败时 `exit(1)` + 输出可操作修复建议
- **扫描**：`validate_config.py V10` 扫描 `hooks/` 裸 except 数量，必须为 0

### R14 适用范围

- **依赖**：npm/pip/cargo 等默认锁定当前 major；安全补丁用同 major 最新版
- **插件/MCP/工具链**：`plugins/`、`.mcp.json`、`installed_plugins.json` 等不做「追 latest major」
- **允许 major**：用户明确要求；CVE 无同 major 修复；阻塞缺陷且 changelog 已评估
- **禁止**：`npm-check-updates -u` 无差别 major、无 changelog/无验证的批量升级

### R15 适用范围（Node / JS）

- **默认**：`pnpm install` / `pnpm add` / `pnpm run` / `pnpm exec` / `pnpm dlx`
- **尊重项目**：已有 `pnpm-lock.yaml` 或 `packageManager` 含 `pnpm` → 必须用 pnpm；仅 `package-lock.json` 且无 pnpm 配置 → 用 npm
- **npm 兜底**：本机无 pnpm、pnpm 执行失败且用户未要求换工具链、或脚本/文档明确写 `npm` 时
- **禁止**：在 pnpm 项目中混用 `npm install` 生成/改写 lock（避免双 lock 漂移）

## 工作原则（来自五柱整合）

- **Tool-First**：先查 MANIFEST → skill → catalog → agent → hook/MCP，不重复造轮子
- **Clear Boundaries**：agent 间职责不重叠，MANIFEST.yaml 定义唯一归属
- **Report Failures**：失败时报告原因 + 已尝试方案 + 建议下一步，不静默重试超过 2 次
- **子 Agent 隔离(R12)**：每个子 agent fresh context，通过 openspec/ + .planning/ + memory/ 三态制品通信
- **制品存活(R13)**：新会话优先加载结构化制品，而非依赖对话历史
- **版本克制(R14)**：维护/升级任务先列变更与风险，默认 minor/patch；major 单独说明理由
- **包管理器(R15)**：Node 任务先判 lock/`packageManager`，能 pnpm 则 pnpm，否则 npm 并说明原因
- **错误暴漏(R16)**：禁止裸 except:pass，异常传播或显式处理+报告；Hook/Agent/子 Agent/配置验证均不静默吞错误

## 项目约定

- 自动维护 `README.md`（架构概览 + 模块说明）
- 每次修改：最小改动集，不破坏现有功能
- 环境配置统一走 `.env`，禁止硬编码

## 输出格式

- 沟通语言：中文
- 代码：仅在明确要求或上下文需要时输出完整代码块

## Git 规范

> 详见 `rules/GIT.md`（分支策略、Commit 规范、PR 模板、危险操作防护等完整覆盖）

## Karpathy 四原则

1. **Think Before Coding** — 先陈述假设；有歧义呈现多种解读
2. **Simplicity First** — 能 50 行不写 200 行；禁止推测性通用化
3. **Surgical Changes** — 只改必须改的；匹配现有风格
4. **Goal-Driven** — 弱命令转强声明式标准（见 CLAUDE.md R1–R11）

详细 → `skills/karpathy-guidelines/SKILL.md`
