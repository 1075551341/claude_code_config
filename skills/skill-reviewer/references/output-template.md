# skill-reviewer评审skill之后输出的报告模板

## 窗口输出的报告格式
- 报告里不需要增加图标

```markdown
## Skill评审报告
### 1. 概览
- 检查项总数: 25
- 通过检查项: 22
- 警告项: 2 
- 失败项: 1
- 总体评分: 88/100
- 状态: pass_with_warnings

### 2. 分类详情
#### 命名规范检查 (G.NAM.*)
- 烤串命名法检查: 通过
- 功能性命名模式检查: 通过
- 避免语义噪音检查: 通过
- 子分类后缀检查: 通过

#### 目录结构检查 (G.FMT.*)
- 目录与Skill名称一致性检查: 通过
- 脚本目录检查: 警告

#### 文件格式检查 (G.FMT.*)
- 变量使用格式检查: 通过
- 命名语言要求检查: 通过

#### 内容要求检查 (G.EXP.*)
- 有效描述检查: 通过
- 术语一致性检查: 通过
- 输入输出前置条件明确性检查: 通过
- 其他检查项: 通过

#### 实践要求检查 (G.PRA.*)
- 文档完整性与结构化检查: 通过
- 错误处理和日志检查: 通过

### 3. 详细问题列表
 |检查项ID|严重级别|问题描述|文件名称|相对路径和行号|
 |:--------:|:--------:|:--------:|:--------:|:--------:|
 |G.EXP.04|告警|未明确提及资源清理机制|SKILL.md|~/skill-creator/，第2行|

### 4. 修复建议
- 针对每个问题，按优先级提供修复建议
```

### 检查结果类型

- **通过 (pass)**: 符合规范要求
- **警告 (warning)**: 基本符合但建议改进
- **失败 (fail)**: 不符合规范要求，必须修复

### 总体评分标准

- **95-100分**: 优秀，完全符合所有规范
- **85-94分**: 良好，有小幅改进建议
- **75-84分**: 合格，部分项目需要改进
- **60-74分**: 待改进，存在多项需要修复的问题
- **60分以下**: 不合格，严重不符合规范要求

## JSON类型的格式（不需要打印）

### 1. 概览

```json
{
  "overall_score": 85,
  "max_score": 100,
  "status": "pass_with_warnings"
}
```

### 2. 分类详情

```json
{
  "categories": {
    "naming_conventions": {
      "score": 90,
      "max_score": 100,
      "status": "pass",
      "details": [
        {
          "check_id": "G.NAM.01",
          "name": "烤串命名法检查",
          "status": "pass",
          "description": "使用烤串命名法，符合要求"
        },
        {
          "check_id": "G.NAM.02",
          "name": "功能性命名模式检查",
          "status": "pass",
          "description": "使用[Action]-[Object]结构，符合要求"
        }
      ]
    },
    "directory_structure": {
      "score": 75,
      "max_score": 100,
      "status": "warning",
      "details": [
        {
          "check_id": "G.FMT.01",
          "name": "目录与Skill名称一致性检查",
          "status": "fail",
          "description": "目录名与Skill名称不一致",
          "suggestion": "建议将目录名改为与Skill名称一致"
        }
      ]
    }
  }
}
```

### 3. 详细问题列表

```json
{
  "issues": [
    {
      "severity": "error",
      "category": "naming",
      "check_id": "G.NAM.03",
      "title": "避免语义噪音词汇",
      "description": "Skill名称中包含'agent'这一噪音词汇",
      "location": "SKILL.md name字段",
      "current_value": "email-agent-skill",
      "recommended_value": "drafting-emails",
      "suggestion": "移除'agent'词汇，使用更具描述性的命名"
    },
    {
      "severity": "warning",
      "category": "content",
      "check_id": "G.EXP.01",
      "title": "有效描述检查",
      "description": "Skill描述过于简短，未充分说明功能和使用场景",
      "location": "SKILL.md description字段",
      "current_value": "这是一个工具",
      "recommended_value": "这是一个用于XXX的专用工具，支持YYY场景",
      "suggestion": "添加详细的功能描述和使用场景说明"
    }
  ]
}
```

### 4. 修复建议

```json
{
  "recommendations": {
    "high_priority": [
      "修改Skill名称，避免使用语义噪音词汇",
      "调整目录名称与Skill名称保持一致",
      "完善Skill描述，添加功能和使用场景说明"
    ],
    "medium_priority": [
      "添加scripts目录存放确定性脚本",
      "完善错误处理和异常情况说明",
      "添加相关文档文件（CHANGELOG.md、LICENSE.md等）"
    ],
    "low_priority": [
      "优化内部代码结构和注释",
      "添加性能优化建议",
      "完善安全考虑和权限控制"
    ]
  }
}
```
