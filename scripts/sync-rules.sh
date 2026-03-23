#!/bin/bash
# 同步 Claude 规则到各编辑器
# 用法: ./sync-rules.sh

set -e

CLAUDE_DIR="$HOME/.claude"
RULES_SOURCE="$CLAUDE_DIR/rules"

# 目标编辑器
EDITORS=("cursor" "windsurf" "trae")

echo "🔄 开始同步 Claude 规则..."

# 同步核心规则到各编辑器根目录
for editor in "${EDITORS[@]}"; do
    target="$HOME/.${editor}rules"
    if [ -f "$RULES_SOURCE/RULES_CORE.md" ]; then
        cp "$RULES_SOURCE/RULES_CORE.md" "$target"
        echo "✅ 已同步核心规则到 $target"
    fi
done

# 同步完整规则到各编辑器的 rules 目录
for editor in "${EDITORS[@]}"; do
    target_dir="$HOME/.${editor}/rules"
    mkdir -p "$target_dir"

    if [ -f "$RULES_SOURCE/RULES_BACKEND.md" ]; then
        cp "$RULES_SOURCE/RULES_BACKEND.md" "$target_dir/backend.md"
    fi

    if [ -f "$RULES_SOURCE/RULES_FRONTEND.md" ]; then
        cp "$RULES_SOURCE/RULES_FRONTEND.md" "$target_dir/frontend.md"
    fi

    echo "✅ 已同步完整规则到 $target_dir/"
done

echo ""
echo "📊 同步完成统计:"
echo "   - 核心规则: ~/.cursorrules, ~/.windsurfrules, ~/.traerules"
echo "   - 完整规则: ~/.cursor/rules/, ~/.windsurf/rules/, ~/.trae/rules/"