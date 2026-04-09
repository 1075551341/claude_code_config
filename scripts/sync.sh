#!/bin/bash
# sync.sh v1.0 - Linux/macOS 同步脚本
# 同步 ~/.claude 内容到各编辑器目录

set -e

# 配置
CLAUDE_DIR="$HOME/.claude"
SYNC_DIRS=("skills" "agents" "rules")
COPY_FILE="CLAUDE.md"
EDITORS=("cursor" "windsurf" "trae" "qoder")

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查源目录
check_source() {
    if [ ! -d "$CLAUDE_DIR" ]; then
        log_error "Claude 目录不存在: $CLAUDE_DIR"
        exit 1
    fi
    log_info "源目录: $CLAUDE_DIR"
}

# 创建软连接
create_symlink() {
    local src="$1"
    local target="$2"

    if [ -L "$target" ]; then
        # 已存在软连接，检查目标
        local current_target=$(readlink -f "$target" 2>/dev/null || readlink "$target")
        if [ "$current_target" = "$src" ]; then
            log_info "  软连接已正确: $(basename $target)"
            return 0
        else
            log_warn "  软连接目标不一致，重建: $(basename $target)"
            rm -f "$target"
        fi
    elif [ -d "$target" ]; then
        # 存在真实目录，备份后替换
        log_warn "  存在真实目录，备份: $(basename $target)"
        mv "$target" "${target}.bak.$(date +%Y%m%d%H%M%S)"
    fi

    ln -sf "$src" "$target"
    log_info "  已创建软连接: $(basename $target)"
}

# 复制文件
copy_file() {
    local src="$1"
    local target="$2"

    if [ -f "$src" ]; then
        cp "$src" "$target"
        log_info "  已复制: $(basename $target)"
    fi
}

# 同步到编辑器
sync_to_editor() {
    local editor="$1"
    local target_dir="$HOME/.$editor"

    if [ ! -d "$target_dir" ]; then
        log_warn "编辑器目录不存在，跳过: $editor"
        return 0
    fi

    log_info "同步到 $editor..."

    # 同步目录（软连接）
    for dir in "${SYNC_DIRS[@]}"; do
        local src_path="$CLAUDE_DIR/$dir"
        local target_path="$target_dir/$dir"

        if [ -d "$src_path" ]; then
            create_symlink "$src_path" "$target_path"
        fi
    done

    # 复制 CLAUDE.md
    copy_file "$CLAUDE_DIR/$COPY_FILE" "$target_dir/$COPY_FILE"

    # 设置环境变量标记
    set_editor_env "$target_dir" "$editor"
}

# 设置编辑器环境变量
set_editor_env() {
    local target_dir="$1"
    local editor="$2"
    local settings_file="$target_dir/settings.json"

    if [ -f "$settings_file" ]; then
        # 检查 jq 是否可用
        if command -v jq &> /dev/null; then
            local temp_file=$(mktemp)
            jq ".env.CLAUDE_IN_EDITOR = \"$editor\"" "$settings_file" > "$temp_file"
            mv "$temp_file" "$settings_file"
            log_info "  已设置 CLAUDE_IN_EDITOR=$editor"
        else
            log_warn "  jq 未安装，跳过环境变量设置"
        fi
    fi
}

# 验证同步
verify_sync() {
    log_info "验证同步完整性..."
    local errors=0

    for editor in "${EDITORS[@]}"; do
        local target_dir="$HOME/.$editor"
        if [ ! -d "$target_dir" ]; then
            continue
        fi

        for dir in "${SYNC_DIRS[@]}"; do
            local link_path="$target_dir/$dir"
            if [ -L "$link_path" ]; then
                local actual_target=$(readlink -f "$link_path" 2>/dev/null || readlink "$link_path")
                if [ "$actual_target" != "$CLAUDE_DIR/$dir" ]; then
                    log_error "$editor/$dir 软连接目标不一致"
                    ((errors++))
                fi
            elif [ -d "$link_path" ]; then
                log_error "$editor/$dir 是真实目录而非软连接"
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

# 清理备份
cleanup_backups() {
    local days=${1:-30}
    log_info "清理超过 $days 天的备份..."

    for editor in "${EDITORS[@]}"; do
        local target_dir="$HOME/.$editor"
        if [ -d "$target_dir" ]; then
            find "$target_dir" -name "*.bak.*" -mtime +$days -delete 2>/dev/null
        fi
    done
    log_info "备份清理完成"
}

# 主函数
main() {
    local action="${1:-sync}"

    case "$action" in
        sync)
            check_source
            for editor in "${EDITORS[@]}"; do
                sync_to_editor "$editor"
            done
            verify_sync
            log_info "✅ 同步完成"
            ;;
        verify)
            verify_sync
            ;;
        cleanup)
            cleanup_backups "${2:-30}"
            ;;
        *)
            echo "用法: $0 {sync|verify|cleanup [days]}"
            echo "  sync   - 执行同步"
            echo "  verify - 验证同步状态"
            echo "  cleanup - 清理旧备份（默认30天）"
            exit 1
            ;;
    esac
}

main "$@"