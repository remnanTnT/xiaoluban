#!/usr/bin/env python3
"""
时区问题修复脚本
自动修复 xiaoluban_api/views.py 中的时间序列化问题

使用方法：
    cd /home/xiaoluban/backend
    python3 fix_timezone_issue.py
    python3 manage.py runserver 0.0.0.0:8001
"""
import os
import sys
import re
from pathlib import Path


def backup_file(filepath):
    """备份原文件"""
    backup_path = filepath.with_suffix('.py.bak')
    if not backup_path.exists():
        import shutil
        shutil.copy2(filepath, backup_path)
        print(f"✓ 已备份原文件到: {backup_path}")


def fix_timezone_serialization():
    """修复时区序列化问题"""
    
    # 定位views.py文件
    views_path = Path(__file__).parent / 'xiaoluban_api' / 'views.py'
    
    if not views_path.exists():
        print(f"✗ 错误: 找不到文件 {views_path}")
        sys.exit(1)
    
    print(f"正在修复文件: {views_path}")
    
    # 备份原文件
    backup_file(views_path)
    
    # 读取文件内容
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经修复过
    if 'def serialize_datetime' in content:
        print("✓ 文件已经修复过了，无需重复修复")
        return
    
    print("开始修复...")
    
    # 1. 在文件开头的imports部分添加timezone导入
    print("  [1/5] 添加 timezone 导入...")
    import_section = """import subprocess
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone"""
    
    content = content.replace(
        """import subprocess
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings""",
        import_section
    )
    
    # 2. 在logger后添加serialize_datetime函数
    print("  [2/5] 添加 serialize_datetime 函数...")
    helper_function = '''

def serialize_datetime(dt):
    """
    序列化datetime对象为本地时间字符串
    
    Args:
        dt: datetime对象（可能是timezone-aware或naive）
    
    Returns:
        str: 本地时间字符串 (格式: "2026-07-24 10:20:29")
    """
    if dt is None:
        return None
    
    from django.utils.timezone import localtime
    
    # 处理naive datetime（历史数据）
    # 这种情况：数据库中存储的是本地时间，但没有时区信息
    if dt.tzinfo is None:
        # 假设为本地时间，直接格式化返回
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # 处理timezone-aware datetime（新数据）
    # 转换为本地时间（Asia/Shanghai）
    local_dt = localtime(dt)
    return local_dt.strftime('%Y-%m-%d %H:%M:%S')
'''
    
    content = content.replace(
        "logger = logging.getLogger('xiaoluban_api')",
        "logger = logging.getLogger('xiaoluban_api')" + helper_function
    )
    
    # 3. 修改get_environments函数中的时间字段
    print("  [3/5] 修复 get_environments 函数...")
    content = content.replace(
        "'offline_time': env.offline_time,",
        "'offline_time': serialize_datetime(env.offline_time),"
    )
    content = content.replace(
        "'created_at': env.created_at,",
        "'created_at': serialize_datetime(env.created_at),"
    )
    content = content.replace(
        "'updated_at': env.updated_at",
        "'updated_at': serialize_datetime(env.updated_at)"
    )
    
    # 4. 修改get_environment_usage函数
    print("  [4/5] 修复 get_environment_usage 函数...")
    
    # 找到并替换整个get_environment_usage函数
    old_usage_pattern = r'''def get_environment_usage\(request\):
    """获取环境占用记录"""
    from \.models import EnvironmentUsage
    
    try:
        env_name = request\.GET\.get\('env_name', ''\)\.strip\(\)
        limit = int\(request\.GET\.get\('limit', 20\)\)
        
        usages = EnvironmentUsage\.objects\.all\(\)
        
        if env_name:
            usages = usages\.filter\(env_name=env_name\)
        
        usages = usages\[:limit\]\.values\(
            'id', 'env_name', 'occupant', 
            'occupy_time', 'release_time', 'is_manual_release',
            'created_at'
        \)
        
        return JsonResponse\(\{
            'success': True,
            'usages': list\(usages\)
        \}\)'''
    
    new_usage_function = '''def get_environment_usage(request):
    """获取环境占用记录"""
    from .models import EnvironmentUsage
    
    try:
        env_name = request.GET.get('env_name', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        usages = EnvironmentUsage.objects.all()
        
        if env_name:
            usages = usages.filter(env_name=env_name)
        
        usages = usages[:limit]
        
        # 手动序列化时间字段，确保正确处理时区
        usage_list = []
        for usage in usages:
            usage_list.append({
                'id': usage.id,
                'env_name': usage.env_name,
                'occupant': usage.occupant,
                'occupy_time': serialize_datetime(usage.occupy_time),
                'release_time': serialize_datetime(usage.release_time),
                'is_manual_release': usage.is_manual_release,
                'created_at': serialize_datetime(usage.created_at)
            })
        
        return JsonResponse({
            'success': True,
            'usages': usage_list
        })'''
    
    content = re.sub(old_usage_pattern, new_usage_function, content, flags=re.DOTALL)
    
    # 5. 写回文件
    print("  [5/5] 保存修复后的文件...")
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("=" * 60)
    print("✓ 修复完成！")
    print("=" * 60)
    print()
    print("下一步操作：")
    print("  1. 重启后端服务:")
    print("     pkill -f 'manage.py runserver'")
    print("     python3 manage.py runserver 0.0.0.0:8001")
    print()
    print("  2. 验证修复:")
    print("     curl http://localhost:8001/api/environments | python3 -m json.tool | head -30")
    print()


if __name__ == '__main__':
    try:
        fix_timezone_serialization()
    except Exception as e:
        print(f"✗ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)