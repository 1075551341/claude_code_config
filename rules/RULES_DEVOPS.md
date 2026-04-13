---
description: DevOps、CI/CD、容器化、部署相关任务时启用
alwaysApply: false
---

# DevOps 规则

## 技术选型

```
CI/CD → GitHub Actions / GitLab CI | 容器化 → Docker + Compose | 编排 → Kubernetes
IaC → Terraform / Pulumi | 监控 → Prometheus + Grafana | 日志 → ELK / Loki
```

## Docker 规范

```dockerfile
# 多阶段构建 + 非 root 用户 + 健康检查
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
RUN addgroup -g 1001 -S appgroup && adduser -u 1001 -S appuser -G appgroup
USER appuser
HEALTHCHECK --interval=30s --timeout=3s CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1
EXPOSE 3000
CMD ["node", "server.js"]
```

**必须**：官方镜像 + 指定版本标签 + 多阶段构建 + 非 root + 健康检查 + .dockerignore

## Kubernetes 原则

```yaml
spec:
  replicas: 3
  resources:
    {
      requests: { cpu: 100m, memory: 128Mi },
      limits: { cpu: 500m, memory: 512Mi },
    }
  livenessProbe: { httpGet: { path: /health, port: 3000 } }
  readinessProbe: { httpGet: { path: /ready, port: 3000 } }
```

**必须**：requests/limits + 健康检查 + Secret 存敏感信息 + RBAC + Pod 反亲和性

## CI/CD 规范

```
流水线：快速反馈 + 增量构建 + 并行执行 + fail-fast
部署策略：蓝绿(零停机) / 金丝雀(渐进流量) / 滚动更新
安全检查：依赖漏洞扫描 + SAST + 密钥扫描 + 镜像安全扫描
```

## 监控告警

```
可操作：每条告警有明确处理步骤 | 低噪声：避免告警疲劳 | 分级：critical/warning/info
SLI/SLO：可用性 99.9% | 延迟 P99<200ms | 错误率<0.1%
```

## 日志规范

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "service": "user-service",
  "trace_id": "abc123",
  "message": "User logged in",
  "duration_ms": 45
}
```

**要求**：结构化 JSON + 追踪 ID + 脱敏敏感信息 + 输出到 stdout/stderr

## Terraform 原则

```
必须：模块化 + 环境隔离 + 状态远程存储 + 变更可审计
流程：terraform fmt → validate → plan → Code Review → apply
```
