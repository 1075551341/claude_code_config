# .claude v10.1 实施任务

> 基于 design-v10.1.md + spec-v10.1.md

---

## Phase A — 文档 ✅

| ID | 任务 | 验证 |
|----|------|------|
| A01 | Firecrawl+Exa 双源刷新 | Exa 确认 superpowers/OpenSpec/GSD 版本 |
| A02 | 27 repo 卡片 | `docs/research/repos/*.md` 齐全 |
| A03 | SSOT v10.1 | 30-repo-deep-research + README + REPO_ANALYSIS |
| A04 | spec 草案 | design/spec/tasks-v10.1.md |

---

## Phase B — 配置

| ID | 任务 | 验证 |
|----|------|------|
| B01 | MANIFEST v10.1 + GSD 1.4.1 | `version: "10.1"` |
| B02 | CLAUDE.md + SPEC.md v10.1 | ≤250 行；探索链无 UA |
| B03 | skills-INDEX + OPENSPEC 引用 | 卡片链接可选 |
| B04 | validate_config 16/16 | `python scripts/validate_config.py` |
| B05 | sync.ps1 -Force | Cursor L0 四文件 |
| B06 | Grep 残留 | UA 活跃路由=0；compound-engineering 启用=0 |

---

## 验收清单

- [x] 27 repo 卡片
- [x] MANIFEST 10.1
- [x] validate 16/16
- [x] sync 完成
