# Skill Name: code-refactoring

[TOC]

## Overview
在不影响代码本身逻辑的前提下重构代码，重构超大函数，提升类型安全，消除代码异味和使用合适的设计模式。重构后，需要提供详细的重构前后对比示例，评估重构风险收益，如果有单元测试，确保重构后依然完美通过现存测试用例。

## Features
This skill provides comprehensive code refactoring capabilities, including:

* **代码异味检测与修复**: 识别并解决10种常见代码异味
* **函数抽取**: 将长方法拆分为专注、可维护的小函数
* **类型安全增强**: 为无类型代码引入正确的类型定义
* **设计模式应用**: 实现策略模式、责任链模式等设计模式
* **安全重构流程**: 逐步进行，持续测试和验证
* **代码质量检查清单**: 全面的重构验证检查清单

## Prerequisites & Setup
Before this skill can be used, ensure the following requirements are met:

* **版本控制**: Git仓库，支持安全重构和回滚
* **测试套件**: 现有测试用例以验证行为保持不变
* **代码理解**: 熟悉代码库结构和依赖关系

## Local Testing & Usage
To run and test the skill locally:

```bash
# 基础测试 - 重构单个函数
# 用户提示: "给我重构这个函数"

# 测试类型安全重构
# 用户提示: "这里的类型不安全，重构一下"

# 测试设计模式应用
# 用户提示: "用策略模式替换这些条件语句"
```

## Trigger Prompts & User Scenarios

Examples of human prompts that should trigger the agent to invoke this skill.

### 直接触发词

- **Scenario 1: 基础重构**
  - *User Prompt:* `给我重构这个函数`
  - *Expected Agent Behavior:* Agent识别函数中的逻辑段落，将每个段落抽取为专注的辅助函数，保持原有行为不变。

- **Scenario 2: 类重构**
  - *User Prompt:* `将这个类重构一下`
  - *Expected Agent Behavior:* Agent应用单一职责原则，将大类拆分为多个专注的小类。

- **Scenario 3: 代码优化**
  - *User Prompt:* `优化这段代码结构`
  - *Expected Agent Behavior:* Agent识别代码异味并应用合适的重构技术。

- **Scenario 4: 代码清理**
  - *User Prompt:* `清理这段代码`
  - *Expected Agent Behavior:* Agent删除未使用代码，优化命名，提升代码质量。

### 场景触发词

- **Scenario 5: 函数太长**
  - *User Prompt:* `这个函数太长了，帮我重构`
  - *Expected Agent Behavior:* Agent将超过50行的函数拆分为多个小函数。

- **Scenario 6: 代码重复**
  - *User Prompt:* `这里有重复代码，优化一下`
  - *Expected Agent Behavior:* Agent提取公共逻辑到共享函数，消除重复代码。

- **Scenario 7: 类型不安全**
  - *User Prompt:* `这里的类型不安全`
  - *Expected Agent Behavior:* Agent引入正确的类型定义，替换`any`类型，添加类型检查。

- **Scenario 8: 参数太多**
  - *User Prompt:* `这个函数参数太多了`
  - *Expected Agent Behavior:* Agent将相关参数组合成对象，优化函数签名。

- **Scenario 9: 嵌套太深**
  - *User Prompt:* `这里的if嵌套太深了`
  - *Expected Agent Behavior:* Agent使用卫语句扁平化嵌套条件。

- **Scenario 10: 类太大**
  - *User Prompt:* `这个类太大了`
  - *Expected Agent Behavior:* Agent应用单一职责原则，拆分大类。

## Input & Output Specification

**Inputs (Provided by User or Agent)**

**Required:**
- 目标代码文件或代码片段

**Optional:**
- 要应用的特定重构技术
- 约束或偏好

**Outputs (Delivered by Skill)**

The skill returns comprehensive refactoring results:

1. 重构代码输出:
   - 结构改进的重构代码
   - 所做更改的摘要
   - 行为保持不变的验证
   - 进一步改进的建议

2. 重构约束检查:
   - 文件数量检查（最多1个文件）
   - 代码行数检查（最多2000行）
   - 风险评估和用户确认提示

## Core Refactoring Principles

