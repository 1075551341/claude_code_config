#!/bin/bash
# sync.sh v2.3 - Linux/macOS 同步脚本（v14.5 仅L0入口 + 个人级单落点）
# v2.3: 根文件集合补 agent.yaml 并与 sync.ps1/check.ps1 统一；workbuddy 仅接收 CLAUDE.md
#
# 全部命令：
#   bash scripts/sync.sh sync           # 8 个总纲根文件软链 + skills/agents/rules 目录联接 + 路由规则部署
#   bash scripts/sync.sh verify         # 只读验证同步状态，不写盘
#   bash scripts/sync.sh cleanup [days] # 清理旧备份，默认 30 天
#   bash scripts/sync.sh full           # 提示信息：全量格式转换须在 Windows 用 sync.ps1 -All
#
# 平台差异：本脚本不做 rules 扩展名转换（.md/.mdc）与 Cursor 插件副本刷新，
#           这两项仅 Windows sync.ps1 具备。健康检查同样只有 check.ps1（Windows）。

set -e

CLAUDE_DIR="$HOME/.claude"
SYNC_DIRS=("skills" "agents")
# 与 sync.ps1 $L0_ROOT_ITEMS / check.ps1 $SYNC_FILES / impact_sync.SYNC_FILES 保持同一集合（8 项）
SYNC_FILES=("CLAUDE.md" "CLAUDE-ROUTER.mdc" "SPEC.md" "MANIFEST.yaml" "agent.yaml" "skills-INDEX.md" "agents-INDEX.md" "rules-INDEX.md")
EDITORS=("cursor" "qoder" "qoder-cn" "trae" "trae-cn" "workbuddy" "codearts")
# workbuddy 无 rules 通道且根目录归其 BOOTSTRAP 契约所有，仅接收 CLAUDE.md
ROOT_INDEX_SKIP_EDITORS=("workbuddy")
FULL_MODE=false

editor_home() {
    case "$1" in
        codearts) echo "$HOME/.codeartsdoer" ;;
        *) echo "$HOME/.$1" ;;
    esac
}

skips_root_index() {
    local editor="$1"
    local skip
    for skip in "${ROOT_INDEX_SKIP_EDITORS[@]}"; do
        [ "$editor" = "$skip" ] && return 0
    done
    return 1
}

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

usage() {
    echo "用法: $0 {sync|verify|cleanup|full} [days]"
    echo "  sync    - 索引模式：8 个总纲根文件软链接 + skills/agents/rules 目录联接 + 路由规则部署"
    echo "  full    - 提示：Full 格式转换请用 sync.ps1 -All（Windows）"
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

remove_same_type_target() {
    # 仅删除与目标同路径、同扩展名的文件/链接（不跨目录、不删其他类型）
    local target="$1"
    local scope="${2:-sync}"
    if [ ! -e "$target" ] && [ ! -L "$target" ]; then
        return 0
    fi
    log_warn "  删除 ${scope}/$(basename "$target")（同类型同名）"
    rm -f "$target" 2>/dev/null || true
}

create_symlink() {
    local src="$1"
    local target="$2"
    local scope="${3:-$(basename "$(dirname "$target")")}"

    if [ -L "$target" ]; then
        local current_target
        current_target=$(readlink -f "$target" 2>/dev/null || readlink "$target")
        if [ "$current_target" = "$src" ]; then
            log_info "  软连接已正确: $(basename "$target")"
            return 0
        fi
    fi

    remove_same_type_target "$target" "$scope"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
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
{"mode":"$mode","version":"14.1","updated":"$(date -Iseconds)","source":"$CLAUDE_DIR"}
EOF
    log_info "  已写入 sync-mode.json ($mode)"
}

deploy_router_rules() {
    log_warn "索引模式 rules/ 单文件链接 + 路由部署请用 Windows sync.ps1（不写回 ~/.claude/rules/）"
}

sync_to_editor() {
    local editor="$1"
    local target_dir
    target_dir="$(editor_home "$editor")"

    if [ ! -d "$target_dir" ]; then
        log_warn "编辑器目录不存在，跳过: $editor"
        return 0
    fi

    log_info "同步到 $editor（索引模式）..."

    for file in "${SYNC_FILES[@]}"; do
        if [ "$file" != "CLAUDE.md" ] && skips_root_index "$editor"; then
            continue
        fi
        local src_path="$CLAUDE_DIR/$file"
        local target_path="$target_dir/$file"
        if [ -f "$src_path" ]; then
            create_symlink "$src_path" "$target_path" "root"
        fi
    done

    for dir in "${SYNC_DIRS[@]}"; do
        local src_path="$CLAUDE_DIR/$dir"
        local target_path="$target_dir/$dir"
        if [ -d "$src_path" ]; then
            create_symlink "$src_path" "$target_path" "$dir"
        fi
    done

    write_sync_mode "$target_dir" "index"
}

full_mode_notice() {
    log_warn "Full 模式（rules/skills 格式转换）需在 Windows 运行:"
    log_warn "  powershell -ExecutionPolicy Bypass -File ~/.claude/scripts/sync.ps1 -All"
}

verify_sync() {
    log_info "验证同步完整性..."
    local errors=0

    for editor in "${EDITORS[@]}"; do
        local target_dir
        target_dir="$(editor_home "$editor")"
        [ -d "$target_dir" ] || continue

        for file in "${SYNC_FILES[@]}"; do
            if [ "$file" != "CLAUDE.md" ] && skips_root_index "$editor"; then
                continue
            fi
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
        local target_dir
        target_dir="$(editor_home "$editor")"
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
