# 小鲁班后端 API 文档

## 概述

小鲁班后端基于 Django 框架，提供环境管理、命令执行、历史记录等 API 服务。

## API 端点

### 1. 登录认证

**POST** `/api/login`

通过 W3 账号密码校验进行登录。

**请求体：**
```json
{
  "uid": "W3账号",
  "password": "密码"
}
```

**成功响应（200）：**
```json
{
  "success": true,
  "uid": "z00123456"
}
```

**失败响应：**
- 缺少参数 → 400 `{ "success": false, "error": "账号和密码不能为空" }`
- 凭据错误 → 401 `{ "success": false, "error": "账号或密码错误" }`
- 超时 → 408 `{ "success": false, "error": "登录校验超时" }`
- 服务不可用 → 503 `{ "success": false, "error": "W3 校验服务不可用" }`

---

### 2. 执行命令

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
      "type": "开发环境",
      "status": "idle",
      "occupant": null,
      "queued_users": [],
      "is_used": true,
      "offline_time": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "env2",
      "description": "环境描述",
      "type": "测试环境",
      "status": "occupied",
      "occupant": "user123",
      "queued_users": ["user456", "user789"],
      "is_used": true,
      "offline_time": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**状态说明：**
- `idle`: 空闲
- `occupied`: 占用

**字段说明：**
- `type`: 环境类型（可选），用于环境分类，如"开发环境"、"测试环境"等
- `queued_users`: 排队用户列表，按排队顺序排列

---

### 3. 添加环境

**POST** `/api/environments/add`

添加新环境。新创建的环境默认状态为 "空闲"。

**请求体：**
```json
{
  "name": "环境名称",
  "description": "环境描述（可选）",
  "type": "环境类型（可选）"
}
```

**参数说明：**
- `name` (必填): 环境名称
- `description` (可选): 环境描述
- `type` (可选): 环境类型，用于环境分类，如"开发环境"、"测试环境"等

**响应：**
```json
{
  "success": true,
  "environment": {
    "id": 1,
    "name": "环境名称",
    "description": "环境描述",
    "type": "环境类型",
    "status": "idle",
    "occupant": null
  }
}
```

---

### 4. 更新环境

**POST** `/api/environments/update`

更新环境信息。

**请求体：**
```json
{
  "id": 1,
  "name": "新环境名称",
  "description": "新环境描述",
  "type": "新环境类型"
}
```

**参数说明：**
- `id` (必填): 环境ID
- `name` (必填): 新环境名称
- `description` (可选): 新环境描述
- `type` (可选): 新环境类型

**响应：**
```json
{
  "success": true,
  "message": "环境信息已更新",
  "environment": {
    "id": 1,
    "name": "新环境名称",
    "description": "新环境描述",
    "type": "新环境类型",
    "status": "idle",
    "occupant": null
  }
}
```

---

### 5. 移除环境

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

### 6. 占用环境

**POST** `/api/environments/occupy`

占用指定环境或加入排队。

**行为说明：**
- 如果环境空闲 → 直接占用
- 如果环境已被占用且用户不在排队中 → 加入排队
- 如果用户已在排队中 → 取消排队（不影响其他人的排队顺序）

**请求体：**
```json
{
  "name": "环境名称",
  "occupant": "占用人"
}
```

**成功占用响应：**
```json
{
  "success": true,
  "action": "occupied",
  "environment": {
    "id": 1,
    "name": "环境名称",
    "status": "occupied",
    "occupant": "占用人",
    "queued_users": []
  }
}
```

**加入排队响应：**
```json
{
  "success": true,
  "action": "queued",
  "queue_position": 2,
  "environment": {
    "id": 1,
    "name": "环境名称",
    "status": "occupied",
    "occupant": "其他用户",
    "queued_users": ["占用人"]
  }
}
```

**取消排队响应：**
```json
{
  "success": true,
  "action": "queue_cancelled",
  "environment": {
    "id": 1,
    "name": "环境名称",
    "status": "occupied",
    "occupant": "其他用户",
    "queued_users": []
  }
}
```

---

### 7. 释放环境

**POST** `/api/environments/release`

释放指定环境。

**行为说明：**
- 如果有排队用户 → 排队第一人自动占用环境
- 如果没有排队用户 → 环境变为空闲状态

**请求体：**
```json
{
  "name": "环境名称",
  "is_manual": true
}
```

**参数说明：**
- `is_manual` (可选): 是否手动释放，默认 true

**自动转给排队用户响应：**
```json
{
  "success": true,
  "action": "transferred",
  "environment": {
    "id": 1,
    "name": "环境名称",
    "status": "occupied",
    "occupant": "排队用户1",
    "queued_users": ["排队用户2"]
  }
}
```

**完全释放响应：**
```json
{
  "success": true,
  "action": "released",
  "environment": {
    "id": 1,
    "name": "环境名称",
    "status": "idle",
    "occupant": null,
    "queued_users": []
  }
}
```

---

### 8. 获取历史记录

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

### 9. 获取环境占用记录

**GET** `/api/environments/usage?env_name=xxx&limit=20`

获取环境占用历史记录。

**查询参数：**
- `env_name` (可选): 环境名称，不传则返回所有环境
- `limit` (可选): 返回记录数量，默认 20

**响应：**
```json
{
  "success": true,
  "usages": [
    {
      "id": 1,
      "env_name": "env1",
      "occupant": "user123",
      "occupy_time": "2024-01-01T10:00:00",
      "release_time": "2024-01-01T12:00:00",
      "is_manual_release": "manual",
      "created_at": "2024-01-01T10:00:00"
    }
  ]
}
```

**字段说明：**
- `occupy_time`: 占用时间（北京时间）
- `release_time`: 释放时间（北京时间），未释放时为 null
- `is_manual_release`: 释放方式
  - `manual`: 手动释放
  - `auto`: 自动释放

---

## 数据库模型

### Environment（环境）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAuto | 主键 |
| name | CharField(100) | 环境名称（唯一） |
| description | TextField | 环境描述 |
| type | CharField(50) | 环境类型（可选），用于环境分类 |
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

### EnvironmentUsage（环境占用记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BigAuto | 主键 |
| env_name | CharField(100) | 环境名称 |
| occupant | CharField(100) | 占用人 |
| occupy_time | DateTime | 占用时间（北京时间） |
| release_time | DateTime | 释放时间（北京时间），未释放时为空 |
| is_manual_release | CharField(10) | 释放方式：manual（手动）/ auto（自动） |
| created_at | DateTime | 创建时间 |

**表名：** `xiaoluban_environment_usage`

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