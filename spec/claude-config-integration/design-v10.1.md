# .claude 配置集成设计 v10.1

> 状态: **已完成** 2026-06-16 | 继承: [design-v10.md](design-v10.md)

---

## v10.1 增量（相对 v10.0）

| 领域 | v10.0 | v10.1 |
|------|-------|-------|
| 文档 | 单文件 SSOT | +27 张 [repos/](../../docs/research/repos/) 卡片 |
| GSD 版本 | 1.42.3 | **1.4.1**（open-gsd semver） |
| MANIFEST | 10.0 | **10.1** |
| 探索链 | codegraph → UA → Grep | codegraph → Grep（UA disabled 明示） |
| 加载 | 已述 | P0 五技能 L1 + L0 四入口（访谈锁定） |

## 设计原则（继承 v10，不变）

```
P1–P10 见 design-v10.md
P11. 文档 SSOT 链：repos/*.md → research → MANIFEST → SPEC
P12. Phase A 仅 docs；Phase B 改配置
```

## 访谈共识（15 项）

见计划文件；核心：UA disabled、ECC cherry-pick、OpenSpec core、claude-mem SSOT、sync L0 only。

## Phase B 范围

1. MANIFEST v10.1 + GSD 1.4.1
2. CLAUDE.md / SPEC.md v10.1 摘要
3. validate 16/16 + sync.ps1
4. 无新 ADR（决策与 v10 一致）

## 验证

- `validate_config.py` 16/16 PASS
- `openspec --version` ≥1.4.1
- Grep：无 UA 活跃路由、无 compound-engineering 启用
