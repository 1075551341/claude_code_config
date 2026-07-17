---
name: test-edge-case-analyzer
description: 深度扫描业务代码的分支路径，识别并推荐开发人员容易遗漏的极端边界测试场景。
tags: [testing, code-analysis, unit-test, boundary-value]
metadata:
  version: 1.0.0
loading_tier: L3
disable-model-invocation: true
---

# Boundary Scanner: 极端边界测试场景生成器

## 1. 技能概述

本技能用于深度扫描业务代码的分支路径，自动识别并推荐容易遗漏的极端边界测试场景，生成结构化的JSON测试报告。帮助开发人员构建更健壮、更全面的测试用例。

## 2. When to trigger

使用此技能的场景包括：

- **代码审查前**：在提交代码或创建PR前，分析关键方法的边界测试覆盖情况
- **测试用例设计**：为复杂业务逻辑设计全面的测试用例时，发现遗漏的边界场景
- **重构风险评估**：重构代码时，识别可能影响的原有边界条件和异常处理
- **质量保障**：在生产环境问题修复后，验证是否覆盖了所有相关的边界条件
- **新人培训**：帮助团队成员理解代码中的潜在边界问题和测试最佳实践
- **架构设计评审**：评估系统设计是否充分考虑了各种边界条件和异常情况

## 3. 核心能力

本技能基于白盒测试原则，重点覆盖以下测试维度：

| 测试维度 | 具体场景 | 测试方法 | 典型事例 |
| :--- | :--- | :--- | :--- |
| **数据边界** | 极端值、空值、类型错误 | 参数变异 + 断言异常 | 测试 `transfer(amount)` 时，输入 `0`、`-1`、`MAX_VALUE`、`null` 或非数字字符串，验证系统是否抛出 `IllegalArgumentException`。 |
| **时间边界** | 闰年、夏令时、时间回拨 | 打桩 Clock / ZonedDateTime | 验证日期计算逻辑在跨越闰年（2月29日）或夏令时切换点时的准确性；模拟系统时间回拨检查定时任务是否重复执行。 |
| **配置边界** | 开关、环境变量、系统属性 | System.setProperty + 清理 | 动态设置 `System.setProperty("feature.switch", "false")`，验证功能降级逻辑是否生效，并在测试后清理环境。 |
| **序列化边界** | 缺失字段、非法值、递归嵌套 | 反 JSON序列化 + 异常捕获 | 构造缺失关键字段的 JSON 字符串进行反序列化，验证是否抛出 `JsonParseException` 或设置了默认值。 |
| **逻辑组合** | 多条件分支未覆盖 | 判定表 + 覆盖率工具 | 对于 `if (A && B)` 逻辑，构造 `(true, false)` 和 `(false, true)` 的组合，确保每个条件的独立影响都被测试。 |
| **事件机制** | 事件是否发出、监听是否生效 | Mock Listener + CountDownLatch | 使用 `MockListener` 验证特定操作后是否触发了 `ApplicationEvent`，并使用 `CountDownLatch` 确保异步事件被消费。 |
| **依赖管理** | Prototype/Singleton 状态 | Bean 获取对比 + 上下文隔离 | 验证从容器获取的 Bean 是单例（引用相同）还是原型（引用不同），确保状态隔离符合预期。 |
| **并发安全** | 共享变量、锁竞争 | 多线程模拟 + volatile/Atomic | 启动 10 个线程同时对 `count++` 操作，验证最终结果是否为 10，若失败则需引入 `AtomicInteger`。 |
| **资源释放** | 流关闭、连接泄漏 | try-with-resources + verifyClosed | 在执行文件读写后，验证 `FileInputStream` 的 `closed()` 方法是否返回 `true`，确保无资源泄漏。 |

## 4. 使用指南

### 4.1 激活条件
当模型接收包含代码分析需求的指令时，技能将被激活。激活语句应包含明确的边界测试分析请求，例如：
"请使用极端边界测试场景生成器分析以下代码。"
"边界测试分析：请深度扫描以下代码的分支路径。"
"请为以下代码生成结构化的JSON测试报告，识别极端边界测试场景。"
"请分析以下代码，识别潜在的边界测试场景。"

### 4.2 输入参数处理
模型需要从用户的提示词中提取以下输入参数：

