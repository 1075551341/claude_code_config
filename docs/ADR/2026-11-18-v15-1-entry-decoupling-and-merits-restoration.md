# v15.1 入口彻底解耦与实操优点补齐

- 状态：已接受
- 日期：2026-11-18
- 决策者：用户
- 关联：`docs/ADR/2026-11-15-risk-based-independent-config.md`、`CLAUDE.md`、`docs/research/config-merits-20261115.md`

## 背景

v15.0.0 已取消跨工具链接与同步器，但 `C:\Users\DELL\.claude` 内仍保留 `CLAUDE.md` 导入 `@AGENTS.md` 的双文件结构，且 `AGENTS.md` 正文夹带本端路径描述；同时在大幅精简中，部分关键实操优点（动态升档与 2 次止损、非目标、正反向双验、三态证据、`STATE.md` 失败尝试、P0–P3 调试分诊、L1–L3 调研分档与清晰底线）被压平。此外需要明确融入“最小改动 vs 共性全局修正、不做不必要兜底”以及“动机/目标不清停下讨论、路径非最短建议更好方案”的要求。

## 备选方案

1. **方案 1A（采纳）：Claude 全局收口为单一自包含 `CLAUDE.md`**
   - 删除全局 `.claude/AGENTS.md`，将通用方法与本端运行提示合并写入 `CLAUDE.md`（约 100 行，远低于建议上限）；其余工具各自独立维护 `AGENTS.md`。
   - 优点：零双入口歧义，彻底断开跨端共享真源错觉。
   - 代价：修改通用方法时需独立同步到各端副本（符合 2026-11-15 独立维护决策）。
2. **方案 1B（未采用）：保留 `CLAUDE.md` `@AGENTS.md` 拆分但去路径绑定**
   - 优点：与项目级多工具模板一致。
   - 缺点：在用户全局 `.claude/` 目录继续存在 `AGENTS.md` 仍易被误解为跨端共享入口。

## 决策

1. **入口与工具独立**：Claude 全局仅用 `CLAUDE.md`；删除 `.claude/AGENTS.md`、遗留 `.trae/` 与 `skills/_bm_skillid_migration.json`。`scripts/check-config.py` 强制校验全局 `AGENTS.md` 不存在且 `CLAUDE.md` 不含 `@AGENTS.md`。项目级模板 `templates/project-init/` 保留项目内按需复用，禁止指向用户全局目录。
2. **原则融入与优点补齐**：将“审慎澄清与最短路径建议”、“局部最小改动 vs 共性全局修改、反静默兜底”、动态升档与 ≤2 次止损、消费者清零走查、正反向验证与三态证据、`STATE.md` 失败尝试、P0–P3 与 L1–L3 分档及 Caveman 清晰底线自然融入 `CLAUDE.md`、8 技能、4 角色、8 命令与 `STATE.md`。
3. **不恢复已淘汰机制**：不恢复 `workflow.yaml` 渲染引擎、Stop 强制阻断门或跨工具同步器。

## 后果

- 正面：Claude 本端结构更单一清晰；保留精简高内聚骨架的同时补回防空转、防漏改与诚实证据边界。
- 回滚：可从 `backups/refactor-20261118-v15.1/` 按需还原修改前快照。
