---
name: security-forensics
description: 进行安全取证分析
triggers: [进行安全取证分析, 威胁狩猎, 日志分析, 入侵检测, 安全审计, 计算机取证]
---

# 安全取证分析

## 核心能力

**日志分析、威胁狩猎、入侵检测、取证报告生成。**

---

## 适用场景

- 安全事件调查
- 入侵检测分析
- 日志取证
- 威胁狩猎
- 安全审计
- Sigma 规则应用

---

## 取证流程

### 1. 证据收集

```
收集内容：
- 系统日志（/var/log/、Windows Event Log）
- 网络日志（防火墙、IDS/IPS）
- 应用日志
- 文件系统快照
- 进程/网络连接记录
- 用户活动记录
```

### 2. 时间线构建

```bash
# Linux
journalctl --since "2024-01-01" --until "2024-01-02"
last -n 50
lastb  # 失败登录

# Windows
wevtutil qe System /c:100 /rd:true /f:text
Get-WinEvent -LogName Security -MaxEvents 100
```

### 3. 异常检测

```
关注指标：
- 异常登录时间/地点
- 权限提升事件
- 文件异常访问
- 网络异常连接
- 进程异常行为
```

### 4. Sigma 规则匹配

```yaml
# Sigma 规则示例
title: Suspicious PowerShell Execution
status: test
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    EventID: 1
    Image|endswith: powershell.exe
    CommandLine|contains: '-enc'
  condition: selection
```

### 5. 报告生成

```markdown
# 安全事件分析报告

## 事件概述
- 时间：{timestamp}
- 类型：{event_type}
- 影响范围：{scope}

## 证据链
1. {evidence_1}
2. {evidence_2}

## 分析结论
- 攻击路径：{path}
- 漏洞利用：{vulnerability}
- 数据影响：{impact}

## 响应建议
- 紧急措施：{immediate}
- 长期改进：{longterm}
```

---

## 常用取证工具

| 类型 | Linux | Windows |
|------|-------|---------|
| 日志分析 | journalctl, logwatch | Event Viewer, wevtutil |
| 进程检查 | ps, top, lsof | Task Manager, Process Explorer |
| 网络检查 | netstat, ss, tcpdump | netstat, Wireshark |
| 文件检查 | find, stat, statx | Get-ChildItem, forfiles |
| 用户检查 | last, who, w | whoami, query user |

---

## 威胁狩猎方法

### 基于假设

```
假设 → 验证 → 发现 → 扩展

示例假设：
- 如果有入侵，可能有异常外联
- 如果有提权，可能有异常进程
- 如果有数据窃取，可能有批量访问
```

### 基于指标

```
IOC（Indicators of Compromise）：
- IP 地址/域名
- 文件哈希
- 特定进程名
- 特定端口
- 特定时间模式
```

---

## 日志分析重点

| 日志类型 | 关键内容 |
|----------|----------|
| 认证日志 | 登录成功/失败、来源IP |
| 系统日志 | 服务启停、错误、警告 |
| 应用日志 | API调用、数据访问 |
| 网络日志 | 连接、流量、阻断 |

---

## 注意事项

```
必须：
- 保留原始证据完整性
- 记录分析步骤和时间戳
- 使用工具而非手动修改
- 时间线关联分析

避免：
- 修改原始日志
- 单一证据定论
- 忽略正常行为基线
- 过早删除分析数据
```

---

## 相关技能

- `logging-monitoring` - 日志监控
- `security-best-practices` - 安全实践
- `report-generator` - 报告生成