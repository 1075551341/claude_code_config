---
description: Python 代码开发时启用
---

# Python 规则（专用）

> 配合核心规则使用，仅在 Python 场景加载

## 版本与工具链

```
Python 版本遵循项目清单与 CI，不设置全局版本地板。
包管理：优先项目声明、现有锁文件与 CI 命令（uv / pip / poetry 等）。
缺少可选辅助工具时用现有能力回退；项目必需工具确实缺失时说明影响并给出解决选项，不擅自换工具或锁文件。
格式化、Lint、类型检查和测试：运行项目已配置的命令；ruff / black / mypy / pyright / pytest 等仅为常见选项。
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

优先复用项目现有依赖；标准库能满足就不增加库。存储和跨系统交换时明确 UTC/偏移，展示时明确目标时区，避免混用无时区时间。需要复杂日历、时区规则或特殊解析时，再评估项目已有的 pendulum / arrow 等成熟库，不为统一风格替换依赖。

```python
from datetime import datetime, timezone
from typing import Callable

def create_service(get_now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)):
    now = get_now()
    return now.isoformat()

# 时间影响业务判断时，测试注入固定时间，不要求新增依赖。
fixed = datetime(2025, 1, 1, tzinfo=timezone.utc)
result = create_service(get_now=lambda: fixed)
```

命名时区转换可使用项目运行时支持的标准库 `zoneinfo`；按项目部署方式提供所需时区数据。

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
