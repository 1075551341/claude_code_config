# 27 仓库调研整合报告 v6.0

> 日期: 2026-06-05 | 基于全量重新 WebFetch | 关联设计: design-v6.md

---

## 调研方法

并行 WebFetch 27 个 GitHub 仓库首页 README，提取版本号、核心功能、架构特点。对比 v5.2 中的 28 仓库列表，去重 P3 安全补强仓库（非独立仓库）。

---

## 关键发现（v5.2 → v6.0 变更）

| # | 仓库 | v5.2 版本 | v6.0 最新 | 关键变化 |
|---|------|-----------|-----------|----------|
| 1 | obra/superpowers | 5.1.0 | 5.1.0 | 不变 |
| 2 | open-gsd/gsd-core | gsd-build/get-shit-done | **v1.42.3** | 仓库已迁移！ |
| 3 | Fission-AI/OpenSpec | 1.x | **v1.4.1** (Jun 3) | 25+ AI工具支持 |
| 4 | garrytan/gstack | 0.x | **v0.19** | iOS专用 + ML注入防御 + 跨模型审查 + 品味记忆 |
| 5 | thedotmack/claude-mem | 13.3.0 | **v13.4.0** (May 29) | 小版本升级 |
| 6 | affaan-m/ECC | 1.9.0 | **v2.0.0-rc.1** | 63 agents + 251 skills + Rust控制平面 + 桌面仪表盘 |
| 7 | bytedance/deer-flow | 1.x | **2.0** | LangGraph ground-up rewrite |
| 8 | rtk-ai/rtk | 0.x | **v0.42.1** (Jun 3) | 100+命令, 198 releases |
| 9 | JuliusBrussee/caveman | 1.x | **v1.8.2** (May 12) | lite/full/ultra/wenyan 四模式 |
| 10 | colbymchenry/codegraph | 0.x | **v0.9.9** (Jun 2) | 7仓库基准: 47% token减少, 58%调用减少 |
| 11 | Lum1104/Understand-Anything | 2.7.5 | **v2.7.3** | 5 Agent管线 |
| 12 | anthropics/skills | - | 147k stars | 三平台(Code/API/Web), formal SKILL.md spec |
| 13 | shanraisshan/best-practice | v2.1.162 | v2.1.162 | paths: glob lazy-load + `<important if>` |
| 14 | forrestchang/karpathy | - | 168k stars | 28 commits, no release |
| 15 | mattpocock/skills | - | 118k stars | 18 skills, no release |
| 16 | 2025Emma/vibe-coding-cn | - | 21.5k stars | 道/法/术/器 + α/Ω 元技能 |
| 17 | eyaltoledano/task-master | - | **v0.43.1** (Mar 31) | MCP协议 + 3级工具裁剪 |
| 18 | nextlevelbuilder/ui-ux-pro-max | - | v2.0 | 67风格 + 161色板 + 99 UX指南 + 设计系统生成器 |
| 19 | VoltAgent/awesome-design-md | - | 87.5k stars | 72 DESIGN.md文件, 9节结构 |
| 20 | github/github-mcp-server | - | 30.4k stars | 16 toolsets + lockdown模式 |
| 21 | anthropics/claude-code-action | - | **v1.0** (Aug 2025) | 4云后端 + 智能模式检测 |
| 22 | zilliztech/claude-context | - | 210 commits | ~40% token减少, BM25+稠密混合搜索 |
| 23 | ComposioHQ/awesome-claude-skills | - | 63.3k stars | 1000+ skills, 渐进式加载 |
| 24 | hesreallyhim/awesome-claude-code | - | 45.7k stars | **重构中** |
| 25 | x1xhlol/system-prompts | - | May 10 2026 | ZeroLeaks 注入防护服务 |
| 26 | Chalarangelo/30-seconds-of-code | - | **v14.0.0** (May 2025) | JavaScript 65.4% |
| 27 | ruvnet/ruflo | - | **v3.10.34** (Jun 2) | HNSW向量记忆 + 蜂群拓扑 + 1524 releases |

---

## 架构公式（v6.0）

```
CLAUDE = 五柱(纵向) × 五阶段(流程) × 三横切(基础设施)

五柱: Superpowers | GSD(open-gsd/gsd-core) | OpenSpec | gstack | claude-mem
五阶段: ①规划 → ②规格 → ③执行 → ④验证 → ⑤学习
三横切:
  L1 治理 — ECC(防互博+hook分级) + deer-flow 2.0(LangGraph编排)
  L2 优化 — RTK(shell) + caveman(输出) + 三级阈值(上下文)
  L3 洞察 — codegraph(47%token减少) + Understand-Anything(知识图) + Firecrawl/Exa(搜索)
```

## 规模约束

| 类型 | v5.2 | v6.0 | 变化 |
|------|------|------|------|
| skills | 28 | 28 | 不变 |
| agents | 20 | 22 | +2 (codex-reviewer, ios-specialist) |
| rules | 10 | 10 | 不变 |
| hooks | 15 | 16 | +1 (pre-loop-guard) |
| CLAUDE.md | ~260行 | 202行 | -58行 (精炼) |
| 仓库覆盖 | 28(含P3) | 27(去P3) | 归并 |

## 关联文档

- 设计: `spec/claude-config-integration/design-v6.md`
- 任务: `spec/claude-config-integration/tasks-v6.md`
- 规格: `spec/claude-config-integration/spec.md`
