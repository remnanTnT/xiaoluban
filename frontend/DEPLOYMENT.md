# 小鲁班前端部署文档

## 部署概述

- **部署路径**: `/home/xiaoluban/frontend`
- **访问端口**: 9000
- **技术栈**: Vue 3 + Vite
- **构建工具**: Vite 5.x
- **Node版本**: 推荐 18.x 或更高

## 目录结构

部署后的目录结构：
```
/home/xiaoluban/
├── frontend/                    # 前端部署目录
│   ├── dist/                   # 构建产物（由npm run build生成）
│   │   ├── index.html         # 入口HTML
│   │   ├── assets/            # 静态资源
│   │   │   ├── index-*.css    # CSS文件
│   │   │   └── index-*.js     # JS文件
│   │   └── ...
│   ├── DEPLOYMENT.md          # 本文档
│   ├── nginx.conf             # Nginx配置文件
│   └── package.json           # 依赖配置
└── logs/                       # 日志目录（可选）
    └── nginx/
        └── xiaoluban-frontend.log
```

## 一、环境准备

### 1.1 服务器要求

- **操作系统**: Linux (CentOS 7+/Ubuntu 18.04+)
- **Node.js**: 18.x 或更高版本
- **Nginx**: 1.18+ 版本
- **内存**: 建议 512MB+
- **磁盘空间**: 建议 500MB+

### 1.2 安装Node.js

```bash
# 方法一：使用NodeSource仓库（推荐）
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# 方法二：使用NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# 验证安装
node --version    # 应显示 v18.x.x
npm --version     # 应显示 9.x.x 或更高
```

### 1.3 安装Nginx

```bash
# CentOS/RHEL
sudo yum install -y nginx

# Ubuntu/Debian
sudo apt update
sudo apt install -y nginx

# 验证安装
nginx -v  # 应显示 nginx version: nginx/1.x.x
```

## 二、代码部署

### 2.1 创建部署目录

```bash
# 创建目录
sudo mkdir -p /home/xiaoluban/frontend
sudo mkdir -p /home/xiaoluban/logs/nginx

# 设置权限（替换为实际用户）
sudo chown -R $USER:$USER /home/xiaoluban
```

### 2.2 上传代码

**方式一：从Git仓库克隆（推荐）**

```bash
cd /home/xiaoluban
git clone <repository-url> frontend
cd frontend
```

**方式二：使用SCP上传**

```bash
# 在本地开发机器上执行
scp -r dist/ package.json package-lock.json user@server:/home/xiaoluban/frontend/
```

**方式三：使用rsync同步**

```bash
# 在本地开发机器上执行
rsync -avz --exclude 'node_modules' \
  ./frontend/ user@server:/home/xiaoluban/frontend/
```

### 2.3 安装依赖并构建

```bash
cd /home/xiaoluban/frontend

# 安装依赖
npm install --production=false

# 配置后端API地址（生产环境）
export VITE_API_BASE_URL=http://your-backend-server:8000

# 构建生产版本
npm run build

# 验证构建产物
ls -la dist/
# 应该看到 index.html, assets/ 等文件
```

### 2.4 配置环境变量（可选）

如果需要配置后端API地址，可以创建 `.env.production` 文件：

```bash
cat > /home/xiaoluban/frontend/.env.production <<EOF
VITE_API_BASE_URL=http://your-backend-server:8000
EOF
```

## 三、Nginx配置

### 3.1 创建Nginx配置文件

```bash
sudo tee /etc/nginx/conf.d/xiaoluban-frontend.conf <<'EOF'
# 小鲁班前端 - Nginx配置
# 监听端口: 9000
# 部署路径: /home/xiaoluban/frontend/dist

server {
    listen 9000;
    server_name localhost;
    
    # 根目录指向构建产物
    root /home/xiaoluban/frontend/dist;
    index index.html;
    
    # 访问日志
    access_log /home/xiaoluban/logs/nginx/xiaoluban-access.log;
    error_log /home/xiaoluban/logs/nginx/xiaoluban-error.log;
    
    # Gzip压缩配置
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml;
    gzip_disable "msie6";
    
    # 静态资源缓存（1年）
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # 主路由 - 处理Vue Router的history模式
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API反向代理（如果前后端同服务器）
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 错误页面
    error_page 404 /index.html;
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
EOF
```

### 3.2 测试Nginx配置

