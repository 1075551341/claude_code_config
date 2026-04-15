---
name: personal-finance
description: 管理个人财务
triggers: [管理个人财务, 记录收支账目, 规划预算开支, 计算投资收益]
---

# 个人财务管理

## 核心能力

**收支记录分析、预算规划管理、投资收益计算。**

---

## 适用场景

- 个人收支记账
- 预算规划执行
- 投资收益分析
- 储蓄目标追踪

---

## 收支记录

### 账目分类

```markdown
收入类别：
- 工资薪资
- 副业收入
- 投资收益
- 其他收入

支出类别：
- 必需支出：房租、水电、通讯、交通
- 生活支出：餐饮、购物、娱乐
- 投资支出：理财、教育、健康
- 其他支出：社交、礼物、突发
```

### 账目记录格式

```javascript
// 账目记录数据结构
const transaction = {
  id: 'txn_001',
  date: '2026-04-08',
  type: 'expense', // income | expense
  category: '餐饮',
  subcategory: '午餐',
  amount: 35.00,
  account: '微信支付',
  note: '公司附近餐厅',
  tags: ['工作日', '日常']
};

// 月度汇总
function monthlySummary(transactions, month) {
  const filtered = transactions.filter(t => t.date.startsWith(month));

  const income = filtered
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + t.amount, 0);

  const expense = filtered
    .filter(t => t.type === 'expense')
    .reduce((sum, t) => sum + t.amount, 0);

  return {
    income: income.toFixed(2),
    expense: expense.toFixed(2),
    balance: (income - expense).toFixed(2)
  };
}
```

---

## 预算规划

### 预算分配方法

```markdown
50/30/20法则：
- 50% 必需支出（房租、水电、通讯、交通）
- 30% 生活支出（餐饮、购物、娱乐）
- 20% 储蓄投资（应急基金、理财、退休）

4-3-2-1法则：
- 40% 生活开销
- 30% 投资理财
- 20% 储蓄备用
- 10% 保险保障
```

### 预算执行追踪

```python
def check_budget_status(actual, budget):
    """
    检查预算执行状态

    参数：
        actual: 实际支出 dict {category: amount}
        budget: 预算额度 dict {category: limit}

    返回：
        dict: 各类别预算状态
    """
    status = {}
    for category, limit in budget.items():
        spent = actual.get(category, 0)
        usage_rate = spent / limit * 100

        if usage_rate > 100:
            alert = 'overspent'
        elif usage_rate > 80:
            alert = 'warning'
        else:
            alert = 'normal'

        status[category] = {
            'spent': spent,
            'limit': limit,
            'usage_rate': round(usage_rate, 1),
            'alert': alert,
            'remaining': limit - spent
        }

    return status
```

---

## 投资计算

### 收益率计算

```javascript
// 单期收益率
function calculateReturn(initial, final) {
  return ((final - initial) / initial) * 100;
}

// 年化收益率
function annualizedReturn(initial, final, days) {
  const totalReturn = (final - initial) / initial;
  const years = days / 365;
  return ((Math.pow(1 + totalReturn, 1 / years) - 1) * 100).toFixed(2);
}

// 复利计算
function compoundInterest(principal, rate, years, frequency = 12) {
  const n = frequency;
  const r = rate / 100;
  return principal * Math.pow(1 + r / n, n * years);
}
```

### 投资组合分析

```python
def portfolio_analysis(holdings):
    """
    投资组合分析

    参数：
        holdings: list of dict [{symbol, shares, cost, current_price}]

    返回：
        dict: 组合分析结果
    """
    total_cost = sum(h['shares'] * h['cost'] for h in holdings)
    total_value = sum(h['shares'] * h['current_price'] for h in holdings)

    profit = total_value - total_cost
    return_rate = (profit / total_cost) * 100

    # 各持仓占比
    allocation = {}
    for h in holdings:
        value = h['shares'] * h['current_price']
        allocation[h['symbol']] = round(value / total_value * 100, 2)

    return {
        'total_cost': total_cost,
        'total_value': total_value,
        'profit': round(profit, 2),
        'return_rate': round(return_rate, 2),
        'allocation': allocation
    }
```

---

## 储蓄计划

### 目标储蓄计算

```javascript
// 目标储蓄计算器
function savingsGoal(targetAmount, monthlySave, annualReturn = 0) {
  const months = [];
  let accumulated = 0;
  const monthlyReturn = annualReturn / 100 / 12;

  for (let m = 1; accumulated < targetAmount; m++) {
    accumulated = accumulated * (1 + monthlyReturn) + monthlySave;
    months.push({
      month: m,
      saved: monthlySave * m,
      accumulated: accumulated.toFixed(2),
      progress: ((accumulated / targetAmount) * 100).toFixed(1)
    });

    if (m > 600) break; // 最多50年
  }

  return {
    goal: targetAmount,
    monthlySave: monthlySave,
    monthsNeeded: months.length,
    yearsNeeded: Math.ceil(months.length / 12),
    progress: months
  };
}
```

---

## 债务管理

### 还款计算

```javascript
// 分期还款计算（等额本息）
function loanPayment(principal, annualRate, months) {
  const monthlyRate = annualRate / 100 / 12;

  // 月供 = P × r × (1+r)^n / ((1+r)^n - 1)
  const payment = principal * monthlyRate *
    Math.pow(1 + monthlyRate, months) /
    (Math.pow(1 + monthlyRate, months) - 1);

  const totalPayment = payment * months;
  const totalInterest = totalPayment - principal;

  return {
    monthlyPayment: payment.toFixed(2),
    totalPayment: totalPayment.toFixed(2),
    totalInterest: totalInterest.toFixed(2)
  };
}
```

---

## 财务健康评估

### 评估指标

```markdown
流动性指标：
- 应急基金 ≥ 3-6个月支出
- 流动资产比率 > 20%

偿债指标：
- 债务收入比 < 50%
- 月供收入比 < 30%

储蓄指标：
- 储蓄率 > 20%
- 投资资产占比 > 40%
```

### 财务健康评分

```python
def financial_health_score(metrics):
    """
    财务健康评分

    参数：
        metrics: dict 包含各项指标

    返回：
        int: 健康评分 0-100
    """
    score = 0

    # 应急基金（权重30）
    if metrics['emergency_fund_months'] >= 6:
        score += 30
    elif metrics['emergency_fund_months'] >= 3:
        score += 20
    else:
        score += 10

    # 储蓄率（权重25）
    if metrics['savings_rate'] >= 20:
        score += 25
    elif metrics['savings_rate'] >= 10:
        score += 15

    # 债务收入比（权重25）
    if metrics['debt_to_income'] <= 30:
        score += 25
    elif metrics['debt_to_income'] <= 50:
        score += 15

    # 投资占比（权重20）
    if metrics['investment_ratio'] >= 40:
        score += 20
    elif metrics['investment_ratio'] >= 20:
        score += 10

    return score
```

---

## 注意事项

```
建议：
- 定期记账保持数据完整
- 预算要合理可执行
- 分散投资降低风险
- 建立应急基金优先

避免：
- 过度消费超预算
- 高利贷和超前消费
- 投资单一资产
- 忽视通货膨胀影响
```

---

## 相关技能

- `health-tracking` - 健康追踪
- `data-analysis` - 数据分析
- `time-management` - 时间管理