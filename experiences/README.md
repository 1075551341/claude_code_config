# Experiences 经验库

> 持续学习系统，置信度 >0.7 的模式固化为 skill/rule
>
> 整合自：
>
> - [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - Instinct系统
> - [zilliztech/claude-context](https://github.com/zilliztech/claude-context) - 上下文管理
> - [obra/superpowers](https://github.com/obra/superpowers) - 工作流模式

---

## 目录结构

```
experiences/
├── README.md              # 本文件
└── patterns/              # 已验证模式
    ├── 2026-04-15-context-management-pattern.md
    ├── 2026-04-15-workflow-patterns.md
    └── 2026-04-15-security-patterns.md
```

---

## 设计原则（来自 everything-claude-code Instinct系统）

### 1. 原子本能

每个经验是独立条目，而非大文件。

### 2. 置信度评估

| 分数    | 含义                   |
| ------- | ---------------------- |
| 0.9+    | 多次验证，几乎总是有效 |
| 0.7-0.9 | 多次出现，通常有效     |
| 0.5-0.7 | 偶尔出现，需更多验证   |
| <0.5    | 不稳定，存入 rejected  |

### 3. 模式提取流程

```
1. 识别：从任务/hooks/agents中发现模式
2. 评估：置信度 >0.7 → 提取
3. 固化：存入 patterns/ + 创建 skill/rule
4. 验证：在后续任务中验证
```

---

## 标准经验文件格式

```markdown
---
name: experience-name
date: 2026-04-15
confidence: 0.85
source: [task|hook|agent]
tags: [tag1, tag2]
---

# 经验标题

## 背景

[什么场景]

## 模式

[发现什么]

## 验证

[如何验证]

## 提取决策

- 置信度: 0.85
- 提取为: skill/rule
- 原因: [why]
```

---

## 已验证模式

### 上下文管理（来自 claude-context）

| 模式                             | 置信度 | 来源                   |
| -------------------------------- | ------ | ---------------------- |
| `merkle-dag-incremental-sync`    | 0.9    | Merkle DAG增量同步     |
| `ast-aware-chunking`             | 0.85   | AST感知分块            |
| `subagent-precise-context`       | 0.95   | 子代理精确上下文构造   |
| `sessionstart-context-injection` | 0.9    | SessionStart上下文注入 |

### 工作流（来自 superpowers/get-shit-done/deer-flow）

| 模式                     | 置信度 | 来源             |
| ------------------------ | ------ | ---------------- |
| `iron-law-enforcement`   | 0.95   | Iron Law强制执行 |
| `phased-implementation`  | 0.85   | Phase工作流      |
| `tdd-red-green-refactor` | 0.9    | TDD循环          |
| `multi-role-pr-review`   | 0.85   | PR多角色审查     |

### 安全（来自 owasp/awesome-claude-code）

| 模式                        | 置信度 | 来源             |
| --------------------------- | ------ | ---------------- |
| `owasp-top10-protection`    | 0.95   | OWASP Top 10防护 |
| `secret-detection-patterns` | 0.95   | 密钥检测模式     |

---

## 来源

- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) - Instinct系统
- [zilliztech/claude-context](https://github.com/zilliztech/claude-context) - 上下文管理
- [obra/superpowers](https://github.com/obra/superpowers) - 工作流模式
- [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) - Phase工作流
- [bytedance/deer-flow](https://github.com/bytedance/deer-flow) - 任务规划

---

## 统计

| 分类       | 数量   |
| ---------- | ------ |
| 上下文管理 | 4      |
| 工作流     | 4      |
| 安全       | 2      |
| **总计**   | **10** |

---

## Instinct 系统命令（来自 everything-claude-code）

| 命令 | 作用 |
|------|------|
| `/instinct-status` | 查看已学习的 Instincts 及其置信度评分 |
| `/instinct-import <file>` | 导入外部 Instincts |
| `/instinct-export` | 导出当前 Instincts 用于分享或备份 |
| `/evolve` | 将相关的 Instincts 聚类聚合成 Skills |
| `/prune` | 删除超过 30 天 TTL 的过期 pending instincts |
| `/learn-eval` | 从当前会话中提取模式，先评估再保存 |

## 添加新经验

1. 在 `patterns/` 目录创建新文件
2. 使用标准格式填充内容
3. 设置合适的置信度
4. 添加相关tags
