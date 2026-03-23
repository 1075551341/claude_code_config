---
name: docker-devops
description: Docker 容器化开发与 DevOps 最佳实践，涵盖 Dockerfile 编写、Compose 配置、CI/CD 流水线等
---

# Docker & DevOps

## Dockerfile 最佳实践

### 基础模板

```dockerfile
# Node.js 应用
FROM node:22-alpine AS builder

WORKDIR /app

# 先复制依赖文件，利用缓存层
COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

# 复制源码并构建
COPY . .
RUN pnpm build

# 生产镜像
FROM node:22-alpine AS runner

WORKDIR /app

# 安全：非 root 用户
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nodejs

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

USER nodejs

EXPOSE 3000

CMD ["node", "dist/server.js"]
```

### Python 应用

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY . .

# 非 root 用户
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile 优化规则

| 规则 | 说明 |
|------|------|
| 使用多阶段构建 | 减小最终镜像体积 |
| 使用特定版本标签 | 避免 `latest`，保证可重复性 |
| 合并 RUN 指令 | 减少镜像层数 |
| 利用构建缓存 | 先复制依赖文件 |
| 非 root 用户运行 | 提高安全性 |
| 使用 .dockerignore | 排除不需要的文件 |

## Docker Compose

### 开发环境配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 生产环境配置

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    image: myapp:${VERSION:-latest}
    restart: always
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          memory: 256M
```

## 常用命令

```bash
# 构建镜像
docker build -t myapp:latest .

# 运行容器
docker run -d -p 3000:3000 --name myapp myapp:latest

# 查看日志
docker logs -f myapp

# 进入容器
docker exec -it myapp /bin/sh

# 清理资源
docker system prune -af

# Compose 操作
docker-compose up -d          # 启动
docker-compose down           # 停止并删除
docker-compose logs -f        # 查看日志
docker-compose exec app sh    # 进入容器
```

## CI/CD 流水线

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v2
        with:
          version: 8

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'

      - run: pnpm install
      - run: pnpm lint
      - run: pnpm test
      - run: pnpm build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build and push Docker image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker push myapp:${{ github.sha }}

      - name: Deploy to server
        run: |
          ssh user@server "cd /app && docker-compose pull && docker-compose up -d"
```

### 检查清单

- [ ] Dockerfile 使用多阶段构建
- [ ] 镜像使用特定版本标签
- [ ] 非 root 用户运行
- [ ] 敏感信息使用 secrets
- [ ] 日志输出到 stdout/stderr
- [ ] 健康检查配置
- [ ] 资源限制设置
- [ ] CI/CD 流水线配置