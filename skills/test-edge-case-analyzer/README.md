# Skill Name: test-edge-case-analyzer

[TOC]

## Overview

**test-edge-case-analyzer** 是一个专业的边界测试场景识别与生成技能，用于深度扫描业务代码的分支路径，自动识别并推荐开发人员容易遗漏的极端边界测试场景。生成结构化、可执行的JSON测试报告，帮助开发人员构建更健壮、更全面的测试用例。

## Features

- **提升测试覆盖率**：自动发现传统测试中难以覆盖的极端边界场景
- **减少生产Bug**：通过提前发现和修复边界条件问题，提高系统稳定性
- **提高开发效率**：自动生成测试用例，减少手动编写边界测试的时间成本
- **统一测试标准**：提供结构化的边界测试分析方法和报告格式
- **增强代码质量**：通过全面的边界测试验证，提升代码健壮性

## Prerequisites & Setup

本技能基于白盒测试原则，覆盖九大关键测试维度：

| 测试维度 | 具体场景 | 测试方法 | 典型事例 |
| :--- | :--- | :--- | :--- |
| **数据边界** | 极端值、空值、类型错误 | 参数变异 + 断言异常 | 测试 `transfer(amount)` 时，输入 `0`、`-1`、`MAX_VALUE`、`null` 或非数字字符串 |
| **时间边界** | 闰年、夏令时、时间回拨 | 打桩 Clock / ZonedDateTime | 验证日期计算逻辑跨越闰年或夏令时切换点的准确性 |
| **配置边界** | 开关、环境变量、系统属性 | System.setProperty + 清理 | 动态设置功能开关，验证功能降级逻辑 |
| **序列化边界** | 缺失字段、非法值、递归嵌套 | 反序列化 + 异常捕获 | 构造缺失字段的JSON验证反序列化异常处理 |
| **逻辑组合** | 多条件分支未覆盖 | 判定表 + 覆盖率工具 | 确保多条件逻辑中所有组合都被测试 |
| **事件机制** | 事件发出与监听 | Mock Listener + CountDownLatch | 验证异步事件是否正确触发和消费 |
| **依赖管理** | Prototype/Singleton 状态 | Bean 获取对比 + 隔离验证 | 确保Bean实例化符合预期单例或原型模式 |
| **并发安全** | 共享变量、锁竞争 | 多线程模拟 + volatile/Atomic | 模拟并发操作验证线程安全性 |
| **资源释放** | 流关闭、连接泄漏 | try-with-resources + 验证关闭 | 确保文件、网络等资源正确释放无泄漏 |

## Trigger Prompts & User Scenarios

### Triggering mode
在对话中直接上传代码片段，或粘贴具体的类/方法代码，并附加指令：
> "请使用极端边界测试场景生成器分析以下代码。"
> "边界测试分析：请深度扫描以下代码的分支路径。"
> "请为以下代码生成结构化的JSON测试报告，识别极端边界测试场景。"
> "请分析以下代码，识别潜在的边界测试场景。"

### Input
- **代码语言**：支持 Java, Python, JavaScript, Go 等主流语言
- **代码范围**：建议提供单个完整的类或方法体，以便进行精确的上下文分析
- **上下文信息**：若代码依赖复杂的Mock对象，请简要描述依赖的行为

### Output Specification
技能按照结构化JSON格式输出分析结果，包含完全有效的JSON格式：