```bash
# 测试配置语法
sudo nginx -t

# 应该看到：
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 3.3 启动/重启Nginx

```bash
# 检查Nginx状态
sudo systemctl status nginx

# 启动Nginx
sudo systemctl start nginx

# 重启Nginx（配置更改后）
sudo systemctl restart nginx

# 重新加载配置（不中断服务）
sudo systemctl reload nginx

# 设置开机自启
sudo systemctl enable nginx
```

### 3.4 防火墙配置（如需要）

```bash
# CentOS/RHEL - firewalld
sudo firewall-cmd --permanent --add-port=9000/tcp
sudo firewall-cmd --reload

# Ubuntu/Debian - ufw
sudo ufw allow 9000/tcp
sudo ufw reload

# 或使用iptables
sudo iptables -A INPUT -p tcp --dport 9000 -j ACCEPT
sudo service iptables save
```

## 四、部署验证

### 4.1 检查服务状态

```bash
# 检查Nginx进程
ps aux | grep nginx

# 检查端口监听
netstat -tlnp | grep 9000
# 或
ss -tlnp | grep 9000

# 检查文件权限
ls -la /home/xiaoluban/frontend/dist/
```

### 4.2 访问测试

```bash
# 本地测试
curl -I http://localhost:9000

# 应该看到类似输出：
# HTTP/1.1 200 OK
# Server: nginx/1.x.x
# Content-Type: text/html
# ...

# 或使用浏览器访问
# http://your-server-ip:9000
```

### 4.3 查看日志

```bash
# 查看访问日志
tail -f /home/xiaoluban/logs/nginx/xiaoluban-access.log

# 查看错误日志
tail -f /home/xiaoluban/logs/nginx/xiaoluban-error.log

# 查看Nginx主日志
tail -f /var/log/nginx/error.log
```

## 五、更新部署

### 5.1 常规更新流程

```bash
cd /home/xiaoluban/frontend

# 1. 拉取最新代码
git pull origin main

# 2. 安装新依赖（如有）
npm install

# 3. 构建新版本
npm run build

# 4. 无需重启Nginx（静态文件自动生效）
# 如配置有更新：
sudo nginx -t && sudo systemctl reload nginx
```

### 5.2 回滚到上一版本

```bash
cd /home/xiaoluban/frontend

# 方式一：Git回滚
git log --oneline -5  # 查看最近5次提交
git reset --hard <commit-hash>  # 回滚到指定版本
npm run build

# 方式二：保留备份
# 部署前备份
cp -r dist/ dist.backup.$(date +%Y%m%d_%H%M%S)

# 恢复备份
rm -rf dist/
cp -r dist.backup.20260723_100000/ dist/
```

### 5.3 自动化部署脚本

创建 `/home/xiaoluban/frontend/deploy.sh`：

```bash
#!/bin/bash
# 小鲁班前端自动部署脚本

set -e

DEPLOY_DIR="/home/xiaoluban/frontend"
LOG_FILE="/home/xiaoluban/logs/deploy.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cd "$DEPLOY_DIR"

log "===== 开始部署 ====="

log "1. 拉取最新代码..."
git pull origin main

log "2. 安装依赖..."
npm install

log "3. 构建项目..."
npm run build

log "4. 验证构建产物..."
if [ ! -f "dist/index.html" ]; then
    log "错误: 构建失败，dist/index.html 不存在"
    exit 1
fi

log "5. 部署成功!"
log "访问地址: http://localhost:9000"

log "===== 部署完成 ====="
```

```bash
# 添加执行权限
chmod +x /home/xiaoluban/frontend/deploy.sh

# 执行部署
/home/xiaoluban/frontend/deploy.sh
```

## 六、性能优化

### 6.1 启用HTTP/2（推荐）

修改Nginx配置：

```nginx
server {
    listen 9000 http2;  # 添加 http2
    # ... 其他配置
}
```

### 6.2 启用Brotli压缩（需安装模块）

```bash
# 安装nginx-module-brotli（CentOS）
sudo yum install -y nginx-module-brotli

# 配置
# 在nginx.conf顶部添加
load_module modules/ngx_http_brotli_filter_module.so;
load_module modules/ngx_http_brotli_static_module.so;

