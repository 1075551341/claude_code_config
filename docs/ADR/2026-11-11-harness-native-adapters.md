# 跨工具薄原生适配器

> 已被 2026-11-15 的风险分级与工具独立副本决策替代；正文保留当时设计，不作为当前运行政策。

- 状态：已接受
- 日期：2026-11-11
- 决策者：用户 + 主会话
- 关联：`AGENTS.md`、`templates/harness-adapter.md`、`docs/ADR/2026-11-11-config-v14-refactor.md`

## 背景

v14 删除了编辑器同步引擎，要求其它工具直接读 `AGENTS.md`。随后出现的「内核 v2」入口把 R1-R21 整表复制进 Cursor / Qoder / DSH / OpenChamber / Trae CN，与 `rules/CORE.md` 双源；Trae 国际版仍是四行指针；Qoder / DSH 不会自动发现 `~/.claude/skills`。结果是：会漂移、技能不可用、与 marketplace 工作流插件互博。

## 决策

1. **真源不变**：工作流、完成门、铁律、技能、子代理正文只在 `~/.claude`。
2. **薄入口**：各端只写原生加载点（优先级、真源指针、发现方式、本工具差异）。禁止复制铁律表与完成门展开。Cursor Customize → Rules 的 User 列表只展示插件规则，不列出 `~/.cursor/rules`；全局可见入口放在本地插件 `~/.cursor/plugins/local/harness-adapter/`。
3. **技能发现**：能自动发现则按技能名逐项接线（Windows junction 到 `skills/<name>`，根目录保持为真实目录，避免编辑器元数据写回真源）。Cursor 官方已扫 `~/.claude/skills`，禁止再接到 `~/.cursor/skills`。Trae 无用户级技能目录，用 Read 指针 + 技能名索引。禁止整目录 junction 到 `skills/`。
4. **子代理不拷贝**：派发时 Read `~/.claude/agents/*.md`。斜杠命令不另建目录。
5. **不恢复同步引擎**：不写 `scripts/sync*.ps1`、不恢复 Guard、不引入场景路由 YAML。新增 `scripts/check-adapters.py` 只校验外部入口与接线。
6. **关掉重叠工作流**：Qoder 关闭 ECC / better-harness / caveman 及同类审查/简化插件；工具型（context7 / firecrawl 等）保留。Cursor 官方 `skills-cursor` 不动；个人 store 中与真源同名或已裁技能隔离到 `_archive/`。

## 后果

- 正面：各端能加载同一套约定与技能；改铁律不必改 N 份入口。
- 负面：Windows 上需维护 14 条 per-skill junction；某端升级加载路径时要改薄入口与自检表。
- 回滚：删 junction、还原入口备份；真源无需回滚。

## 明确不做

不恢复已删除的同步脚本与机械完成门；不绑定模型；不把 MCP 名单写入各端；不改项目级 `AGENTS.md`。
