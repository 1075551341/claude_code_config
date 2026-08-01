# musistudio/claude-code-router

> 层: reference（评估=不集成） | 置信度: 高 | 刷新: 2026-08-01 | 来源: 主 agent 网络核实快照

## v10.11 delta (2026-08-01)

- **最新元数据**：CCR 本地模型网关（127.0.0.1:3456），内置 **Kimi preset**（Kimi Code 订阅/API 一键导入）；路由/fallback/凭证池/重试/观测面板；支持 Claude Code/Codex/Kimi CLI/OpenCode 等 10+ agent
- **本地映射**：用户当前 Kimi 直连（`settings.json` ANTHROPIC_BASE_URL=https://api.kimi.com/coding/）

## 核心价值

- 多供应商路由/故障转移/凭证管理（未来多模型场景）

## 吸收决策

**reference（评估=不集成）** — 内置 Kimi preset 有吸引力，但常驻进程 ~100-200MB 内存 vs 当前单供应商直连收益不匹配；未来切换多供应商时重新评估（MANIFEST 已登记 concern: claude-code-router）。
