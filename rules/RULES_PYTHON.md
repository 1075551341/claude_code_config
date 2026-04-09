---
description: Python 代码开发时启用
alwaysApply: false
---

# Python 规则（专用）

> 配合核心规则使用，仅在 Python 场景加载

## 版本与工具链

```markdown
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
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── core/
│       ├── services/
│       └── utils/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── pyproject.toml
├── .python-version
└── README.md
```

## 代码风格

### 命名规范

```python
# 模块/包：snake_case
# my_module.py

# 类：PascalCase
class UserService:
    pass

# 函数/方法/变量：snake_case
def get_user_by_id(user_id: int) -> User:
    user_name = "test"
    return User(name=user_name)

# 常量：UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30

# 私有属性：_前缀
class User:
    def __init__(self):
        self._internal_cache = {}

# 类型别名：PascalCase
UserId = int
UserDict = dict[str, Any]
```

### 类型注解

```python
from typing import Optional, Union, Any
from collections.abc import Callable, Iterable

# 函数参数和返回值必须注解
def fetch_user(
    user_id: int,
    include_deleted: bool = False,
) -> Optional[User]:
    ...

# 复杂类型使用 TypeAlias
type JsonDict = dict[str, Any]
type AsyncHandler = Callable[[Request], Awaitable[Response]]

# 泛型
from typing import Generic, TypeVar

T = TypeVar('T')

class Repository(Generic[T]):
    def get(self, id: int) -> T | None:
        ...
```

### 文档字符串

```python
def calculate_discount(
    price: float,
    discount_rate: float,
    min_price: float = 0.0,
) -> float:
    """计算折扣后价格。

    Args:
        price: 原始价格，必须大于 0。
        discount_rate: 折扣率，范围 0-1。
        min_price: 最低价格限制。

    Returns:
        折扣后价格，不低于 min_price。

    Raises:
        ValueError: 当 price <= 0 或 discount_rate 不在 0-1 范围内。

    Examples:
        >>> calculate_discount(100, 0.2)
        80.0
    """
    if price <= 0:
        raise ValueError("价格必须大于 0")
    if not 0 <= discount_rate <= 1:
        raise ValueError("折扣率必须在 0-1 之间")

    final_price = price * (1 - discount_rate)
    return max(final_price, min_price)
```

## 异步编程

```python
import asyncio
from contextlib import asynccontextmanager

# 异步函数
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# 并发执行
async def fetch_all(urls: list[str]) -> list[dict]:
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks, return_exceptions=True)

# 异步上下文管理器
@asynccontextmanager
async def get_db_connection():
    conn = await create_connection()
    try:
        yield conn
    finally:
        await conn.close()
```

## 错误处理

```python
# 自定义异常层次
class AppError(Exception):
    """应用基础异常"""
    pass

class ValidationError(AppError):
    """验证错误"""
    pass

class NotFoundError(AppError):
    """资源未找到"""
    pass

# 使用 context 而非裸 raise
def get_user(user_id: int) -> User:
    user = db.query(User).get(user_id)
    if user is None:
        raise NotFoundError(f"用户 {user_id} 不存在") from None
    return user

# 异常链保留原始信息
try:
    await external_api.call()
except aiohttp.ClientError as e:
    raise AppError("外部服务调用失败") from e
```

## 数据验证

```python
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(..., ge=0, le=150)

    @field_validator('name')
    @classmethod
    def name_must_not_contain_numbers(cls, v: str) -> str:
        if any(c.isdigit() for c in v):
            raise ValueError('姓名不能包含数字')
        return v.title()  # 首字母大写
```

## 性能优化

```python
# 使用生成器避免内存问题
def read_large_file(file_path: str) -> Iterable[str]:
    with open(file_path) as f:
        for line in f:
            yield line.strip()

# 列表推导式 vs 生成器表达式
# 小数据量用列表推导
squares = [x**2 for x in range(100)]

# 大数据量用生成器
squares_gen = (x**2 for x in range(1000000))

# 使用 functools.lru_cache 缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

## 配置管理

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    redis_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## 常用模式

### 依赖注入

```python
from functools import lru_cache

class UserService:
    def __init__(self, db: Database):
        self.db = db

@lru_cache
def get_user_service() -> UserService:
    return UserService(db=get_database())
```

### 单例模式

```python
class Singleton:
    _instance = None

    def __new__(cls) -> "Singleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 工厂模式

```python
from abc import ABC, abstractmethod

class Handler(ABC):
    @abstractmethod
    def handle(self, data: dict) -> None:
        pass

class HandlerFactory:
    _handlers: dict[str, type[Handler]] = {}

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(handler_cls: type[Handler]) -> type[Handler]:
            cls._handlers[name] = handler_cls
            return handler_cls
        return decorator

    @classmethod
    def create(cls, name: str) -> Handler:
        return cls._handlers[name]()
```