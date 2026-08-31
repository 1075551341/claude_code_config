# LLM-as-a-Verifier 优点提取与融合记录（v11.3.5）

> 来源：[llm-as-a-verifier/llm-as-a-verifier](https://github.com/llm-as-a-verifier/llm-as-a-verifier)（通用验证框架，SOTA across agentic benchmarks）
> 目的：提取验证方法论优点 → 与 Claude 配置自身优点对比 → 融合缺失项（v11.3.5）→ 同步 DSH（v1.3.4，合并源指针 v11.4.1）
> 变更史：`CHANGELOG.md` v11.3.5 | 模板 SSOT：`skills/verification-before-completion/SKILL.md`

---

## 一、仓库优点提取（9 项）

| # | 优点 | 机制 | 数据/证据 |
|---|------|------|-----------|
| 1 | **细粒度评分** | 1-20 分（实际实现用 A-T 字母）刻度替代二值/小刻度判断，区分度更高 | 评分规则 "1 = incorrect, 10 = borderline, 20 = correct" |
| 2 | **Logprob 分布期望** | 对评分 token 的完整概率分布取期望 `R = 1/(CK) Σ Σ Σ p(v_g)·φ(v_g)`，而非单次采样 | 抗单次采样噪声，比 LLM-as-a-Judge 离散打分稳定 |
| 3 | **准则分解** | 单一「正确性」拆为多准则（例：Correctness / Root cause / Verification 三问） | 评估示例：`"Root cause": "Did the agent fix the real cause?", "Verification": "Did the agent confirm the fix?"` |
| 4 | **重复评估** | 每准则重复 K 次评估取平均（`n_evaluations=4`），抵消随机性 | K 越大越稳，成本线性 |
| 5 | **成对比较消偏** | A/B 槽位交替（repeated evaluations 交换 prompt 槽位）+ 环形哈密顿圈使每候选各出现一次 A/B，消除位置偏差 | PPT 锦标赛把成本从 O(N²) 降到 O(Nk) |
| 6 | **信任观察输出** | 评估原则原文："Trust observed output — **NOT** the agent's narration" | 进度评分 prompt 明文 |
| 7 | **进度跟踪止损** | 每步打分（ProgressTracker），hopeless 轨迹（score < 0.05）提前放弃 | `score < 0.05: abandon a hopeless rollout early` |
| 8 | **Best-of-N 自验证** | 同一模型验证自身 rollout 仍显著提升（Terminal-Bench 2.1：Pass@1 79.4% → 86.5%±1.1%） | 自验证有效，无需更强模型 |
| 9 | **Prefix-cache + 记账** | 准则放 prompt 尾部共享前缀 + 实测 token 计数（cache hit 5.2% → 78.4%，省 ~3.4× uncached input） | 测量而非假设 |

---

## 二、Claude 配置自身优点盘点（对照基线）

> 盘点对象：`~/.claude` v11.3.4（五柱×五阶段×三横切，hooks 16 注册激活）。

| 层 | 优点 | 现状要点 |
|----|------|----------|
| 方法论 | 五阶段流程 + HARD-GATE | ①规划 grill→HARD-GATE 用户批准 →②规格 spec-validation →③执行原子任务 →④验证 →⑤学习沉淀 |
| 方法论 | 任务分类六维判定 SSOT | 简单/非简单客观判定（Phase0 盘点 + 关联需改≤2 + 白名单 + 六维矩阵 + attempt=1），防过度/不足处理 |
| 方法论 | verify_tier 两档 | 比例/全量按复杂度分级；持续处理（attempt≥2）自动升档全量 + 执行升档非简单 |
| 机械门 | hooks 16 注册激活 | 验证硬门（Stop exit 2 反空模板）、每文件首编影响门、初次修改五维迷你验收、bash-guard（stash 硬拦截）、secret-detector、问题指纹追踪（相似度匹配+回归升级）、RTK 压缩 |
| 铁律 | R1–R20 | 任务完成=验证通过；Read→Edit→Read；Bug grep 全修；重试上限 2；交叉验证；版本克制；错误暴露；Git 禁令；会话终验五字段 |
| 终验 | R20 反空模板 + 反合理化 | 满足/遗漏/错改/漏改/原功能五字段硬门校验；反合理化借口表（"我检查过了"→重跑验证） |
| 彻底性 | 变更场景 A–F | 同类模式全修 / 配置引用同步 / 残留引用=0 / 非功能回归证据 / 行为变更消费者核验 / 文档一致 |
| 护栏 | 质量门 + 上下文阈值 | Schema Drift / Security Anchor / Scope Reduction；70% 择机压缩 / 90% 强制 / 100% 禁止 |
| 记忆 | claude-mem（R18） | 跨会话记忆 SSOT，为什么/约定/偏好优先查记忆 |
| 探索 | MCP 分层 9 项 | 本地代码 4（codegraph 常驻 R17）+ 远端 2 + Web 3；code-review-graph 专用 test-gap |
| 审查 | 审查路由 | eng-reviewer 必审 + ceo/designer/dx/qa/security 按类型 + codex 跨模型验证 |
| 同步 | 多编辑器 1+N | sync.ps1 SSOT → Cursor/qoder-cn/trae-cn/workbuddy；DSH 手工对齐协议 |

---

## 三、对比矩阵与融合决策

| 仓库优点 | Claude 现状（v11.3.4） | 决策 |
|---|---|---|
| 1 细粒度评分 | R20 五字段为定性逐条回放，无定量刻度 | **融合**：关键结论 1–20 评分，<10 不声称完成 |
| 2 logprob 分布期望 | 理念等价物：重复评估/交叉验证/反向验证 | **不单独融合**（模型层无 logprob API；理念已含于 #4 强化） |
| 3 准则分解 | 验证清单按代码/测试/功能/安全分级，但无「根因/验证确认」显式三问 | **融合**：验证前显式分解准则（正确性/根因/验证确认） |
| 4 重复评估 | 已有交叉验证（换视角/反向验证/遗漏扫描） | **强化**：关键验证项 ≥2 次独立核验 |
| 5 成对比较消偏 | 无显式机制 | **融合**：方案选择/审查候选成对比较 + A/B 交换复评 |
| 6 观察输出优先 | 理念已有（「无新鲜验证证据不声称完成」「贴命令证据」），无一句话显式表述 | **融合**：一句话显式化进 R20 与验证模板 |
| 7 进度止损 | GSD 逻辑断点 70% / 持续处理升档 | **融合**：每个原子任务后自评进度分（1–20），连续 2 次 <10 上报止损 |
| 8 Best-of-N 自验证 | 等价物：审查路由（eng-reviewer 等）+ codex 跨模型复核 | **不单独融合**（已有更强机制） |
| 9 prefix-cache/记账 | 配置层不适用 | **不融合**（工程实现细节，非方法论） |

---

## 四、融合落点（v11.3.5）

| 落点 | 内容 |
|------|------|
| `skills/verification-before-completion/SKILL.md` | 新增「验证准则分解评分」小节（SSOT，全文六条：观察输出优先 / 准则三问 / 1-20 评分 / 重复评估≥2 / 成对比较消偏 / 进度止损） |
| `CLAUDE.md` R20 行 | 「信任观察输出而非叙述」并入 |
| `rules/CORE.md` R20 段 | 「验证证据须为观察输出（命令/测试/文件），不信叙述」 |
| `hooks/_lib/gate_messages.md` | 软性短句「验证证据须为观察输出」（不碰硬门字段） |

**未纳入项及理由**（记录防回潮）：#2（无 logprob API）、#8（审查路由已覆盖）、#9（工程实现细节）。若未来启用带 logprob 的验证后端，可重新评估 #2。

---

## 六、v11.4.5 追加

- GSD honest-verifier 三态 → R20「满足」行承认/反驳/弃权（硬门仍 coverage_ok）
- **不吸收**：竞品 code-graph plugin、ralph-loop、实验性 agent-Stop hook

---

## 五、SSOT

- 融合正文 SSOT：`skills/verification-before-completion/SKILL.md`（v11.3.5 小节）
- 本记录：变更决策与对比矩阵（仅记录，不承载规则）
- 变更史：`CHANGELOG.md` v11.3.5
- DSH 同步：`~/.dsh/AGENTS.md` v1.3.4（合并源指针 v11.4.1）+ `~/.dsh/skills/verification-before-completion/SKILL.md`（含需求指纹小节；手工对齐，非 sync 目标）
