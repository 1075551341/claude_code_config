---
description: C# / .NET 开发规则
globs: ["*.cs", "*.csx", "*.fs", "*.fsx"]
---

# C# / .NET 开发规则

> 运行时、版本和包管理器遵循项目清单、锁文件及 CI；本资料不设置全局地板。

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

优先使用项目现有时间模型与依赖。一般时间点可使用标准库 `DateTimeOffset`，时区转换使用 `TimeZoneInfo`；按语义明确 UTC、偏移与本地时间。时间影响业务判断时，可用项目已有时钟接口、运行时支持的 `TimeProvider` 或简单委托注入，不强制升级运行时或新增库。

```csharp
public class MyService {
    private readonly Func<DateTimeOffset> _now;
    public MyService(Func<DateTimeOffset> now) { _now = now; }
    public DateTimeOffset CurrentTime() { return _now(); }
}

var service = new MyService(() => DateTimeOffset.UtcNow);
var fixedTime = new DateTimeOffset(2025, 1, 1, 0, 0, 0, TimeSpan.Zero);
var testService = new MyService(() => fixedTime);
```

已有 NodaTime 的项目可继续使用 `IClock` / `Instant`；复杂日历及时区需求再评估该库的收益、数据部署和迁移成本。标准库能满足时不新增依赖，不强制替换现有实现。

