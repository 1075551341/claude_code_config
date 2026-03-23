---
name: python-backend
description: Python 后端开发最佳实践，涵盖 FastAPI/Flask/Django、异步编程、数据处理、性能优化等
---

# Python Backend Development

## 框架选择

| 框架 | 适用场景 | 特点 |
|------|----------|------|
| FastAPI | API 服务、微服务 | 高性能、异步、自动文档 |
| Flask | 小型应用、原型 | 轻量、灵活 |
| Django | 全栈应用、CMS | ORM、Admin、生态完善 |

## FastAPI 标准结构

```
app/
├── main.py             # 应用入口
├── config.py           # 配置管理
├── dependencies.py     # 依赖注入
├── routers/            # 路由
│   ├── __init__.py
│   └── users.py
├── services/           # 业务逻辑
├── models/             # 数据模型
├── schemas/            # Pydantic 模型
├── crud/               # 数据库操作
└── utils/              # 工具函数
```

## FastAPI 核心

### 应用入口
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, tasks
from app.config import settings

app = FastAPI(
    title="API Server",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
```

### Pydantic 模型
```python
# schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
```

### 路由层
```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.user import User, UserCreate, UserUpdate
from app.crud import user as user_crud

router = APIRouter()

@router.get("/", response_model=list[User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return user_crud.get_users(db, skip=skip, limit=limit)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if user_crud.get_by_email(db, user.email):
        raise HTTPException(400, "邮箱已存在")
    return user_crud.create_user(db, user)
```

### 数据库操作
```python
# crud/user.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

## 异步编程

### 异步路由
```python
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/external")
async def fetch_external():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
```

### 异步数据库
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## 错误处理

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=400,
        content={"code": exc.code, "msg": exc.message, "data": None}
    )

# 使用
raise AppException(40001, "参数错误")
```

## 配置管理

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "API Server"
    DEBUG: bool = False
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

## 性能优化

| 场景 | 方案 |
|------|------|
| 数据库查询 | 索引 + select_related/prefetch_related |
| 缓存 | Redis + functools.lru_cache |
| 异步任务 | Celery + Redis/RabbitMQ |
| 大文件 | 流式响应 + 分块上传 |
| 并发 | uvicorn workers + gunicorn |

## 常用依赖

```txt
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
sqlalchemy>=2.0
pydantic>=2.0
pydantic-settings>=2.0
python-dotenv
httpx
redis
celery
```