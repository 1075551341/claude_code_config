# 上游覆盖摘要（v12）

现行覆盖以 `MANIFEST.yaml` 五柱/横切为准。

保留：`docs/research/45-upstream-stability-v11.4.md`。

| 柱          | 上游                  | 本地落点                        |
| ----------- | --------------------- | ------------------------------- |
| Superpowers | obra/superpowers      | 本地 skills 覆盖 + 插件自动更新 |
| GSD         | open-gsd/gsd-core     | 概念集成（未装 npm 包）         |
| OpenSpec    | Fission-AI/OpenSpec   | CLI + `/opsx:*`                 |
| gstack      | garrytan/gstack       | 审查 agents                     |
| claude-mem  | thedotmack/claude-mem | 插件通道，跟随上游              |

横切：ECC cherry-pick、deer-flow 概念、RTK、caveman、codegraph、Firecrawl/Exa。codebase-memory 已禁用。
