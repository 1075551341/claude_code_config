# .claude 配置集成设计 v10.0

> 状态: **已完成** 2026-06-16 | SSOT: [30-repo-deep-research-v10.md](../../docs/research/30-repo-deep-research-v10.md)

---

## 设计原则（继承 v9 + v10 增量）

```
P1. 五柱清晰 — Superpowers/GSD/OpenSpec/gstack/claude-mem 不互博
P2. ECC cherry-pick — 吸收 MANIFEST module resolver，不安装 ECC 插件
P3. OpenSpec CLI — core profile（v1.4.1 含 sync）+ `openspec init`
P4. 阈值双轨 — Cursor/Claude 70/90 + GSD 70% 逻辑断点
P5. codegraph mandate — 探索前须索引就绪
P6. Superpowers — 插件更新 + 本地 skills 后加载覆盖
P7. ruflo — reference_only，不集成
P8. UA — **disabled**；探索 codegraph-only（ADR-2026-06-16）
P9. Git — 禁止 Agent auto commit / stash（Guard 1.1.6）
P10. Firecrawl — `firecrawl-mcp.ps1` 系统 Key 包装
```

---

## v10 架构增量

| 领域 | v9.2 | v10.0 |
|------|------|-------|
| MANIFEST | concerns 防互博 | + module_resolver + ecc_integration |
| OpenSpec | core 三命令 | **core** CLI + 本地 commands（verify/onboard 无 preset） |
| 阈值 | 70/90 | + GSD 70% 逻辑断点 |
| codegraph | 推荐 | mandate init + V16 校验 |
| ECC | 部分 hook 概念 | cherry-pick 明示 |

---

## 阈值双轨

| 类型 | 阈值 | 行动 |
|------|------|------|
| Cursor 压缩 | 70% / 90% | `/summarize` 或新子 Agent |
| Claude Code | 70% / 90% | `/compact` |
| GSD 逻辑断点 | 70% | 任务边界、子 Agent 切换（非强制压缩） |

---

## ECC cherry-pick（无插件）

吸收项：
- MANIFEST `module_resolver.conflicts`
- `LOCAL_HOOK_PROFILE=minimal|standard|strict`（映射本地 hook 子集）
- GateGuard 概念 → stop-context-monitor + pre-suggest-compact

禁止：
- 安装 everything-claude-code 插件（duplicate hooks）
- install-state / doctor 脚本（保持 MANIFEST-only，访谈确认）

---

## OpenSpec core + 本地 commands

```
/opsx:propose → /opsx:continue|ff → /opsx:apply → /opsx:verify → /opsx:sync → /opsx:archive
/opsx:onboard — CLI 原生；Cursor 用 onboarding-guide 精简版
```

**去重策略（访谈）**：`openspec init` 生成 `.cursor/skills` 作参考；**权威**在 `~/.claude/commands` + `rules/OPENSPEC.md`，不删本地薄路由。

---

## 可选外部

| 组件 | 层级 | 触发 |
|------|------|------|
| deer-flow | L3 | >30min 自主任务 |
| task-master | L4 | PRD 长项目，`TASK_MASTER_TOOLS=core` |
| ruflo | 文档 | 仅概念参考 |

---

## 验证

- `validate_config.py` V1–V16 全 PASS
- `openspec --version` 可用
- `sync.ps1 -Force` Cursor L0 四文件
