#!/bin/bash
# sync.sh v2.0 - Linux/macOS 同步脚本（v14 索引模式）
# 全量格式转换（rules/skills-native）请使用 Windows sync.ps1 -Full

set -e

CLAUDE_DIR="$HOME/.claude"
SYNC_DIRS=("skills" "agents")
SYNC_FILES=("CLAUDE.md" "CLAUDE-ROUTER.mdc" "SPEC.md" "MANIFEST.yaml" "skills-INDEX.md" "agents-INDEX.md" "rules-INDEX.md")
EDITORS=("cursor" "windsurf" "trae" "qoder")
FULL_MODE=false

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

usage() {
    echo "用法: $0 {sync|verify|cleanup|full} [days]"
    echo "  sync    - 索引模式：7总纲软链接 + skills/agents/rules 目录联接 + 路由规则部署"
    echo "  full    - 提示：Full 格式转换请用 sync.ps1 -Full（Windows）"
    echo "  verify  - 验证同步状态"
    echo "  cleanup - 清理旧备份（默认30天）"
}

check_source() {
    if [ ! -d "$CLAUDE_DIR" ]; then
        log_error "Claude 目录不存在: $CLAUDE_DIR"
        exit 1
    fi
    log_info "源目录: $CLAUDE_DIR"
}

create_symlink() {
    local src="$1"
    local target="$2"

    if [ -L "$target" ]; then
        local current_target
        current_target=$(readlink -f "$target" 2>/dev/null || readlink "$target")
        if [ "$current_target" = "$src" ]; then
            log_info "  软连接已正确: $(basename "$target")"
            return 0
        else
            log_warn "  软连接目标不一致，重建: $(basename "$target")"
            rm -f "$target"
        fi
    elif [ -e "$target" ]; then
        log_warn "  存在实体路径，备份: $(basename "$target")"
        mv "$target" "${target}.bak.$(date +%Y%m%d%H%M%S)"
    fi

    ln -sf "$src" "$target"
    log_info "  已创建软连接: $(basename "$target")"
}

write_sync_mode() {
    local target_dir="$1"
    local mode="$2"
    local path="$target_dir/sync-mode.json"
    cat > "$path" <<EOF
{"mode":"$mode","version":"14.0","updated":"$(date -Iseconds)","source":"$CLAUDE_DIR"}
EOF
    log_info "  已写入 sync-mode.json ($mode)"
}

deploy_router_rules() {
    log_warn "索引模式 rules/ 单文件链接 + 路由部署请用 Windows sync.ps1（不写回 ~/.claude/rules/）"
}

sync_to_editor() {
    local editor="$1"
    local target_dir="$HOME/.$editor"

    if [ ! -d "$target_dir" ]; then
        log_warn "编辑器目录不存在，跳过: $editor"
        return 0
    fi

    log_info "同步到 $editor（索引模式）..."

    for file in "${SYNC_FILES[@]}"; do
        local src_path="$CLAUDE_DIR/$file"
        local target_path="$target_dir/$file"
        if [ -f "$src_path" ]; then
            create_symlink "$src_path" "$target_path"
        fi
    done

    for dir in "${SYNC_DIRS[@]}"; do
        local src_path="$CLAUDE_DIR/$dir"
        local target_path="$target_dir/$dir"
        if [ -d "$src_path" ]; then
            create_symlink "$src_path" "$target_path"
        fi
    done

    write_sync_mode "$target_dir" "index"
}

full_mode_notice() {
    log_warn "Full 模式（rules/skills 格式转换）需在 Windows 运行:"
    log_warn "  powershell -ExecutionPolicy Bypass -File ~/.claude/scripts/sync.ps1 -Full -Force"
}

verify_sync() {
    log_info "验证同步完整性..."
    local errors=0

    for editor in "${EDITORS[@]}"; do
        local target_dir="$HOME/.$editor"
        [ -d "$target_dir" ] || continue

        for file in "${SYNC_FILES[@]}"; do
            local link_path="$target_dir/$file"
            if [ ! -L "$link_path" ]; then
                log_error "$editor/$file 不是软连接"
                ((errors++))
            fi
        done

        for dir in "${SYNC_DIRS[@]}"; do
            local link_path="$target_dir/$dir"
            if [ -L "$link_path" ]; then
                local actual_target
                actual_target=$(readlink -f "$link_path" 2>/dev/null || readlink "$link_path")
                if [ "$actual_target" != "$CLAUDE_DIR/$dir" ]; then
                    log_error "$editor/$dir 软连接目标不一致"
                    ((errors++))
                fi
            elif [ -d "$link_path" ]; then
                log_error "$editor/$dir 是实体目录而非软连接"
                ((errors++))
            else
                log_error "$editor/$dir 缺失"
                ((errors++))
            fi
        done
    done

    if [ $errors -eq 0 ]; then
        log_info "✅ 同步验证通过"
    else
        log_error "❌ 发现 $errors 个问题"
    fi
}

cleanup_backups() {
    local days=${1:-30}
    log_info "清理超过 $days 天的备份..."
    for editor in "${EDITORS[@]}"; do
        local target_dir="$HOME/.$editor"
        if [ -d "$target_dir" ]; then
            find "$target_dir" -name "*.bak.*" -mtime +"$days" -delete 2>/dev/null || true
        fi
    done
    log_info "备份清理完成"
}

main() {
    local action="${1:-sync}"

    case "$action" in
        sync)
            check_source
            for editor in "${EDITORS[@]}"; do
                sync_to_editor "$editor"
            done
            deploy_router_rules
            verify_sync
            log_info "✅ 索引同步完成"
            ;;
        full)
            full_mode_notice
            ;;
        verify)
            verify_sync
            ;;
        cleanup)
            cleanup_backups "${2:-30}"
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

main "$@"
