---
name: threat-hunting
description: 当需要进行威胁狩猎、Sigma规则应用、安全威胁检测、APT攻击分析时调用此技能。触发词：威胁狩猎、Threat Hunting、Sigma规则、威胁检测、APT分析、攻击链分析、威胁情报、安全分析。
---

# 威胁狩猎

## 核心能力

**Sigma规则应用、威胁检测、攻击链分析。**

---

## 适用场景

- 威胁狩猎
- Sigma规则编写
- 攻击链分析
- 威胁检测

---

## Sigma 规则

### 规则结构

```yaml
title: 检测可疑PowerShell执行
status: stable
description: 检测使用编码命令的PowerShell执行
author: Security Team
date: 2024/01/15
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    EventID: 1
    Image|endswith: powershell.exe
    CommandLine|contains:
      - '-enc'
      - '-encodedcommand'
      - 'FromBase64String'
  condition: selection
falsepositives:
  - 合法的管理脚本
level: high
tags:
  - attack.execution
  - attack.t1059.001
```

### 规则字段说明

```yaml
# 日志源
logsource:
  category: process_creation  # 进程创建
  product: windows            # Windows系统
  service: security           # 安全日志

# 检测逻辑
detection:
  selection:          # 选择条件
    Field: Value      # 字段匹配
    Field|contains:   # 包含匹配
    Field|startswith: # 前缀匹配
    Field|endswith:   # 后缀匹配
    Field|re:         # 正则匹配
  
  condition: selection  # 组合条件

# 严重级别
level: low | medium | high | critical
```

---

## 威胁狩猎流程

### 1. 假设驱动

```markdown
## 狩猎假设

假设：攻击者可能使用PowerShell进行横向移动

推理依据：
- APT组织常用手法
- 近期类似攻击案例
- 环境中PowerShell使用频繁

狩猎目标：
- 检测可疑PowerShell命令
- 发现横向移动痕迹
```

### 2. 数据收集

```markdown
## 数据源

- 进程创建日志 (EventID 4688/1)
- 网络连接日志 (EventID 3)
- 文件操作日志 (EventID 11/15)
- 注册表修改 (EventID 12/13/14)
- PowerShell日志 (Module/Script Block)
```

### 3. 分析检测

```yaml
# 检测横向移动
title: 横向移动检测
logsource:
  product: windows
  service: security
detection:
  selection_psexec:
    EventID: 4688
    NewProcessName|contains: psexec
  selection_wmi:
    EventID: 4688
    NewProcessName|contains: wmic
  selection_psremote:
    EventID: 4688
    ProcessCommandLine|contains: 'Enter-PSSession'
  condition: selection_psexec or selection_wmi or selection_psremote
```

---

## MITRE ATT&CK 映射

### 战术与技术

```markdown
## 攻击链分析

1. Initial Access (初始访问)
   - T1566: Phishing
   - T1190: Exploit Public App

2. Execution (执行)
   - T1059: Command and Scripting
   - T1204: User Execution

3. Persistence (持久化)
   - T1053: Scheduled Task
   - T1547: Boot or Logon Autostart

4. Lateral Movement (横向移动)
   - T1021: Remote Services
   - T1077: Windows Admin Shares

5. Exfiltration (数据窃取)
   - T1048: Exfiltration Over Alternative Protocol
```

---

## 常见检测规则

### 凭证窃取

```yaml
title: 检测凭证转储
logsource:
  product: windows
  service: security
detection:
  selection_lsass:
    EventID: 4656
    ObjectName|contains: lsass.exe
    AccessMask|contains: '0x1010'
  selection_sam:
    EventID: 4662
    ObjectName|contains: SAM
  condition: selection_lsass or selection_sam
level: critical
```

### 可疑网络连接

```yaml
title: 检测C2通信
logsource:
  product: windows
  service: sysmon
detection:
  selection:
    EventID: 3
    DestinationPort:
      - 4444
      - 6667
      - 8888
    Image|contains:
      - powershell.exe
      - cmd.exe
      - rundll32.exe
  condition: selection
level: high
```

---

## 分析工具

### Sigma CLI

```bash
# 转换Sigma规则
sigmac -t splunk rule.yml
sigmac -t elasticsearch rule.yml
sigmac -t sentinel rule.yml

# 验证规则
sigmac -c config.yml rule.yml
```

### 搜索工具

```bash
# Loki - IOC扫描
loki.exe -p C:\ --onlyrelevant

# Hayabusa - 事件日志分析
hayabusa.exe -d logs/ -r rules/
```

---

## 报告输出

```markdown
# 威胁狩猎报告

## 概述
- 时间范围：2024-01-15
- 数据源：Windows Event Logs
- 假设：检测PowerShell滥用

## 发现
### 高危告警
1. 可疑PowerShell执行 (3次)
2. 横向移动尝试 (1次)

### 分析结论
- 发现可疑活动，需进一步调查
- 建议强化PowerShell监控

## IOC列表
| 类型 | 值 |
|------|-----|
| IP | 192.168.1.100 |
| Hash | abc123... |
| Domain | evil.com |
```

---

## 相关技能

- `security-forensics` - 安全取证
- `security-best-practices` - 安全实践
- `logging-monitoring` - 日志监控