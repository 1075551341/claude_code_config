# ADR: v10 UA 暂禁 + claude-mem Endless Mode 评估

**日期**: 2026-06-16  
**状态**: Accepted (revised 2026-06-17 — UA l3_on_demand)  
**决策人**: 用户访谈（第 4 轮）

---

## 背景

v10 要求：降 token、避免互博、探索优先 codegraph。UA 与 codegraph 在「项目全貌」场景重叠，双轨增加路由歧义与插件常驻成本。

---

## 决策 1 — Understand-Anything **disabled**

### 选择

- `settings.json`: `understand-anything@Lum1104: false`
- `MANIFEST`: `understand_anything.status: disabled`
- 探索链：**codegraph_explore → Grep → Read**（R17）
- 保留 `skills/understand-anything/` 作 catalog，不删仓库优点文档

### 理由

- 全局 `~/.claude` 已 `codegraph index`（92 文件），符号级探索足够
- 减少 L3 双轨与 SessionStart/PostToolUse hook 开销
- 避免与 codegraph 的「左右手互博」

### 复启用条件（任一）

1. 业务项目需要 `.understand-anything/` 团队共享图谱 + `/understand-onboard`
2. codegraph 无法覆盖的概念聚类场景经评估成立
3. 用户显式要求启用 → 改 `settings.json` + MANIFEST `status: active` + 新 ADR 修订

---

## 决策 2 — claude-mem Endless Mode **默认不启用**

### 选择

- **P1 评估**：记录利弊，不修改默认 `CLAUDE_MEM_*` 配置
- 维持现有 `search → get_observations` 三层（R18）

### 评估结论（P1 — 2026-06-16）

| 维度 | Endless On | 现状（推荐） |
|------|------------|--------------|
| 长会话连续性 | PostToolUse **阻塞**注入压缩观察（~90s timeout） | `/summarize` + claude-mem 检索 + GSD 70% 断点 |
| 延迟 | **更慢**（官方标注 experimental） | 标准 hook 非阻塞 |
| Token | 理论 O(N) 线性；**生产收益未验证** | `CLAUDE_MEM_CONTEXT_OBSERVATIONS=50` 受控注入 |
| 稳定性 | `beta/endless-mode` 分支；需手动 checkout | 稳定 main + 插件 `@thedotmack` |
| 与 GSD 70% | Save-hook 阻塞可能与断点/压缩叠加 | 任务边界 + 压缩语义清晰 |

**结论**：维持 `CLAUDE_MEM_ENDLESS_MODE=false`（默认）。长会话用：压缩 + claude-mem R18 + 子 Agent 切换。

**Opt-in 路径**（仅用户明确要求）：marketplace `beta/endless-mode` → `npm run worker:restart` → 本 ADR 追加观察记录。

### 复启用

用户 opt-in 后更新 `settings.json` env 并在此 ADR 追加「启用日期 + 观察结论」。

---

## 关联

- `MANIFEST.yaml` → `understand_anything`, `concept_navigation`
- `CLAUDE.md` L3 五轨
- `docs/TOOL_MATCHING_GUIDE.md`

---

## 修订 1 — UA L3 按需启用

**日期**: 2026-06-17
**决策**: v10.2 访谈（8 轮第 3 项）— 将 UA 从 disabled 调整为 L3 按需启用（catalog 保留）
**理由**: 
- codegraph 覆盖代码结构查询，但 onboarding/领域分析场景需 UA 概念层能力
- 不常驻（避免 5-agent pipeline token 开销），显式 /understand-* 触发
- MANIFEST: `understand_anything.status: l3_on_demand`
- settings.json 不变（UA 不常驻 MCP）
**关联**: `MANIFEST.yaml` → `understand_anything`, `concept_navigation`
