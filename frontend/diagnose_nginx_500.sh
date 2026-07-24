#!/bin/bash
# 小鲁班前端 Nginx 500错误诊断脚本
# 用法: ./diagnose_nginx_500.sh [日志文件路径]
# 示例: ./diagnose_nginx_500.sh /tmp/nginx_debug.log

# 自动转换Windows换行符(CRLF)为Unix换行符(LF)
SCRIPT_PATH="$0"
if file "$SCRIPT_PATH" | grep -q "CRLF\|with CR line terminators"; then
    echo "检测到Windows换行符，正在自动转换..."
    sed -i 's/\r$//' "$SCRIPT_PATH"
    echo "换行符转换完成，请重新执行脚本"
    exit 0
fi

# ==================== 配置区域 ====================
LOG_FILE="${1:-/home/xiaoluban/logs/nginx_diagnose_$(date +%Y%m%d_%H%M%S).log}"
FRONTEND_DIR="/home/xiaoluban/frontend"
DIST_DIR="$FRONTEND_DIR/dist"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ==================== 初始化 ====================

init() {
    # 创建日志目录
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # 清空日志文件
    > "$LOG_FILE"
    
    # 同时输出到控制台和日志文件
    exec > >(tee -a "$LOG_FILE")
    exec 2>&1
    
    echo "=================================================="
    echo "小鲁班前端 Nginx 500错误诊断脚本"
    echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "服务器: $(hostname)"
    echo "IP地址: $(hostname -I | awk '{print $1}')"
    echo "日志文件: $LOG_FILE"
    echo "=================================================="
    echo ""
}

# ==================== 工具函数 ====================

print_section() {
    echo ""
    echo "========================================"
    echo "$1"
    echo "========================================"
}

check_pass() {
    echo "${GREEN}[✓]${NC} $1"
}

check_fail() {
    echo "${RED}[✗]${NC} $1"
}

check_warn() {
    echo "${YELLOW}[!]${NC} $1"
}

# ==================== 诊断函数 ====================

check_nginx_status() {
    print_section "1. Nginx 服务状态"
    
    if systemctl is-active --quiet nginx; then
        check_pass "Nginx 服务正在运行"
        systemctl status nginx --no-pager | head -10
    else
        check_fail "Nginx 服务未运行"
        systemctl status nginx --no-pager
    fi
}

check_nginx_error_log() {
    print_section "2. Nginx 错误日志 (最近50行)"
    
    if [ -f /var/log/nginx/error.log ]; then
        tail -50 /var/log/nginx/error.log
    else
        check_warn "/var/log/nginx/error.log 不存在"
        
        # 查找其他可能的错误日志位置
        if [ -f /home/xiaoluban/logs/nginx/xiaoluban-error.log ]; then
            echo "找到项目错误日志:"
            tail -50 /home/xiaoluban/logs/nginx/xiaoluban-error.log
        fi
    fi
}

check_directory_structure() {
    print_section "3. 前端目录结构"
    
    echo "检查 /home/xiaoluban/"
    ls -la /home/xiaoluban/ 2>&1
    
    echo ""
    echo "检查 $FRONTEND_DIR/"
    if [ -d "$FRONTEND_DIR" ]; then
        ls -la "$FRONTEND_DIR/" 2>&1
        check_pass "前端目录存在"
    else
        check_fail "前端目录不存在: $FRONTEND_DIR"
    fi
}

check_dist_directory() {
    print_section "4. Dist 目录检查"
    
    if [ -d "$DIST_DIR" ]; then
        check_pass "dist目录存在"
        ls -la "$DIST_DIR/" 2>&1
        
        # 检查关键文件
        echo ""
        if [ -f "$DIST_DIR/index.html" ]; then
            check_pass "index.html 存在"
            echo "文件大小: $(du -h $DIST_DIR/index.html | cut -f1)"
        else
            check_fail "index.html 不存在"
        fi
        
        # 检查assets目录
        if [ -d "$DIST_DIR/assets" ]; then
            check_pass "assets目录存在"
            echo "assets文件数: $(find $DIST_DIR/assets -type f | wc -l)"
        else
            check_fail "assets目录不存在"
        fi
    else
        check_fail "dist目录不存在: $DIST_DIR"
        check_warn "请先执行: cd $FRONTEND_DIR && npm run build"
    fi
}

check_nginx_config() {
    print_section "5. Nginx 配置检查"
    
    echo "测试配置语法..."
    if nginx -t 2>&1; then
        check_pass "Nginx配置语法正确"
    else
        check_fail "Nginx配置语法错误"
    fi
    
    echo ""
    echo "配置文件列表:"
    ls -la /etc/nginx/conf.d/ 2>&1
    
    echo ""
    if [ -f /etc/nginx/conf.d/xiaoluban-frontend.conf ]; then
        check_pass "前端配置文件存在"
        echo ""
        echo "配置文件内容:"
        echo "----------------------------------------"
        cat /etc/nginx/conf.d/xiaoluban-frontend.conf
        echo "----------------------------------------"
    else
        check_fail "前端配置文件不存在"
        check_warn "请复制配置文件: cp $FRONTEND_DIR/nginx.conf.example /etc/nginx/conf.d/xiaoluban-frontend.conf"
    fi
}

