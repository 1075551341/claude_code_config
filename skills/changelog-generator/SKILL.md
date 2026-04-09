---
name: changelog-generator
description: 当需要生成变更日志、版本发布说明、提交历史整理、版本更新记录时调用此技能。触发词：变更日志、CHANGELOG、版本日志、发布说明、Release Notes、版本更新记录、提交历史整理、版本历史。
---

# 变更日志生成

## 核心能力

**从 Git 历史自动生成结构化 CHANGELOG。**

---

## 适用场景

- 版本发布说明
- CHANGELOG.md 维护
- 提交历史整理
- 版本更新记录

---

## 生成流程

### 1. 收集变更

```bash
# 获取上次发布后的提交
git log v1.0.0..HEAD --oneline

# 获取带详细信息
git log v1.0.0..HEAD --pretty=format:"%h %s%n%b"

# 按类型分类
git log v1.0.0..HEAD --pretty=format:"%s" | grep -E "^(feat|fix|refactor)"
```

### 2. 分类整理

```
提交类型 → 分类：
- feat → Features（新功能）
- fix → Bug Fixes（修复）
- refactor → Refactoring（重构）
- perf → Performance（性能）
- docs → Documentation（文档）
- test → Tests（测试）
- chore → Maintenance（维护）
```

### 3. 格式化输出

```markdown
## [v1.1.0] - 2024-01-15

### Features
- Add user authentication (#123)
- Implement search functionality (#124)

### Bug Fixes
- Fix login validation error (#125)
- Correct date formatting (#126)

### Performance
- Optimize database query (#127)

### Documentation
- Update API documentation (#128)
```

---

## CHANGELOG 规范

### Keep a Changelog 格式

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- ...

## [1.0.0] - 2024-01-01

### Added
- Initial release

### Changed
- ...

### Deprecated
- ...

### Removed
- ...

### Fixed
- ...

### Security
- ...
```

---

## 自动生成脚本

### Python 示例

```python
import subprocess
from datetime import datetime

def get_commits(from_tag, to_ref='HEAD'):
    cmd = f'git log {from_tag}..{to_ref} --pretty=format:"%h|%s|%an|%ad" --date=short'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip().split('\n')

def categorize(commit_line):
    hash, subject, author, date = commit_line.split('|')
    if subject.startswith('feat'):
        return 'Features', subject.replace('feat:', '').strip()
    elif subject.startswith('fix'):
        return 'Bug Fixes', subject.replace('fix:', '').strip()
    # ...

def generate_changelog(version, from_tag):
    commits = get_commits(from_tag)
    sections = {}
    for c in commits:
        category, desc = categorize(c)
        sections.setdefault(category, []).append(desc)
    
    output = f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n"
    for cat, items in sections.items():
        output += f"### {cat}\n"
        for item in items:
            output += f"- {item}\n"
        output += "\n"
    return output
```

---

## 版本号规则

### Semantic Versioning

```
MAJOR.MINOR.PATCH

- MAJOR: 不兼容的 API 变化
- MINOR: 向后兼容的功能添加
- PATCH: 向后兼容的问题修复
```

---

## 常用工具

| 工具 | 特点 |
|------|------|
| github-changelog-generator | GitHub PR/Issue 集成 |
| git-changelog | 简单 CLI |
| standard-version | 自动版本+CHANGELOG |
| conventional-changelog | Conventional Commits 支持 |

---

## 注意事项

```
必须：
- 使用 Conventional Commits 格式
- 标注版本号和日期
- 包含链接（PR/Issue）
- 维护 Unreleased 区段

避免：
- 手动编辑（优先自动化）
- 隐藏破坏性变更
- 版本号跳跃无理由
- 遗漏重要变更
```

---

## 相关技能

- `git-workflow` - Git 工作流
- `report-generator` - 报告生成
- `doc-coauthoring` - 文档协作