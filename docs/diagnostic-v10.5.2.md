# Claude 配置全量诊断报告 v10.5.2

**诊断时间**：2026-07-28
**诊断范围**：MCP服务器 / 插件 / Hooks / Skills / Agents / Rules / 环境变量
**诊断方法**：只读检查（settings.json + 文件系统 + 环境变量 + 插件注册表）

---

## 一、可用性矩阵

### 1.1 核心工具可用性

| 工具                     | 类型     | 安装状态                            | 配置状态             | 实际可用          | 问题                                                                                        | 修复建议                                 |
| ------------------------ | -------- | ----------------------------------- | -------------------- | ----------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------- |
| **codegraph**            | MCP+CLI  | ✅ 已安装（volta）                  | ✅ MCP已配置         | ✅ **可用**       | 无                                                                                          | 无                                       |
| **RTK**                  | CLI+Hook | ✅ 已安装（`~/.local/bin/rtk.exe`） | ❌ **hook未绑定**    | ❌ **不生效**     | `pre-rtk-rewrite.py`存在于hooks/但未在settings.json绑定                                     | 绑定到PreToolUse:Bash                    |
| **claude-mem**           | 插件     | ✅ 已安装（v13.12.4）               | ❌ **未启用**        | ❌ **不生效**     | `claude-mem@thedotmack`在installed_plugins但未在enabledPlugins                              | 添加`"claude-mem@thedotmack": true`      |
| **Firecrawl(crawl)**     | MCP      | ✅ MCP已配置                        | ❌ **API key占位符** | ❌ **不可用**     | settings.json中`FIRECRAWL_API_KEY="你的FirecrawlAPIKey"`覆盖系统环境变量（系统已有真实key） | 改为`"${FIRECRAWL_API_KEY}"`引用环境变量 |
| **Exa**                  | MCP      | ✅ MCP已配置                        | ✅ 环境变量已配置    | ✅ **可用**       | settings.json用`"${EXA_API_KEY}"`正确引用                                                   | 无                                       |
| **codebase-memory(cbm)** | MCP      | ✅ MCP已配置                        | ✅ L4按需            | ✅ **可用**       | 无                                                                                          | 无                                       |
| **caveman**              | Skill    | ✅ skills/caveman存在               | ✅ L3按需            | ⚠️ **调用率不足** | 无硬性门控，依赖模型自觉                                                                    | 在CLAUDE.md添加阈值触发规则              |

### 1.2 插件启用状态

| 插件                                | 安装 | 启用          | 问题                          | 修复建议            |
| ----------------------------------- | ---- | ------------- | ----------------------------- | ------------------- |
| superpowers@claude-plugins-official | ✅   | ✅            | 无                            | 无                  |
| claude-md-management                | ✅   | ✅            | 无                            | 无                  |
| code-review                         | ✅   | ✅            | 无                            | 无                  |
| commit-commands                     | ✅   | ✅            | 无                            | 无                  |
| feature-dev                         | ✅   | ✅            | 无                            | 无                  |
| frontend-design                     | ✅   | ✅            | 无                            | 无                  |
| skill-creator                       | ✅   | ✅            | 无                            | 无                  |
| claude-code-setup                   | ✅   | ✅            | 无                            | 无                  |
| **claude-mem@thedotmack**           | ✅   | ❌ **未启用** | **R18记忆优先不生效的根因**   | **启用**            |
| claude-hud@jarrodwatts              | ✅   | ❌            | 未评估                        | 保持禁用            |
| firecrawl@claude-plugins-official   | ✅   | ❌            | 与crawl MCP冲突（功能重复）   | 保持禁用（MCP优先） |
| github@claude-plugins-official      | ✅   | ❌            | 与gh MCP冲突（功能重复）      | 保持禁用（MCP优先） |
| context7                            | ✅   | ❌            | 与ctx7 MCP冲突                | 保持禁用（MCP优先） |
| chrome-devtools-mcp                 | ✅   | ❌            | 与chrome-devtools MCP冲突     | 保持禁用（MCP优先） |
| playwright                          | ✅   | ❌            | 与pw MCP冲突                  | 保持禁用（MCP优先） |
| ralph-loop                          | ✅   | ❌            | 未评估                        | 保持禁用            |
| security-guidance                   | ✅   | ❌            | 未评估                        | 保持禁用            |
| typescript-lsp                      | ✅   | ❌            | 未评估                        | 保持禁用            |

