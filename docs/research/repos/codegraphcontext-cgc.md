# CodeGraphContext/CodeGraphContext v0.5.5

> 层: L3 洞察（评估未引入） | 置信度: 中 | 刷新: 2026-08-07 | 来源: GitHub 双源

## 核心价值

- **Tree-sitter + SCIP 双索引**：23 语言支持（比 codegraph 更广）
- **Windows 原生后端**：KuzuDB / LadybugDB 嵌入式图数据库（无需服务器）
- **实时监听**：`cgc watch` 文件变更自动增量更新
- **死代码检测**：unreferenced symbols 分析
- **CGC Language Server**：IDE 集成能力

## v10.14 评估决策（2026-08-07）

- **不引入**：与 codegraph R17 主位高度重叠；CRG 已覆盖审查场景缺口
- **理由**：
  - 三图谱并存互博风险高（codegraph + CRG + CGC 职责边界难清晰）
  - codegraph 实测指标优（~47% token↓ / ~58% 工具调用↓），已常驻稳定
  - CGC v0.5.5 仍处于早期（0.x 版本，API 可能变化）
  - CRG 的 test-gap/detect_changes 是本方案核心需求，CGC 无此能力
- **备选价值**（记录不删除）：
  - 若 codegraph 出现重大故障或停止维护，CGC 可作为 R17 备选（Windows 原生后端是差异化优势）
  - 23 语言广度在多语言项目场景有潜力
  - `cgc watch` 实时监听能力优于 codegraph 的 debounce 同步

## 双源证据

- GitHub: CodeGraphContext/CodeGraphContext v0.5.5（2026-08-07 核实）
- README + docs/

## 与 codegraph/CRG 对比

| 维度 | codegraph | code-review-graph | CodeGraphContext |
|------|-----------|-------------------|------------------|
| 定位 | 探索主位（R17） | 审查/验证专用 | （未引入）备选 |
| 语言数 | 20+ | 同 codegraph 基底 | 23 |
| 后端 | 自带运行时 | 同 codegraph | KuzuDB/LadybugDB |
| 实时监听 | debounce hook | 增量 ~2.5s | cgc watch |
| test-gap | 无 | 有 | 无 |
| 版本成熟度 | v1.4.1 | v2.3.6 | v0.5.5（早期） |
