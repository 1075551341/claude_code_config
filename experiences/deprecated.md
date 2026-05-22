# 已废弃 / 迁移对照

> 全局配置 v2 整合后，以下项不再位于根目录。

## 已迁移到 catalog/

| 原路径 | 新路径 | 恢复方式 |
|--------|--------|----------|
| skills/* (非 core 17) | catalog/skills/ | migrate-from-legacy.py --skill |
| agents/* (非 core 8) | catalog/agents/ | migrate-from-legacy.py --agent |
| rules/RULES_*.md (语言/领域) | catalog/rules/ | migrate-from-legacy.py --rule |

## 已重命名 rules

| 旧名 | 新名 |
|------|------|
| RULES_CORE.md | CORE.md |
| RULES_SECURITY.md | SECURITY.md |
| RULES_GIT.md | GIT.md |
| RULES_WORKFLOW.md | WORKFLOW.md |
| RULES_AGENTS.md | AGENTS.md |
| RULES_MCP.md | MCP.md |
| — | DESIGN.md（新建） |

## 独立 code-review skill（改用 requesting/receiving-code-review）

- orchestration-workflow → subagent-driven-development + agentic-orchestrator
- execution-planner / planning-expert → agent/planner + writing-plans

## hook/pre-task-planner（改用 skill/writing-plans + /plan + agent/planner）

文件已移至 `hooks/_deprecated/pre-task-planner.py`，不再注册于 settings.json。

## catalog 重复项（已删）

skills: orchestration-workflow, dispatching-parallel-agents  
agents: context-compressor, planning-expert, 及 6 个与全局 core 重复项

## catalog 低频批量删除（2026-05-23）

skills ×35、agents ×10（保留 d3-visualization、mini-program、capacitor/uniapp/ios-simulator 及全套移动端 skills）

详见 `experiences/rejected/deletion-candidates.md`

## 参考 only（未并入 runtime）

get-shit-done 原仓库、deer-flow、ECC 232 skills 整包
