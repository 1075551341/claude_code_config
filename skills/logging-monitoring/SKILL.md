---
name: logging-monitoring
description: 可观测性系统搭建，包括日志
triggers: [可观测性系统搭建，包括日志, 监控, 链路追踪, Prometheus, Grafana, OpenTelemetry]
---

# 日志与监控

## 描述
应用日志采集与系统监控方案，涵盖结构化日志、链路追踪、指标采集与告警

## 触发条件
当用户提到：日志、监控、Winston、Pino、ELK、Prometheus、Grafana、链路追踪、OpenTelemetry、告警、日志级别、结构化日志、APM、loguru 时使用此技能

## 方案选型

| 场景 | 推荐方案 | 适用范围 |
|------|----------|----------|
| Node.js 日志 | Pino（性能优先）/ Winston（功能丰富） | 后端服务 |
| Python 日志 | loguru / structlog | 后端/脚本 |
| 日志聚合 | ELK Stack / Loki + Grafana | 多服务集中查询 |
| 指标监控 | Prometheus + Grafana | 系统/业务指标 |
| 链路追踪 | OpenTelemetry + Jaeger | 微服务调用链 |
| 错误追踪 | Sentry | 异常采集 + 告警 |

## 核心代码示例

### TypeScript - Pino 结构化日志
```typescript
import pino from 'pino';
import { randomUUID } from 'crypto';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'development'
    ? { target: 'pino-pretty', options: { colorize: true } }
    : undefined,
  formatters: {
    level: (label) => ({ level: label }),
  },
  serializers: {
    err: pino.stdSerializers.err,
    req: pino.stdSerializers.req,
    res: pino.stdSerializers.res,
  },
});

// Express 请求日志中间件
function requestLogger(req: Request, res: Response, next: NextFunction) {
  const requestId = req.headers['x-request-id'] as string || randomUUID();
  const child = logger.child({ requestId, method: req.method, url: req.url });
  req.log = child;

  const start = Date.now();
  res.on('finish', () => {
    child.info({
      statusCode: res.statusCode,
      duration: Date.now() - start,
    }, '请求完成');
  });
  next();
}
```

### TypeScript - Prometheus 指标采集
```typescript
import { Registry, Counter, Histogram, collectDefaultMetrics } from 'prom-client';

const register = new Registry();
collectDefaultMetrics({ register });

const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'HTTP 请求总数',
  labelNames: ['method', 'route', 'status'] as const,
  registers: [register],
});

const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP 请求耗时',
  labelNames: ['method', 'route'] as const,
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 5],
  registers: [register],
});

// Express 中间件
function metricsMiddleware(req: Request, res: Response, next: NextFunction) {
  const end = httpRequestDuration.startTimer({ method: req.method, route: req.route?.path || req.path });
  res.on('finish', () => {
    httpRequestsTotal.inc({ method: req.method, route: req.route?.path || req.path, status: res.statusCode });
    end();
  });
  next();
}

// GET /metrics 端点
app.get('/metrics', async (_req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

### Python - loguru 结构化日志
```python
from loguru import logger
import sys, json

logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {extra[request_id]} | {message}",
    level="INFO",
    serialize=False,
)
logger.add("logs/app.log", rotation="100 MB", retention="30 days", compression="gz")

# FastAPI 请求日志中间件
from starlette.middleware.base import BaseHTTPMiddleware
import uuid, time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        with logger.contextualize(request_id=request_id):
            start = time.monotonic()
            response = await call_next(request)
            duration = round(time.monotonic() - start, 3)
            logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}s)")
            response.headers["X-Request-ID"] = request_id
            return response
```

## 最佳实践

1. **结构化** → JSON 格式日志，方便机器解析和检索
2. **请求 ID** → 全链路传递 requestId，串联分布式调用
3. **日志分级** → ERROR（需告警）> WARN（需关注）> INFO（业务流程）> DEBUG（调试）
4. **脱敏** → 密码、Token、手机号等敏感字段序列化前脱敏
5. **采样** → 高流量场景对 DEBUG/INFO 日志采样，避免磁盘爆满
6. **告警** → 错误率突增、P99 延迟飙升 → 自动告警（PagerDuty/飞书/钉钉）
7. **保留** → 生产日志至少保留 30 天，审计日志按合规要求保留