### The Golden Rules
1. **行为保持不变** - 重构不改变代码做什么，只改变如何做
2. **小步前进** - 做微小的改动，每步之后测试
3. **修改需要版本控制** - 在每个安全状态前后提交
4. **测试至关重要** - 没有测试，你是在编辑而不是重构
5. **一次只做一件事** - 不要混合重构和功能变更

### When NOT to Refactor
- 稳定运行了很久的代码，不要轻易重构
- 没有测试用例的代码不要重构（先添加测试）
- 需要非常清晰的重构目标，否则不要重构
- 当你处于紧迫的截止日期时

## Refactoring Constraints

为了确保重构的安全性和可控性，此技能遵循以下约束条件：

### 建议约束条件

| 约束项           | 建议值        | 说明                                   |
| ---------------- | ------------- | -------------------------------------- |
| 单次重构文件数   | 最多 1 个文件 | 避免跨文件的大规模重构，降低风险       |
| 单次重构代码行数 | 最多 2000 行  | 防止一次性修改过多代码，便于审查和回滚 |

### 约束检查流程

```
1. 检查阶段 (CHECK)
   - 统计目标文件数量
   - 统计目标代码行数
   - 评估是否超出约束

2. 风险提示 (ALERT)
   如果超出约束，执行以下操作：
   - 明确告知用户超出的约束项
   - 列出具体数据（文件数、代码行数）
   - 说明潜在风险
   - 请求用户手动确认

3. 用户确认 (CONFIRM)
   用户可选择：
   - 确认继续：继续执行重构（风险自负）
   - 取消操作：终止重构，建议分批进行
   - 调整范围：缩小重构范围以符合约束

4. 执行重构 (EXECUTE)
   - 约束内：直接执行
   - 约束外且用户确认：执行并标记为高风险操作
```

### 风险提示示例

**场景 1：文件数量超限**
```
⚠️ 重构约束警告

检测到您请求重构 3 个文件，建议最多重构 1 个文件。

超出约束：
- 请求文件数：3 个
- 约束限制：1 个
- 超出数量：2 个

潜在风险：
- 跨文件重构可能引入不一致性
- 难以追踪和回滚变更
- 增加测试验证难度

建议：
- 分批重构，每次处理 1 个文件
- 优先重构依赖最少的文件

是否继续重构所有 3 个文件？(继续/取消/调整范围)
```

**场景 2：代码行数超限**
```
⚠️ 重构约束警告

检测到目标代码共 3500 行，遵循“小步快跑”原则，建议单次重构范围控制在2000行以内。

超出约束：
- 实际代码行数：3500 行
- 约束限制：2000 行
- 超出行数：1500 行

潜在风险：
- 大规模修改难以全面审查
- 增加引入bug的风险
- 回滚成本高

建议：
- 将重构拆分为多个小批次
- 每批次不超过 2000 行
- 每批次完成后运行测试

是否继续重构这 3500 行代码？(继续/取消/调整范围)
```

### 约束豁免场景

以下场景可申请约束豁免（仍需用户确认）：

- **紧急修复**：生产环境严重bug需要立即重构
- **简单重构**：仅涉及格式化、重命名等低风险操作
- **用户明确要求**：用户充分理解风险并明确要求大规模重构

## Supported Code Smells

The skill addresses the following common code smells:

1. **大函数重构 (Long Method/Function)** - 将超过50行的函数进行拆分
2. **重复代码 (Duplicated Code)** - 提取公共逻辑到共享函数
3. **大类/大模块 (Large Class/Module)** - 应用单一职责原则
4. **过长参数列表 (Long Parameter List)** - 将相关参数组合成对象
5. **特性依赖 (Feature Envy)** - 将方法移到合适的类中
6. **基本类型偏执 (Primitive Obsession)** - 引入领域类型
7. **魔鬼数字/字符串 (Magic Numbers/Strings)** - 用命名常量替代
8. **嵌套条件 (Nested Conditionals)** - 使用卫语句扁平化
9. **未使用代码 (Dead Code)** - 删除未使用的代码
10. **不当亲密 (Inappropriate Intimacy)** - 提高封装性

## Refactoring Process

