---
name: vibe-coding-cn
description: 中文 vibe 编码模式 — 道/法/术/器框架 + α/Ω 元技能 + 五步协作流程
layer: supplement
source: 2025Emma/vibe-coding-cn
triggers:
  - vibe编码
  - 中文编码
  - 中文AI协作
  - vibe-coding
---

# Vibe Coding CN — 道/法/术/器

> 来源：2025Emma/vibe-coding-cn | MIT | 21.5k stars

## 道（原则）

1. **凡是 AI 能做的，就不要人工做** — 自动化优先
2. **一切问题问 AI** — 先问再动手
3. **先结构，后代码** — 规划驱动，模块化优先
4. **上下文是 vibe coding 的第一性要素** — 没上下文 AI 就瞎猜

## 法（策略）

1. **接口先行，实现后补** — 先定义契约
2. **能抄不写，不重复造轮子** — 复用 > 原创
3. **文档即上下文，不是事后补** — 边做边写

## 术（技巧）

1. **明确写清：能改什么，不能改什么** — 给 AI 画边界
2. **Debug 只给：预期 vs 实际 + 最小复现** — 不喂屎山
3. **每步小而具体，每步含验证** — 原子任务

## 器（工具）

Claude Code（主）| Cursor | Codex CLI | Warp | Neovim
→ 选最顺手的，不追新。

## α/Ω 元技能

- **α-提示词（生成器）**：唯一职责是生成其他提示词或技能 → 对应 skill/writing-skills
- **Ω-提示词（优化器）**：唯一职责是优化其他提示词或技能 → 对应 skill/instinct-learning

## 五步协作流程

```
1. 生成设计文档(GDD/PRD) → 交给 AI
2. 确认技术栈 + 生成 CLAUDE.md/AGENTS.md 规则文件
3. 生成实施计划，每步小而具体含验证
4. 建立记忆库(memory-bank)：设计/技术栈/计划/进度/架构
5. 分步执行：每步先 Plan Mode 确认 → 通过后执行 → 更新进度
```

## 与全局配置协同

- 五步流程已融入五阶段（①规划→②规格→③执行→④验证→⑤学习）
- 道/法/术/器 原则已迁入 rules/CORE.md 骨架层
- 中文输出遵循 CLAUDE.md 语言规则
