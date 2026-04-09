---
name: ffuf-fuzzing
description: 当需要进行Web安全测试、目录枚举、参数模糊测试、漏洞扫描时调用此技能。触发词：ffuf、Web模糊测试、目录扫描、参数Fuzz、安全测试、渗透测试、Web安全、目录枚举。
---

# FFUF Web 模糊测试

## 核心能力

**Web目录枚举、参数模糊测试、漏洞发现。**

---

## 适用场景

- Web 安全测试
- 目录/文件枚举
- 参数模糊测试
- 子域名发现

---

## 安装与配置

```bash
# 安装
go install github.com/ffuf/ffuf/v2@latest

# 或使用包管理器
apt install ffuf      # Debian/Ubuntu
brew install ffuf     # macOS
```

---

## 基本用法

### 目录枚举

```bash
# 基本目录扫描
ffuf -u https://target.com/FUZZ -w wordlist.txt

# 指定扩展名
ffuf -u https://target.com/FUZZ -w wordlist.txt -e .php,.html,.bak

# 递归扫描
ffuf -u https://target.com/FUZZ -w wordlist.txt -recursion -recursion-depth 2
```

### 参数模糊测试

```bash
# GET参数
ffuf -u "https://target.com/?FUZZ=value" -w wordlist.txt

# POST参数
ffuf -u https://target.com -X POST -d "FUZZ=value" -w wordlist.txt

# JSON参数
ffuf -u https://target.com -X POST -H "Content-Type: application/json" -d '{"FUZZ":"value"}' -w wordlist.txt
```

### 子域名枚举

```bash
ffuf -u https://FUZZ.target.com -w subdomains.txt -H "Host: FUZZ.target.com"
```

---

## 过滤选项

### 状态码过滤

```bash
# 只显示200
ffuf -u https://target.com/FUZZ -w wordlist.txt -mc 200

# 排除404
ffuf -u https://target.com/FUZZ -w wordlist.txt -fc 404

# 多个状态码
ffuf -u https://target.com/FUZZ -w wordlist.txt -mc 200,301,302
```

### 大小过滤

```bash
# 过滤特定响应大小
ffuf -u https://target.com/FUZZ -w wordlist.txt -fs 1234

# 过滤范围
ffuf -u https://target.com/FUZZ -w wordlist.txt -fs 1234-5678
```

### 内容过滤

```bash
# 过滤包含特定内容
ffuf -u https://target.com/FUZZ -w wordlist.txt -fr "Not Found"

# 匹配特定内容
ffuf -u https://target.com/FUZZ -w wordlist.txt -mr "admin"
```

---

## 常用词表

```bash
# SecLists词表位置
/usr/share/seclists/Discovery/Web-Content/
/usr/share/seclists/Discovery/DNS/
/usr/share/seclists/Fuzzing/

# 常用词表
- common.txt          # 通用目录
- raft-medium.txt     # 中等规模
- directory-list.txt  # 目录列表
- subdomains-top1million.txt  # 子域名
```

---

## 高级用法

### 多点模糊

```bash
# 同时模糊多个位置
ffuf -u https://target.com/FUZZ1/FUZZ2 -w dirs.txt:FUZZ1 -w files.txt:FUZZ2
```

### 认证测试

```bash
# 带Cookie
ffuf -u https://target.com/FUZZ -w wordlist.txt -H "Cookie: session=xxx"

# Basic认证
ffuf -u https://target.com/FUZZ -w wordlist.txt -H "Authorization: Basic xxx"
```

### 速率控制

```bash
# 限制速率
ffuf -u https://target.com/FUZZ -w wordlist.txt -rate 50

# 限制并发
ffuf -u https://target.com/FUZZ -w wordlist.txt -t 20
```

---

## 输出选项

```bash
# 输出到文件
ffuf -u https://target.com/FUZZ -w wordlist.txt -o results.json

# 输出格式
ffuf -u https://target.com/FUZZ -w wordlist.txt -o results.json -of json
ffuf -u https://target.com/FUZZ -w wordlist.txt -o results.csv -of csv
ffuf -u https://target.com/FUZZ -w wordlist.txt -o results.html -of html
```

---

## 测试场景

### API 测试

```bash
# API端点发现
ffuf -u https://api.target.com/v1/FUZZ -w api_endpoints.txt -H "Authorization: Bearer xxx"

# 参数测试
ffuf -u "https://api.target.com/v1/users?FUZZ=1" -w params.txt
```

### 登录测试

```bash
# 用户名枚举
ffuf -u https://target.com/login -X POST -d "username=FUZZ&password=xxx" -w users.txt -fr "Invalid username"

# 密码测试（需授权）
ffuf -u https://target.com/login -X POST -d "username=admin&password=FUZZ" -w passwords.txt -fr "Invalid password"
```

---

## 注意事项

```
必须：
- 获得授权后测试
- 控制请求速率
- 记录测试过程

避免：
- 未授权扫描
- 过高并发
- 忽略robots.txt
- 生产环境暴力测试
```

---

## 相关技能

- `security-best-practices` - 安全实践
- `api-development` - API 开发
- `security-forensics` - 安全取证