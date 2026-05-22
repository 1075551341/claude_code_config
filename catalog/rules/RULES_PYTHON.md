---
description: Python 代码开发时启用
alwaysApply: false
---

# Python 规则（专用）

> 配合核心规则使用，仅在 Python 场景加载

## 版本与工具链

```
Python 版本：3.11+（推荐 3.12）
包管理：uv / poetry / pip + venv
格式化：ruff format / black
Lint：ruff check / flake8
类型检查：mypy / pyright
测试：pytest
```

## 项目结构

```
project/
├── src/package_name/  (__init__.py, core/, services/, utils/)
├── tests/  (conftest.py, test_*.py)
├── pyproject.toml
└── README.md
```

## 代码风格

### 命名规范

```python
# 模块/包：snake_case | 类：PascalCase | 函数/方法/变量：snake_case
# 常量：UPPER_SNAKE_CASE | 私有属性：_前缀 | 类型别名：PascalCase
class UserService: pass
def get_user_by_id(user_id: int) -> User: ...
MAX_RETRY_COUNT = 3
UserId = int  # 类型别名
```

### 类型注解

```python
from typing import Optional, Generic, TypeVar

def fetch_user(user_id: int, include_deleted: bool = False) -> Optional[User]: ...
type JsonDict = dict[str, Any]  # TypeAlias

T = TypeVar('T')
class Repository(Generic[T]):
    def get(self, id: int) -> T | None: ...
```

### 文档字符串

```python
def calculate_discount(price: float, discount_rate: float, min_price: float = 0.0) -> float:
    """计算折扣后价格。

    Args:
        price: 原始价格，必须大于 0。
        discount_rate: 折扣率，范围 0-1。
    Returns:
        折扣后价格，不低于 min_price。
    Raises:
        ValueError: 当 price <= 0 或 discount_rate 不在 0-1 范围内。
    """
```

## 异步编程

```python
import asyncio

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# 并发执行
async def fetch_all(urls: list[str]) -> list[dict]:
    return await asyncio.gather(*[fetch_data(url) for url in urls], return_exceptions=True)
```

## 错误处理

```python
# 自定义异常层次
class AppError(Exception): """应用基础异常"""
class ValidationError(AppError): """验证错误"""
class NotFoundError(AppError): """资源未找到"""

# 异常链保留原始信息
try: await external_api.call()
except aiohttp.ClientError as e: raise AppError("外部服务调用失败") from e
```

## 数据验证

```python
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(..., ge=0, le=150)
```

## 性能优化

```python
# 生成器避免内存问题
def read_large_file(file_path: str) -> Iterable[str]:
    with open(file_path) as f: yield from (line.strip() for line in f)

# functools.lru_cache 缓存
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int: ...
```

## 时间处理

### 禁止 `datetime.now()`，使用 pendulum / arrow

标准库 `datetime` 时区处理繁琐、API 不直观。使用时间库获得更好的时区支持和链式 API。

```python
# ❌ 禁止
from datetime import datetime
now = datetime.now()
utc_now = datetime.utcnow()  # 已弃用

# ✅ pendulum（首选，API 优雅、时区一流）
import pendulum
now = pendulum.now('UTC')
in_shanghai = pendulum.now('Asia/Shanghai')
formatted = now.format('YYYY-MM-DD HH:mm:ss')
parsed = pendulum.parse('2025-01-01T00:00:00Z')

# ✅ arrow（轻量替代）
import arrow
now = arrow.now('Asia/Shanghai')
formatted = now.format('YYYY-MM-DD HH:mm:ss')
```

### 时间库选型

| 场景 | 推荐 | 理由 |
|------|------|------|
| 通用项目 | pendulum | API 最优雅、时区一流、duration 支持 |
| 轻量需求 | arrow | 更轻量、API 简洁 |
| 仅格式化 | strftime + babel | 无需额外依赖 |

### 依赖注入（业务逻辑）

```python
import pendulum
from typing import Callable

def create_service(get_now: Callable[[], pendulum.DateTime] = lambda: pendulum.now('UTC')):
    now = get_now()

# ✅ 测试中注入固定时间
fixed = pendulum.datetime(2025, 1, 1, 0, 0, 0, tz='UTC')
service = create_service(get_now=lambda: fixed)
```

例外：CLI 一次性脚本、纯 UI 展示时间

## 配置管理

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    class Config: env_file = ".env"
```

## 常用模式

```python
# 依赖注入
@lru_cache
def get_user_service() -> UserService: return UserService(db=get_database())

# 工厂模式
class HandlerFactory:
    _handlers: dict[str, type[Handler]] = {}
    @classmethod
    def register(cls, name: str) -> Callable: ...  # 装饰器注册
    @classmethod
    def create(cls, name: str) -> Handler: return cls._handlers[name]()
```
