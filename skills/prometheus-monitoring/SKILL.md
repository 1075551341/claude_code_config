---
name: prometheus-monitoring
description: 当需要配置Prometheus监控、设置Grafana仪表板、实现系统监控告警时调用此技能。触发词：Prometheus、Grafana、监控配置、告警设置、系统监控、指标采集、监控仪表板。
---

# Prometheus 监控

## 核心能力

**Prometheus配置、Grafana仪表板、告警规则设置。**

---

## 适用场景

- 系统监控
- 指标采集
- 告警配置
- 仪表板可视化

---

## Prometheus 配置

### prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093

rule_files:
  - "alerts.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
    - targets: ['node-exporter:9100']

  - job_name: 'app'
    static_configs:
    - targets: ['app:8080']
```

---

## 常用指标类型

| 类型 | 说明 | 示例 |
|------|------|------|
| Counter | 累计计数 | 请求总数 |
| Gauge | 瞬时值 | 内存使用 |
| Histogram | 分布统计 | 请求延迟 |
| Summary | 分位数 | 响应时间P99 |

---

## 告警规则

### alerts.yml

```yaml
groups:
- name: node_alerts
  rules:
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "CPU使用率过高"
      description: "实例 {{ $labels.instance }} CPU使用率 {{ $value }}%"

  - alert: HighMemoryUsage
    expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "内存使用率过高"

  - alert: InstanceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "实例不可达"
```

---

## Alertmanager 配置

```yaml
global:
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alert@example.com'
  smtp_auth_username: 'alert@example.com'
  smtp_auth_password: 'password'

route:
  receiver: 'default'
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
  - match:
      severity: critical
    receiver: 'critical-team'

receivers:
- name: 'default'
  email_configs:
  - to: 'team@example.com'

- name: 'critical-team'
  email_configs:
  - to: 'critical@example.com'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/xxx'
    channel: '#alerts'
```

---

## Grafana 仪表板

### 常用面板

```
1. CPU使用率
   查询: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

2. 内存使用率
   查询: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

3. 磁盘使用率
   查询: (1 - (node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"})) * 100

4. 网络流量
   查询: rate(node_network_receive_bytes_total[5m])
```

### Dashboard JSON 导入

```bash
# 通过ID导入
grafana-cli admin data-migration --dashboard-id 1860

# 常用Dashboard ID
- Node Exporter: 1860
- Nginx: 12708
- Redis: 11835
- PostgreSQL: 9628
```

---

## PromQL 查询

```promql
# 请求速率
rate(http_requests_total[5m])

# P99延迟
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# 错误率
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))

# 按服务分组
sum by (service) (rate(http_requests_total[5m]))
```

---

## 应用埋点

### Python

```python
from prometheus_client import Counter, Histogram, start_http_server

# Counter
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])

# Histogram
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency')

@REQUEST_LATENCY.time()
def handle_request():
    REQUEST_COUNT.labels(method='GET', endpoint='/api').inc()
    # 处理请求
```

### Node.js

```javascript
const client = require('prom-client');

const counter = new client.Counter({
    name: 'http_requests_total',
    help: 'Total HTTP Requests',
    labelNames: ['method', 'path']
});

const histogram = new client.Histogram({
    name: 'http_request_duration_seconds',
    help: 'HTTP Request Duration',
    buckets: [0.1, 0.5, 1, 2, 5]
});

// 暴露指标端点
app.get('/metrics', async (req, res) => {
    res.set('Content-Type', client.register.contentType);
    res.end(await client.register.metrics());
});
```

---

## 注意事项

```
必须:
- 设置合理告警阈值
- 配置告警静默
- 定期检查仪表板
- 监控监控系统本身

避免:
- 告警过多告警疲劳
- 忽略关键指标
- 无文档的Dashboard
- 缺少告警分级
```

---

## 相关技能

- `logging-monitoring` - 日志监控
- `kubernetes` - K8s 部署
- `docker-devops` - Docker 配置