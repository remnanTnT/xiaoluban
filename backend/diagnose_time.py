#!/usr/bin/env python3
"""
诊断时间问题脚本
在生产服务器上运行：python3 diagnose_time.py
"""
import os
import sys
import django
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xiaoluban_project.settings')
django.setup()

from django.utils import timezone
from django.db import connection
from xiaoluban_api.models import EnvironmentUsage

print("=" * 70)
print("时间问题诊断")
print("=" * 70)

# 1. 当前时间对比
print("\n【1】当前时间对比：")
now_aware = timezone.now()  # timezone-aware
now_naive = datetime.now()  # naive
print(f"  timezone.now():      {now_aware} ({now_aware.tzinfo})")
print(f"  datetime.now():      {now_naive} (无时区)")
print(f"  本地时间:            {timezone.localtime(now_aware)}")

# 2. Django配置
from django.conf import settings
print(f"\n【2】Django配置：")
print(f"  TIME_ZONE:           {settings.TIME_ZONE}")
print(f"  USE_TZ:              {settings.USE_TZ}")

# 3. 数据库最新记录
print(f"\n【3】数据库最新5条记录（通过ORM）：")
usages = EnvironmentUsage.objects.all().order_by('-id')[:5]
for usage in usages:
    print(f"\n  ID {usage.id}: {usage.env_name}")
    print(f"    占用时间(ORM):     {usage.occupy_time}")
    if usage.occupy_time:
        print(f"      类型: {type(usage.occupy_time)}")
        print(f"      时区: {usage.occupy_time.tzinfo}")
        print(f"      本地: {timezone.localtime(usage.occupy_time)}")
    
    if usage.release_time:
        print(f"    释放时间(ORM):     {usage.release_time}")
        print(f"      时区: {usage.release_time.tzinfo}")
        print(f"      本地: {timezone.localtime(usage.release_time)}")

# 4. 数据库原生时间
print(f"\n【4】数据库原生时间（直接查询）：")
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
        print(f"    DB occupy_time:    {row[2]}")
        print(f"    DB release_time:   {row[3]}")

# 5. 序列化测试
print(f"\n【5】序列化测试：")
test_usage = usages.first()
if test_usage:
    print(f"  原始occupy_time:     {test_usage.occupy_time}")
    print(f"  本地时间:            {timezone.localtime(test_usage.occupy_time)}")
    print(f"  格式化字符串:        {timezone.localtime(test_usage.occupy_time).strftime('%Y-%m-%d %H:%M:%S')}")

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)