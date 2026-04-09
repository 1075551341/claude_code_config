---
name: troubleshooting-guide
description: 问题排查和故障诊断指南。触发词：问题排查、故障诊断、troubleshooting、问题定位、故障分析、错误排查、调试指南、问题诊断。
---

# 问题排查指南

## 排查流程

```
1️⃣ 确认问题 → 明确症状、复现条件、影响范围
2️⃣ 收集信息 → 日志、错误信息、配置、环境
3️⃣ 定位原因 → 缩小范围、假设验证、根因分析
4️⃣ 解决问题 → 制定方案、执行修复、验证结果
5️⃣ 总结预防 → 记录经验、优化监控、防止复发
```

## 常见问题分类

### 应用启动失败

```
排查步骤：
1. 检查依赖是否安装完整
2. 检查配置文件格式是否正确
3. 检查端口是否被占用
4. 检查环境变量是否设置
5. 查看启动日志错误信息

常见原因：
- 依赖缺失：npm install / pip install
- 配置错误：检查 JSON/YAML 格式
- 端口冲突：更换端口或终止占用进程
- 环境变量：检查 .env 文件
- 权限问题：检查文件读写权限
```

### API 请求失败

```
排查步骤：
1. 检查网络连接是否正常
2. 检查 URL 和参数是否正确
3. 检查认证信息是否有效
4. 检查请求格式是否符合 API 规范
5. 查看服务器端日志

常见原因：
- 网络问题：ping/dns 检查
- URL 错误：对比 API 文档
- 认证失效：刷新 Token
- 参数格式：检查 Content-Type
- 服务端错误：查看服务日志
```

### 数据库连接失败

```
排查步骤：
1. 检查数据库服务是否运行
2. 检查连接参数（host/port/user/password）
3. 检查网络是否可达
4. 检查用户权限是否足够
5. 检查连接池配置

常见原因：
- 服务未启动：启动数据库服务
- 参数错误：核对配置文件
- 网络不通：防火墙/网络配置
- 权限不足：授予必要权限
- 连接耗尽：调整连接池大小
```

### 性能问题

```
排查步骤：
1. 确定性能指标（响应时间、吞吐量）
2. 使用监控工具定位瓶颈
3. 分析资源使用情况
4. 检查是否有 N+1 查询
5. 检查是否有内存泄漏

常用工具：
- Node.js: clinic.js, node --inspect
- Python: cProfile, memory_profiler
- 数据库: EXPLAIN ANALYZE, slow query log
- 网络: curl timing, wireshark

常见原因：
- 查询慢：添加索引、优化 SQL
- 内存泄漏：检查对象生命周期
- CPU 高：分析热点函数
- 网络：检查带宽、延迟
```

### 内存泄漏

```
排查步骤：
1. 监控内存使用趋势
2. 使用内存分析工具
3. 检查对象是否被正确释放
4. 检查是否有循环引用
5. 检查缓存是否有清理机制

工具：
- Node.js: heapdump, node-memwatch
- Python: tracemalloc, gc.get_objects()
- Java: VisualVM, MAT
- Go: pprof

常见原因：
- 未清理的缓存：添加过期机制
- 未关闭的连接：确保资源释放
- 全局对象累积：改为局部作用域
- 事件监听器未移除：off/removeEventListener
```

### 前端渲染问题

```
排查步骤：
1. 检查浏览器兼容性
2. 检查控制台错误信息
3. 检查网络请求是否成功
4. 检查 CSS 是否加载
5. 检查 JavaScript 执行顺序

常见原因：
- 兼容性：使用 polyfill 或调整代码
- 资源加载：检查 CDN/路径
- CSS 问题：检查选择器、优先级
- JS 错误：检查变量声明、顺序
- 状态管理：检查数据流
```

## 排查工具速查

### 网络排查

```bash
# 检查连接
ping <host>
curl -I <url>
telnet <host> <port>

# DNS 检查
nslookup <domain>
dig <domain>

# 端口检查
netstat -tlnp | grep <port>
lsof -i :<port>

# 抓包分析
tcpdump -i eth0 port <port>
wireshark
```

### 进程排查

```bash
# 查看进程
ps aux | grep <name>
top -p <pid>
htop

# 查看资源
lsof -p <pid>        # 打开文件
strace -p <pid>      # 系统调用
/proc/<pid>/status   # 进程状态

# 进程控制
kill -9 <pid>
kill -STOP <pid>     # 暂停
kill -CONT <pid>     # 继续
```

### 日志排查

```bash
# 查看日志
tail -f /var/log/app.log
grep -i error /var/log/*.log
awk '/ERROR/ {print}' log.txt

# 日志分析
grep -c "error" log.txt    # 错误计数
grep "error" | sort | uniq -c  # 错误分类统计
journalctl -u service -f   # systemd 服务日志
```

### 数据库排查

```sql
-- 查看连接
SHOW PROCESSLIST;

-- 查看慢查询
SELECT * FROM mysql.slow_log LIMIT 10;

-- 分析查询
EXPLAIN SELECT * FROM table WHERE condition;

-- 查看锁
SHOW OPEN TABLES WHERE In_use > 0;

-- 查看状态
SHOW STATUS LIKE 'Threads%';
```

## 问题记录模板

```markdown
## 问题记录

### 基本信息

- 发现时间：2024-01-15 10:30
- 发现人：张三
- 影响范围：用户登录功能

### 问题描述

用户登录时出现 500 错误，错误信息：
```

Error: Connection refused to database

```

### 排查过程
1. 检查数据库服务状态 → 运行正常
2. 检查连接参数 → 配置正确
3. 检查网络连接 → telnet 失败
4. 发现防火墙新增规则阻断端口

### 根因
防火墙规则更新时误将数据库端口（3306）阻断

### 解决方案
修改防火墙规则，开放 3306 端口

### 验证
- 登录功能恢复正常
- 数据库连接成功率 100%

### 预防措施
- 防火墙变更需经过测试
- 添加数据库端口监控
- 建立变更审批流程
```

## 排查原则

1. **先确认症状** — 明确问题是什么，不要急于解决
2. **缩小范围** — 从宏观到微观，逐步定位
3. **假设验证** — 提出假设，验证假设，不要猜测
4. **保留现场** — 在修复前收集日志和状态
5. **记录总结** — 每次问题都要记录，形成知识库
