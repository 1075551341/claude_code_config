# affaan-m/ECC v2.0.0-rc.1

> 层: L1 治理 | 置信度: 高 | 刷新: 2026-06-16

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
