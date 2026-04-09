---
name: d3-visualization
description: 当需要创建D3.js数据可视化图表、交互式图表、自定义可视化时调用此技能。触发词：D3.js、D3可视化、数据可视化、交互图表、SVG图表、D3图表、数据图表、可视化开发。
---

# D3.js 数据可视化

## 核心能力

**创建交互式数据可视化图表、SVG绑定、动画效果。**

---

## 适用场景

- 数据可视化图表
- 交互式仪表盘
- 自定义图表开发
- SVG 数据绑定

---

## 基本概念

### 选择与绑定

```javascript
// 选择元素
d3.select('div')      // 选择第一个
d3.selectAll('p')     // 选择所有

// 数据绑定
d3.selectAll('div')
  .data([1, 2, 3])
  .enter()
  .append('div')
  .text(d => d)
```

### 比例尺

```javascript
// 线性比例尺
const xScale = d3.scaleLinear()
  .domain([0, 100])
  .range([0, 800])

// 序数比例尺
const colorScale = d3.scaleOrdinal()
  .domain(['A', 'B', 'C'])
  .range(['red', 'green', 'blue'])

// 时间比例尺
const timeScale = d3.scaleTime()
  .domain([new Date(2024, 0, 1), new Date(2024, 11, 31)])
  .range([0, 800])
```

---

## 常用图表

### 柱状图

```javascript
const svg = d3.select('svg');

svg.selectAll('rect')
  .data(data)
  .enter()
  .append('rect')
  .attr('x', (d, i) => i * 30)
  .attr('y', d => height - yScale(d.value))
  .attr('width', 25)
  .attr('height', d => yScale(d.value))
  .attr('fill', 'steelblue');
```

### 折线图

```javascript
const line = d3.line()
  .x(d => xScale(d.date))
  .y(d => yScale(d.value))
  .curve(d3.curveMonotoneX);

svg.append('path')
  .datum(data)
  .attr('d', line)
  .attr('fill', 'none')
  .attr('stroke', 'steelblue');
```

### 饼图

```javascript
const pie = d3.pie().value(d => d.value);
const arc = d3.arc().innerRadius(0).outerRadius(radius);

svg.selectAll('path')
  .data(pie(data))
  .enter()
  .append('path')
  .attr('d', arc)
  .attr('fill', (d, i) => colors[i]);
```

---

## 交互功能

### Tooltip

```javascript
const tooltip = d3.select('body')
  .append('div')
  .attr('class', 'tooltip')
  .style('opacity', 0);

svg.selectAll('rect')
  .on('mouseover', function(event, d) {
    tooltip.transition().duration(200).style('opacity', .9);
    tooltip.html(`Value: ${d.value}`)
      .style('left', (event.pageX + 10) + 'px')
      .style('top', (event.pageY - 28) + 'px');
  })
  .on('mouseout', function() {
    tooltip.transition().duration(500).style('opacity', 0);
  });
```

### 缩放

```javascript
const zoom = d3.zoom()
  .scaleExtent([1, 8])
  .on('zoom', (event) => {
    svg.selectAll('g').attr('transform', event.transform);
  });

svg.call(zoom);
```

### 拖拽

```javascript
const drag = d3.drag()
  .on('start', dragstarted)
  .on('drag', dragged)
  .on('end', dragended);

svg.selectAll('circle')
  .call(drag);
```

---

## 动画效果

### 过渡动画

```javascript
// 基本过渡
d3.select('rect')
  .transition()
  .duration(1000)
  .attr('width', 200);

// 链式过渡
d3.select('rect')
  .transition()
  .duration(500)
  .attr('width', 200)
  .transition()
  .duration(500)
  .attr('height', 100);
```

### 缓动函数

```javascript
d3.transition()
  .ease(d3.easeLinear)      // 线性
  .ease(d3.easeBounce)      // 弹跳
  .ease(d3.easeElastic)     // 弹性
  .ease(d3.easeCubicInOut); // 三次缓动
```

---

## 坐标轴

```javascript
// 创建轴
const xAxis = d3.axisBottom(xScale);
const yAxis = d3.axisLeft(yScale);

// 添加轴
svg.append('g')
  .attr('transform', `translate(0, ${height})`)
  .call(xAxis);

svg.append('g')
  .call(yAxis);
```

---

## 项目结构

```
d3-project/
├── index.html
├── styles.css
├── main.js
│   ├── data/          # 数据处理
│   ├── scales/        # 比例尺配置
│   ├── charts/        # 图表组件
│   └── utils/         # 工具函数
└── data/
    └── dataset.csv
```

---

## 注意事项

```
必须：
- 理解SVG基础知识
- 处理数据格式转换
- 添加交互提示
- 响应式设计

避免：
- 过多元素影响性能
- 复杂动画卡顿
- 忽略数据更新场景
- 缺少错误处理
```

---

## 相关技能

- `data-analysis` - 数据分析
- `frontend-design` - 前端设计
- `report-generator` - 报告生成