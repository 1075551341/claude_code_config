---
description: Rust 开发规则
globs: ["*.rs", "Cargo.toml"]
---

# Rust 开发规则

## 所有权与借用

- 遵循所有权规则：一个所有者、借用不超生命周期
- 优先用引用（&T / &mut T）而非转移所有权
- 避免不必要的 clone() — 考虑引用或 Cow
- 生命周期标注仅在编译器无法推断时添加

## 错误处理

- 使用 Result<T, E>，不使用 panic!（除不可恢复错误）
- 库代码定义自定义 Error 枚举 + thiserror
- 应用代码用 anyhow 或 eyre
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
- async/await 用 tokio 运行时
- 避免在异步代码中调用阻塞操作（用 spawn_blocking）

## 性能

- 零成本抽象：trait 对象（dyn）仅必要时使用，优先泛型单态化
- 避免频繁堆分配：栈分配优先、Vec 预分配容量
- 热路径避免 String 格式化，用 write! 宏
- 大数据用迭代器链（惰性求值）而非中间集合

## 时间处理

### 禁止直接 `Utc::now()` / `SystemTime::now()`，通过 Clock trait 注入

使用 chrono / time crate 作为时间库，并通过 trait 注入实现可测试性。

```rust
// ❌ 禁止在业务逻辑中直接调用
let now = Utc::now();
let now = SystemTime::now();

// ✅ chrono（功能全面）+ Clock trait 注入
use chrono::{DateTime, Utc};

trait Clock { fn now(&self) -> DateTime<Utc>; }
struct SystemClock; impl Clock for SystemClock { fn now(&self) -> DateTime<Utc> { Utc::now() } }
struct FixedClock(DateTime<Utc>); impl Clock for FixedClock { fn now(&self) -> DateTime<Utc> { self.0 } }

fn create_service(clock: &dyn Clock) { let now = clock.now(); }

// ✅ 测试中注入固定时间
let svc = create_service(&FixedClock(Utc.with_ymd_and_hms(2025, 1, 1, 0, 0, 0).unwrap()));

// ✅ time crate（更轻量、更安全）
// use time::OffsetDateTime;
// trait Clock { fn now(&self) -> OffsetDateTime; }
```

### 时间库选型

| 场景 | 推荐 | 理由 |
|------|------|------|
| 功能全面 | chrono | 日期时间解析、格式化、时区 |
| 轻量安全 | time | 无 panic、更小体积 |

例外：CLI 一次性脚本、纯 UI 展示

## Clippy

- 项目级启用 `#![warn(clippy::all, clippy::pedantic)]`
- Clippy 警告视为错误修复，不抑制
