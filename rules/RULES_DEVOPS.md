---
description: DevOps、CI/CD、容器化、部署相关任务时启用
alwaysApply: false
---

# DevOps 规则（专用）

> 配合核心规则使用，仅在 DevOps 场景加载

## 技术选型

```markdown
场景               →  推荐方案
───────────────────────────────────
CI/CD              →  GitHub Actions / GitLab CI / Jenkins
容器化             →  Docker + Docker Compose
编排               →  Kubernetes / Docker Swarm
基础设施即代码     →  Terraform / Pulumi
配置管理           →  Ansible / Chef
监控               →  Prometheus + Grafana
日志               →  ELK Stack / Loki
服务网格           →  Istio / Linkerd
```

## Docker 规范

### Dockerfile 最佳实践

```dockerfile
# 使用多阶段构建
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .

# 非 root 用户
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

EXPOSE 3000
CMD ["node", "server.js"]
```

### Dockerfile 规则

```markdown
必须遵循：
- 使用官方基础镜像
- 指定镜像版本标签（不用 latest）
- 多阶段构建减小镜像体积
- 非 root 用户运行
- 健康检查配置
- .dockerignore 排除不必要文件

优化建议：
- 合并 RUN 指令减少层数
- 利用构建缓存
- 最小化镜像体积（alpine）
```

### Docker Compose 模板

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://user:pass@db:5432/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 10s
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

## Kubernetes 规范

### 部署配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:v1.0.0
        ports:
        - containerPort: 3000
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: myapp
              topologyKey: kubernetes.io/hostname
```

### K8s 最佳实践

```markdown
资源管理：
- 设置 requests 和 limits
- 使用 LimitRange 和 ResourceQuota
- HPA/VPA 自动伸缩

安全：
- 使用 Secret 存储敏感信息
- 网络策略限制流量
- Pod Security Standards
- RBAC 权限控制

可靠性：
- 多副本部署
- Pod 反亲和性
- 优雅关闭
- 健康检查
```

## CI/CD 规范

### GitHub Actions 模板

```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '20'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test -- --coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Build Docker image
      run: |
        docker build -t myapp:${{ github.sha }} .
    
    - name: Push to registry
      run: |
        docker push myapp:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
```

### CI/CD 原则

```markdown
流水线设计：
- 快速反馈（测试先行）
- 增量构建（利用缓存）
- 并行执行（独立任务）
- 失败快速（fail-fast）

部署策略：
- 蓝绿部署：零停机切换
- 金丝雀发布：渐进式流量
- 滚动更新：逐步替换

安全检查：
- 依赖漏洞扫描
- SAST 静态分析
- 密钥扫描
- 镜像安全扫描
```

## 监控告警

### Prometheus 规则

```yaml
groups:
- name: app.rules
  rules:
  - alert: HighErrorRate
    expr: |
      sum(rate(http_requests_total{status=~"5.."}[5m])) 
      / sum(rate(http_requests_total[5m])) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: High error rate detected
      description: Error rate is {{ $value | humanizePercentage }}

  - alert: HighLatency
    expr: |
      histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
```

### 告警原则

```markdown
告警设计：
- 可操作：每条告警都有明确处理步骤
- 低噪声：避免告警疲劳
- 分级：critical/warning/info
- 聚合：相同告警合并

SLI/SLO：
- 可用性：99.9% 可用时间
- 延迟：99% 请求 < 200ms
- 错误率：< 0.1%
```

## 日志规范

```markdown
日志级别：
- ERROR：系统错误、异常
- WARN：潜在问题、告警
- INFO：关键业务事件
- DEBUG：调试信息（生产关闭）

日志格式（JSON）：
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "service": "user-service",
  "trace_id": "abc123",
  "user_id": "user123",
  "message": "User logged in",
  "duration_ms": 45
}

日志规范：
- 结构化日志
- 包含追踪 ID
- 脱敏敏感信息
- 统一输出到 stdout/stderr
```

## 基础设施即代码

### Terraform 规范

```hcl
# 模块化组织
module "vpc" {
  source = "./modules/vpc"
  
  name               = "production"
  cidr               = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  
  tags = {
    Environment = "production"
    Project     = "myapp"
  }
}

# 输出
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}
```

### IaC 原则

```markdown
代码组织：
- 模块化设计
- 环境隔离
- 状态远程存储
- 变更可审计

最佳实践：
- terraform fmt 格式化
- terraform validate 验证
- terraform plan 预览变更
- Code Review 变更
```