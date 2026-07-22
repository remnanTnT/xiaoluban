# 小鲁班后端 API 文档

## 概述

小鲁班后端基于 Django 框架，提供环境管理、命令执行、历史记录等 API 服务。

## API 端点

### 1. 执行命令

**POST** `/api/execute`

执行 shell 命令。

**请求体：**
```json
{
  "command": "shell 命令",
  "cwd": "工作目录（可选，默认 /home/public）"
}
```

**响应：**
```json
{
  "success": true,
  "output": "命令输出",
  "returncode": 0
}
```

**错误响应：**
```json
{
  "success": false,
  "error": "错误信息"
}
```

---

### 2. 获取环境列表

**GET** `/api/environments`

获取所有环境配置。

**响应：**
```json
{
  "success": true,
  "environments": [
    {
      "id": 1,
      "name": "env1",
      "description": "环境描述",
      "status": "idle",
      "occupant": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "env2",
      "description": "环境描述",
      "status": "occupied",
      "occupant": "user123",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**状态说明：**
- `idle`: 空闲
- `occupied`: 占用

---

### 3. 添加环境

**POST** `/api/environments/add`

添加新环境。新创建的环境默认状态为 "空闲"。

**请求体：**
```json
{
  "name": "环境名称",
  "description": "环境描述（可选）"
}
```

**响应：**
```json
{
  "success": true,
  "environment": {
    "id": 1,
    "name": "环境名称",
    "description": "环境描述",
    "status": "idle",
    "occupant": null
  }
}
```

---

### 4. 移除环境

**POST** `/api/environments/remove`

移除环境。

**请求体：**
```json
{
  "name": "环境名称"
}
```

**响应：**
```json
{
  "success": true,
  "message": "环境 \"环境名称\" 已删除"
}
```

---

### 5. 占用环境

**POST** `/api/environments/occupy`

占用指定环境。环境必须处于 "空闲" 状态才能被占用。

**请求体：**
```json
{
  "name": "环境名称",
  "occupant": "占用人"
}
```

**响应：**
```json
{
  "success": true,
  "environment": {
    "id": 1,
    "name": "环境名称",
    "status": "occupied",
    "occupant": "占用人"
  }
}
```

**错误响应：**
```json
{
  "success": false,
  "error": "环境 \"环境名称\" 已被 user123 占用"
}
```

---

### 6. 释放环境

**POST** `/api/environments/release`

释放指定环境。释放后状态变为 "空闲"，占用人清空。

**请求体：**
```json
{
  "name": "环境名称"
}
```

**响应：**
```json
{
  "success": true,
  "environment": {
    "id": 1,
    "name": "环境名称",
    "status": "idle",
    "occupant": null
  }
}
```

---

### 7. 获取历史记录

**GET** `/api/history?limit=50`

获取操作历史记录。

**查询参数：**
- `limit` (可选): 返回记录数量，默认 50

**响应：**
```json
{
  "success": true,
  "history": [
    {
      "id": 1,
      "env_id": 1,
      "action": "upgrade",
      "command": "执行命令",
      "user": "anonymous",
      "success": true,
      "output": "输出内容",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## 数据库模型

### Environment（环境）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAuto | 主键 |
| name | CharField(100) | 环境名称（唯一） |
| description | TextField | 环境描述 |
| status | CharField(20) | 状态：idle（空闲）/ occupied（占用） |
| occupant | CharField(100) | 占用人（占用时必填，空闲时为空） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**表名：** `xiaoluban_environments`

**状态约束：**
- `idle`（空闲）：occupant 必须为空
- `occupied`（占用）：occupant 不能为空

### History（历史记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAuto | 主键 |
| env_id | BigInteger | 环境ID |
| action | CharField(50) | 操作类型 |
| command | TextField | 执行的命令 |
| user | CharField(100) | 操作用户 |
| success | Boolean | 是否成功 |
| output | TextField | 输出内容 |
| timestamp | DateTime | 时间戳 |

**表名：** `xiaoluban_history`

---

## 工具命令

### 数据库 Schema 检查

```bash
# 检查 schema 差异
python manage.py check_db_schema

# 自动修复 schema 差异
python manage.py check_db_schema --fix
```

### 启动开发服务器

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 部署说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DJANGO_SECRET_KEY | - | Django 密钥 |
| DJANGO_DEBUG | True | 调试模式 |
| DJANGO_ALLOWED_HOSTS | localhost | 允许的主机 |
| DB_NAME | xiaoluban | 数据库名 |
| DB_USER | postgres | 数据库用户 |
| DB_PASSWORD | postgres | 数据库密码 |
| DB_HOST | localhost | 数据库主机 |
| DB_PORT | 5432 | 数据库端口 |
| CORS_ALLOWED_ORIGINS | - | CORS 允许的来源 |

### 生产部署

```bash
# 安装依赖
pip install -r requirements.txt

# 收集静态文件
python manage.py collectstatic --noinput

# 启动 Gunicorn
gunicorn xiaoluban_project.wsgi:application --bind 0.0.0.0:8000
```