# .claude 配置集成规格 v10.0

> 状态: **已完成** 2026-06-16 | 验收: [tasks-v10.md](tasks-v10.md)

---

## FR-10.01 MANIFEST v10

- `version: "10.0"`
- `ecc_integration: cherry_pick`
- `module_resolver.conflicts` 声明 deer-flow/workstream、RTK/caveman 等
- `openspec_config.profile: core` + `cli_required: true`
- `superpowers.override: local_post_load`
- `thresholds`: cursor [70,90], gsd_logical_breakpoint 70
- `codegraph.policy: mandate_init`
- `ruflo.status: reference_only`

## FR-10.02 阈值文档

- `rules/CORE.md` + `rules/CONTEXT.md` + `CLAUDE.md` 双轨一致

## FR-10.03 OpenSpec CLI

- 全局 `npm i -g @fission-ai/openspec@latest`（Node >=20.19）
- `openspec init --tools cursor` 于 `~/.claude`
- core profile 含 propose/explore/apply/sync/archive
- `rules/OPENSPEC.md` 含 verify/bulk-archive/onboard 本地路由

## FR-10.04 codegraph mandate

- `validate_config.py` V16：检测 `~/.claude/.codegraph/` 索引就绪
- `docs/RUNTIME_PLAYBOOK.md` 含 `codegraph init` 步骤

## FR-10.05 文档 SSOT

- `docs/research/30-repo-deep-research-v10.md`
- `docs/REPO_ANALYSIS.md` v2.0 无过时缺口

## FR-10.06 同步

- `sync.ps1 -Force` 后 Cursor `~/.cursor/rules/` 仅 L0 四入口

## 非目标

- 不安装 ECC 全量插件
- 不集成 ruflo
- 不扩充 catalog 到全局 skills/agents
