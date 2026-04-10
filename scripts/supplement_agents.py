#!/usr/bin/env python3
"""Batch supplement missing advantages from deleted agents to target agents."""
import os

base = r'C:\Users\DELL\.claude\agents'

# Define supplements: (target_file, append_content)
supplements = []

# 1. doc-generator: add doc-updater's checklist and templates
doc_gen_path = os.path.join(base, 'doc-generator.md')
if os.path.exists(doc_gen_path):
    with open(doc_gen_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if '文档更新检查清单' not in content:
        supplements.append(('doc-generator.md', """

## 文档更新检查清单

代码变更时: □ 更新README功能列表 □ 更新API文档 □ 更新代码注释 □ 更新CHANGELOG □ 检查文档链接 □ 验证准确性

发布新版本时: □ 更新版本号 □ 记录变更 □ 更新迁移指南 □ 检查过期信息

## 文档验证

```bash
markdown-link-check README.md  # 检查链接
markdownlint *.md              # 检查格式
cspell *.md                    # 检查拼写
```
"""))

# 2. git-expert: add git-workflow's branch strategies and merge strategies
git_expert_path = os.path.join(base, 'git-expert.md')
if os.path.exists(git_expert_path):
    with open(git_expert_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if '分支策略' not in content:
        supplements.append(('git-expert.md', """

## 分支策略对比

| 策略 | 适用 | 分支模型 |
|------|------|----------|
| Git Flow | 版本发布 | main+develop+feature/*+release/*+hotfix/* |
| GitHub Flow | 持续部署 | main+feature/* (PR合并) |
| Trunk Based | 小团队 | main唯一分支+Feature Flags |

## 合并策略对比

| 策略 | 命令 | 优点 | 缺点 |
|------|------|------|------|
| Merge | `git merge feature` | 保留完整历史 | 大量merge commits |
| Rebase | `git rebase main` | 线性历史 | 改变历史，不适合公共分支 |
| Squash | `git merge --squash feature` | 简洁历史 | 丢失详细历史 |

## 冲突解决流程

1. `git status` 识别冲突文件 → `git diff` 查看冲突内容
2. 手动选择/合并代码 → `git add resolved-file` → `git commit`
3. 工具辅助: `code --merge` / `git mergetool --tool=meld`

## Semantic Versioning

`MAJOR.MINOR.PATCH` — MAJOR:不兼容API / MINOR:向下兼容新功能 / PATCH:Bug修复
"""))

# 3. security-reviewer: add OWASP scanning checklist
sec_path = os.path.join(base, 'security-reviewer.md')
if os.path.exists(sec_path):
    with open(sec_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'OWASP' not in content:
        supplements.append(('security-reviewer.md', """

## OWASP Top 10 扫描清单

| 风险 | 检查项 | 修复 |
|------|--------|------|
| A01 权限 | 每个API端点验证权限+所有权 | `findOne({ id, userId: req.user.id })` |
| A02 敏感数据 | HTTPS+加密存储+日志脱敏 | 不记录密码/Token/信用卡号 |
| A03 注入 | 参数化查询+命令参数化 | `db.query('SELECT * FROM users WHERE id=?', [id])` |
| A03 XSS | textContent替代innerHTML | `DOMPurify.sanitize(userInput)` |
| A05 安全配置 | helmet.js+CORS白名单+CSP | 禁用X-Powered-By |
| A06 依赖 | npm audit / pip-audit | 定期更新依赖 |
| A07 认证 | bcrypt(cost≥12)+JWT(≤15min)+HttpOnly | 登录限流(5次失败锁定) |
"""))

# 4. code-reviewer: add quality checklist and 3-phase gate
cr_path = os.path.join(base, 'code-reviewer.md')
if os.path.exists(cr_path):
    with open(cr_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if '命名规范' not in content:
        supplements.append(('code-reviewer.md', """

## 代码质量检查清单

### 命名规范
- 变量/函数: camelCase | 常量: UPPER_SNAKE | 类/组件: PascalCase | 文件: kebab-case | 布尔: is/has/can前缀

### 函数设计
- 单一职责 | ≤50行 | ≤3参数(超过用对象解构) | ≤3层嵌套(提前返回) | 纯函数优先

### 类型安全
- 禁止`any`(用`unknown`) | 参数类型明确 | 返回值显式声明 | 联合类型用类型守卫

### 重复代码
- 相同逻辑2+次→提取函数 | 相同常量→命名常量 | 相似组件→泛化抽象

## 三阶段质量门禁

1. **静默修复**: 格式化+导入排序+简单lint → 自动执行无需确认
2. **补救**: 类型错误+复杂lint+安全漏洞 → 子代理修复+用户确认
3. **报告**: 架构/性能/业务逻辑问题 → 生成报告+标记
"""))

# 5. prompt-engineer: add LLM cost optimization
pe_path = os.path.join(base, 'prompt-engineer.md')
if os.path.exists(pe_path):
    with open(pe_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'Token' not in content:
        supplements.append(('prompt-engineer.md', """

## LLM成本优化

| 技术 | 效果 | 适用场景 |
|------|------|----------|
| Prompt缓存 | 减少50%-90% | 重复请求相似内容 |
| 流式输出 | 降低首字延迟 | 长文本生成 |
| 模型降级 | 成本降低10x | 简单任务用Haiku |
| 批量请求 | API调用减少 | 多条相似查询 |
| 上下文裁剪 | Token减少30% | 长对话历史 |

### Prompt压缩原则
1. 移除冗余空格和换行
2. 用缩写替代重复短语
3. 精简示例数量(保留最具代表性的)
4. 合并相似指令
5. 使用符号替代描述性文字(如`→`替代"然后执行")
"""))

# 6. project-manager: add business analysis frameworks
pm_path = os.path.join(base, 'project-manager.md')
if os.path.exists(pm_path):
    with open(pm_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'AARRR' not in content:
        supplements.append(('project-manager.md', """

## 业务分析框架

### AARRR增长指标
- **获取**: 日新增用户、获客成本(CAC)、渠道流量占比
- **激活**: 注册转化率、新手引导完成率、首单转化率
- **留存**: 次日/7日/30日留存率、DAU/MAU
- **变现**: GMV、ARPU、ARPPU、付费率
- **传播**: 邀请转化率、K因子

### RFM用户分层
- 高价值(R高F高M高): 重点维护 | 潜力(R高F低M低): 培育提频 | 沉睡(R低F高M高): 唤醒营销 | 流失(R低F低M低): 谨慎投入

### A/B测试报告要素
实验名称+周期+分流比例 → 核心指标(对照组/实验组/提升幅度/置信度) → 结论(p<0.05显著)
"""))

# 7. refactoring-expert: add migration scenarios
re_path = os.path.join(base, 'refactoring-expert.md')
if os.path.exists(re_path):
    with open(re_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if '渐进式迁移' not in content:
        supplements.append(('refactoring-expert.md', """

## 渐进式迁移原则

1. **渐进式**(不大爆炸重写): 新功能用新技术，旧代码按优先级逐步迁移，保持新旧共存兼容
2. **测试先行**: 迁移前补充测试覆盖关键行为，迁移后验证行为一致
3. **小步提交**: 每次迁移一个模块，独立PR可回滚
4. **风险降序**: 先迁移低风险高价值代码，复杂业务逻辑最后

## 常见迁移场景

| 场景 | 关键步骤 |
|------|----------|
| JS→TS | allowJs→逐文件重命名→noImplicitAny→strict |
| 类组件→Hooks | 生命周期→useEffect | this.setState→useState | bind→箭头函数 |
| CJS→ESM | require→import | module.exports→export | package.json加type:"module" |
| 回调→async | promisify回调 → Promise链 → async/await |
"""))

# 8. web-tester: add API testing strategies
wt_path = os.path.join(base, 'web-tester.md')
if os.path.exists(wt_path):
    with open(wt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'API测试' not in content:
        supplements.append(('web-tester.md', """

## API测试策略

### 测试层次
1. **功能测试**: 正常CRUD + 分页/过滤/排序
2. **边界测试**: 空数据/最大长度/超出限制/不存在的ID
3. **错误处理**: 400缺参数 / 401无Token / 403权限不足 / 404不存在 / 409重复
4. **安全测试**: SQL注入 / XSS / 越权访问
5. **性能测试**: `ab -n 100 -c 10` → 平均<200ms, P99<1s, 错误率=0%

### curl测试模板
```bash
# GET with auth
curl -s -X GET "http://localhost:3000/api/v1/users" -H "Authorization: Bearer $TOKEN" | jq .

# POST with body
curl -s -w "\\n%{http_code}" -X POST "http://localhost:3000/api/v1/users" -H "Content-Type: application/json" -d '{"username":"test"}'
```
"""))

# Execute all supplements
for filename, append_text in supplements:
    filepath = os.path.join(base, filename)
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(append_text)
    print(f'Supplemented: {filename}')

if not supplements:
    print('No supplements needed (all already present)')
else:
    print(f'Total: {len(supplements)} files supplemented')
