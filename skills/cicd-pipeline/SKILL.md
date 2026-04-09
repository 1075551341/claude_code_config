---
name: cicd-pipeline
description: 当需要配置CI/CD流水线、设置GitHub Actions/GitLab CI、实现自动化构建部署时调用此技能。触发词：CI/CD、持续集成、持续部署、GitHub Actions、GitLab CI、自动化部署、流水线、构建流水线、部署自动化。
---

# CI/CD 流水线最佳实践

## 描述
持续集成与持续部署技能，涵盖 GitHub Actions/GitLab CI 配置、
Docker 镜像构建、自动化测试、部署策略和环境管理。

## 触发条件
当需要配置自动化构建、测试、部署流水线时使用。

## 技术选型

| 平台 | 推荐方案 | 适用场景 |
|------|----------|----------|
| GitHub | GitHub Actions | 开源项目、GitHub 生态 |
| GitLab | GitLab CI/CD | 私有部署、安全要求高 |
| 通用 | Jenkins | 企业级、高度定制 |
| 容器 | Docker + K8s | 微服务、弹性伸缩 |

## GitHub Actions 模板

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '20'
  REGISTRY: ghcr.io

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm type-check
      - run: pnpm test -- --coverage
      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/

  build:
    needs: lint-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ${{ env.REGISTRY }}/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - name: 部署到生产环境
        run: |
          echo "执行部署脚本"
```

## Dockerfile 模板（多阶段构建）

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

## 最佳实践

1. **分支策略**：main（生产）→ develop（开发）→ feature/* （功能）
2. **自动检查**：PR 必须通过 lint + test + type-check
3. **缓存优化**：缓存 node_modules 和 Docker 层
4. **环境隔离**：dev/staging/production 环境独立配置
5. **回滚机制**：保留最近 5 个版本的镜像和部署记录
6. **密钥管理**：通过 GitHub Secrets / Vault 注入，禁止硬编码
