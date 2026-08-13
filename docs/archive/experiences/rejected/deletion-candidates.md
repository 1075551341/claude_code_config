# 低频组件删除清单

> 最后更新：2026-05-23 | 状态：**待删候选已执行**（保留 3D/小程序/微信/移动端）

---

## 用户保留例外（未删）

| 类别 | 保留项 |
|------|--------|
| 3D 可视化 | d3-visualization |
| 小程序/微信 | mini-program |
| 移动端 | capacitor-app, uniapp-development, ios-simulator, android-development, flutter-development, react-native, mobile-ui, mobile-performance, mobile-deployment |
| 语言 reviewer | go/rust/java/kotlin/swift/cpp/csharp/flutter/ruby/typescript/python/react reviewer |

---

## 已删除汇总

### 第一轮（废弃/重复）
- skills: orchestration-workflow, dispatching-parallel-agents
- agents: context-compressor, planning-expert + 6 个 global core 重复
- MCP: puppeteer, glif, perplexity

### 第二轮（低频，2026-05-23）

**catalog skills ×35**：academic-paper-review, competitive-ads-extractor, investor-materials, life-assistant, ffuf-fuzzing, meta-prompting, prompt-guard, secure-deletion, security-forensics, agent-browser, canvas-design, theme-factory, clickhouse-analytics, rpa-automation, video-processing, audio-processing, architecture-diagrams, icon-search, image-enhancement, web-artifacts-builder, snippet-expert, token-conservation, context-rot-guard, context-engineering, context-budget, continuous-learning, must-execute-tools, quality-gate, progress-tracking, eval-driven-dev, spec-first, domain-brainstorm, design-reasoning, iterative-refinement, skill-creator

**catalog agents ×10**：game-developer, embedded-engineer, cloud-cost-optimizer, claude-code-optimizer, connect, artifacts-builder, payment-integration, prompt-engineer, file-organizer, business-writing

---

## 当前 catalog 规模

| 目录 | 数量 |
|------|------|
| skills/ | 97 |
| agents/ | 43 |
| rules/ | 15 |

恢复：Git 历史或 `migrate-from-legacy.py` 从源仓库 re-import。
