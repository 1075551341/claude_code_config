---
name: health-tracking
description: 当需要记录健康数据、追踪运动健身、管理饮食营养、监测睡眠质量时调用此技能。触发词：健康追踪、运动记录、健身数据、饮食管理、睡眠监测、健康数据、运动统计、卡路里计算、体重记录。
---

# 健康数据追踪

## 核心能力

**健康数据记录、运动健身追踪、饮食营养管理。**

---

## 适用场景

- 运动健身数据记录
- 饮食营养分析
- 睡眠质量监测
- 健康指标追踪

---

## 运动追踪

### 常见指标

```markdown
基础指标：
- 步数（steps）
- 卡路里消耗（calories）
- 活动时长（active minutes）
- 距离（distance km/miles）

运动类型：
- 步行/跑步
- 骑行
- 游泳
- 力量训练
- HIIT
- 瑜伽
```

### 数据计算示例

```javascript
// 卡路里消耗估算
function calculateCalories(weight, activity, duration) {
  // MET值（代谢当量）
  const MET_VALUES = {
    walking: 3.5,
    running: 7.0,
    cycling: 5.0,
    swimming: 8.0,
    yoga: 2.5
  };

  const met = MET_VALUES[activity] || 3.0;
  // 卡路里 = MET × 体重(kg) × 时长(小时)
  return met * weight * (duration / 60);
}

// 步数转距离（平均步长约0.7米）
function stepsToDistance(steps, strideLength = 0.7) {
  return (steps * strideLength) / 1000; // 返回公里数
}
```

---

## 饮食营养

### 营养指标

```markdown
关键营养素：
- 热量（calories）
- 蛋白质（protein g）
- 碳水（carbs g）
- 脂肪（fat g）
- 纤维（fiber g）

微量元素：
- 维生素A/B/C/D/E
- 钙、铁、锌、镁
- 钠、钾
```

### 营养计算

```javascript
// 每日营养目标（参考值）
const DAILY_TARGETS = {
  calories: { male: 2500, female: 2000 },
  protein: { min: 50, max: 120 }, // 克
  carbs: { min: 225, max: 325 },
  fat: { min: 44, max: 77 },
  fiber: { min: 25, max: 38 }
};

// 餐食营养分析
function analyzeMeal(foods) {
  return foods.reduce((total, food) => ({
    calories: total.calories + food.calories,
    protein: total.protein + food.protein,
    carbs: total.carbs + food.carbs,
    fat: total.fat + food.fat
  }), { calories: 0, protein: 0, carbs: 0, fat: 0 });
}
```

---

## 睡眠监测

### 睡眠指标

```markdown
关键指标：
- 总睡眠时长（total sleep time）
- 深睡时长（deep sleep）
- 浅睡时长（light sleep）
- REM睡眠（REM sleep）
- 睡眠效率（sleep efficiency %）

睡眠质量评分：
- 优秀：睡眠效率 > 90%
- 良好：睡眠效率 85-90%
- 一般：睡眠效率 80-85%
- 较差：睡眠效率 < 80%
```

### 睡眠数据分析

```python
def calculate_sleep_quality(sleep_data):
    """
    计算睡眠质量评分

    参数：
        sleep_data: dict 包含 deep_sleep, light_sleep, rem_sleep, awake_time

    返回：
        float: 睡眠质量评分 0-100
    """
    total_time = sum(sleep_data.values())
    efficiency = (total_time - sleep_data['awake_time']) / total_time * 100

    # 深睡占比权重更高
    deep_ratio = sleep_data['deep_sleep'] / total_time
    quality_score = efficiency * 0.6 + (deep_ratio * 100) * 0.4

    return round(quality_score, 1)
```

---

## 体重管理

### BMI计算

```javascript
// BMI = 体重(kg) / 身高²(m)
function calculateBMI(weight, height) {
  const bmi = weight / Math.pow(height / 100, 2);

  const categories = [
    { max: 18.5, label: '偏瘦', color: 'blue' },
    { max: 24, label: '正常', color: 'green' },
    { max: 28, label: '超重', color: 'yellow' },
    { max: 32, label: '肥胖', color: 'orange' },
    { max: Infinity, label: '重度肥胖', color: 'red' }
  ];

  const category = categories.find(c => bmi < c.max);
  return { bmi: bmi.toFixed(1), category: category.label };
}
```

### 体重趋势分析

```python
def analyze_weight_trend(records):
    """
    分析体重变化趋势

    参数：
        records: list of dict [{date, weight}]

    返回：
        dict: {trend, weekly_change, prediction}
    """
    if len(records) < 2:
        return {'trend': 'insufficient_data'}

    recent = records[-7:]  # 最近7天
    older = records[-14:-7]  # 前7天

    avg_recent = sum(r['weight'] for r in recent) / len(recent)
    avg_older = sum(r['weight'] for r in older) / len(older)

    weekly_change = avg_recent - avg_older

    if weekly_change > 0.5:
        trend = 'increasing'
    elif weekly_change < -0.5:
        trend = 'decreasing'
    else:
        trend = 'stable'

    return {
        'trend': trend,
        'weekly_change': round(weekly_change, 2),
        'current_avg': round(avg_recent, 1)
    }
```

---

## 数据可视化

### 图表类型

```markdown
趋势图：
- 体重变化折线图
- 卡路里摄入/消耗对比
- 睡眠时长柱状图

统计图：
- 周运动量分布
- 营养摄入构成饼图
- 月度健康评分雷达图
```

---

## 注意事项

```
建议：
- 数据记录保持一致性
- 关注长期趋势而非短期波动
- 结合个人目标设定阈值
- 定期回顾调整计划

避免：
- 过度依赖单一指标
- 忽视身体感受信号
- 数据焦虑影响心理健康
- 与他人不恰当比较
```

---

## 相关技能

- `time-management` - 时间管理
- `data-analysis` - 数据分析
- `personal-finance` - 个人理财