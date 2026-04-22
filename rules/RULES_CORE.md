---
description: 代码开发时始终启用
alwaysApply: true
---

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
- 安全防御 → 详见 `RULES_SECURITY.md`

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

| 语言 | 推荐库 | 选型依据 |
|------|--------|----------|
| TypeScript/JS | dayjs（首选）/ date-fns（函数式） | 轻量、不可变、链式 API；避免 moment（已弃用、体积大） |
| Python | pendulum（首选）/ arrow | 比 datetime 更好的 API 和时区支持；delorean 可选 |
| Go | 标准库 time + Clock 接口 | Go 标准库已足够，通过接口注入即可 |
| Rust | chrono / time crate | chrono 功能全面；time crate 更轻量 |
| C# | NodaTime（首选）/ 标准库 + IDateTimeProvider | NodaTime 时区处理远优于 DateTime |

```typescript
// ❌ 禁止
const now = new Date();
const ts = new Date().toISOString();
const formatted = new Date().toLocaleDateString();

// ✅ 使用 dayjs
import dayjs from 'dayjs';
const now = dayjs();
const ts = dayjs().toISOString();
const formatted = dayjs().format('YYYY-MM-DD');

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

## 项目约定

- 自动维护 `README.md`（架构概览 + 模块说明）
- 每次修改：最小改动集，不破坏现有功能
- 环境配置统一走 `.env`，禁止硬编码

## 输出格式

- 沟通语言：中文
- 代码：仅在明确要求或上下文需要时输出完整代码块

## Git 规范

> 详见 `RULES_GIT.md`（分支策略、Commit规范、PR模板、危险操作防护等完整覆盖）
