---
name: nginx-config
description: 当需要配置Nginx服务器、设置反向代理负载均衡、配置SSL证书时调用此技能。触发词：Nginx配置、反向代理、负载均衡、SSL配置、Nginx服务器、Nginx部署、HTTPS配置、静态资源服务、gzip压缩。
---

# Nginx 配置生成

生成各类 Nginx 配置文件。

## 使用方式

```
/nginx-config <type> [options]
```

**类型说明：**
- `reverse-proxy` - 反向代理配置
- `load-balance` - 负载均衡配置
- `ssl` - SSL/HTTPS 配置
- `static` - 静态文件服务配置
- `api` - API 网关配置

## 反向代理配置

### 基础反向代理

```nginx
# /etc/nginx/sites-available/myapp
server {
    listen 80;
    server_name api.example.com;

    # 访问日志
    access_log /var/log/nginx/myapp-access.log;
    error_log /var/log/nginx/myapp-error.log;

    # 代理配置
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;

        # 请求头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 32k;
    }

    # 健康检查端点
    location /health {
        proxy_pass http://127.0.0.1:3000/health;
        access_log off;
    }
}
```

### 多应用代理

```nginx
# 多个应用代理到不同路径
server {
    listen 80;
    server_name example.com;

    # API 服务
    location /api/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 前端应用
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
    }

    # 管理后台
    location /admin/ {
        proxy_pass http://127.0.0.1:3001/;
        proxy_set_header Host $host;
    }
}
```

## SSL/HTTPS 配置

### Let's Encrypt 自动证书

```nginx
server {
    listen 80;
    server_name api.example.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 证书自动续期

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d example.com -d www.example.com

# 自动续期（crontab）
0 0 1 * * /usr/bin/certbot renew --quiet --post-hook "systemctl reload nginx"
```

## 负载均衡配置

```nginx
upstream backend {
    # 负载均衡策略
    least_conn;  # 最少连接（默认 round-robin）

    # 后端服务器
    server 127.0.0.1:3000 weight=3;
    server 127.0.0.1:3001 weight=2;
    server 127.0.0.1:3002 backup;  # 备用服务器

    # 健康检查（需第三方模块）
    # health_check interval=5s fails=3 passes=2;

    # 长连接
    keepalive 32;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";

        # 超时
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
}
```

## 缓存配置

```nginx
# 缓存区域定义
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m
                 max_size=1g inactive=60m use_temp_path=off;

server {
    listen 80;
    server_name api.example.com;

    location /api/ {
        proxy_pass http://127.0.0.1:3000/;

        # 缓存配置
        proxy_cache api_cache;
        proxy_cache_key "$request_uri|$request_body";
        proxy_cache_valid 200 10m;
        proxy_cache_valid 404 1m;

        # 缓存头
        add_header X-Cache-Status $upstream_cache_status;

        # 不缓存的请求
        proxy_cache_bypass $http_x_nocache;
        proxy_no_cache $http_pragma;
    }

    # 静态资源缓存
    location /static/ {
        alias /var/www/static/;

        expires 30d;
        add_header Cache-Control "public, immutable";

        # Gzip 压缩
        gzip on;
        gzip_types text/css application/javascript image/svg+xml;
    }
}
```

## API 网关配置

```nginx
# 限流配置
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

server {
    listen 80;
    server_name api.example.com;

    # API 版本路由
    location /v1/ {
        proxy_pass http://127.0.0.1:3001/;
    }

    location /v2/ {
        proxy_pass http://127.0.0.1:3002/;
    }

    # 限流
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn conn_limit 10;

        proxy_pass http://127.0.0.1:3000/;
    }

    # IP 白名单
    location /admin/ {
        allow 192.168.1.0/24;
        allow 10.0.0.0/8;
        deny all;

        proxy_pass http://127.0.0.1:3000/admin/;
    }

    # 请求体大小限制
    client_max_body_size 10m;
}
```

## 静态文件服务

```nginx
server {
    listen 80;
    server_name static.example.com;

    root /var/www/static;
    index index.html;

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript
               text/xml application/xml application/xml+rss text/javascript;

    # Brotli 压缩（需安装模块）
    # brotli on;
    # brotli_types text/plain text/css application/json application/javascript;
}
```

## 常用命令

```bash
# 测试配置
sudo nginx -t

# 重载配置
sudo nginx -s reload

# 重启服务
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx

# 查看日志
sudo tail -f /var/log/nginx/error.log
```