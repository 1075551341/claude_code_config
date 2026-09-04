# SPEC.md — 配置法典索引

> CLAUDE.md 为纯路由（≤120 行）；本文件为精简法典。计数/版本只手写在 `MANIFEST.yaml`，本文件禁止再抄一份。变更史 → `CHANGELOG.md`。
> 版本：见 MANIFEST `version` | 五柱×五阶段×三横切 | 机械门控 + 全任务独立审查

---

## 架构公式

```
RUNTIME  = Superpowers + GSD + OpenSpec + gstack + claude-mem
GUARD    = hooks（图谱 deny / 编码 / bash / 密钥 / Stop 审查硬门 / R17 软门）
SYNC     = scripts/sync.ps1（cursor / qoder-cn / trae-cn / trae）
INSIGHT  = codegraph（R17）+ CRG（影响面/审查）+ Firecrawl/Exa
```

codebase-memory 已禁用。UA removed v10.5。

## 三层

- **骨架**：CLAUDE.md + `rules/CORE.md`（FRONTEND 仅 paths 匹配）
- **执行**：skills / agents / commands（按 INDEX 按需 Read）
- **护栏**：hooks + `config/quality_gates.json` + MANIFEST excludes

## 五柱

| 柱          | 职责                    | 版本 SSOT                      |
| ----------- | ----------------------- | ------------------------------ |
| Superpowers | 方法论 + P0 + HARD-GATE | MANIFEST `superpowers.version` |
| GSD         | 上下文阈值与制品        | MANIFEST `pillars.gsd`         |
| OpenSpec    | delta-spec + `/opsx:*`  | MANIFEST `openspec_config`     |
| gstack      | 审查角色（只找问题）    | MANIFEST `pillars.gstack`      |
| claude-mem  | 跨会话记忆（跟随上游）  | MANIFEST `pillars.claude_mem`  |

## 门控

- 用户批准设计前禁止实现（HARD-GATE）
- 无双图 deny；有写入则 Stop 须新鲜独立审查记录（缺失 Claude Code exit 2；Cursor 注入提醒）
- 独立审查一次找齐、每轮全新开审；修改走 `change-implementer`
- 配置/文档/注释必须同步；验证证据须观察输出

## 同步

Claude Code 原生读 `~/.claude`。编辑器视图由 `sync.ps1` 按 `config/sync-manifest.json` 生成。不生成 `AGENTS.md`（Codex/OpenCode 自管）。

## 规模

以 MANIFEST `global_*_max` 与磁盘 INDEX 为准；`scripts/validate_config.py` 校验一致。