# 在server块中添加
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css application/javascript application/json;
```

### 6.3 CDN加速（可选）

将静态资源上传到CDN：
- 修改 `vite.config.js` 中的 `base` 配置
- 使用对象存储（OSS/S3）存储 `dist/assets/` 目录

### 6.4 开启浏览器缓存

已在Nginx配置中添加：
- 静态资源缓存1年
- HTML文件不缓存（确保更新及时）

## 七、监控与运维

### 7.1 日志轮转

创建 `/etc/logrotate.d/xiaoluban-nginx`：

```
/home/xiaoluban/logs/nginx/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 nginx nginx
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

### 7.2 健康检查脚本

创建 `/home/xiaoluban/frontend/healthcheck.sh`：

```bash
#!/bin/bash
# 健康检查脚本

URL="http://localhost:9000"
EXPECTED_STATUS="200"

response=$(curl -s -o /dev/null -w "%{http_code}" "$URL")

if [ "$response" = "$EXPECTED_STATUS" ]; then
    echo "✅ 服务正常 (HTTP $response)"
    exit 0
else
    echo "❌ 服务异常 (HTTP $response)"
    # 可以添加告警通知
    exit 1
fi
```

```bash
# 添加到crontab，每5分钟检查一次
crontab -e
# 添加：
*/5 * * * * /home/xiaoluban/frontend/healthcheck.sh >> /home/xiaoluban/logs/healthcheck.log 2>&1
```

### 7.3 性能监控

使用Nginx状态模块：

```nginx
# 在server块中添加
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}
```

```bash
# 查看状态
curl http://localhost:9000/nginx_status
```

## 八、常见问题

### 8.1 页面404错误

**问题**: 访问页面显示404 Not Found

**原因**: 
- dist目录不存在或为空
- Nginx配置的root路径不正确
- 没有执行构建命令

**解决**:
```bash
# 检查dist目录
ls -la /home/xiaoluban/frontend/dist/

# 如果为空，重新构建
cd /home/xiaoluban/frontend
npm run build

# 检查Nginx配置
sudo nginx -t
```

### 8.2 API请求失败

**问题**: 前端无法访问后端API

**原因**: 
- 后端服务未启动
- CORS配置问题
- API地址配置错误

**解决**:
```bash
# 检查后端服务
curl http://localhost:8000/api/environments

# 检查前端环境变量
cat /home/xiaoluban/frontend/.env.production

# 查看浏览器控制台Network面板
# 检查API请求地址是否正确
```

### 8.3 静态资源404

**问题**: CSS/JS文件加载失败

**原因**: 
- 文件路径不正确
- Nginx没有读取权限

**解决**:
```bash
# 检查文件权限
ls -la /home/xiaoluban/frontend/dist/assets/

# 修复权限
chmod -R 755 /home/xiaoluban/frontend/dist/

# 检查Nginx错误日志
tail -f /home/xiaoluban/logs/nginx/xiaoluban-error.log
```

### 8.4 内存不足

**问题**: 构建过程中内存溢出

**解决**:
```bash
# 增加Node.js内存限制
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build

# 或在package.json中修改build命令
"build": "node --max-old-space-size=4096 ./node_modules/vite/bin/vite.js build"
```

### 8.5 端口被占用

**问题**: Nginx启动失败，端口9000被占用

**解决**:
```bash
# 查看端口占用
sudo lsof -i :9000

# 结束占用进程
sudo kill -9 <PID>

# 或修改Nginx监听端口
sudo vim /etc/nginx/conf.d/xiaoluban-frontend.conf
# 将 listen 9000 改为其他端口
```

## 九、安全建议

### 9.1 使用HTTPS（推荐）

```bash
# 安装Certbot
sudo yum install -y certbot python3-certbot-nginx

# 获取证书（需要有域名）
sudo certbot --nginx -d yourdomain.com

# 自动续期
sudo crontab -e
# 添加：
0 12 * * * /usr/bin/certbot renew --quiet
```

### 9.2 限制访问IP（可选）

```nginx
# 在server块中添加
allow 192.168.1.0/24;  # 允许内网
deny all;              # 拒绝其他
```

### 9.3 隐藏Nginx版本

```nginx
# 在nginx.conf的http块中添加
http {
    server_tokens off;
    # ...
}
```

## 十、联系与支持

- **项目地址**: `/home/xiaoluban/frontend`
- **配置文件**: `/etc/nginx/conf.d/xiaoluban-frontend.conf`
- **访问地址**: `http://your-server-ip:9000`
- **日志路径**: `/home/xiaoluban/logs/nginx/`

---

**文档版本**: 1.0  
**最后更新**: 2026-07-23  
**维护者**: 小鲁班开发团队