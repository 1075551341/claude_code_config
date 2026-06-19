# 输入验证模板

## 系统边界验证

```python
from pydantic import BaseModel, Field, field_validator

class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(ge=0, le=150)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()
```

## 内部代码信任类型系统

```python
def process_user(user: User) -> None:
    # 不重复验证 User 类型 —— 边界已通过 pydantic 验证
    send_welcome_email(user.email)
```