1. **代码内容**：从提示词中获取要分析的代码片段。若未提供，则向用户要求添加代码内容。
2. **语言类型**：从提示词中识别代码语言类型（Java、Python、JavaScript、Go等）。若无法识别，假设为Java并提供相应的处理逻辑。
3. **上下文信息**：从提示词中获取Mock对象等依赖行为的描述。若未提供，执行基本的边界分析并在结果中注明缺失上下文的影响。

当任一必要输入参数无法从提示词中获取时，模型应向用户反馈缺失的输入项并提供获取指引。

### 4.3 输出格式规范
技能将按照以下结构输出分析结果，并确保生成完全有效的JSON格式：

#### 4.3.1 JSON格式验证要求
- 所有数字值必须完整（如 `0.92`，不能是 `0., 92`）
- 字符串中的特殊字符必须正确转义
- 确保所有数字和字符串值格式一致
- 所有数组成员的格式必须统一

#### 4.3.2 输出结构
技能将按照以下结构输出分析结果：

```json
### [方法名] 边界测试分析报告
{
  "skill_id": "boundary-scan-v1.0.0",
  "timestamp": "2025-04-05T10:30:00Z",
  "target_function": "method_signature",
  "source_file": "file_path:line_number",
  "issues_found": [
    {
      "dimension": "data_boundary|logic_boundary|exception_boundary|performance_edge|system_error",
      "category": "category_name",
      "scenario": "scenario_description",
      "input_values": ["value1", "value2"],
      "expected_behavior": "expected_behavior_description",
      "recommended_test": {
        "method": "test_method_name",
        "code_snippet": "test_code_snippet",
        "test_strategy": "test_strategy_description"
      },
      "confidence": 0.XX,
      "severity": "high|medium|low"
    }
  ],
  "summary": {
    "total_issues": number,
    "high_severity": number,
    "medium_severity": number,
    "low_severity": number,
    "recommendations": [
      "recommendation1",
      "recommendation2"
    ]
  }
}
```

#### 4.3.3 数据处理规则
- **置信度(confidence)**: 值范围必须为 0.0-1.0，保留两位小数，如 0.95
- **严重程度(severity)**: 只能是 "high", "medium", "low" 之一
- **数字值**: 必须是有效的JSON数字，不能包含常量名或格式错误的数字
- **代码示例**: 必须是有效的字符串，特殊字符需要转义
- **输入值数组**: 所有值应为简单数据类型（数字、字符串、布尔值）

## 5. 示例输出

```json
### CaseReviewService#getCaseReviewRecords 边界测试分析报告
{
  "skill_id": "boundary-scan-v1.0.0",
  "timestamp": "2026-03-19T12:00:00Z",
  "target_function": "getCaseReviewRecords(String caseId, String projectId, int pageNum, int pageSize, String reviewId)",
  "source_file": "com.huawei.cloudtc.v2.review.service.CaseReviewService.java:89",
  "issues_found": [
    {
      "dimension": "data_boundary",
      "category": "null_parameter_validation",
      "scenario": "caseId和projectId均为null且reviewId为空",
      "input_values": ["null", "null", 1, 10, ""],
      "expected_behavior": "返回ResultInfo，状态为FAILED，结果列表为空",
      "recommended_test": {
        "method": "assertResultStatus",
        "code_snippet": "ResultInfo<CaseReviewEntity> result = caseReviewService.getCaseReviewRecords(null, null, 1, 10, \"\");\nassert CommonStatusEnum.FAILED.getValue() == result.getStatus();",
        "test_strategy": "parameterized"
      },
      "confidence": 0.98,
      "severity": "high"
    }
  ],
  "summary": {
    "total_issues": 1,
    "high_severity": 1,
    "medium_severity": 0,
    "low_severity": 0,
    "recommendations": [
      "为负页码添加输入验证",
      "实现最大页码大小限制以防止性能问题"
    ]
  }
}
```

## 6. 最佳实践

- 在生成测试用例前，确保完全理解代码逻辑和业务需求
- 为每个边界场景提供清晰的描述和确切的预期行为
- 优先考虑高严重性(low confidence)的边界条件
- 确保测试用例可重复执行，不依赖外部环境状态
- 定期更新测试用例库，覆盖新发现的边界情况

**1. 数据边界检查**
- **场景**：参数为 null 或 负数时的处理。
- **风险点**：代码中未做空校验，可能导致 `NullPointerException`。
- **推荐用例**：
  ```java
  assertThrows(IllegalArgumentException.class, () -> userService.process(null));
