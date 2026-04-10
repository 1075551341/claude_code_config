---
name: api-gateway
description: API 网关配置与管理。触发词：API网关、Kong、网关配置、路由管理、流量控制、API管理。
---

# API 网关

## 核心功能

- 路由管理 - 请求转发、负载均衡
- 安全防护 - 认证、限流、WAF
- 监控分析 - 日志、指标、追踪
- 协议转换 - HTTP/HTTPS、gRPC

## Kong 网关

### 安装配置

```yaml
# docker-compose.yml
services:
  kong:
    image: kong:latest
    environment:
      KONG_DATABASE: "off"
      KONG_ADMIN_LISTEN: "0.0.0.0:8001"
    ports:
      - "8000:8000" # Proxy
      - "8001:8001" # Admin API
      - "8443:8443" # Proxy SSL
```

### 服务配置

```bash
# 添加服务
curl -X POST http://localhost:8001/services \
  -d "name=user-service" \
  -d "url=http://user-service:3000"

# 添加路由
curl -X POST http://localhost:8001/services/user-service/routes \
  -d "paths[]=/api/users"

# 添加限流插件
curl -X POST http://localhost:8001/services/user-service/plugins \
  -d "name=rate-limiting" \
  -d "config.minute=100"
```

### 声明式配置

```yaml
# kong.yml
_format_version: "3.0"

services:
  - name: user-service
    url: http://user-service:3000
    routes:
      - name: users-route
        paths: [/api/users]
    plugins:
      - name: rate-limiting
        config: { minute: 100 }
      - name: jwt
```

## 认证配置

### JWT 认证

```bash
# 创建消费者
curl -X POST http://localhost:8001/consumers -d "username=app-user"

# 添加 JWT 凭证
curl -X POST http://localhost:8001/consumers/app-user/jwt \
  -d "key=app-key" -d "secret=app-secret"

# 启用 JWT 插件
curl -X POST http://localhost:8001/plugins -d "name=jwt"
```

### API Key 认证

```bash
curl -X POST http://localhost:8001/plugins -d "name=key-auth"
curl -X POST http://localhost:8001/consumers/app-user/key-auth -d "key=your-api-key"
```

## 限流配置

```bash
# 基于请求次数
curl -X POST http://localhost:8001/plugins \
  -d "name=rate-limiting" \
  -d "config.second=10" \
  -d "config.hour=1000"

# 基于请求大小
curl -X POST http://localhost:8001/plugins \
  -d "name=request-size-limiting" \
  -d "config.allowed_payload_size=10"  # MB
```

## 监控配置

```bash
# Prometheus
curl -X POST http://localhost:8001/plugins -d "name=prometheus"

# 文件日志
curl -X POST http://localhost:8001/plugins \
  -d "name=file-log" \
  -d "config.path=/var/log/kong/access.log"

# Zipkin 追踪
curl -X POST http://localhost:8001/plugins \
  -d "name=zipkin" \
  -d "config.http_endpoint=http://zipkin:9411/api/v2/spans"
```

## Nginx 网关

### 基础配置

```nginx
upstream backend {
    least_conn;
    server backend1:3000 weight=5;
    server backend2:3000 weight=3;
}

server {
    listen 80;
    server_name api.example.com;

    # 限流
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }
}
```

### 缓存配置

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

location /api/public/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 10m;
    proxy_cache_key $scheme$host$request_uri;
    proxy_pass http://backend/;
}
```

## 最佳实践

1. 使用 HTTPS 强制加密
2. 配置合理的超时和重试
3. 实施限流防止滥用
4. 记录详细日志便于排查
5. 监控关键指标（延迟、错误率）
6. 使用蓝绿/金丝雀发布
7. 准备回滚方案