### 1.3 Hooks绑定状态

**settings.json已绑定的hooks**：

| Hook                             | 文件存在      | 绑定事件                                                    | 状态        |
| -------------------------------- | ------------- | ----------------------------------------------------------- | ----------- |
| post-edit-format.py              | ✅            | PostToolUse:Edit\|Write\|MultiEdit                          | ✅ 正常     |
| post-operation-log.py            | ✅            | PostToolUse:Edit\|Write\|MultiEdit + Bash\|Read\|Glob\|Grep | ✅ 正常     |
| post-secret-detector.py          | ✅            | PostToolUse:Edit\|Write\|MultiEdit                          | ✅ 正常     |
| pre-context-injector.py          | ✅            | PreToolUse:Task\|Bash\|Write\|Edit                          | ✅ 正常     |
| pre-bash-guard.py                | ✅            | PreToolUse:Bash                                             | ✅ 正常     |
| pre-config-protection.py         | ✅            | PreToolUse:Write\|Edit\|MultiEdit                           | ✅ 正常     |
| stop-readme-updater.py           | ✅            | Stop                                                        | ✅ 正常     |
| **post-edit-lint.py**            | ❌ **不存在** | PostToolUse:Edit\|Write\|MultiEdit                          | ⚠️ 悬空引用 |
| **post-doc-reminder.py**         | ❌ **不存在** | PostToolUse:Edit\|Write\|MultiEdit                          | ⚠️ 悬空引用 |
| **post-test-runner.py**          | ❌ **不存在** | PostToolUse:Edit\|Write\|MultiEdit                          | ⚠️ 悬空引用 |
| **pre-task-planner.py**          | ❌ **不存在** | PreToolUse:Task\|Bash\|Write                                | ⚠️ 悬空引用 |
| **pre-dep-checker.py**           | ❌ **不存在** | PreToolUse:Bash                                             | ⚠️ 悬空引用 |
| **pre-git-hook-bypass-block.py** | ❌ **不存在** | PreToolUse:Bash                                             | ⚠️ 悬空引用 |
| **stop-notify.py**               | ❌ **不存在** | Stop                                                        | ⚠️ 悬空引用 |
| **stop-debug-checker.py**        | ❌ **不存在** | Stop                                                        | ⚠️ 悬空引用 |
| **stop-daily-summary.py**        | ❌ **不存在** | Stop                                                        | ⚠️ 悬空引用 |

**存在但未绑定的hooks**：

| Hook                       | 文件存在 | 应绑定事件                         | 影响                      |
| -------------------------- | -------- | ---------------------------------- | ------------------------- |
| **pre-rtk-rewrite.py**     | ✅       | PreToolUse:Bash                    | **RTK shell压缩不生效**   |
| **post-codegraph-sync.py** | ✅       | PostToolUse:Write\|Edit\|MultiEdit | **codegraph变更后不同步** |

注：hooks/目录共22个.py文件，其中9个被settings.json引用但不存在（可能通过`_editor_hook_launcher.py`容错处理，不报错但也不执行）。

### 1.4 Skills/Agents/Rules完整性

| 类别   | INDEX声明 | 实际文件               | 差异                                                                                                                                 | 状态                  |
| ------ | --------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | --------------------- |
| Skills | 38个      | 42个目录               | +4个（frontend-design-pattern-applier/frontend-library-advisor/frontend-refactor-proposer/skill-reviewer/test-edge-case-analyzer等） | ⚠️ INDEX未同步        |
| Agents | 24个      | 26个.md（含README.md） | +1 README                                                                                                                            | ✅ 正常（README不计） |
| Rules  | 10个      | 12个.md（含README.md） | +1 README                                                                                                                            | ✅ 正常（README不计） |

---

## 二、调用链复杂度分析

### 2.1 当前四级调用链

```
代码探索: codegraph_explore (L3) → cbm search_graph (L4) → Grep → Read
外部调研: Firecrawl (不可用❌) / Exa (可用✅) / WebFetch (兜底)
记忆检索: claude-mem (未启用❌) → 重复Read (违反R18)
输出压缩: RTK (未绑定❌) / caveman (L3按需，无门控)
```

### 2.2 复杂度问题

