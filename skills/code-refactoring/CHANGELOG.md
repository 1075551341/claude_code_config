# Changelog

All notable changes to this agent skill will be documented in this file.

## [Unreleased]

### Planned
- 更多设计模式示例（工厂模式、观察者模式、装饰器模式）
- 语言特定重构指南（Python、Java、Go）
- 自动化代码异味检测集成
- 性能优化重构技术
- 代码复杂度分析工具集成

## [1.1.0] - 2026-03-19

### Added
- **触发关键词系统** - 新增完整的关键词触发机制
  - 直接触发词：重构、优化代码、改进代码、清理代码、整理代码
  - 场景触发词：函数太长、代码重复、代码异味、难以理解、难以维护、类型不安全、参数太多、嵌套太深、类太大
  - 8个示例触发语句，帮助系统准确识别用户意图
- 在SKILL.md中新增 `## Trigger Keywords` 章节
- 在README.md中新增 `## Trigger Keywords` 章节

### Changed
- 更新README.md中的使用场景示例，使其更贴近实际用户表达
- 优化Scenario示例，添加多种触发方式

### Documentation
- 完善触发关键词文档，提供丰富的示例
- 统一SKILL.md和README.md中的触发关键词描述

## [1.0.0] - 2026-03-17

### Added
- 初始发布code-refactoring技能
- 全面的代码异味检测和修复能力
  - 大函数重构（Long Method/Function）
  - 重复代码消除（Duplicated Code）
  - 大类/大模块分解（Large Class/Module）
  - 过长参数列表优化（Long Parameter List）
  - 特性依赖解决（Feature Envy）
  - 基本类型偏执修正（Primitive Obsession）
  - 魔鬼数字/字符串替换（Magic Numbers/Strings）
  - 嵌套条件扁平化（Nested Conditionals）
  - 未使用代码删除（Dead Code）
  - 不当亲密修复（Inappropriate Intimacy）
- Extract Method重构及详细示例
- 类型安全增强工作流
- 设计模式应用
  - 策略模式（Strategy Pattern）实现
  - 责任链模式（Chain of Responsibility）
- 安全重构流程及逐步指导
- 全面的重构检查清单，覆盖：
  - 代码质量指标
  - 结构组织
  - 类型安全要求
  - 测试验证
- 17种常见重构操作文档
- 安全重构黄金规则
- 不应重构的场景指南
- 重构风险评估框架
- 收益评估体系

### Documentation
- 完整的README.md及使用场景
- 详细的输入/输出规范
- 重构工作流文档
- 前后对比代码示例
- 局限性和已知问题文档

### Features
- **抽取公共方法**：避免一个函数过长，一个函数不要超过50行代码
- **类型安全检测**：检测到不安全的类型转换要重构
- **类型匹配检查**：能够检测到类型不匹配风险，例如返回了long类型的数据赋值给了int类型的变量
- **安全重构**：要一步一步解决，持续测试和验证

### References
- Martin Fowler的《重构》原则
- Clean Code指南
- SOLID设计原则

## [0.1.0] - 2026-03-11

### Added
- 初始技能结构和基础文档
