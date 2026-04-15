---
name: deploy-script
description: 编写部署脚本、配置PM2/systemd服务、实现应用部署
triggers: [部署脚本, PM2配置, systemd服务, 应用部署, 部署配置, 生产部署, 服务启动脚本, 部署自动化]
---

# 部署脚本生成

生成各类部署配置和脚本

## 使用方式

```
/deploy-script <type> [options]
```

**类型说明：**
- `pm2` - PM2 部署配置
- `systemd` - Systemd 服务配置
- `docker` - Docker 部署脚本
- `nginx` - Nginx 反向代理配置
- `all` - 生成完整部署方案

## PM2 部署

### 配置文件

```javascript
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'myapp-api',
      script: 'dist/server.js',
      instances: 'max',
      exec_mode: 'cluster',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'development',
        PORT: 3000,
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000,
      },
      error_file: 'logs/error.log',
      out_file: 'logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
    },
  ],

  deploy: {
    production: {
      user: 'deploy',
      host: ['server1.example.com', 'server2.example.com'],
      ref: 'origin/main',
      repo: 'git@github.com:user/repo.git',
      path: '/var/www/myapp',
      'post-deploy': 'pnpm install && pnpm build && pm2 reload ecosystem.config.js --env production',
      'pre-setup': 'apt-get install git -y',
    },
    staging: {
      user: 'deploy',
      host: 'staging.example.com',
      ref: 'origin/develop',
      repo: 'git@github.com:user/repo.git',
      path: '/var/www/myapp-staging',
      'post-deploy': 'pnpm install && pnpm build && pm2 reload ecosystem.config.js --env staging',
    },
  },
}
```

### 部署命令

```bash
# 初始部署
pm2 deploy production setup

# 部署更新
pm2 deploy production

# 回滚
pm2 deploy production revert 1

# 查看状态
pm2 status
pm2 logs myapp-api
pm2 monit
```

### 部署脚本

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

APP_NAME="myapp"
DEPLOY_DIR="/var/www/$APP_NAME"
BACKUP_DIR="/var/backups/$APP_NAME"
GIT_BRANCH="${1:-main}"

echo "🚀 开始部署 $APP_NAME..."

# 1. 备份当前版本
if [ -d "$DEPLOY_DIR" ]; then
  echo "📦 备份当前版本..."
  mkdir -p "$BACKUP_DIR"
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" -C "$DEPLOY_DIR" .
fi

# 2. 拉取代码
echo "📥 拉取最新代码..."
cd "$DEPLOY_DIR"
git fetch origin
git checkout "$GIT_BRANCH"
git pull origin "$GIT_BRANCH"

# 3. 安装依赖
echo "📦 安装依赖..."
pnpm install --frozen-lockfile

# 4. 构建
echo "🔨 构建项目..."
pnpm build

# 5. 数据库迁移
echo "📊 执行数据库迁移..."
pnpm knex migrate:latest

# 6. 重启服务
echo "🔄 重启服务..."
pm2 reload ecosystem.config.js --env production

# 7. 健康检查
echo "🏥 健康检查..."
sleep 5
curl -f http://localhost:3000/health || exit 1

echo "✅ 部署完成!"
```

## Systemd 服务

### 服务配置

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=MyApp API Server
Documentation=https://github.com/user/myapp
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/myapp
ExecStart=/usr/bin/node dist/server.js
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=myapp

# 环境变量
Environment=NODE_ENV=production
Environment=PORT=3000
EnvironmentFile=/var/www/myapp/.env

# 资源限制
LimitNOFILE=65535
MemoryMax=1G
TasksMax=4096

# 安全加固
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/www/myapp/logs

[Install]
WantedBy=multi-user.target
```

### 管理命令

```bash
# 重载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start myapp

# 停止服务
sudo systemctl stop myapp

# 重启服务
sudo systemctl restart myapp

# 查看状态
sudo systemctl status myapp

# 查看日志
sudo journalctl -u myapp -f

# 开机自启
sudo systemctl enable myapp
```

## Docker 部署

```bash
#!/bin/bash
# scripts/docker-deploy.sh

set -e

IMAGE_NAME="myapp"
IMAGE_TAG="${1:-latest}"
REGISTRY="registry.example.com"

echo "🐳 Docker 部署..."

# 构建镜像
docker build -t $IMAGE_NAME:$IMAGE_TAG .

# 推送到仓库
docker tag $IMAGE_NAME:$IMAGE_TAG $REGISTRY/$IMAGE_NAME:$IMAGE_TAG
docker push $REGISTRY/$IMAGE_NAME:$IMAGE_TAG

# 拉取并重启
docker-compose pull
docker-compose up -d

# 清理旧镜像
docker image prune -af --filter "until=168h"
```

## 健康检查脚本

```bash
#!/bin/bash
# scripts/health-check.sh

API_URL="http://localhost:3000"
MAX_RETRIES=3
RETRY_INTERVAL=5

check_health() {
  curl -sf "$API_URL/health" > /dev/null 2>&1
}

echo "🏥 健康检查开始..."

for i in $(seq 1 $MAX_RETRIES); do
  if check_health; then
    echo "✅ 服务健康"
    exit 0
  fi

  echo "⚠️ 检查失败 ($i/$MAX_RETRIES)，${RETRY_INTERVAL}秒后重试..."
  sleep $RETRY_INTERVAL
done

echo "❌ 服务不健康，发送告警..."
# 发送告警通知
# curl -X POST $WEBHOOK_URL -d '{"text":"服务健康检查失败"}'

exit 1
```

## 回滚脚本

```bash
#!/bin/bash
# scripts/rollback.sh

set -e

BACKUP_DIR="/var/backups/myapp"
DEPLOY_DIR="/var/www/myapp"
VERSION="${1:-latest}"

echo "🔙 开始回滚..."

# 列出可用备份
if [ "$VERSION" = "list" ]; then
  ls -la "$BACKUP_DIR"
  exit 0
fi

# 选择备份
if [ "$VERSION" = "latest" ]; then
  BACKUP_FILE=$(ls -t "$BACKUP_DIR"/*.tar.gz | head -1)
else
  BACKUP_FILE="$BACKUP_DIR/backup_$VERSION.tar.gz"
fi

if [ ! -f "$BACKUP_FILE" ]; then
  echo "❌ 备份文件不存在: $BACKUP_FILE"
  exit 1
fi

# 执行回滚
echo "📦 恢复备份: $BACKUP_FILE"
rm -rf "$DEPLOY_DIR"/*
tar -xzf "$BACKUP_FILE" -C "$DEPLOY_DIR"

# 重启服务
pm2 reload all

echo "✅ 回滚完成"
```

## CI/CD 配置

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
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

      - run: pnpm install --frozen-lockfile
      - run: pnpm build

      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/myapp
            git pull origin main
            pnpm install --frozen-lockfile
            pnpm build
            pm2 reload all
```