```json
### [方法名] 边界测试分析报告
{
  "skill_id": "boundary-scan-v1.0",
  "timestamp": "2025-04-05T10:30:00Z",
  "target_function": "method_signature",
  "source_file": "file_path:line_number",
  "issues_found": [
    {
      "dimension": "data_boundary|logic|_boundaryexception_boundary|performance_edge|system_error",
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

### Data Processing Rules
- **置信度(confidence)**: 值范围必须为 0.0-1.0，保留两位小数
- **严重程度(severity)**: 只能是 "high", "medium", "low" 之一
- **数字值**: 必须是有效的JSON数字，不能包含常量名
- **代码示例**: 必须是有效的字符串，特殊字符已正确转义
- **输入值数组**: 所有值应为简单数据类型（数字、字符串、布尔值）

## Actual application scenario

### Scenario 1: API parameter verification
分析服务层方法的处理参数逻辑，识别可能导致系统异常的极端参数值。

**示例输出**:
```json
### UserService#processUserRegistration 边界测试分析报告
{
  "skill_id": "boundary-scan-v1.0",
  "timestamp": "2026-03-19T12:00:00Z",
  "target_function": "processUserRegistration(String username, int age, String email)",
  "source_file": "com.example.service.UserService.java:45",
  "issues_found": [
    {
      "dimension": "data_boundary",
      "category": "parameter_validation",
      "scenario": "username为空字符串，age为负数",
      "input_values": ["", -5, "test@example.com"],
      "expected_behavior": "抛出IllegalArgumentException，包含具体的参数错误信息",
      "recommended_test": {
        "method": "testProcessWithInvalidParameters",
        "code_snippet": "assertThrows(IllegalArgumentException.class, () -> userService.processUserRegistration(\"\", -5, \"test@example.com\"));",
        "test_strategy": "parameterized"
      },
      "confidence": 0.95,
      "severity": "high"
    }
  ],
  "summary": {
    "total_issues": 1,
    "high_severity": 1,
    "medium_severity": 0,
    "low_severity": 0,
    "recommendations": [
      "添加参数级别验证注解",
      "实现统一的参数校验框架"
    ]
  }
}
```

### Scenario 2: Data processing algorithm boundary
分析数据处理逻辑，特别是数值计算、字符串处理等场景的边界问题。

### Scene 3: Precision Testing of the Financial System
针对金融计算场景识别潜在的精度丢失、溢出等边界问题。

### Scenario 4: High-Concurrency Test Scenario 4
识别并发访问资源时的竞态条件、死锁等边界情况。

## Best Practice

### 1. Best practices for data boundary check
- **场景**：测试参数为null、空字符串、负数等极端值时的处理
- **风险点**：代码中未做适当校验，可能导致NullPointerException或业务逻辑错误
- **推荐用例**：
  ```java
  // 参数为null测试
  assertThrows(IllegalArgumentException.class, () -> userService.process(null));
  
  // 参数为负数测试
  assertThrows(IllegalArgumentException.class, () -> transferService.transfer(-100));
  
  // 参数为空字符串测试
  assertFalse(validationService.isValid(""));
  ```

### 2. Best Practices for Logical Combination Testing
- **场景**：测试复杂条件分支的所有组合情况
- **风险点**：多条件逻辑中的某些组合未被测试覆盖
- **测试方法**：使用判定表法确保所有组合都被测试
  ```java
  // 测试 (A && B) 的所有组合
  assertTrue(validator.check(true, true));  // 两个条件都满足
  assertFalse(validator.check(true, false)); // 条件B不满足
  assertFalse(validator.check(false, true));  // 条件A不满足
  assertFalse(validator.check(false, false)); // 两个条件都不满足
  ```

### 3. Best Practices of Performance Boundary Testing
- **场景**：测试大数据量、高频次调用下的性能表现
- **风险点**：大数据量或高频次调用可能导致性能下降或内存问题
- **测试工具**：使用JMH进行基准测试，监控内存使用情况

### 4. Best Practices for Concurrent Safety Testing
- **场景**：模拟多线程环境下的资源竞争和状态同步
- **风险点**：共享变量修改导致的数据不一致
- **测试方法**：
  ```java
  // 使用多线程测试共享变量
  ExecutorService executor = Executors.newFixedThreadPool(10);
  CountDownLatch latch = new CountDownLatch(100);
  AtomicInteger count = new AtomicInteger(0);
  
  for (int i = 0; i < 100; i++) {
      executor.execute(() -> {
          count.incrementAndGet();
          latch.countDown();
      });
  }
  latch.await();
  assertEquals(100, count.get());
  ```

## Core advantages

1. **全面覆盖**：系统性地覆盖九大类边界场景，不留死角
2. **自动化分析**：深度分析代码逻辑结构，自动识别潜在边界问题
3. **结构化输出**：生成标准化JSON测试报告，便于集成到CI/CD流程
4. **实用性导向**：提供的测试用例可直接在项目中使用
5. **置信度评估**：对每个边界问题提供置信度评估，优先解决高风险场景

## Practical value in application

### For development teams
- **提高产品质量**：通过全面边界测试减少生产环境问题
- **加速开发流程**：自动生成测试用例，减少手动测试工作
- **降低维护成本**：早期发现问题，减少后期修复成本

### For the test team
- **扩大测试覆盖**：发现传统测试中容易遗漏的边界场景
- **提升测试效率**：提供结构化的测试用例生成框架
- **统一测试标准**：建立边界测试的最佳实践和方法论

### For service systems
- **增强系统稳定性**：通过全面的边界测试提高系统健壮性
- **保障数据准确性**：特别适合金融、数据处理等高精度场景
- **提升用户体验**：减少因极端条件导致的系统错误

## Version

- **技能ID**: test-edge-case-analyzer
- **版本**: 1.0.1
- **标签**: [testing, code-analysis, unit-test, boundary-value]
- **许可证**: 华为内源License (HISL V2.0)

## Acknowledgments & References

N/A

## License

本项目已获得许可，详情请参见 [LICENSE](LICENSE.txt) 文件。

---

使用本技能将帮助您构建更健壮、更可靠的软件系统，有效预防和解决边界条件导致的各类问题。