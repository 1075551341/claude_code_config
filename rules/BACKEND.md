---
trigger: glob
description: 后端 / API / 服务端代码开发时启用
globs:
  - "**/*.{py,go,rs,java,kt,cs}"
  - "**/{api,server,backend,services}/**/*.{ts,js}"
---

# 后端规则（薄层）

> 配合 CORE 使用。项目级覆盖（框架模板、目录约定）→ `catalog/rules/RULES_BACKEND.md`。允许与 FRONTEND glob 重叠，禁止互斥 if-else。
> 语言/运行时地板 → `config/toolchain.yaml`。缺工具 BLOCKED，禁止静默回退。

## API

```
GET    /resources          # 列表
GET    /resources/:id      # 详情
POST   /resources          # 创建
PUT    /resources/:id      # 全量更新
PATCH  /resources/:id      # 部分更新
DELETE /resources/:id      # 删除
```

响应格式项目内统一；错误码初始化时统一定义，禁止魔法数字散落。

## 错误处理

```
外部依赖  → timeout + fallback，避免雪崩
所有异步  → 必须显式处理异常，禁止裸 await / 裸 except
边界校验  → 系统入口验证入参；内部信任类型系统
```

通用错误处理 → `rules/CORE.md`（R16）。安全基线 → `rules/SECURITY.md`。

## 何时必须写文档注释

```
① 业务流程 > 3 步
② 外部服务调用（标注超时 / 重试）
③ 定时任务 / Worker
④ 与 DATABASE 规则交叉的 Migration
```

最小内容：目的 + 入参/出参 + 异常 + 依赖。表设计/事务/Migration → `rules/DATABASE.md`。
