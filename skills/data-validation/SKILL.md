# 数据校验

## 描述
请求参数与数据模型校验方案，涵盖 Zod、Joi、class-validator、Pydantic 等主流校验库。

## 触发条件
当用户提到：数据校验、参数校验、Zod、Joi、Yup、class-validator、Pydantic、表单验证、Schema 校验、输入验证、类型校验 时使用此技能。

## 方案选型

| 场景 | 推荐方案 | 适用范围 |
|------|----------|----------|
| TypeScript 全栈 | Zod | 前后端共享 Schema，类型推导强 |
| Express/Koa | Joi / Zod | 中间件式校验 |
| NestJS | class-validator + class-transformer | 装饰器风格 |
| 前端表单 | Zod + react-hook-form | React 表单 |
| Python API | Pydantic v2 | FastAPI 原生集成 |
| Python 通用 | marshmallow / cerberus | Flask/Django 场景 |

## 核心代码示例

### TypeScript - Zod 全栈校验
```typescript
import { z } from 'zod';

// 定义 Schema（前后端共享）
const createUserSchema = z.object({
  username: z.string().min(3).max(20).regex(/^[a-zA-Z0-9_]+$/),
  email: z.string().email('邮箱格式错误'),
  password: z.string().min(8).regex(/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, '需包含大小写字母和数字'),
  age: z.number().int().min(1).max(150).optional(),
  role: z.enum(['admin', 'user', 'editor']).default('user'),
  tags: z.array(z.string()).max(10).optional(),
});

type CreateUserInput = z.infer<typeof createUserSchema>;

// Express 校验中间件
function validate<T extends z.ZodSchema>(schema: T) {
  return (req: Request, res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      const errors = result.error.issues.map((e) => ({
        field: e.path.join('.'),
        message: e.message,
      }));
      return res.status(400).json({ code: 1, msg: '参数校验失败', data: errors });
    }
    req.body = result.data;
    next();
  };
}

app.post('/users', validate(createUserSchema), createUserHandler);
```

### TypeScript - Zod + react-hook-form
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

function RegisterForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<CreateUserInput>({
    resolver: zodResolver(createUserSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('username')} />
      {errors.username && <span>{errors.username.message}</span>}
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
      <button type="submit">注册</button>
    </form>
  );
}
```

### Python - Pydantic v2 校验
```python
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    user = "user"
    editor = "editor"

class CreateUserRequest(BaseModel):
    """
    描述：用户创建请求参数校验模型
    """
    username: str = Field(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(min_length=8)
    age: Optional[int] = Field(None, ge=1, le=150)
    role: Role = Role.user
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("需包含大写字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("需包含数字")
        return v

# FastAPI 自动集成
from fastapi import APIRouter
router = APIRouter()

@router.post("/users")
async def create_user(body: CreateUserRequest):
    return {"code": 0, "msg": "ok", "data": body.model_dump()}
```

## 最佳实践

1. **前后端共享** → Zod Schema 定义一次，前端表单 + 后端接口共用
2. **永远不信前端** → 即使前端已校验，后端必须再次校验
3. **友好提示** → 校验错误返回字段名 + 中文描述，前端直接展示
4. **白名单模式** → 只接受已定义字段，strip 未知字段（Zod `.strict()`）
5. **组合复用** → 基础 Schema 通过 `.pick()` / `.extend()` 派生变体
6. **自定义校验** → 业务规则（如唯一性检查）放在 Service 层，不混入 Schema
7. **错误码统一** → 校验失败统一返回 400 + 结构化错误列表
