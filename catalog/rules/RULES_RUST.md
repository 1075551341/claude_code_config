---
description: Rust 开发规则
globs: ["*.rs", "Cargo.toml"]
---

# Rust 开发规则

> 运行时、版本和包管理器遵循项目清单、锁文件及 CI；本资料不设置全局地板。

## 所有权与借用

- 遵循所有权规则：一个所有者、借用不超生命周期
- 优先用引用（&T / &mut T）而非转移所有权
- 避免不必要的 clone() — 考虑引用或 Cow
- 生命周期标注仅在编译器无法推断时添加

## 错误处理

- 使用 Result<T, E>，不使用 panic!（除不可恢复错误）
- 库代码按项目约定定义错误类型；已有 thiserror 时可复用，标准库能满足时无需引入
- 应用代码复用项目既有错误处理；anyhow / eyre 是可选方案，不强制新增
- ? 操作符传播错误，不手动 match
- 避免 unwrap() / expect() 在生产代码中

## 类型系统

- newtype 模式区分语义相同类型（UserId vs OrderId）
- 枚举建模有限状态，不用常量 + if/else
- trait 定义行为接口，impl 块保持内聚
- 泛型约束用 where 子句（复杂约束时）

## 并发

- Send + Sync 标记线程安全
- 优先用 std::sync 通道 / crossbeam 而非共享状态
- async/await 遵循项目现有运行时；tokio 仅为可选方案，不强制替换
- 避免在异步代码中调用阻塞操作（用 spawn_blocking）

## 性能

- 零成本抽象：trait 对象（dyn）仅必要时使用，优先泛型单态化
- 避免频繁堆分配：栈分配优先、Vec 预分配容量
- 热路径避免 String 格式化，用 write! 宏
- 大数据用迭代器链（惰性求值）而非中间集合

## 时间处理

优先复用项目依赖。简单时间点使用标准库 `SystemTime`，耗时测量使用单调的 `Instant`；需要日历、解析或时区能力时，再评估项目已有 chrono / time crate，不强制新增库。时间影响业务判断时注入取时能力，避免测试依赖真实时钟。

```rust
use std::time::{Duration, SystemTime, UNIX_EPOCH};

trait Clock { fn now(&self) -> SystemTime; }
struct SystemClock;
impl Clock for SystemClock { fn now(&self) -> SystemTime { SystemTime::now() } }
struct FixedClock(SystemTime);
impl Clock for FixedClock { fn now(&self) -> SystemTime { self.0 } }

fn create_service(clock: &dyn Clock) -> SystemTime { clock.now() }
let fixed = FixedClock(UNIX_EPOCH + Duration::from_secs(1_735_689_600));
let result = create_service(&fixed);
```

## Clippy

- 项目级启用 `#![warn(clippy::all, clippy::pedantic)]`
- Clippy 警告视为错误修复，不抑制
