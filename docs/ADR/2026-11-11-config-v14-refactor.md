# 配置 v14 精简重构

> 已被 2026-11-15 的风险分级与工具独立副本决策替代；正文保留当时设计，不作为当前运行政策。

- 状态：已接受
- 日期：2026-11-11
- 决策者：用户 + 主会话
- 关联：`AGENTS.md`、`CLAUDE.md`、`CHANGELOG.md`

## 背景

v13.1 的金华配置存在结构性互博：

- 同一流程被 `scripts/workflow.py render` 派生到 `CLAUDE.md`、`rules/*`、`commands/*`、`agents/*`，改一处需全套重渲染。
- 并存四套计划/规格轨：brainstorming+writing-plans、`openspec/changes/`、`.planning/`、`spec/<project>/`。
- 本地 25 个 skills 与 `superpowers` 插件大量同名，靠「本地覆盖」维持。
- 审查机械门由 `stop-verification-gate.py`（37KB）+ `r20_replay.py`（40KB）+ `graph_freshness.py`（49KB）构成，小改也受机械轮次/BLOCKED 逻辑约束。
- 本仓承担 6 个编辑器的同步适配（`sync.ps1`、`sync-editors.ps1` 39KB、`principles.py`、`validate_config.py` 65KB、`check.ps1` 47KB、`templates/cursor-guard` 40+ 文件）。
- `SPEC.md` 31KB、`MANIFEST.yaml` 36KB、3 个 INDEX 与 docs 互相引用，改配置要同步 6 处。
- 残留冲突插件：`ralph-loop`（明令禁止）、`feature-dev`、`code-review`、`commit-commands`、`claude-md-management` 与本仓流程重叠。

## 调研结论

| 上游 | 吸收 | 不吸收 |
| --- | --- | --- |
| obra/superpowers | 渐进披露（description 只写何时用）；原子任务；审查成本两档 | 强制 TDD、所有小改派子代理、不可跳过的流程 |
| affaan-m/ECC | 安装/禁用分层；hook 严格度 profile | 全量插件、记忆 vault、continuous-learning |
| open-gsd/gsd-core | 行为开关化；计划适配单上下文窗口；跨会话制品 | `.planning/` 轨道、installer、强制五阶段 |
| Fission-AI/OpenSpec | delta 思路；WHEN/THEN 验收 | OpenSpec 命令/目录/CLI 绑定 |
| garrytan/gstack | reviewer persona「只找问题」；跨模型二审；三步就停 | 30+ 命令、team-mode、GBrain |
| agents.md 标准 | 中性 `AGENTS.md` 入口；只写模型推断不出的约定 | 为每个工具生成副本 |
| Claude Code 官方 | `CLAUDE.md` + `@import`；skills 用标准 `SKILL.md`；hooks 在 `settings.json`；建议 <200 行 | 模型/effort 字段、单文件承载全部正文 |

来源：

- https://github.com/obra/superpowers
- https://github.com/affaan-m/ecc
- https://github.com/open-gsd/gsd-core
- https://github.com/Fission-AI/OpenSpec
- https://github.com/garrytan/gstack
- https://agents.md/
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/hooks
- https://opencode.ai/docs/rules/
- https://docs.trae.ai/ide/rules
- https://docs.qoder.com/cli/memory

## 决策

1. **单一调度面**：`AGENTS.md` 承载工作流、完成门、审查路由、工具能力路由；`CLAUDE.md` 只做 `@AGENTS.md` + Claude 差异。删除 `workflow.yaml` 与 render 机制。
2. **保留审查门，简化机械实现**：完成 = 观察证据 + 本轮全新独立审查 PASS（两道门）；删除 Stop 硬门与七维解析，改为「有编辑且未见审查派发时提醒一次」的轻量 Stop hook。
3. **只保留轻量规格轨**：`spec/<project>/`；删除 OpenSpec 命令与 GSD 引用。
4. **组件收敛**：skills 25→14、agents 9→5、rules 7→4、commands 15→10、hooks 19→6 个关注点；删除 `SPEC.md`/`MANIFEST.yaml`/3 个 INDEX。
5. **删除编辑器同步与适配**：`sync*.ps1`、`principles.py`、`validate_config.py`、`check.ps1`、`templates/cursor-guard`、`templates/editor-graph-hooks`、`.cursor/`；不在本仓写任何工具专属路径。
6. **插件收敛**：18 个插件当前均为 disabled；冲突项（`superpowers`、`feature-dev`、`code-review`、`commit-commands`、`claude-md-management`、`github`、`skill-creator`、`ralph-loop`）保持禁用；工具型插件由用户按需启用，`chrome-devtools` 默认关。
7. **自检替代巨型校验器**：新增 `scripts/check-config.py`（结构/frontmatter/hook 路径/MCP/预算/死引用）。
8. **审查不限轮次**：保留两道门与「每轮全新」要求，但不设 3 轮上限；每轮必须带来实质修复，无进展/无法继续时报告用户并请求决策。
9. **铁律编号重排**：活跃铁律改为连续 R1-R21（工程原则 R17-R21）；历史 CHANGELOG/ADR/research 保留当时编号。
10. **外部受管副本清理**：删除各编辑器 home 中旧同步副本与 hooks；规则入口只保留指向 `~/.claude/AGENTS.md` 的指针；`settings.example.json` 提供 hooks 注册模板。

## 后果

- 正面：单一事实源；改流程只改 `AGENTS.md`；token 与维护面显著下降；跨工具只需 `AGENTS.md` + 标准 `SKILL.md`。
- 负面：失去 Stop 强制阻断与 65KB 校验器的细粒度检查；由规则 + 轻量自检承担。
- 回滚：重构前全量备份在 `backups/refactor-20261111-114808/`；插件可用 `claude plugin enable` 恢复。

## 备选方案

- 维持现状，只删重复：不解决四套阶段机与插件双套。
- 激进精简（skills 10 / agents 3 / 删 catalog）：丢失按需资料与领域能力。
- 保留全部 hooks 与机械门：与「配置驱动、模型高效开发」目标冲突。

## 后续

- 观察 Stop 提醒的实际误报率；必要时改为纯提示（exit 0）。
- `settings.local.json` 的明文 token 迁移到环境变量/凭据管理器并轮换。
- catalog 中与主流程重叠的条目（deer-flow、taskmaster、office-hours 等）按需清理。
