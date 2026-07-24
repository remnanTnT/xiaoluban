#!/bin/bash
# 时间问题深度诊断

echo "=================================================="
echo "深度诊断时间问题"
echo "=================================================="

echo ""
echo "【1】检查serialize_datetime函数是否正确"
grep -A 20 "def serialize_datetime" xiaoluban_api/views.py
echo ""

echo "【2】检查get_environments中是否使用了serialize_datetime"
grep -B 3 -A 3 "offline_time\|created_at\|updated_at" xiaoluban_api/views.py | grep -A 3 "env_list.append"
echo ""

echo "【3】检查后端进程启动时间"
ps aux | grep "manage.py runserver" | grep -v grep
echo ""

echo "【4】测试API返回的时间格式（原始数据）"
curl -s http://localhost:8001/api/environments | python3 -m json.tool | grep -E "name|occupy_time|release_time|updated_at" | head -20
echo ""

echo "【5】测试占用记录API"
curl -s "http://localhost:8001/api/environments/usage?limit=2" | python3 -m json.tool
echo ""

echo "【6】数据库原始时间"
cat > /tmp/check_db_time.py << 'PYEOF'
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xiaoluban_project.settings')
django.setup()

from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT id, env_name, occupy_time, release_time FROM xiaoluban_environment_usage ORDER BY id DESC LIMIT 3")
    for row in cursor.fetchall():
        print(f"ID {row[0]}: {row[1]} - 占用:{row[2]} - 释放:{row[3]}")
PYEOF

cd /home/xiaoluban/backend
python3 /tmp/check_db_time.py
echo ""

echo "【7】当前系统时间"
date '+%Y-%m-%d %H:%M:%S %Z'
echo ""

echo "=================================================="