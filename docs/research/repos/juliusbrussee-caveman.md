# JuliusBrussee/caveman v1.9.0

> 层: L2 优化 | 置信度: 高 | 刷新: 2026-07-31 | 来源: GitHub + 官网 + npm 双源

## v10.6 delta (2026-07-30)

- **本地 skill 刷新至 v1.9.1**：六档（+wenyan-lite/full/ultra）、诚实数字 65%（弃 ~75% 宣称）、Auto-Clarity 自动降档、禁用自造缩写/箭头新规
- caveman 本体为 skill/plugin 而非 CLI：本地 `skills/caveman-compress` 即安装形态；不跑上游全 Agent 安装器（避免与本地 skill 重复）
- PyPI/npm 同名 `caveman` 包为无关项目，本机未安装、无需清除
- MANIFEST `L2_optimization` 版本对齐 1.9.1

## v10.5 delta (2026-07-17)

- **最新元数据**：90,085 stars；GitHub Release **v1.9.1**；`pushed_at` 2026-07-03T11:10:42Z。
- **自 2026-06-29 的变化**：v1.9.0 后有 v1.9.1 patch release；未发现需要改变输出压缩能力边界的重大漂移。
- **本地吸收**：不变——caveman-compress 保持按需 skill；继续与 RTK 保持输出侧/输入侧互补关系。
- **双源**：GitHub API（stars/release/push）+ 仓库 README/既有官网与 npm 研究记录。

## v10.5.1 delta (2026-07-17)

- **最新元数据**：90,097★；Release **v1.9.1**；`pushed_at` 2026-07-03T11:10:42Z。
- **漂移要点**：宣称 ~65% 输出 token；patch 级。
- **本地吸收 / 缺口**：skill integrated；文档标 patch **可跟**（不改钉扎强制）。
- **不吸收**：始终开启（按任务/上下文阈值启用）。
- **双源**：GitHub API + 既有卡片交叉。

## 核心价值

- 输出 ~75% token 压缩
- lite/full/ultra/wenyan 四档
- Agent 响应压缩（与 RTK 输入侧互补）
- caveman-compress skill 按需触发

## 证据

- [GitHub JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)

## 本地映射

| MANIFEST concern | 路径                               |
| ---------------- | ---------------------------------- |
| output_token     | `skills/caveman-compress/SKILL.md` |

## 吸收决策

**采纳** — skill 按需 L3；与 RTK hook 互斥。

## 互博检查

- vs RTK：`excludes: [hook/pre-rtk-rewrite]` 对称

## v10.1 增量

- v1.8.2 维持；无 breaking

## v10.2.1 增量（双源刷新 2026-06-19）

- **v1.9.0** (2026-06-12)；六档（lite/full/ultra + wenyan ×3）
- **F3**：`caveman-shrink` MCP 中间件可压缩任意 MCP server 工具描述 → 服务 x1xhlol 描述密度目标；**catalog 记录，不默认接入**（v10.3 backlog 评估）
- `caveman-compress` 压 CLAUDE.md 输入侧 ~46%（代码/URL/路径字节保留）
