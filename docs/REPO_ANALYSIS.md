# 仓库全量分析报告 v2.1

> 版本 v2.1 | 日期: 2026-06-16 | 分析范围: 27 仓库 | 运行配置: **v10.1**
> 调研 SSOT: [docs/research/30-repo-deep-research-v10.md](research/30-repo-deep-research-v10.md) | 卡片: [repos/](research/repos/)

---

## v10.1 实现状态

| 能力 | 状态 |
|------|------|
| 五柱 + MANIFEST v10.1 | ✅ |
| 27 repo 卡片 | ✅ [repos/](research/repos/) |
| 阈值双轨 + GSD 70% 断点 | ✅ |
| OpenSpec CLI core + init + 本地 commands | ✅ |
| codegraph V16 + global index | ✅ |
| ECC cherry_pick | ✅ |
| 文档 SSOT 链 v10.1 | ✅ |
| Firecrawl L3 双源 | ✅ `firecrawl-mcp.ps1` |
| Git 禁令（无 auto commit/stash） | ✅ Guard + pre-bash-guard |
| UA | ✅ disabled（ADR） |
| GSD forensics | ✅ 仅文档 [gsd-gaps-v10.md](research/gsd-gaps-v10.md) |
| claude-mem Endless | ✅ 评估→默认关闭（ADR） |
| Node OpenSpec | ✅ Volta 20.20.2 |

---

## 一、五柱评估

### 1. superpowers ⭐⭐⭐⭐⭐

**仓库**: `obra/superpowers` v5.1.0 | 插件已装

| 核心价值 | SDD+TDD、HARD-GATE、两阶段审查、原子任务 |
| 本地 | 38 skills；插件 + 后加载本地优先 |
| v10 | P0 路由集 5；保持 |

### 2. GSD (open-gsd/gsd-core) ⭐⭐⭐⭐⭐

| 核心价值 | 制品优先、DAG、Trust-But-Verify、workstreams |
| 版本 | **v1.4.5**（open-gsd；v1.5.0-rc 仅跟踪） |
| 本地 | workstream-management、adr-management、context-engineering ✅ |
| v10.1 | 70% 逻辑断点；forensics/resume 不实现（见 gsd-gaps-v10） |

### 3. OpenSpec ⭐⭐⭐⭐

**仓库**: `Fission-AI/OpenSpec` v1.4.1

| 核心价值 | OPSX、delta specs、brownfield |
| 本地 | openspec/changes/ 三轨；onboarding-guide |
| v10 | **core** CLI（无 expanded preset）；verify 走本地 commands |

### 4. gstack ⭐⭐⭐⭐⭐

| 核心价值 | 25 agents、审查路由、品味记忆、ML 防御 |
| 本地 | dx-reviewer、taste-memory、land-and-deploy ✅ |
| v10 | compound-engineering 禁用 |

### 5. claude-mem ⭐⭐⭐⭐⭐

| 核心价值 | 渐进式披露、Chroma、平台隔离 |
| 本地 | 插件 13.6.1；R18；claude-mem-maintenance |
| v10 | Endless Mode 评估后默认关 |

---

## 二、横切层

| 层 | 仓库 | 本地 | v10 |
|----|------|------|-----|
| L1 | ECC (cherry-pick) | MANIFEST module_resolver | ✅ 无插件 |
| L1 | deer-flow 2.0 | claude-to-deerflow L3 | 可选 |
| L2 | RTK + caveman | hooks + skills | ✅ |
| L3 | codegraph | MCP + mandate | ✅ |
| L3 | Understand-Anything | **disabled** | codegraph-only |
| 参考 | ruflo | 文档 only | reference_only |

---

## 三、辅助工具

| 仓库 | 角色 | 本地 |
|------|------|------|
| task-master | PRD L4 | 可选 MCP core |
| karpathy-skills | 四原则 | karpathy-guidelines ✅ |
| Firecrawl + Exa | L2/L3 调研 | ✅ MCP 已验收 |

---

## 四、冗余/互博（已解决）

1. codegraph vs UA — UA disabled
2. deer-flow vs workstream — MANIFEST excludes
3. gstack vs compound-engineering — 插件禁用
4. RTK vs caveman — 输入 vs 输出

---

## 五、SSOT 链

```
docs/research/repos/*.md  （27 张卡片）
        ↓
docs/research/30-repo-deep-research-v10.md  （SSOT v10.1）
        ↓
docs/REPO_ANALYSIS.md  （本文件）
        ↓
MANIFEST.yaml → SPEC.md → CLAUDE.md
```

历史调研：`docs/research/archive/`（只读归档）
