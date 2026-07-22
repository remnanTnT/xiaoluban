# 小鲁班后端

Django 4.2 后端服务，提供环境管理、命令执行、历史记录等 API。

## 快速开始

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

## 数据库配置

设置环境变量：

```bash
export DB_NAME=xiaoluban
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_HOST=localhost
export DB_PORT=5432
```

初始化数据库：

```bash
python manage.py check_db_schema --fix
```

## API 端点

- `POST /api/execute` - 执行 shell 命令
- `GET /api/environments` - 获取环境列表
- `POST /api/environments/add` - 添加环境
- `POST /api/environments/remove` - 移除环境
- `GET /api/history` - 获取历史记录

## 文档

- [API 文档](docs/API.md)
- [部署指南](docs/DEPLOYMENT.md)
- [开发指南](docs/DEVELOPMENT.md)