### Safe Refactoring Workflow
```
1. 准备 (PREPARE)
   - 确保测试存在（如果缺失则编写）
   - 提交当前状态
   - 创建功能分支

2. 识别 (IDENTIFY)
   - 找到要处理的代码异味
   - 理解代码做什么
   - 规划重构

3. 重构 (REFACTOR) - 小步骤
   - 做一个小改动
   - 运行测试
   - 如果测试通过则提交
   - 重复

4. 验证 (VERIFY)
   - 所有测试通过
   - 如需要则手动测试
   - 性能不变或改进

5. 清理 (CLEAN UP)
   - 更新注释
   - 更新文档
   - 最终提交
```

## Refactoring Checklist

### Code Quality
- [ ] 函数代码行数合理（< 50行）
- [ ] 去除重复代码
- [ ] 描述性名称（变量、函数、类）
- [ ] 无魔鬼数字/字符串
- [ ] 删除未使用代码

### Structure
- [ ] 相关代码在一起
- [ ] 清晰的模块边界
- [ ] 依赖单向流动
- [ ] 无循环依赖

### Type Safety
- [ ] 所有公共API定义类型
- [ ] 无未说明的`any`类型
- [ ] 可空类型明确标记
- [ ] 无不安全的类型转换
- [ ] 类型匹配检查（如long到int）

### Testing
- [ ] 重构代码通过单元测试
- [ ] 测试覆盖边界情况
- [ ] 所有测试通过

## Common Refactoring Operations

| Operation                                     | Description                           |
| --------------------------------------------- | ------------------------------------- |
| Extract Method                                | 将代码片段转为方法                     |
| Extract Class                                 | 将行为移到新类                         |
| Extract Interface                             | 从实现创建接口                         |
| Inline Method                                 | 将方法体移回调用者                     |
| Inline Class                                  | 将类行为移到调用者                     |
| Pull Up Method                                | 将方法移到超类                         |
| Push Down Method                              | 将方法移到子类                         |
| Rename Method/Variable                        | 提高清晰度                             |
| Introduce Parameter Object                    | 分组相关参数                           |
| Replace Conditional with Polymorphism         | 用多态替代switch/if                    |
| Replace Magic Number with Constant            | 命名常量                               |
| Decompose Conditional                         | 分解复杂条件                           |
| Consolidate Conditional                       | 合并重复条件                           |
| Replace Nested Conditional with Guard Clauses | 提前返回                               |
| Introduce Null Object                         | 消除null检查                           |
| Replace Type Code with Class/Enum             | 强类型                                 |
| Replace Inheritance with Delegation           | 组合优于继承                           |

## Risk Assessment

### 重构风险评估

| 风险类型           | 评估标准                           | 缓解措施                     |
| ------------------ | ---------------------------------- | ---------------------------- |
| 测试覆盖率不足     | 测试覆盖率 < 90%                   | 先补充测试用例               |
| 代码复杂度高       | 圈复杂度 > 10                      | 分步重构，每步验证           |
| 依赖关系复杂       | 依赖深度 > 3层                     | 先解耦，再重构               |
| 业务逻辑关键       | 核心业务流程                       | 增加集成测试                 |
| 代码历史久远       | 最后修改时间 > 1年                 | 与业务方确认需求             |

### 收益评估

| 收益类型           | 评估标准                           |
| ------------------ | ---------------------------------- |
| 可维护性提升       | 代码行数减少、结构清晰             |
| 可测试性提升       | 测试覆盖率提升                     |
| 性能改善           | 执行时间减少                       |
| Bug风险降低        | 类型安全提升、边界检查完善         |

## Limitations & Known Issues

**行为保持**: 该技能旨在保持行为不变，但无法在所有情况下保证。重构后务必运行全面的测试。

**复杂重构**: 一些大规模重构可能需要多次迭代和人工干预。

**语言支持**: 示例主要为Java/C/C++，但原则适用于大多数语言。

## Non-Functional Metrics

* **Average Latency**: 取决于代码库大小和重构复杂度
* **Token Consumption**: 中等；需要理解代码结构和模式
* **Safety**: 高；强调小步前进和测试

## Packaging Instructions

N/A

## Contributing

When improving this skill:
- 添加更多代码异味示例及前后对比代码
- 包含更多设计模式应用
- 扩展语言特定指导
- 保持对行为保持的关注

## Acknowledgments & References

- Martin Fowler的《重构：改善既有代码的设计》
- Robert C. Martin的Clean Code原则
- SOLID设计原则

## License

This project is licensed, please see the [LICENSE](LICENSE.txt) file for details.
