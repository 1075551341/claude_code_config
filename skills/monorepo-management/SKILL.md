---
name: monorepo-management
description: 当需要管理Monorepo项目、使用Turborepo/Nx/pnpm workspace、配置多包仓库时调用此技能。触发词：Monorepo、Turborepo、Nx、pnpm workspace、多包管理、组件库开发、包管理、工作区配置。
---

# Monorepo 项目管理最佳实践

## 描述
Monorepo 项目管理技能，涵盖 Turborepo/Nx/pnpm workspace 的配置、
包管理、依赖共享、构建缓存和 CI/CD 集成。

## 触发条件
当需要搭建或管理多包项目、前后端统一仓库、组件库 + 应用共存时使用。

## 技术选型

| 工具 | 适用场景 | 特点 |
|------|----------|------|
| pnpm workspace | 中小型 Monorepo | 轻量、原生支持、磁盘节省 |
| Turborepo | 前端 Monorepo | 增量构建、远程缓存、简单 |
| Nx | 大型企业级 | 依赖图分析、插件生态丰富 |

## pnpm workspace 初始化

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

```
monorepo/
├── apps/
│   ├── web/          # 前端应用
│   ├── api/          # 后端服务
│   └── admin/        # 管理后台
├── packages/
│   ├── ui/           # 共享 UI 组件
│   ├── utils/        # 工具函数
│   ├── types/        # 共享类型
│   └── config/       # 共享配置（ESLint/TS/Prettier）
├── pnpm-workspace.yaml
├── package.json
└── turbo.json
```

## Turborepo 配置

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {},
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```

## 常用命令

```bash
# 全部构建
pnpm turbo build

# 仅构建指定包
pnpm turbo build --filter=web

# 开发模式
pnpm turbo dev

# 添加共享依赖
pnpm add zod --filter=packages/utils

# 包间引用
pnpm add @monorepo/utils --filter=apps/web --workspace
```

## 最佳实践

1. **共享配置**：ESLint/TypeScript/Prettier 配置抽到 packages/config
2. **类型共享**：公共 TypeScript 类型放 packages/types
3. **版本一致**：pnpm 的 catalog 功能统一依赖版本
4. **增量构建**：配置 Turborepo 远程缓存加速 CI
5. **依赖隔离**：每个包声明自己的依赖，不依赖 hoist
