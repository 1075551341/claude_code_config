---
name: observability-setup
description: 可观测性系统搭建与配置。触发词：可观测性、OpenTelemetry、APM、监控搭建、链路追踪。
---

# 可观测性搭建

## 三大支柱

```
📊 指标 (Metrics) - Prometheus、Grafana
📝 日志 (Logs) - ELK、Loki
🔗 追踪 (Traces) - Jaeger、Zipkin
```

## OpenTelemetry

### Node.js 集成

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-grpc';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-grpc';
import { PrometheusExporter } from '@opentelemetry/exporter-prometheus';

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: 'http://localhost:4317',
  }),
  metricReader: new PrometheusExporter({
    port: 9464,
  }),
  instrumentations: [
    // 自动埋点
    new HttpInstrumentation(),
    new ExpressInstrumentation(),
    new PgInstrumentation(),
  ],
});

sdk.start();
```

### 手动埋点

```typescript
import { trace, metrics } from '@opentelemetry/api';

const tracer = trace.getTracer('my-service');
const meter = metrics.getMeter('my-service');

// 创建计数器
const requestCounter = meter.createCounter('requests_total', {
  description: 'Total requests',
});

// 创建直方图
const requestDuration = meter.createHistogram('request_duration_ms', {
  description: 'Request duration in ms',
});

// 使用 Span
async function handleRequest(req, res) {
  const span = tracer.startSpan('handleRequest');

  try {
    // 记录指标
    requestCounter.add(1, { method: req.method, path: req.path });

    const startTime = Date.now();

    // 业务逻辑
    await doSomething();

    // 记录耗时
    requestDuration.record(Date.now() - startTime, {
      method: req.method,
      status: 'success',
    });

    span.setStatus({ code: SpanStatusCode.OK });
  } catch (error) {
    span.recordException(error);
    span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
    throw error;
  } finally {
    span.end();
  }
}
```

### 上下文传播

```typescript
import { context, propagation } from '@opentelemetry/api';

// 提取上下文（接收请求时）
const receivedContext = propagation.extract(context.active(), headers);

// 在上下文中执行
context.with(receivedContext, () => {
  // 后续调用会自动关联
  tracer.startActiveSpan('child-operation', (span) => {
    // ...
    span.end();
  });
});

// 注入上下文（发送请求时）
const headers = {};
propagation.inject(context.active(), headers);
```

## Prometheus

### 指标类型

```typescript
import client from 'prom-client';

// 计数器 - 只增
const counter = new client.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'path', 'status'],
});

counter.inc({ method: 'GET', path: '/api/users', status: '200' });

// 仪表盘 - 可增可减
const gauge = new client.Gauge({
  name: 'active_connections',
  help: 'Active connections',
});

gauge.inc();
gauge.dec();

// 直方图 - 分布统计
const histogram = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Request duration in seconds',
  buckets: [0.1, 0.5, 1, 2, 5],
});

const end = histogram.startTimer();
// ... 处理请求
end();

// 摘要 - 分位数
const summary = new client.Summary({
  name: 'response_size_bytes',
  help: 'Response size in bytes',
  percentiles: [0.5, 0.9, 0.99],
});
```

### 告警规则

```yaml
# prometheus/alerts.yml
groups:
  - name: api-alerts
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

      - alert: HighLatency
        expr: |
          histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: P99 latency exceeds 1 second
```

## Grafana

### Dashboard 配置

```json
{
  "dashboard": {
    "title": "API Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (service)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))"
          }
        ]
      },
      {
        "title": "P99 Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))"
          }
        ]
      }
    ]
  }
}
```

## 日志集成

### 结构化日志

```typescript
import winston from 'winston';

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'app.log' }),
  ],
});

// 添加追踪 ID
logger.info('Request processed', {
  trace_id: trace.getActiveSpan()?.spanContext().traceId,
  span_id: trace.getActiveSpan()?.spanContext().spanId,
  user_id: user.id,
  duration_ms: duration,
});
```

### Loki 集成

```yaml
# loki-config.yml
auth_enabled: false

server:
  http_listen_port: 3100

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h
```

## 最佳实践

```markdown
1. 使用 OpenTelemetry 统一埋点
2. 日志关联 TraceID
3. 关键指标设置告警
4. Dashboard 按服务组织
5. 定义 SLO 和 SLI
6. 定期审查告警阈值
7. 使用采样控制成本
```