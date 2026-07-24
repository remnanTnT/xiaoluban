#!/usr/bin/env python3
"""
诊断release接口是否会修改occupy_time
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xiaoluban_project.settings')
sys.path.insert(0, '/home/xiaoluban/backend')
django.setup()

from xiaoluban_api.models import EnvironmentUsage
from django.utils import timezone

print("=" * 60)
print("测试：释放环境时是否修改了occupy_time")
print("=" * 60)

# 1. 找一个有occupy_time但没有release_time的记录
usage = EnvironmentUsage.objects.filter(release_time__isnull=True).first()

if not usage:
    print("没有找到未释放的记录")
    sys.exit(0)

print(f"\n原始数据：")
print(f"  ID: {usage.id}")
print(f"  环境: {usage.env_name}")
print(f"  占用时间(原始): {usage.occupy_time}")
print(f"  占用时间(类型): {type(usage.occupy_time)}")
print(f"  占用时间(时区): {usage.occupy_time.tzinfo}")

# 2. 记录原始occupy_time
original_occupy_time = usage.occupy_time

# 3. 只修改release_time
usage.release_time = timezone.now()
usage.is_manual_release = 'manual'
usage.save()

# 4. 重新读取并检查
usage.reload()  # 或 usage = EnvironmentUsage.objects.get(id=usage.id)
print(f"\n保存后数据：")
print(f"  占用时间(新): {usage.occupy_time}")
print(f"  占用时间(类型): {type(usage.occupy_time)}")
print(f"  占用时间(时区): {usage.occupy_time.tzinfo}")

# 5. 比较
if usage.occupy_time == original_occupy_time:
    print("\n✓ 结论：occupy_time没有被修改")
else:
    print("\n✗ 结论：occupy_time被修改了！")
    print(f"  原始: {original_occupy_time}")
    print(f"  新值: {usage.occupy_time}")

print("=" * 60)