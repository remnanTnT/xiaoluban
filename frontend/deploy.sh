#!/bin/bash
# 小鲁班前端自动部署脚本
# 用法: ./deploy.sh [环境]
# 示例: ./deploy.sh production

set -e  # 遇到错误立即退出

# ==================== 配置区域 ====================
DEPLOY_DIR="/home/xiaoluban/frontend"
LOG_DIR="/home/xiaoluban/logs"
LOG_FILE="$LOG_DIR/deploy.log"
BACKUP_DIR="$DEPLOY_DIR/backups"

# 后端API地址配置（根据环境修改）
PRODUCTION_API="http://your-production-server:8000"
TEST_API="http://7.197.65.7:8000"

# ==================== 工具函数 ====================

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

error_exit() {
    log "❌ 错误: $1"
    exit 1
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        error_exit "命令 '$1' 未安装，请先安装"
    fi
}

# ==================== 环境检查 ====================

check_environment() {
    log "===== 环境检查 ====="
    
    # 检查必要命令
    check_command "node"
    check_command "npm"
    check_command "git"
    
    # 检查Node版本
    NODE_VERSION=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        error_exit "Node.js 版本过低 ($NODE_VERSION)，需要 16.x 或更高"
    fi
    log "✓ Node.js 版本: $(node -v)"
    
    # 检查目录
    if [ ! -d "$DEPLOY_DIR" ]; then
        error_exit "部署目录不存在: $DEPLOY_DIR"
    fi
    
    # 创建必要目录
    mkdir -p "$LOG_DIR"
    mkdir -p "$BACKUP_DIR"
    
    log "✓ 环境检查通过"
}

# ==================== 部署步骤 ====================

backup_dist() {
    log "1. 备份当前版本..."
    
    if [ -d "$DEPLOY_DIR/dist" ]; then
        BACKUP_NAME="dist.backup.$(date +%Y%m%d_%H%M%S)"
        cp -r "$DEPLOY_DIR/dist" "$BACKUP_DIR/$BACKUP_NAME"
        log "✓ 已备份到: $BACKUP_DIR/$BACKUP_NAME"
    else
        log "  dist目录不存在，跳过备份"
    fi
}

pull_code() {
    log "2. 拉取最新代码..."
    
    cd "$DEPLOY_DIR"
    
    # 检查是否是Git仓库
    if [ -d ".git" ]; then
        git fetch origin
        git status
        git pull origin main || error_exit "代码拉取失败"
        log "✓ 代码已更新"
    else
        log "  不是Git仓库，跳过拉取"
    fi
}

install_dependencies() {
    log "3. 安装依赖..."
    
    cd "$DEPLOY_DIR"
    
    # 检查package.json是否有变化
    if [ "package.json" -nt "package-lock.json" ] || [ ! -d "node_modules" ]; then
        npm install --production=false || error_exit "依赖安装失败"
        log "✓ 依赖安装完成"
    else
        log "  依赖无变化，跳过安装"
    fi
}

build_project() {
    log "4. 构建项目..."
    
    cd "$DEPLOY_DIR"
    
    # 根据环境设置API地址
    ENV="${1:-production}"
    if [ "$ENV" = "production" ]; then
        export VITE_API_BASE_URL="$PRODUCTION_API"
        log "  使用生产环境API: $PRODUCTION_API"
    else
        export VITE_API_BASE_URL="$TEST_API"
        log "  使用测试环境API: $TEST_API"
    fi
    
    # 执行构建
    npm run build || error_exit "构建失败"
    
    # 验证构建产物
    if [ ! -f "dist/index.html" ]; then
        error_exit "构建失败: dist/index.html 不存在"
    fi
    
    log "✓ 构建完成"
}

verify_build() {
    log "5. 验证构建产物..."
    
    cd "$DEPLOY_DIR/dist"
    
    # 检查关键文件
    local files=("index.html")
    local missing_files=()
    
    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        error_exit "缺少关键文件: ${missing_files[*]}"
    fi
    
    # 检查assets目录
    if [ ! -d "assets" ]; then
        error_exit "assets目录不存在"
    fi
    
    # 统计文件数量
    local js_count=$(find assets -name "*.js" 2>/dev/null | wc -l)
    local css_count=$(find assets -name "*.css" 2>/dev/null | wc -l)
    
    log "✓ 构建产物验证通过"
    log "  - JavaScript文件: $js_count 个"
    log "  - CSS文件: $css_count 个"
}

reload_nginx() {
    log "6. 重载Nginx配置..."
    
    # 测试Nginx配置
    if sudo nginx -t; then
        # 重载Nginx
        sudo systemctl reload nginx || error_exit "Nginx重载失败"
        log "✓ Nginx配置已重载"
    else
        error_exit "Nginx配置测试失败"
    fi
}

show_result() {
    log ""
    log "===== 部署成功 ====="
    log "✅ 部署路径: $DEPLOY_DIR/dist"
    log "✅ 访问地址: http://localhost:9000"
    log "✅ API地址: ${VITE_API_BASE_URL:-未设置}"
    log ""
    log "查看日志:"
    log "  - 访问日志: tail -f $LOG_DIR/nginx/xiaoluban-access.log"
    log "  - 错误日志: tail -f $LOG_DIR/nginx/xiaoluban-error.log"
    log "  - 部署日志: tail -f $LOG_FILE"
    log ""
}

# ==================== 主流程 ====================

main() {
    log ""
    log "========================================"
    log "  小鲁班前端部署脚本"
    log "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    log "========================================"
    log ""
    
    # 环境检查
    check_environment
    
    # 执行部署步骤
    backup_dist
    pull_code
    install_dependencies
    build_project "$1"
    verify_build
    reload_nginx
    
    # 显示结果
    show_result
    
    log "===== 部署完成 ====="
}

# ==================== 执行入口 ====================

# 检查是否在正确的目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$SCRIPT_DIR" != "$DEPLOY_DIR" ]; then
    echo "⚠️  警告: 脚本目录 ($SCRIPT_DIR) 与配置目录 ($DEPLOY_DIR) 不一致"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 执行主流程
main "$@"