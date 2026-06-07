# Skills 功能速查

| # | Skill | 描述 | 加载 |
|---|-------|------|:--:|
| 1 | autoplan | 自动审查流水线，一条命令完成 CEO→Design→Eng 审查，仅暴露品味决策。 | 按需 |
| 2 | brainstorming | 设计头脑风暴，HARD-GATE：批准前禁止实现。触发词：方案设计、架构、新功能、需求分析、设计决策。 | **必须** |
| 3 | browser-qa | 浏览器QA测试，真实浏览器点击验证，发现bug并原子提交修复。 | 按需 |
| 4 | caveman-compress | 压缩 agent 长输出与冗余解释。触发词：压缩输出、精简回复、caveman、token 浪费。 | 按需 |
| 5 | change-impact-analysis | 变更影响分析 — 改任何文件前必须先执行，codegraph_impact+Grep+MANIFEST depends_on。 | **必须** |
| 6 | context-engineering | 上下文工程方法，管理上下文窗口质量，防止上下文腐烂。 | 按需 |
| 7 | design-pipeline | 设计管线，从探索到生产。shotgun 多方案→对比板→选定→HTML 转化。吸收 gstack /design-shotgun + /design-html。 | 按需 |
| 8 | executing-plans | 计划执行技能，与writing-plans配对，按计划逐步执行任务 | 按需 |
| 9 | finishing-a-development-branch | 开发分支完成时检查、清理、创建PR、合并策略 | 按需 |
| 10 | improve-codebase-architecture | 领域驱动架构改进。对现有代码做结构化重构，跨文件、渐进式、有验证保障。 | 按需 |
| 11 | instinct-learning | Instinct v2 置信度学习系统，从会话提取可复用模式，带置信度评分。 | 按需 |
| 12 | karpathy-guidelines | Karpathy 编码四原则及实施规则。触发词：简洁代码、过度设计、surgical changes、think before coding | 按需 |
| 13 | memory-compression | 上下文压缩与跨会话记忆协调。触发：记忆压缩、上下文腐败、/compact。 | 按需 |
| 14 | office-hours | 六问产品框架，重新定义问题，挑战前提，生成实现方案。触发：/office-hours、产品讨论。 | 按需 |
| 15 | receiving-code-review | 接收代码审查反馈，验证后再实施修改 | 按需 |
| 16 | requesting-code-review | 请求代码审查，向审查者提供精确的上下文 | 按需 |
| 17 | ship | 发布管线，整合测试→覆盖审计→推送→开PR→可选部署验证。 | 按需 |
| 18 | spec-validation | 规格可执行验证，将 spec.md 转化为可验证的验收标准 | 按需 |
| 19 | structured-artifacts | GSD 结构化制品管理，确保跨会话状态存活。 | 按需 |
| 20 | subagent-driven-development | 将原子任务计划分派给子Agent，两阶段审查（spec合规→代码质量），连续执行不问"继续"。与writing-plans配对。 | 按需 |
| 21 | systematic-debugging | 当遇到程序报错、运行时异常、测试失败，遵循系统化调试流程（含根因分析/5Why） | **必须** |
| 22 | test-driven-development | 遵循TDD流程开发功能，RED-GREEN-REFACTOR循环 | 按需 |
| 23 | triage | 问题分诊，Bug报告/Issue的第一道分类关卡，判断类型、严重度、指派方向 | 按需 |
| 24 | understand-anything | 代码知识图谱分析 — 扫描项目生成交互式知识图，支持结构/领域/引导导览视图 | 按需 |
| 25 | using-git-worktrees | 使用 Git Worktree 进行并行开发、隔离分支 | 按需 |
| 26 | using-superpowers | 技能发现与 Tool-First 路由。触发：会话开始、不确定用什么技能、开始任务。 | **必须** |
| 27 | verification-before-completion | ★强制执行★ 完成前必须交叉验证，不可跳过。含残留引用检测 + MANIFEST 一致性。 | **必须** |
| 28 | writing-plans | 编写原子级实施计划（2-5分钟/任务），含精确路径+代码+验证命令。与 executing-plans 配对。 | 按需 |
| 29 | writing-skills | 技能编写元技能，将TDD应用于技能文档本身 | 按需 |

> 29 skills | P0必须=5 | 按需=24 | 完整定义: skills/<name>/SKILL.md