1. **工具不可用导致链断裂**：
   - Firecrawl不可用 → 外部调研只能依赖Exa单源（违反L3双源原则）
   - claude-mem未启用 → 记忆检索退化为重复Read（违反R18）
   - RTK未绑定 → Shell输出无压缩（上下文膨胀风险）

2. **调用链过长**：
   - 代码探索需4级（codegraph→cbm→Grep→Read），每级都需模型判断，决策点多
   - 缺少场景→工具的直接映射，依赖模型记忆R17/R18规则

3. **强制性不足**：
   - R17（codegraph首选）/R18（claude-mem首选）仅在CLAUDE.md文本声明，无硬性门控
   - 阈值70/90压缩触发依赖模型自觉，无PreToolUse hook拦截

---

## 三、强制性缺口清单

| 场景           | 当前状态                       | 缺口                               | 影响                              |
| -------------- | ------------------------------ | ---------------------------------- | --------------------------------- |
| 代码结构探索   | R17声明codegraph首选           | 无PreToolUse拦截Grep/Read          | 模型可能直接用Grep跳过codegraph   |
| 跨会话记忆     | R18声明claude-mem首选          | claude-mem未启用+无拦截重复Read    | 重复Read相同文件，浪费上下文      |
| 外部深度调研   | L3双源（Firecrawl+Exa）        | Firecrawl不可用+无禁止WebFetch规则 | 退化为WebFetch单源浅层抓取        |
| Shell输出压缩  | RTK压缩声明                    | pre-rtk-rewrite.py未绑定           | Bash输出全量进入上下文            |
| 上下文>70%压缩 | 阈值铁律声明                   | 无PreToolUse hook评估上下文占比    | 依赖模型自觉，易遗漏              |
| ①规划阶段      | brainstorming HARD-GATE        | 无SessionStart hook强制Read        | 模型可能跳过brainstorming直接规划 |
| ④验证阶段      | verification-before-completion | 无PreToolUse:Task拦截              | 模型可能跳过验证直接声明完成      |

---

## 四、根因定位

**用户反馈**："必要工具调用不足（当前仅codegraph调用比较多，其余均存在问题）"

**复合型根因**（按影响排序）：

1. **工具不可用**（硬性问题）：
   - claude-mem未启用 → R18记忆优先完全失效
   - Firecrawl API key占位符 → L3双源退化为单源
   - RTK hook未绑定 → Shell压缩不生效

2. **调用链复杂**（设计问题）：
   - 四级调用链决策点多，模型需记忆R17/R18规则
   - 缺少场景→工具直接映射表

3. **强制性不足**（治理问题）：
   - 核心规则仅文本声明，无PreToolUse hook硬性门控
   - 阈值压缩触发依赖模型自觉

---

## 五、修复优先级

| 优先级 | 修复项                               | 影响              | 工作量  |
| ------ | ------------------------------------ | ----------------- | ------- |
| **P0** | 启用claude-mem插件                   | 恢复R18记忆优先   | 1行配置 |
| **P0** | 绑定pre-rtk-rewrite.py               | 恢复RTK shell压缩 | 1行配置 |
| **P0** | 修复Firecrawl API key引用            | 恢复L3双源调研    | 1行配置 |
| **P1** | 绑定post-codegraph-sync.py           | codegraph自动同步 | 1行配置 |
| **P1** | 清理9个悬空hook引用                  | 减少配置噪音      | 删除9行 |
| **P2** | CLAUDE.md添加工具调用门控            | 增强强制性        | ~30行   |
| **P2** | CLAUDE-ROUTER.mdc添加场景-工具映射表 | 简化调用链        | ~15行   |
| **P3** | 更新skills-INDEX.md（+4个）          | 同步INDEX         | ~4行    |

---

## 六、验证清单

修复后需验证：

- [ ] claude-mem启用后，SessionStart自动注入记忆上下文
- [ ] RTK绑定后，Bash命令输出被压缩（观察`rtk hook claude`日志）
- [ ] Firecrawl修复后，`firecrawl_scrape`可正常调用
- [ ] codegraph-sync绑定后，Edit/Write代码文件触发`codegraph sync --incremental`
- [ ] CLAUDE.md门控生效后，模型在代码探索前主动调用codegraph_explore
- [ ] 场景-工具映射表生效后，模型在调研场景主动调用Firecrawl+Exa而非WebFetch
