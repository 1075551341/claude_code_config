# shanraisshan/claude-code-best-practice

> 层: 技能/实践 | 置信度: 高 | 刷新: 2026-06-24 | 来源: GitHub + WebSearch 双源

## 核心价值

- lazy-load rules：按需 Read，非 alwaysApply 全量
- `<important if>` 条件触发语法
- 规则分层：总纲 → 按需 supplement
- Token 高效规则加载模式

## 证据

- [GitHub shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice)

## 本地映射

| MANIFEST concern | 路径 |
|------------------|------|
| best_practice | `rules/BESTPRACTICE.md` |
| 加载策略 | `SPEC.md` L0–L4；sync L0 only |

## 吸收决策

**采纳** — lazy rules + L0 四入口 sync 策略对齐。

## 互博检查

- vs alwaysApply 膨胀：L0 四 + P0 五技能门控

## v10.1 增量

- 与 v10.1 P0 五技能常驻策略一致

## v10.3 增量

- Delta 刷新：51.3K+ Stars（2026-06）
- 决策不变：lazy rules + L0 四入口 sync 策略对齐
