# 数据库初始化指南

## 问题描述

当遇到以下错误时：
```
column xiaoluban_environments.name does not exist
```

这表示数据库表结构不匹配，需要初始化数据库表。

## 解决方案

### 方法一：使用SQL脚本初始化（推荐）

执行以下命令连接到数据库并初始化表结构：

```bash
# 测试环境（端口 5430）
PGPASSWORD=123456 psql -h 7.197.65.7 -p 5430 -U postgres -d postgres -f init_db.sql

# 生产环境（端口 5431）
PGPASSWORD=123456 psql -h 7.197.65.7 -p 5431 -U postgres -d postgres -f init_db.sql
```

### 方法二：手动创建表（如果没有psql）

如果系统中没有安装 `psql` 客户端，可以：

1. 使用数据库管理工具（如 DBeaver, pgAdmin, Navicat 等）连接到数据库
2. 执行 `init_db.sql` 中的SQL语句

### 方法三：使用Django管理命令（需要虚拟环境）

```bash
cd backend

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 执行数据库检查和修复
python manage.py check_db_schema --fix
```

## 表结构说明

### xiaoluban_environments（环境配置表）
- `id`: 主键（自增）
- `name`: 环境名称（唯一，必填）
- `description`: 环境描述（可选）
- `type`: 环境类型（可选，新增）
- `status`: 状态（idle/occupied）
- `occupant`: 当前占用人
- `queued_users`: 排队用户列表
- `is_used`: 是否启用
- `offline_time`: 下线时间
- `created_at`: 创建时间
- `updated_at`: 更新时间

### xiaoluban_history（操作历史表）
- `id`: 主键（自增）
- `env_id`: 环境ID
- `action`: 操作类型
- `command`: 执行命令
- `user`: 执行用户
- `success`: 是否成功
- `output`: 输出结果
- `timestamp`: 时间戳

### xiaoluban_environment_usage（环境占用记录表）
- `id`: 主键（自增）
- `env_name`: 环境名称
- `occupant`: 占用人
- `occupy_time`: 占用时间
- `release_time`: 释放时间
- `is_manual_release`: 是否手动释放
- `created_at`: 创建时间

## 验证

执行SQL后，可以验证表是否创建成功：

```sql
-- 查看所有表
\dt

-- 查看表结构
\d xiaoluban_environments
\d xiaoluban_history
\d xiaoluban_environment_usage
```

## 常见问题

### Q: 执行SQL时报错 "relation already exists"
A: 表已经存在，可以忽略此错误，或者先删除表再重新创建：
```sql
DROP TABLE IF EXISTS xiaoluban_environments CASCADE;
DROP TABLE IF EXISTS xiaoluban_history CASCADE;
DROP TABLE IF EXISTS xiaoluban_environment_usage CASCADE;
```

### Q: 如何添加type字段到已存在的表？
A: 如果表已存在但缺少type字段，执行：
```sql
ALTER TABLE xiaoluban_environments ADD COLUMN type VARCHAR(50);
```

### Q: 数据库连接失败怎么办？
A: 检查以下配置：
- HOST: 7.197.65.7
- PORT: 5430（测试）/ 5431（生产）
- USER: postgres
- PASSWORD: 123456
- DATABASE: postgres