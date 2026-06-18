# .claude 配置集成规格 v10.1

> 状态: **已完成** | 继承: [spec-v10.md](spec-v10.md)

---

## FR-10.1.01 MANIFEST v10.1

- `version: "10.1"`
- GSD pillar `version: "1.4.1"`（open-gsd/gsd-core）
- 其余 v10 字段不变（ecc_integration、thresholds、codegraph.policy、ruflo、UA disabled）

## FR-10.1.02 文档 SSOT

- 27 张 `docs/research/repos/{slug}.md`
- `30-repo-deep-research-v10.md` 标题 v10.1 + 卡片链接
- `docs/research/README.md` 索引 repos/

## FR-10.1.03 路由文档

- `CLAUDE.md` / `SPEC.md` 引用 v10.1
- 探索链：`codegraph → Grep → Read`（不含 UA）
- P0 五技能 L1 明示

## FR-10.1.04 验收

- validate_config 16/16
- sync.ps1 -Force → Cursor L0 四入口

## 非目标

- 同 spec-v10 非目标 + 不启用 UA/Endless/ruflo/ECC 插件
