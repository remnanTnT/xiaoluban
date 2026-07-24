#!/usr/bin/env python3
"""
完整的时间修复脚本
修复所有API的时间序列化问题
"""
import re
from pathlib import Path

def fix_timezone_completely():
    views_path = Path('xiaoluban_api/views.py')
    
    if not views_path.exists():
        print("错误：找不到views.py")
        return False
    
    # 读取文件
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("开始修复...")
    
    # 1. 确保有serialize_datetime函数
    if 'def serialize_datetime' not in content:
        print("错误：缺少serialize_datetime函数")
        return False
    else:
        print("✓ serialize_datetime函数存在")
    
    # 2. 检查并修复get_environments函数
    print("检查get_environments函数...")
    
    # 查找env_list.append部分
    append_pattern = r"'offline_time':\s*env\.offline_time[,,\s]"
    if re.search(append_pattern, content):
        print("  发现未序列化的offline_time，正在修复...")
        content = re.sub(append_pattern, "'offline_time': serialize_datetime(env.offline_time),", content)
    else:
        print("  offline_time已修复或不存在")
    
    append_pattern = r"'created_at':\s*env\.created_at[,,\s]"
    if re.search(append_pattern, content):
        print("  发现未序列化的created_at，正在修复...")
        content = re.sub(append_pattern, "'created_at': serialize_datetime(env.created_at),", content)
    else:
        print("  created_at已修复或不存在")
    
    append_pattern = r"'updated_at':\s*env\.updated_at[,,\s}]"
    if re.search(append_pattern, content):
        print("  发现未序列化的updated_at，正在修复...")
        content = re.sub(append_pattern, "'updated_at': serialize_datetime(env.updated_at)", content)
    else:
        print("  updated_at已修复或不存在")
    
    # 3. 检查并修复get_environment_usage函数
    print("检查get_environment_usage函数...")
    
    # 检查是否使用了.values()
    if '.values(' in content and 'get_environment_usage' in content:
        print("  发现使用了.values()，需要重构...")
        
        # 找到get_environment_usage函数并重构
        usage_pattern = r'''def get_environment_usage\(request\):
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
        
        replacement = '''def get_environment_usage(request):
    """获取环境占用记录"""
    from .models import EnvironmentUsage
    
    try:
        env_name = request.GET.get('env_name', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        usages = EnvironmentUsage.objects.all()
        
        if env_name:
            usages = usages.filter(env_name=env_name)
        
        usages = usages[:limit]
        
        # 手动序列化时间字段
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
        
        content = re.sub(usage_pattern, replacement, content, flags=re.DOTALL)
        print("  已重构get_environment_usage函数")
    else:
        print("  get_environment_usage函数已正确实现")
    
    # 保存文件
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n修复完成！")
    print("\n下一步：")
    print("1. 停止旧进程：pkill -f 'manage.py runserver'")
    print("2. 启动新进程：python3 manage.py runserver 0.0.0.0:8001")
    print("3. 测试API：curl http://localhost:8001/api/environments | python3 -m json.tool | head -30")
    
    return True

if __name__ == '__main__':
    fix_timezone_completely()