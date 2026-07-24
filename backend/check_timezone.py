#!/usr/bin/env python3
"""
检查时区和数据库时间问题
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xiaoluban_project.settings')
sys.path.insert(0, '/home/j30048192/xiaoluban/backend')

django.setup()

from django.utils import timezone
from datetime import datetime
from xiaoluban_api.models import EnvironmentUsage

print("=" * 60)
print("时区诊断")
print("=" * 60)

# 1. 检查Django时区配置
from django.conf import settings
print(f"\nDjango配置:")
print(f"  TIME_ZONE: {settings.TIME_ZONE}")
print(f"  USE_TZ: {settings.USE_TZ}")

# 2. 检查当前时间
print(f"\n当前时间:")
print(f"  timezone.now(): {timezone.now()}")
print(f"  timezone.now().tzinfo: {timezone.now().tzinfo}")
print(f"  datetime.now(): {datetime.now()}")

# 3. 检查数据库中的最新记录
print(f"\n数据库最新5条占用记录:")
usages = EnvironmentUsage.objects.all().order_by('-id')[:5]
for usage in usages:
    print(f"\n  ID: {usage.id}")
    print(f"  环境: {usage.env_name}")
    print(f"  占用时间: {usage.occupy_time}")
    print(f"    - 类型: {type(usage.occupy_time)}")
    print(f"    - 时区: {usage.occupy_time.tzinfo if hasattr(usage.occupy_time, 'tzinfo') else 'N/A'}")
    if usage.release_time:
        print(f"  释放时间: {usage.release_time}")
        print(f"    - 类型: {type(usage.release_time)}")
        print(f"    - 时区: {usage.release_time.tzinfo if hasattr(usage.release_time, 'tzinfo') else 'N/A'}")

# 4. 检查数据库原生查询
print(f"\n数据库原生时间查询:")
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT id, env_name, occupy_time, release_time 
        FROM xiaoluban_environment_usage 
        ORDER BY id DESC 
        LIMIT 5
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f"\n  ID {row[0]}: {row[1]}")
        print(f"    DB occupy_time: {row[2]}")
        print(f"    DB release_time: {row[3]}")

print("\n" + "=" * 60)