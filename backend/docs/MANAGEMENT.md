# 管理命令文档

本文档记录 xiaoluban 后端的所有管理命令。

## 命令列表

### 1. 启动开发服务器

```bash
python manage.py runserver 0.0.0.0:8000
```

---

### 2. 数据库 Schema 检查与修复

检查 Django 模型与数据库表结构是否一致。

```bash
# 检查 schema 差异
python manage.py check_db_schema

# 自动修复 schema 差异
python manage.py check_db_schema --fix
```

**功能说明：**
- 检测缺失的表和列
- 自动生成并执行 DDL 语句
- 支持处理 PostgreSQL 保留关键字

---

### 3. 释放所有环境

每日定时清空所有环境占用人。

```bash
# 测试运行（仅显示将要释放的环境，不实际执行）
python manage.py release_all_environments --dry-run

# 实际执行释放
python manage.py release_all_environments
```

**功能说明：**
- 将所有占用状态的环境改为空闲（`idle`）
- 清空所有环境占用人（`occupant = null`）
- 更新未结束的占用记录为"自动释放"

**定时任务配置（crontab）：**

```bash
# 编辑定时任务
crontab -e

# 添加以下行（每日凌晨 00:00 执行）
0 0 * * * cd /home/xiaoluban/backend && /usr/bin/python3 manage.py release_all_environments >> /var/log/xiaoluban_release.log 2>&1
```

---

## 定时任务配置

| 任务 | 执行时间 | 命令 |
|------|----------|------|
| 释放所有环境 | 每日 00:00 | `python manage.py release_all_environments` |

---

## 常见问题

### 1. Schema 检查失败

确保数据库连接正常：
```bash
# 检查数据库连接
python manage.py check
```

### 2. 定时任务不执行

检查 crontab 日志：
```bash
# 查看 cron 日志
tail -f /var/log/syslog | grep CRON

# 查看任务执行日志
tail -f /var/log/xiaoluban_release.log
```

### 3. 权限问题

确保脚本有执行权限：
```bash
chmod +x manage.py
```