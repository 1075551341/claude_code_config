---
name: openspec-rules
description: OpenSpec delta-spec 规范。触发：openspec、/opsx:、proposal、spec 变更。
triggers: [openspec, opsx, proposal, spec变更]
layer: supplement
source: local
loading_tier: L3
disable-model-invocation: true
paths:
  - "**/openspec/**"
---

# OpenSpec 使用规范

> 来源 Fission-AI/OpenSpec v1.4.1 | 归属 `MANIFEST.yaml` concern `change_spec`

## 三处表面职责（v10.6.0 边界声明）

| 表面 | 位置 | 职责 |
|------|------|------|
| 规则 SSOT（本文件） | `skills/openspec-rules/SKILL.md` | 规范唯一权威：轨道选择、门控、禁止项 |
| Claude Code 入口 | `commands/propose|apply|archive|sync.md` | Claude Code 斜杠命令（`/propose` 等） |
| Cursor 入口 | `.cursor/commands/opsx-*.md` + `.cursor/skills/openspec-*` | Cursor 斜杠命令（`/opsx:*`）+ 技能 |

> 三者为同一流程的不同编辑器入口，语义以本文件为准；`~/.claude/.cursor/` 属 OpenSpec 集成本地资产，**不在 sync.ps1 同步范围**（sync 仅 L0 入口 + rules/skills/agents）。

## 核心概念

- **delta specs**：只描述变更，不重写全量 spec（brownfield 首选）
- **四大制品**：`proposal.md` + `specs/` + `design.md` + `tasks.md`
- **三轨互斥**：OpenSpec / GSD `.planning/` / 轻量 `spec/<project>/` 不可同功能混用

## 命令链

| 命令 | 作用 |
|------|------|
| `/opsx:propose <idea>` | 创建 `openspec/changes/<id>/` |
| `/opsx:continue` | 单步创建下一制品（依赖链自动判断） |
| `/opsx:ff` | 快进创建全部制品 |
| `/opsx:apply` | 按 `tasks.md` 实现 |
| `/opsx:verify` | 验收实现与制品一致 |
| `/opsx:sync` | 将 delta specs 同步到主 spec |
| `/opsx:archive` | 归档到 `archive/` |
| `/opsx:bulk-archive` | 批量归档（检测冲突） |
| `/opsx:onboard` | CLI 引导；Cursor 用 `skills/onboarding-guide` |

## 触发条件

| 场景 | 轨道 |
|------|------|
| 新功能 ≥3 文件变更 | OpenSpec |
| 小修复 <3 文件 | 轻量 `spec/<project>/` |
| 多阶段大功能 | GSD + workstreams |
| 新人引导 | skills/onboarding-guide |

## CLI 安装（v1.4.1 core profile，含 sync）

```bash
npm install -g @fission-ai/openspec@latest   # 需 Node >=20.19
openspec init --tools cursor --force         # 项目内生成 .cursor/skills + openspec/
openspec update                              # 刷新 agent skills
```

> v1.4.1 仅 `core` preset；`sync` 已默认包含。`verify`/`onboard` 见本地 commands + `skills/onboarding-guide`。

## 门控

- 禁止跳过 `proposal.md` 直接写 `tasks.md`
- `apply` 前须经用户确认 `design.md`（brainstorming HARD-GATE）
- `archive` 前 `verification-before-completion` 通过

## 禁止

- 同功能在 `.planning/phases/` 与 `openspec/changes/` 双写
- apply 时静默缩小 scope（须更新 spec）
