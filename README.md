# 小鲁班自验证工具

自动化测试与部署平台，支持升级、测试、复位等操作。

## 架构说明

本项目采用前后端分离架构：

- **前端**：Vue 3 + Vite，独立部署
- **后端**：Django 4.2 + PostgreSQL，独立部署

```
┌─────────────────┐      ┌─────────────────┐
│   前端服务器     │      │   后端服务器     │
│   (Vue 3)       │      │   (Django)      │
│                 │      │                 │
│  localhost:5173 │─────▶│  localhost:8000 │
│  (开发模式)     │ API  │  (开发模式)     │
└─────────────────┘      └────────┬────────┘
                                  │
                         ┌────────▼────────┐
                         │   PostgreSQL    │
                         │   localhost:5432│
                         └─────────────────┘
```

## 目录结构

```
xiaoluban/
├── frontend/                # 前端项目（Vue 3）
│   ├── src/
│   │   ├── App.vue         # 主组件
│   │   ├── main.js         # 入口文件
│   │   └── style.css       # 样式文件
│   ├── index.html          # HTML入口
│   ├── vite.config.js      # Vite配置
│   ├── package.json        # 前端依赖
│   ├── .env.example        # 环境变量示例
│   └── README.md           # 前端文档
│
├── backend/                 # 后端项目（Django）
│   ├── xiaoluban_project/  # Django项目配置
│   │   ├── settings.py     # 项目配置
│   │   └── urls.py         # 根URL路由
│   ├── xiaoluban_api/      # API应用
│   │   ├── models.py       # 数据模型
│   │   ├── views.py        # API视图
│   │   └── urls.py         # API路由
│   ├── docs/               # 文档
│   │   ├── API.md          # API文档
│   │   ├── DEPLOYMENT.md   # 部署指南
│   │   └── DEVELOPMENT.md  # 开发指南
│   ├── manage.py           # Django管理脚本
│   └── requirements.txt    # Python依赖
│
└── README.md                # 本文件
```

## 快速开始

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env，设置 VITE_API_BASE_URL=http://localhost:8000

# 启动开发服务器
npm run dev
```

### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库环境变量
# 测试环境（默认）
export DB_NAME=xiaoluban
export DB_USER=postgres
export DB_PASSWORD=123456
export DB_HOST=7.197.65.7
export DB_PORT=5430

# 或生产环境
# export DB_HOST=7.197.65.7
# export DB_PORT=5431

# 或使用 .env 文件（推荐）
cp .env.example .env
# 编辑 .env 文件，修改数据库配置

# 初始化数据库
python manage.py check_db_schema --fix

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

## 功能特性

### 工具操作

- **升级**：选择环境、输入 build_version、选择升级方式
- **测试**：执行自动化测试
- **复位**：恢复系统初始状态

### RoCE 环境排队

- 环境资源管理
- 排队调度

### API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /api/execute | 执行 shell 命令 |
| GET | /api/environments | 获取环境列表 |
| POST | /api/environments/add | 添加环境 |
| POST | /api/environments/remove | 移除环境 |
| GET | /api/history | 获取历史记录 |

## 数据库工具

```bash
# 检查 schema 差异
python manage.py check_db_schema

# 自动修复 schema 差异
python manage.py check_db_schema --fix
```

## 部署

详细部署说明请参考：
- [后端部署指南](backend/docs/DEPLOYMENT.md)
- [API 文档](backend/docs/API.md)
- [开发指南](backend/docs/DEVELOPMENT.md)

## 技术栈

### 前端
- Vue 3
- Vite 5
- 原生 CSS（深色科技主题）

### 后端
- Django 4.2
- PostgreSQL
- django-cors-headers

## 开发调试

开发环境需要同时启动前端和后端：

**终端 1 - 启动后端：**
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm run dev
```

访问：
- 前端：http://localhost:5173
- 后端 API：http://localhost:8000/api/environments

## License

Internal Tool