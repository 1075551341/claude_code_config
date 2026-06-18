# .claude v10 实施任务

> 基于 design-v10.md + spec-v10.md | **状态: 已完成** 2026-06-16

---

## P0 — 配置核心 ✅

| ID | 任务 | 验证 |
|----|------|------|
| T01 | MANIFEST v10.0 | `version: "10.0"` |
| T02 | CLAUDE.md v10 | ≤250 行；GSD 断点；codegraph |
| T03 | CORE + CONTEXT 阈值双轨 | 逻辑断点 |
| T04 | SPEC.md v10 | v10 变更摘要 |
| T05 | rules/OPENSPEC.md **core** + 本地 commands | `opsx:sync` |
| T06 | openspec CLI 1.4.1 + init | `openspec --version` |
| T07 | validate_config V16 | 16/16 PASS |
| T08 | RUNTIME_PLAYBOOK codegraph init | mandate |
| T09 | hooks/README LOCAL_HOOK_PROFILE | ECC cherry-pick |
| T10 | sync + validate | sync.ps1 -Force |

---

## P1 — 短期 ✅

| 项 | 状态 |
|----|------|
| Firecrawl MCP + 包装脚本 | ✅ |
| claude-mem Endless Mode 评估 | ✅ ADR 默认关 |
| OpenSpec custom schemas | 按需（未触发） |

---

## P2 — 持续 / 刻意不实现 ✅

| 项 | 状态 |
|----|------|
| GSD forensics/resume | ✅ gsd-gaps-v10.md 仅文档 |
| ECC install-state/doctor | ✅ 访谈拒绝 |
| Git auto commit/stash 禁令 | ✅ Guard 1.1.6 |
| UA disabled | ✅ ADR |
| open-gsd / gstack 品味 | 上游跟踪（非阻塞） |

---

## 验收清单

- [x] MANIFEST v10.0
- [x] 调研仅 v10（v7/v8 → archive/）
- [x] 文档 SSOT 链同步
- [x] openspec CLI core + init
- [x] validate_config 16 checks PASS
- [x] 无 ECC 插件
- [x] Firecrawl L3 双源
- [x] sync.ps1 Cursor L0
