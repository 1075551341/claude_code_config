---
name: api-gateway
description: API 网关配置与管理。触发词：API网关、Kong、网关配置、路由管理、流量控制、API管理。
---

# API 网关

## 核心功能

```
🔀 路由管理 - 请求转发、负载均衡
🔒 安全防护 - 认证、限流、WAF
📊 监控分析 - 日志、指标、追踪
🔄 协议转换 - HTTP/HTTPS、gRPC
```

## Kong 网关

### 安装配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  kong:
    image: kong:latest
    environment:
      KONG_DATABASE: "off"
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: "0.0.0.0:8001"
    ports:
      - "8000:8000"   # Proxy
      - "8001:8001"   # Admin API
      - "8443:8443"   # Proxy SSL
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

# 添加插件
curl -X POST http://localhost:8001/services/user-service/plugins \
  -d "name=rate-limiting" \
  -d "config.minute=100" \
  -d "config.policy=local"
```

### Kong 声明式配置

```yaml
# kong.yml
_format_version: "3.0"

services:
  - name: user-service
    url: http://user-service:3000
    routes:
      - name: users-route
        paths:
          - /api/users
    plugins:
      - name: rate-limiting
        config:
          minute: 100
          policy: local
      - name: jwt
        config:
          secret_is_base64: false

  - name: order-service
    url: http://order-service:3000
    routes:
      - name: orders-route
        paths:
          - /api/orders
    plugins:
      - name: key-auth
```

## 认证配置

### JWT 认证

```bash
# 创建消费者
curl -X POST http://localhost:8001/consumers \
  -d "username=app-user"

# 添加 JWT 凭证
curl -X POST http://localhost:8001/consumers/app-user/jwt \
  -d "key=app-key" \
  -d "secret=app-secret"

# 启用 JWT 插件
curl -X POST http://localhost:8001/plugins \
  -d "name=jwt"
```

### API Key 认证

```bash
# 启用 key-auth
curl -X POST http://localhost:8001/plugins \
  -d "name=key-auth"

# 创建 API Key
curl -X POST http://localhost:8001/consumers/app-user/key-auth \
  -d "key=your-api-key"
```

### OAuth2

```bash
# 配置 OAuth2 插件
curl -X POST http://localhost:8001/plugins \
  -d "name=oauth2" \
  -d "config.scopes=email,profile" \
  -d "config.mandatory_scope=true" \
  -d "config.enable_authorization_code=true"
```

## 限流配置

### 基于请求次数

```bash
curl -X POST http://localhost:8001/plugins \
  -d "name=rate-limiting" \
  -d "config.second=10" \
  -d "config.hour=1000" \
  -d "config.policy=redis" \
  -d "config.redis_host=redis"
```

### 基于并发

```bash
curl -X POST http://localhost:8001/plugins \
  -d "name=request-size-limiting" \
  -d "config.allowed_payload_size=10"  # MB
```

### 熔断器

```bash
curl -X POST http://localhost:8001/plugins \
  -d "name=ai-rate-limiting-advanced" \
  -d "config.limit=100" \
  -d "config.window_size=60"
```

## 日志与监控

### Prometheus 集成

```bash
curl -X POST http://localhost:8001/plugins \
  -d "name=prometheus"

# 访问指标
curl http://localhost:8001/metrics
```

### ELK 日志

```bash
curl -X POST http://localhost:8001/plugins \
  -d "name=file-log" \
  -d "config.path=/var/log/kong/access.log"
```

### 请求追踪

```bash
curl -X POST http://localhost:8001/plugins \
  -d "name=zipkin" \
  -d "config.http_endpoint=http://zipkin:9411/api/v2/spans" \
  -d "config.sample_ratio=0.1"
```

## Nginx 网关

### 基础配置

```nginx
upstream backend {
    least_conn;
    server backend1:3000 weight=5;
    server backend2:3000 weight=3;
    server backend3:3000 backup;
}

server {
    listen 80;
    server_name api.example.com;

    # 限流
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # 日志
    access_log /var/log/nginx/api.access.log json;
    error_log /var/log/nginx/api.error.log;

    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # 超时
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
        proxy_send_timeout 30s;

        # 缓冲
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "OK";
    }
}
```

### 缓存配置

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

server {
    location /api/public/ {
        proxy_cache api_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_key $scheme$host$request_uri;
        add_header X-Cache-Status $upstream_cache_status;

        proxy_pass http://backend/;
    }
}
```

### JWT 验证

```nginx
location /api/ {
    auth_jwt "Protected API";
    auth_jwt_key_file /etc/nginx/jwt_key.pem;

    proxy_pass http://backend/;
}
```

## 最佳实践

```markdown
1. 使用 HTTPS 强制加密
2. 配置合理的超时和重试
3. 实施限流防止滥用
4. 记录详细日志便于排查
5. 监控关键指标（延迟、错误率）
6. 使用蓝绿/金丝雀发布
7. 准备回滚方案
```