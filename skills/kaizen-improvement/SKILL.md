---
name: kaizen-improvement
description: 持续改进
triggers: [持续改进, 优化流程, 提升效率, 实施精益改善]
---

# 持续改进（Kaizen）

## 核心能力

**持续改进方法论、流程优化、效率提升。**

---

## 适用场景

- 工作流程优化
- 个人效率提升
- 团队持续改善
- 质量改进项目

---

## 核心理念

### Kaizen原则

```markdown
改善理念：
- 持续的小改进优于一次大变革
- 人人参与改进
- 质疑现状，追求更好
- 用数据说话
- 标准化成功经验

三大支柱：
1. 标准化：建立基准
2. 改善：持续提升
3. 消除浪费：精益思维
```

### PDCA循环

```markdown
Plan（计划）：
- 识别问题
- 分析原因
- 制定改进计划
- 设定目标

Do（执行）：
- 小范围试点
- 收集数据
- 记录过程
- 验证方案

Check（检查）：
- 对比目标
- 分析结果
- 识别偏差
- 总结经验

Act（处理）：
- 标准化成功经验
- 推广应用
- 开始下一轮循环
```

---

## 改进方法

### 价值流分析

```markdown
步骤：
1. 绘制当前状态价值流图
2. 识别增值/非增值活动
3. 分析瓶颈和浪费
4. 设计未来状态图
5. 制定改进计划

增值活动：客户愿意付费的工作
非增值活动：不创造价值的工作

七种浪费：
1. 过度生产
2. 等待
3. 运输
4. 过度加工
5. 库存
6. 动作
7. 缺陷返工
```

### 5S管理

```markdown
整理（Seiri）：
- 区分必要和 unnecessary 物品
- 清除 unnecessary 物品
- 只保留必需品

整顿（Seiton）：
- 合理摆放物品
- 明确标识位置
- 取用方便快捷

清扫（Seiso）：
- 保持环境清洁
- 定期检查维护
- 及时发现异常

清洁（Seiketsu）：
- 制度化前三S
- 保持标准化状态
- 目视化管理

素养（Shitsuke）：
- 养成良好习惯
- 遵守规章制度
- 持续改进提升
```

### 问题解决八步法

```markdown
1. 明确问题
   - 什么是问题？
   - 问题的本质是什么？

2. 分解问题
   - 将大问题分解为小问题
   - 识别关键子问题

3. 设定目标
   - 明确改进目标
   - 量化衡量指标

4. 分析根因
   - 使用5Why分析
   - 鱼骨图等工具

5. 制定对策
   - 针对根因制定方案
   - 评估可行性

6. 实施对策
   - 制定执行计划
   - 分配责任

7. 评估结果
   - 对比目标和实际
   - 分析差距原因

8. 标准化
   - 固化成功经验
   - 形成标准流程
```

---

## 改进工具

### 检查表

```markdown
# 日常工作改进检查表

□ 今日工作有哪些可以简化？
□ 是否有重复性工作可以自动化？
□ 工作流程中是否有不必要的步骤？
□ 时间是否花在了最重要的任务上？
□ 今天是否学到了新东西？
□ 是否有需要记录的经验教训？
□ 明天可以做得更好的是什么？
```

### 改进日志模板

```markdown
# 改进日志

日期：2025-01-15

## 发现的问题
[描述发现的问题或改进机会]

## 原因分析
- 现象：
- 原因：
- 影响：

## 改进措施
- 方案：
- 预期效果：
- 实施计划：

## 实施结果
- 实际效果：
- 与预期差距：
- 经验教训：

## 后续行动
- [ ] 待办事项1
- [ ] 待办事项2
```

### 效率追踪

```python
import pandas as pd
from datetime import datetime

class ImprovementTracker:
    """改进追踪器"""

    def __init__(self, log_file='improvements.csv'):
        self.log_file = log_file
        self.records = []

    def log_improvement(self, category, description, before, after):
        """
        记录改进

        参数：
            category: 改进类别
            description: 改进描述
            before: 改进前指标
            after: 改进后指标
        """
        record = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'category': category,
            'description': description,
            'before': before,
            'after': after,
            'improvement': f"{((after - before) / before * 100):.1f}%"
        }
        self.records.append(record)

        df = pd.DataFrame(self.records)
        df.to_csv(self.log_file, index=False)

    def summary(self):
        """生成改进总结"""
        df = pd.DataFrame(self.records)

        summary = {
            'total_improvements': len(df),
            'categories': df['category'].value_counts().to_dict(),
            'avg_improvement': df['improvement'].mean()
        }

        return summary
```

---

## 改进案例

### 开发流程改进

```markdown
问题：代码评审效率低

现状分析：
- 平均评审时间：2天
- 返工率：30%
- 评审意见数：平均15条/次

根因分析：
1. PR粒度太大
2. 缺少评审checklist
3. 缺少自动化检查

改进措施：
1. 限制PR大小（<400行）
2. 制定代码评审checklist
3. 引入CI自动检查

改进结果：
- 评审时间：0.5天（提升75%）
- 返工率：10%（降低67%）
- 评审意见：平均8条/次

标准化：
- 更新开发规范文档
- 配置CI检查规则
- 团队培训分享
```

### 个人效率改进

```markdown
问题：经常被打断，无法专注工作

现状分析：
- 日均被打断次数：15次
- 专注工作时长：2小时/天
- 任务完成率：60%

改进措施：
1. 设置勿扰时段（上午9-11点）
2. 消息集中处理（每2小时一次）
3. 使用番茄工作法

改进结果：
- 日均被打断：5次（减少67%）
- 专注时长：4小时/天（提升100%）
- 任务完成率：85%（提升42%）

标准化：
- 团队约定沟通规范
- 个人日程管理习惯
```

---

## 持续改进文化

### 团队实践

```markdown
日常实践：
- 每日站会分享改进点
- 每周改进回顾
- 每月改进成果展示

激励机制：
- 改进建议奖
- 最佳实践分享
- 改进成果表彰

可视化：
- 改进看板
- 进度追踪
- 成果展示
```

### 个人习惯

```markdown
每日：
- 复盘今日工作
- 记录一个改进点
- 明日计划优化

每周：
- 总结本周改进
- 设定下周目标
- 学习一个新技能

每月：
- 评估月度进步
- 更新工作方法
- 分享改进经验
```

---

## 注意事项

```
建议：
- 从小处着手
- 数据驱动决策
- 保持耐心和毅力
- 庆祝每一个进步

避免：
- 好高骛远
- 频繁改变方向
- 忽视小改进
- 只有想法没有行动
```

---

## 相关技能

- `time-management` - 时间管理
- `systematic-debugging` - 系统化调试
- `performance-optimization` - 性能优化