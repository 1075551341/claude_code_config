# affaan-m/ECC v2.0.0

> 层: L1 治理 | 置信度: 高 | 刷新: 2026-06-19 | 来源: GitHub Releases + Discussion #2213 双源

## v10.5 delta (2026-07-17)

- **最新元数据**：230,370 stars；GitHub Release **v2.0.0**；`pushed_at` 2026-07-14T01:31:12Z。
- **自 2026-06-29 的变化**：无重大漂移——最新 release 仍为 v2.0.0，只有持续仓库维护信号。
- **本地吸收**：不变——继续 cherry-pick MANIFEST/hook 概念，禁止安装全量 ECC 以避免 duplicate hooks。
- **双源**：GitHub API（stars/release/push）+ 仓库 README/既有 Release 与 Discussion 研究记录。


## v10.5.1 delta (2026-07-17)
- **最新元数据**：230,376★；Release **v2.0.0**；`pushed_at` 2026-07-14T01:31:12Z。
- **漂移要点**：仍定位 agent harness OS（skills/instincts/memory/security/research-first）。
- **本地吸收 / 缺口**：**cherry_pick** 不变；已吸收模块冲突声明 + hook 分级模式。
- **不吸收**：全量 ECC 插件安装。
- **双源**：GitHub API + 既有决策交叉。
## 核心价值

- Module Resolver → Target Adapter → Operation Planner → Install-State
- harness-first 架构；ecc-universal npm v1.10
- duplicate hooks 警告机制
- GateGuard 概念；hook_profile 分级（minimal/standard/strict）
- MANIFEST 防互博 module resolver 模式

## 证据

- [GitHub affaan-m/ECC](https://github.com/affaan-m/ECC) v2.0 README
- npm `ecc-universal` v1.10

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| ecc_integration | `MANIFEST.yaml` → `cherry_pick` |
| module_resolver | `MANIFEST.yaml` → `conflicts`, `hook_profile` |
| multi_agent | `agents/agentic-orchestrator.md` |
| hooks | `hooks/README.md` → `LOCAL_HOOK_PROFILE` |

## 吸收决策

**cherry-pick** — 吸收 MANIFEST/hook 概念；**不安装** ECC 全量插件（避免 duplicate hooks）。

## 互博检查

- vs 本地 Guard hooks：ECC 插件会 duplicate → 禁止安装
- install-state/doctor：访谈拒绝，MANIFEST-only

## v10.1 增量

- v2.0 仍为 rc；跟踪正式版但不阻塞 v10.1
- cherry-pick 策略访谈二次确认

## v10.2.1 增量（双源刷新 2026-06-19）

- **v2.0.0 stable 已发布**（2026-06-10，Discussion #2213）：跨 harness OS（CC/Codex/OpenCode/Cursor/Gemini/Zed）
- ⚠️ **Node 21+ plugin hook 静默失效**（rc.1 缺陷，stable 已修）→ 本地 cherry-pick 不装插件，不受影响
- cherry-pick 策略保持；`hook_profile` 三档为 MANIFEST 声明（落地在 v10.3 backlog）