check_file_permissions() {
    print_section "6. 文件权限检查"
    
    if [ -f "$DIST_DIR/index.html" ]; then
        echo "index.html 权限:"
        ls -l "$DIST_DIR/index.html"
        
        echo ""
        echo "权限链检查:"
        namei -l "$DIST_DIR/index.html" 2>&1
    else
        check_fail "无法检查权限 - index.html不存在"
    fi
}

check_selinux() {
    print_section "7. SELinux 检查"
    
    if command -v getenforce &> /dev/null; then
        SELINUX_STATUS=$(getenforce 2>&1)
        echo "SELinux状态: $SELINUX_STATUS"
        
        if [ "$SELINUX_STATUS" = "Enforcing" ]; then
            check_warn "SELinux 正在强制执行 - 可能会阻止文件访问"
            echo ""
            echo "临时关闭命令: setenforce 0"
            echo "查看拒绝日志: ausearch -m avc -ts recent | tail -20"
            
            # 检查SELinux拒绝日志
            if command -v ausearch &> /dev/null; then
                echo ""
                echo "最近的SELinux拒绝记录:"
                ausearch -m avc -ts recent 2>&1 | tail -20 || echo "无拒绝记录"
            fi
        elif [ "$SELINUX_STATUS" = "Permissive" ]; then
            check_warn "SELinux 处于宽容模式 - 记录但不阻止"
        else
            check_pass "SELinux 已禁用"
        fi
    else
        check_pass "SELinux 未安装（非CentOS/RHEL系统）"
    fi
}

check_nginx_user() {
    print_section "8. Nginx 用户检查"
    
    echo "Nginx 进程:"
    ps aux | grep nginx | grep -v grep
    
    echo ""
    echo "Nginx配置的用户:"
    grep "^user" /etc/nginx/nginx.conf 2>&1 || echo "未找到user配置"
    
    echo ""
    echo "测试以nginx用户读取文件:"
    if id "nginx" &>/dev/null; then
        sudo -u nginx cat "$DIST_DIR/index.html" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            check_pass "nginx用户可以读取index.html"
        else
            check_fail "nginx用户无法读取index.html"
            check_warn "修复命令: chown -R nginx:nginx $DIST_DIR/"
        fi
    elif id "www-data" &>/dev/null; then
        sudo -u www-data cat "$DIST_DIR/index.html" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            check_pass "www-data用户可以读取index.html"
        else
            check_fail "www-data用户无法读取index.html"
            check_warn "修复命令: chown -R www-data:www-data $DIST_DIR/"
        fi
    else
        check_warn "未找到nginx或www-data用户"
    fi
}

check_port_binding() {
    print_section "9. 端口监听检查"
    
    echo "9000端口监听状态:"
    netstat -tlnp | grep :9000 2>&1 || ss -tlnp | grep :9000 2>&1 || lsof -i :9000 2>&1
    
    echo ""
    echo "所有Nginx监听端口:"
    netstat -tlnp | grep nginx 2>&1 || ss -tlnp | grep nginx 2>&1
}

check_connectivity() {
    print_section "10. 连通性测试"
    
    echo "本地访问测试:"
    curl -I http://localhost:9000 2>&1
    
    echo ""
    echo "HTML内容测试:"
    curl -s http://localhost:9000 | head -20
}

# ==================== 修复建议 ====================

print_recommendations() {
    print_section "11. 修复建议"
    
    echo "根据以上诊断结果，建议按以下顺序修复："
    echo ""
    echo "1. 如果dist目录不存在，执行："
    echo "   cd $FRONTEND_DIR"
    echo "   npm install"
    echo "   npm run build"
    echo ""
    echo "2. 如果文件权限错误，执行："
    echo "   chmod -R 755 $DIST_DIR/"
    echo "   chown -R nginx:nginx $DIST_DIR/  # CentOS"
    echo "   # 或"
    echo "   chown -R www-data:www-data $DIST_DIR/  # Ubuntu"
    echo ""
    echo "3. 如果SELinux阻止，执行："
    echo "   setenforce 0  # 临时关闭"
    echo "   # 或"
    echo "   semanage fcontext -a -t httpd_sys_content_t \"$DIST_DIR(/.*)?\""
    echo "   restorecon -Rv $DIST_DIR/"
    echo ""
    echo "4. 如果Nginx配置不存在，执行："
    echo "   cp $FRONTEND_DIR/nginx.conf.example /etc/nginx/conf.d/xiaoluban-frontend.conf"
    echo "   nginx -t"
    echo "   systemctl restart nginx"
    echo ""
    echo "5. 重启服务："
    echo "   systemctl restart nginx"
    echo "   systemctl status nginx"
}

# ==================== 主流程 ====================

main() {
    init
    
    check_nginx_status
    check_nginx_error_log
    check_directory_structure
    check_dist_directory
    check_nginx_config
    check_file_permissions
    check_selinux
    check_nginx_user
    check_port_binding
    check_connectivity
    print_recommendations
    
    echo ""
    echo "=================================================="
    echo "诊断完成"
    echo "日志已保存到: $LOG_FILE"
    echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=================================================="
    
    # 显示如何查看日志
    echo ""
    echo "查看完整日志:"
    echo "  cat $LOG_FILE"
    echo ""
    echo "搜索错误关键词:"
    echo "  grep -i 'error\|fail\|denied' $LOG_FILE"
}

# 执行主流程
main