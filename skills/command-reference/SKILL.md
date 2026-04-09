---
name: command-reference
description: 常用CLI命令速查表。触发词：命令速查、CLI命令、Git命令、Docker命令、Linux命令、npm命令、命令行、命令参考。
---

# 常用命令速查

## Git 命令

### 基础操作

```bash
# 克隆仓库
git clone <url> [--depth=1]  # 浅克隆

# 查看状态
git status [-s]              # 简洁模式
git diff [--cached]          # 查看暂存区差异
git log --oneline -10        # 最近10条提交

# 添加提交
git add <file>               # 添加文件
git add -p                   # 交互式添加
git commit -m "message"
git commit --amend           # 修改上次提交

# 分支操作
git branch [-a]              # 查看分支
git checkout -b <branch>     # 创建并切换
git merge <branch>           # 合并分支
git branch -d <branch>       # 删除分支
```

### 高级操作

```bash
# 暂存工作区
git stash [push -m "msg"]
git stash pop
git stash list

# 回退操作
git reset --soft HEAD~1      # 保留修改
git reset --hard HEAD~1      # 丢弃修改
git revert <commit>          # 创建反向提交

# 远程操作
git remote -v
git fetch --all
git push origin <branch>
git pull --rebase            # 拉取并变基

# 清理操作
git clean -fd                # 删除未跟踪文件
git gc --prune=now           # 清理垃圾
```

## Docker 命令

### 容器操作

```bash
# 运行容器
docker run -d --name <name> -p 80:80 <image>
docker run -it <image> bash  # 交互模式

# 查看容器
docker ps [-a]               # 查看运行中/所有
docker logs <container> [-f] # 查看日志
docker exec -it <c> bash     # 进入容器

# 控制容器
docker start/stop/restart <container>
docker rm <container> [-f]   # 删除容器
docker kill <container>      # 强制停止
```

### 镜像操作

```bash
# 镜像管理
docker images                # 查看镜像
docker pull <image>[:tag]
docker push <image>
docker rmi <image>

# 构建镜像
docker build -t <name> . [-f Dockerfile]
docker build --no-cache .    # 无缓存构建

# 镜像信息
docker inspect <image>
docker history <image>
```

### Docker Compose

```bash
docker-compose up [-d]       # 启动服务
docker-compose down          # 停止服务
docker-compose ps            # 查看状态
docker-compose logs [-f]     # 查看日志
docker-compose build         # 构建服务
```

## npm/yarn 命令

### 包管理

```bash
# 安装
npm install [package] [--save-dev]
npm install -g <package>     # 全局安装
yarn add <package> [--dev]

# 更新
npm update [package]
npm outdated                 # 查看过时包
yarn upgrade

# 删除
npm uninstall <package>
yarn remove <package>
npm prune                    # 清理多余包

# 查看
npm list [--depth=0]
npm info <package>
npm view <package> versions  # 查看版本
```

### 脚本和配置

```bash
# 运行脚本
npm run <script>
npm test
npm start
yarn <script>

# 配置
npm init [-y]                # 初始化
npm config set <key> <value>
npm config list

# 发布
npm version <major|minor|patch>
npm publish [--access public]
```

## Python 命令

### pip 管理

```bash
pip install <package>        # 安装
pip install -r requirements.txt
pip uninstall <package>
pip list [--outdated]
pip freeze > requirements.txt
pip show <package>

# pipx（全局工具）
pipx install <tool>
pipx run <tool>
```

### Python 执行

```bash
python -m venv .venv         # 创建虚拟环境
python -m pip install <pkg>  # 模块方式运行pip
python -c "code"             # 执行代码
python -m pytest             # 运行测试
python -m http.server 8000   # 启动HTTP服务
```

## Linux 常用命令

### 文件操作

```bash
ls -la                       # 详细列表
cd <dir>                     # 切换目录
pwd                          # 当前路径
mkdir -p <dir>               # 创建目录
rm -rf <dir>                 # 强制删除
cp -r <src> <dst>            # 复制
mv <src> <dst>               # 移动/重命名

find . -name "*.py"          # 查找文件
grep -r "text" .             # 搜索内容
chmod 755 <file>             # 修改权限
chown user:group <file>      # 修改所有者
```

### 进程管理

```bash
ps aux                       # 查看进程
kill -9 <pid>                # 强制终止
killall <name>               # 按名终止
top                          # 实时监控
htop                         # 增强版监控

bg                           # 后台运行
fg                           # 前台恢复
nohup <cmd> &                # 持久后台
jobs                         # 查看任务
```

### 系统信息

```bash
uname -a                     # 系统信息
df -h                        # 磁盘使用
free -h                      # 内存使用
uptime                       # 运行时间
whoami                       # 当前用户
```

## 网络命令

### 端口和连接

```bash
netstat -tlnp                # 监听端口
ss -tlnp                     # 端口状态
lsof -i :3000                # 端口占用
curl -I <url>                # HTTP头
wget <url>                   # 下载文件

# Windows 替代
netstat -ano | findstr :3000
Get-NetTCPConnection -LocalPort 3000
```

### SSH 操作

```bash
ssh user@host                # 连接
ssh -L 8080:localhost:80 host  # 本地转发
ssh -R 80:host:80 user@host    # 远程转发
scp <file> user@host:/path  # 上传
scp user@host:/path <file>  # 下载
```

## 数据库命令

### PostgreSQL

```bash
psql -U user -d db           # 连接
pg_dump -U user db > backup.sql  # 备份
pg_restore -U user db < backup.sql  # 恢复
```

### MySQL

```bash
mysql -u user -p             # 连接
mysqldump -u user db > backup.sql  # 备份
mysql -u user db < backup.sql      # 恢复
```

### Redis

```bash
redis-cli                    # 连接
redis-cli -h host -p 6379    # 远程连接
redis-cli INFO               # 查看信息
redis-cli FLUSHALL           # 清空数据
```

## 命令组合技巧

```bash
# 查找并删除
find . -name "*.tmp" -delete

# 统计代码行数
find . -name "*.py" | xargs wc -l

# 监控文件变化
watch -n 1 'ls -la'

# 后台运行并记录日志
nohup command > log.txt 2>&1 &

# 管道组合
cat file | grep "error" | sort | uniq -c
```
