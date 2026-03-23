#!/bin/bash
# 同步 Claude 工具到其他 AI 编辑器
# 用法: ~/.claude/scripts/sync-tools.sh

set -e

CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE_DIR/backups/$(date +%Y%m%d_%H%M%S)"
TARGETS=("cursor" "trae" "windsurf")

# 启用 Windows 原生软链接
export MSYS=winsymlinks:nativestrictly

echo "╔══════════════════════════════════════════╗"
echo "║     Claude 工具同步脚本 v1.0             ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

for target in "${TARGETS[@]}"; do
  TARGET_DIR="$HOME/.$target"

  if [ ! -d "$TARGET_DIR" ]; then
    echo "⚠️  .$target 目录不存在，跳过"
    continue
  fi

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📦 处理 $target..."
  echo ""

  # 备份并处理 skills
  if [ -d "$TARGET_DIR/skills" ]; then
    if [ -L "$TARGET_DIR/skills" ]; then
      echo "  ✅ skills 已是软链接，跳过"
    else
      echo "  📁 备份 skills..."
      cp -r "$TARGET_DIR/skills" "$BACKUP_DIR/${target}_skills/"
      rm -rf "$TARGET_DIR/skills"
      echo "  🗑️  删除旧目录"
    fi
  fi

  if [ ! -L "$TARGET_DIR/skills" ]; then
    echo "  🔗 创建 skills 软链接..."
    ln -s "$CLAUDE_DIR/skills" "$TARGET_DIR/skills"
    echo "  ✅ skills 同步完成"
  fi

  # 处理 agents
  if [ -d "$TARGET_DIR/agents" ]; then
    if [ -L "$TARGET_DIR/agents" ]; then
      echo "  ✅ agents 已是软链接，跳过"
    else
      echo "  📁 备份 agents..."
      cp -r "$TARGET_DIR/agents" "$BACKUP_DIR/${target}_agents/"
      rm -rf "$TARGET_DIR/agents"
      echo "  🗑️  删除旧目录"
    fi
  fi

  if [ ! -L "$TARGET_DIR/agents" ]; then
    echo "  🔗 创建 agents 软链接..."
    ln -s "$CLAUDE_DIR/agents" "$TARGET_DIR/agents"
    echo "  ✅ agents 同步完成"
  fi

  echo ""
  echo "  📊 $target 统计:"
  echo "     - Skills: $(ls $TARGET_DIR/skills 2>/dev/null | wc -l) 个"
  echo "     - Agents: $(ls $TARGET_DIR/agents 2>/dev/null | wc -l) 个"
  echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 同步完成！"
echo ""
echo "📂 备份位置: $BACKUP_DIR"
echo ""
echo "💡 提示:"
echo "   - 新增 skill 请在 ~/.claude/skills/ 添加"
echo "   - 删除软链接: rm ~/.cursor/skills ~/.trae/skills ~/.windsurf/skills"
echo "   - 重新同步: 运行此脚本即可"