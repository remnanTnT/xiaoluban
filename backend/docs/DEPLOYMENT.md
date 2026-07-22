# 小鲁班后端部署指南

## 架构说明

小鲁班后端采用前后端分离架构：
- **前端**：Vue 3 + Vite，独立部署
- **后端**：Django 4.2 + PostgreSQL，独立部署

## 部署架构图

```
┌─────────────────┐      ┌─────────────────┐
│   前端服务器     │      │   后端服务器     │
│  (Nginx/Vite)   │      │   (Django)      │
│                 │      │                 │
│  localhost:5173 │─────▶│  localhost:8000 │
│  (开发模式)     │ API  │  (开发模式)     │
│                 │      │                 │
└─────────────────┘      └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │   PostgreSQL    │
                         │   localhost:5432│
                         └─────────────────┘
```

## 后端部署步骤

### 1. 环境准备

```bash
# 创建虚拟环境
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

创建 PostgreSQL 数据库：

```sql
CREATE DATABASE xiaoluban;
CREATE USER xiaoluban_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE xiaoluban TO xiaoluban_user;
```

### 3. 环境变量配置

创建 `.env` 文件：

```bash
# Django 配置
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# 数据库配置
DB_NAME=xiaoluban
DB_USER=xiaoluban_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# CORS 配置（前端域名）
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### 4. 初始化数据库

```bash
# 检查并修复数据库 schema
python manage.py check_db_schema --fix

# 收集静态文件
python manage.py collectstatic --noinput
```

### 5. 启动服务

**开发模式：**
```bash
python manage.py runserver 0.0.0.0:8000
```

**生产模式（Gunicorn）：**
```bash
pip install gunicorn
gunicorn xiaoluban_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --access-logfile - \
    --error-logfile -
```

## Nginx 反向代理配置

```nginx
# 后端 API 代理
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置（命令执行可能较慢）
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

## Docker 部署（可选）

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "xiaoluban_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

构建并运行：

```bash
docker build -t xiaoluban-backend .
docker run -d \
    -p 8000:8000 \
    --env-file .env \
    --name xiaoluban-api \
    xiaoluban-backend
```

## 常见问题

### 1. CORS 错误

确保 `settings.py` 中的 CORS 配置正确：

```python
CORS_ALLOWED_ORIGINS = ['https://your-frontend-domain.com']
```

### 2. 数据库连接失败

检查 PostgreSQL 服务状态：
```bash
sudo systemctl status postgresql
```

### 3. 命令执行超时

调整 `settings.py` 中的超时配置：
```python
EXECUTE_TIMEOUT = 600  # 10分钟
```

---

## 监控与日志

### 日志位置

- Django 日志：控制台输出
- Gunicorn 日志：`/var/log/gunicorn/`

### 健康检查

```bash
curl http://localhost:8000/api/environments
```

---

## 安全建议

1. **密钥管理**：使用环境变量存储敏感信息
2. **HTTPS**：生产环境必须使用 HTTPS
3. **数据库**：使用强密码，限制访问IP
4. **防火墙**：只开放必要端口（80/443/8000）
5. **定期备份**：设置数据库自动备份