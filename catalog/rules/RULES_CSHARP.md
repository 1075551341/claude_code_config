---
description: C# / .NET 开发规则
globs: ["*.cs", "*.csx", "*.fs", "*.fsx"]
---

# C# / .NET 开发规则

## 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 类/接口/结构体 | PascalCase | `UserService`, `IRepository` |
| 方法/属性 | PascalCase | `GetById()`, `UserName` |
| 私有字段 | _camelCase | `_logger`, `_repository` |
| 参数/局部变量 | camelCase | `userId`, `result` |
| 常量 | PascalCase | `MaxRetryCount` |
| 命名空间 | PascalCase（点分隔） | `MyApp.Services` |

## 异步编程

- 异步方法以 `Async` 后缀命名
- 禁止 `.Result` / `.Wait()` / `.GetAwaiter().GetResult()`（死锁风险）
- 库代码使用 `ConfigureAwait(false)`
- 异步 Lambda 正确标注 `async`

## Nullable Reference Types

- 项目级启用 `<Nullable>enable</Nullable>`
- 不用 `!` 操作符除非有注释说明非空保证
- `null` 检查用 `is null` / `is not null`
- 集合默认初始化为空集合而非 null

## 依赖注入

- 构造函数注入优先
- 禁止 Service Locator 反模式（从 IServiceProvider 直接 GetService）
- 生命周期匹配：Singleton 不依赖 Scoped/Transient
- 选项模式用 `IOptions<T>` / `IOptionsMonitor<T>`

## LINQ

- 延迟执行：注意 IQueryable vs IEnumerable 边界
- 避免 N+1：Include / ThenInclude 显式加载关联
- 大集合用 AsNoTracking（只读查询）
- 避免在循环中执行查询

## 资源管理

- IDisposable + using 语句 / using 声明
- IAsyncDisposable + await using
- 避免终结器（~ClassName）除非持有非托管资源
- CancellationToken 传播到所有异步操作

## 时间处理

### 禁止 `DateTime.Now` / `DateTime.UtcNow`，使用 NodaTime + IClock 注入

`DateTime` 时区处理缺陷、`Kind` 语义混乱。NodaTime 提供类型安全的时间模型，`IClock` 接口天然支持测试。

```csharp
// ❌ 禁止
var now = DateTime.Now;
var utc = DateTime.UtcNow;

// ✅ NodaTime（首选，时区处理远优于 DateTime）
using NodaTime;
using NodaTime.Testing;  // FakeClock 用于测试

public class MyService {
    private readonly IClock _clock;
    public MyService(IClock clock) { _clock = clock; }
    public void DoWork() {
        var now = _clock.GetCurrentInstant();
        var inShanghai = now.InZone(DateTimeZoneProviders.Tzdb["Asia/Shanghai"]);
    }
}

// ✅ 注册到 DI
services.AddSingleton<IClock>(SystemClock.Instance);

// ✅ 测试中注入固定时间
var fixedInstant = Instant.FromUtc(2025, 1, 1, 0, 0);
var service = new MyService(new FakeClock(fixedInstant));
```

### 时间库选型

| 场景 | 推荐 | 理由 |
|------|------|------|
| 正式项目 | NodaTime | 类型安全时区、Instant/Duration/ZonedDateTime |
| 简单项目 | IDateTimeProvider + DateTime | 最小依赖，接口注入即可 |

例外：CLI 一次性脚本、纯 UI 展示
