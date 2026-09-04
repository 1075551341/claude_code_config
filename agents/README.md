# Agents 智能体库

> 计数以 `MANIFEST.yaml` 与 [agents-INDEX.md](../agents-INDEX.md) 为准。v12：删 architect / sre / doc-writer / code-explorer；`code-reviewer` 并入 `eng-reviewer`。

## 审查与修改

`eng-reviewer`（必经，只找问题）→ `change-implementer` 集中改。ceo / designer / dx / qa / security / codex 按需叠加。

## 低频变体

`land-and-deploy` / `design-shotgun`：`disable-model-invocation`，按需 Read。

高 token 检索（search / grep / 轻量调研）并入 `explore`：父代理用 `Task` `subagent_type=explore` 调用。该入口使用**指定模型标准版**，不沿用主代理。
