---
description: 架构决策记录（ADR）管理
---

# /adr — 架构决策记录

> **正文在 skill/adr-management**。本命令触发该 skill。

## 子命令

| 命令 | 作用 |
|------|------|
| `/adr new <title>` | 创建 `docs/ADR/YYYY-MM-DD-<title>.md` |
| `/adr list` | 列出全部 ADR |
| `/adr search <query>` | 搜索已有决策（防重复讨论） |

## 时机

技术选型、架构变更、重大重构 — 讨论前先 `/adr search`。
