# openai/codex-plugin-cc

> 层: reference（评估=不集成） | 置信度: 高 | 刷新: 2026-08-01 | 来源: 主 agent 网络核实快照

## v10.11 delta (2026-08-01)

- **最新元数据**：从 Claude Code 内调用 Codex：`/codex:review`（只读审查）、`/codex:adversarial-review`（对抗审查）、`/codex:rescue`/`/codex:transfer`/`/codex:status`（委派与后台任务管理）
- **安装**：`/plugin marketplace add openai/codex-plugin-cc` + `/plugin install codex@openai-codex`
- **本地映射**：本地已有 `agents/codex-reviewer`（gstack_codex，跨模型独立审查）；能力互补

## 核心价值

- 对抗性审查模式（adversarial review）概念参考

## 吸收决策

**reference（评估=不集成）** — 跨模型调用双倍计费，且本地 codex-reviewer 已承接；如需对抗审查可在 codex-reviewer 提示词中注入该模式（MANIFEST 已登记 concern: codex-plugin-cc）。
