---
name: data-analysis
description: 当需要分析CSV/Excel数据、统计计算、数据可视化、生成数据报告、汇总数据洞察时调用此技能。触发词：数据分析、CSV分析、数据汇总、统计分析、数据可视化、数据报告、Excel分析、数据洞察、数据清洗、图表生成。
---

# 数据分析

## 核心能力

**数据清洗、统计计算、可视化生成、洞察提取。**

---

## 适用场景

- CSV/Excel 文件分析
- 统计报告生成
- 数据可视化图表
- 业务指标计算
- 数据质量检查
- 异常值识别

---

## 分析流程

### 1. 数据加载与检查

```python
# 使用 pandas 或 polars
import pandas as pd

# 加载
df = pd.read_csv('data.csv')

# 检查
df.info()       # 结构信息
df.describe()   # 统计摘要
df.head()       # 预览
df.isnull().sum()  # 缺失值
```

### 2. 数据清洗

```python
# 缺失值处理
df.dropna()           # 删除
df.fillna(0)          # 填充
df.fillna(df.mean())  # 平均值填充

# 异常值处理
df = df[df['value'] < threshold]

# 类型转换
df['date'] = pd.to_datetime(df['date'])
df['amount'] = df['amount'].astype(float)
```

### 3. 统计计算

```python
# 基础统计
df.mean()      # 平均值
df.median()    # 中位数
df.std()       # 标准差
df.var()       # 方差

# 分组统计
df.groupby('category').agg({
    'value': ['mean', 'sum', 'count']
})

# 时间序列
df.resample('M').sum()  # 月汇总
```

### 4. 可视化

```python
import matplotlib.pyplot as plt

# 柱状图
df.plot(kind='bar')

# 折线图
df.plot(kind='line')

# 散点图
plt.scatter(df['x'], df['y'])

# 热力图
plt.imshow(df.corr(), cmap='hot')
```

### 5. 输出报告

```python
# 导出分析结果
df.to_csv('analysis_result.csv')
df.to_excel('report.xlsx')

# 导出图表
plt.savefig('chart.png')
```

---

## 常用分析模板

### 汇总报告

```markdown
## 数据概览
- 记录数：{count}
- 字段数：{columns}
- 时间范围：{min_date} 至 {max_date}

## 关键统计
- 平均值：{mean}
- 最大值：{max}
- 最小值：{min}
- 标准差：{std}

## 分布特征
- 正态分布/偏态分布
- 峰值位置：{peak}

## 异常检测
- 异常记录数：{outliers}
- 异常类型：{types}
```

### 对比分析

```markdown
## 分组对比
| 组别 | 数量 | 平均值 | 总计 |
| A | {a_count} | {a_mean} | {a_sum} |
| B | {b_count} | {b_mean} | {b_sum} |
```

---

## Python 库选择

| 库 | 适用场景 |
|------|----------|
| pandas | 一般数据分析 |
| polars | 大数据高性能 |
| numpy | 数值计算 |
| matplotlib | 基础可视化 |
| seaborn | 统计可视化 |
| plotly | 交互可视化 |

---

## 注意事项

```
必须：
- 保留原始数据副本
- 记录清洗步骤
- 验证计算结果
- 标注数据来源

避免：
- 直接修改原始文件
- 隐藏异常值
- 过度聚合丢失细节
- 单一指标误导
```

---

## 相关技能

- `xlsx` - Excel 文件操作
- `report-generator` - 报告生成
- `deep-research` - 研究分析