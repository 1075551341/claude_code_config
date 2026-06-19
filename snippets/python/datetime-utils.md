# 时间处理模板

> 遵守 CORE.md 时间禁令：业务逻辑禁止 `new Date()` / `Date.now()` / `datetime.now()`

## Python (pendulum)

```python
import pendulum

# 获取当前时间（通过依赖注入 Clock 接口）
class Clock:
    def now(self) -> pendulum.DateTime:
        return pendulum.now()

# 格式化
dt = clock.now()
iso_str = dt.to_iso8601_string()    # "2026-06-17T10:30:00+08:00"
human_str = dt.format("YYYY-MM-DD HH:mm:ss")
```
