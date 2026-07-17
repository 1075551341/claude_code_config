# colbymchenry/codegraph v1.0.1

> 层: L3 洞察 | 置信度: 高 | 刷新: 2026-06-19 | 来源: GitHub Releases + npm + 官网 双源交叉

## v10.5 delta (2026-07-17)

- **最新元数据**：60,419 stars；GitHub Release **v1.4.1**；`pushed_at` 2026-07-17T00:09:01Z。
- **自 2026-06-29 的变化**：从 v1.0.1 升至 v1.4.1，版本漂移显著；本轮元数据核验未产生足以替换 R17 日常符号探索/`blast-radius` 定位的反证。
- **本地吸收**：不变——codegraph 继续为 R17 常驻主位；cbm 仍只承担架构、ADR、跨服务与 diff 风险的 L4 按需职责。
- **双源**：GitHub API（stars/release/push）+ 仓库 README/既有 npm 与官网研究记录。


## v10.5.1 delta (2026-07-17)
- **最新元数据**：60,432★；Release **v1.4.1**（2026-07-10）；`pushed_at` 2026-07-17T00:09:01Z。
- **漂移要点**：MCP update-check 通知；NL 查询词不再劫持符号排序；PHP DI 属性调用解析；增量 sync 跨文件边修复；Windows `upgrade`/`uninstall` 修复。
- **本地吸收 / 缺口**：R17 mandate + `.mcp.json` 常驻；钉扎文档跟踪 1.4.1 **不自动升**。已有：explore/impact env。
- **不吸收**：自动 `codegraph upgrade`（需人工评估）。
- **双源**：GitHub API + Firecrawl（v1.4.1 release）。
## 核心价值

- 本地优先（100% local）预索引代码知识图谱 MCP；Tree-sitter 20+ 语言增量解析
- 官方实测指标（7 仓库 / Opus 4.8 / 2026-06-02 重验，4 次中位）：**~16% 更便宜 · ~47% 更少 token · ~58% 更少工具调用 · ~22% 更快**；官网 headline 仅强调「16% cheaper · 58% fewer tool calls」
- 自带运行时（无需 Node）；`codegraph upgrade` 原地升级；MCP watchdog 自愈
- R17 探索首选（先于 Grep/Read）；mandate init 策略

## 版本与变更

- v1.0.1 (2026-06-13)：`codegraph daemon` 交互管理器、MCP 进程 watchdog 自愈（`CODEGRAPH_WATCHDOG_TIMEOUT_MS` / `CODEGRAPH_NO_WATCHDOG=1`）、`serve --mcp` 人工运行提示
- v1.0.0 (2026-06-12)：配置值脱敏（breaking）、symlink 安全、**MCP 默认工具收敛为 4 个**
- Unreleased：constant-reader impact 分析（常量消费者纳入影响面，`CODEGRAPH_VALUE_REFS=0` 关闭）

## ⚠️ F1 — MCP 默认仅暴露 4 工具（本地集成关键）

v1.0.0 起 MCP 默认工具列表收敛为 **4 个**：`codegraph_explore` · `codegraph_node` · `codegraph_search` · `codegraph_callers`。

其余 4 个（`codegraph_callees` · **`codegraph_impact`** · `codegraph_files` · `codegraph_status`）**默认不再向 agent 暴露**，需 `CODEGRAPH_MCP_TOOLS` 显式启用（CLI/库 API 不变）。

官方理由：impact/callees 信息已内联到 `codegraph_explore` 的 blast-radius 段与 `codegraph_node` 的 dependents 注记中；精简工具列表每会话省 token。

**对本地的影响**：`rules/CORE.md` 变更彻底性保障强制 `codegraph_impact`，但默认不可用 → 铁律落空。
**纠偏（F1 动作）**：影响分析优先用 `codegraph_explore` 的 blast-radius；需精确 impact 时文档化 `CODEGRAPH_MCP_TOOLS=codegraph_impact`（同步 `.mcp.json`）。

## 本地集成状态

| MANIFEST concern | 路径 | 状态 |
|------------------|------|------|
| codegraph | `MANIFEST.yaml` → `policy: mandate_init` | ✅ |
| R17 探索优先 | `rules/CORE.md`, `rules/CURSOR-EDITOR.mdc` | ✅ |
| MCP | `.mcp.json` user-codegraph | ✅ |
| playbook | `docs/RUNTIME_PLAYBOOK.md` | ✅ |
| 默认工具集 (F1) | CORE 变更彻底性 / R17 反模式 | 🟡 需纠偏（impact 默认不可用） |
| 指标文案 (F2) | 全库 `~47% token` | 🟢 47% **是官方数字**（current build），仅需补全为四元组 |

## 去重决策

- vs UA：codegraph 主（符号级低 token）；UA L3 按需（`/understand-*` 拓扑/业务流）
- vs Grep：codegraph 首选，Grep fallback
- vs codebase-memory-mcp（v10.4）：**双引擎互补** — codegraph=R17 日常符号/blast-radius；cbm=架构全景/ADR/`detect_changes`/跨服务（L4 按需）。日常探索不重复调用 cbm `search_graph`

## 吸收优先级

| 优先级 | 内容 |
|--------|------|
| P0 | 全局 `~/.claude` index + 业务项目 mandate init |
| P0 | F1 纠偏：impact 默认不可用 → explore blast-radius / env |
| P0 | F2 补全：~47% token 保留（官方），补 ~16% 成本 / ~58% 工具调用 / ~22% 更快 |

## 证据

- [GitHub Releases v1.0.1/v1.0.0](https://github.com/colbymchenry/codegraph/releases)（2026-06-19 核验）
- [npm @colbymchenry/codegraph 1.0.1](https://www.npmjs.com/package/@colbymchenry/codegraph)
- [官网 colbymchenry.github.io/codegraph](https://colbymchenry.github.io/codegraph/)

## v10.2.1 增量

- **F1**（确认）：MCP 默认 4 工具（explore/node/search/callers），`codegraph_impact` 需 `CODEGRAPH_MCP_TOOLS` env 启用（本地铁律纠偏）
- **F2**（修订）：**~47% token 系官方数字**（README L122 current-build 均值），原计划「47% 失实」premise 不成立；动作改为补全官方四元组 ~16%成本/~47%token/~58%工具调用/~22%更快
- v1.0.1 daemon + watchdog 自愈补充
- 证据：[README L122/L536 双源核验](https://raw.githubusercontent.com/colbymchenry/codegraph/main/README.md)（2026-06-19 fetch）

## v10.4 增量

- 与 [deusdata-codebase-memory-mcp](deusdata-codebase-memory-mcp.md) 建立双引擎边界：codegraph 保持 R17 常驻主位；cbm 不替代日常 `codegraph_explore`
- 变更影响：`codegraph_impact` / explore blast-radius 仍为默认；cbm `detect_changes` 作 L4 备选（git diff→风险分类场景）
