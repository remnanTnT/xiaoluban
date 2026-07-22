"""
Xiaoluban API Views

实现原有的 Express API 功能：
- POST /api/execute - 执行 shell 命令
- GET /api/environments - 获取环境列表
- POST /api/environments/add - 添加环境
- POST /api/environments/remove - 移除环境
- GET /api/history - 获取历史记录
"""
import subprocess
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

logger = logging.getLogger('xiaoluban_api')


@csrf_exempt
@require_http_methods(["POST"])
def execute_command(request):
    """
    执行 shell 命令
    
    请求体:
    {
        "command": "shell 命令",
        "cwd": "工作目录（可选）"
    }
    """
    import json
    
    try:
        data = json.loads(request.body)
        command = data.get('command', '').strip()
        cwd = data.get('cwd', '/home/public')
        
        if not command:
            return JsonResponse({
                'success': False,
                'error': '命令不能为空'
            }, status=400)
        
        logger.info(f"执行命令: {command}")
        logger.info(f"工作目录: {cwd}")
        
        # 执行命令
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=settings.EXECUTE_TIMEOUT
        )
        
        success = result.returncode == 0
        output = result.stdout or result.stderr or '命令执行完成'
        
        logger.info(f"执行结果: {'成功' if success else '失败'}")
        
        return JsonResponse({
            'success': success,
            'output': output,
            'returncode': result.returncode
        })
        
    except subprocess.TimeoutExpired:
        logger.error(f"命令执行超时")
        return JsonResponse({
            'success': False,
            'error': f'命令执行超时（超过 {settings.EXECUTE_TIMEOUT} 秒）'
        }, status=408)
        
    except Exception as e:
        logger.error(f"执行失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_environments(request):
    """获取环境列表"""
    from .models import Environment
    
    try:
        environments = Environment.objects.all().values(
            'id', 'name', 'description', 'status', 'occupant', 'created_at', 'updated_at'
        )
        return JsonResponse({
            'success': True,
            'environments': list(environments)
        })
    except Exception as e:
        logger.error(f"获取环境列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_environment(request):
    """添加环境"""
    import json
    from .models import Environment
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        description = data.get('description', '')
        
        if not name:
            return JsonResponse({
                'success': False,
                'error': '环境名称不能为空'
            }, status=400)
        
        # 检查是否已存在
        if Environment.objects.filter(name=name).exists():
            return JsonResponse({
                'success': False,
                'error': f'环境 "{name}" 已存在'
            }, status=400)
        
        env = Environment(name=name, description=description)
        env.save()
        
        logger.info(f"添加环境: {name}")
        
        return JsonResponse({
            'success': True,
            'environment': {
                'id': env.id,
                'name': env.name,
                'description': env.description
            }
        })
        
    except Exception as e:
        logger.error(f"添加环境失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def remove_environment(request):
    """移除环境"""
    import json
    from .models import Environment
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        
        if not name:
            return JsonResponse({
                'success': False,
                'error': '环境名称不能为空'
            }, status=400)
        
        deleted, _ = Environment.objects.filter(name=name).delete()
        
        if deleted == 0:
            return JsonResponse({
                'success': False,
                'error': f'环境 "{name}" 不存在'
            }, status=404)
        
        logger.info(f"移除环境: {name}")
        
        return JsonResponse({
            'success': True,
            'message': f'环境 "{name}" 已删除'
        })
        
    except Exception as e:
        logger.error(f"移除环境失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_history(request):
    """获取历史记录"""
    from .models import History
    
    try:
        limit = int(request.GET.get('limit', 50))
        history = History.objects.all()[:limit].values(
            'id', 'env_id', 'action', 'command', 'user', 
            'success', 'output', 'timestamp'
        )
        return JsonResponse({
            'success': True,
            'history': list(history)
        })
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def occupy_environment(request):
    """占用环境"""
    import json
    from datetime import datetime
    from .models import Environment, EnvironmentUsage
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        occupant = data.get('occupant', '').strip()
        
        if not name:
            return JsonResponse({
                'success': False,
                'error': '环境名称不能为空'
            }, status=400)
        
        if not occupant:
            return JsonResponse({
                'success': False,
                'error': '占用人不能为空'
            }, status=400)
        
        try:
            env = Environment.objects.get(name=name)
        except Environment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'环境 "{name}" 不存在'
            }, status=404)
        
        if env.status == Environment.STATUS_OCCUPIED:
            return JsonResponse({
                'success': False,
                'error': f'环境 "{name}" 已被 {env.occupant} 占用'
            }, status=400)
        
        env.status = Environment.STATUS_OCCUPIED
        env.occupant = occupant
        env.save()
        
        # 创建占用记录
        usage = EnvironmentUsage(
            env_name=name,
            occupant=occupant,
            occupy_time=datetime.now()
        )
        usage.save()
        
        logger.info(f"环境 {name} 被 {occupant} 占用")
        
        return JsonResponse({
            'success': True,
            'environment': {
                'id': env.id,
                'name': env.name,
                'status': env.status,
                'occupant': env.occupant
            },
            'usage_id': usage.id
        })
        
    except Exception as e:
        logger.error(f"占用环境失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def release_environment(request):
    """释放环境"""
    import json
    from datetime import datetime
    from .models import Environment, EnvironmentUsage
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        is_manual = data.get('is_manual', True)
        
        if not name:
            return JsonResponse({
                'success': False,
                'error': '环境名称不能为空'
            }, status=400)
        
        try:
            env = Environment.objects.get(name=name)
        except Environment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'环境 "{name}" 不存在'
            }, status=404)
        
        env.status = Environment.STATUS_IDLE
        env.occupant = None
        env.save()
        
        # 更新占用记录
        latest_usage = EnvironmentUsage.objects.filter(
            env_name=name, 
            release_time__isnull=True
        ).order_by('-occupy_time').first()
        
        if latest_usage:
            latest_usage.release_time = datetime.now()
            latest_usage.is_manual_release = EnvironmentUsage.RELEASE_MANUAL if is_manual else EnvironmentUsage.RELEASE_AUTO
            latest_usage.save()
        
        logger.info(f"环境 {name} 已释放")
        
        return JsonResponse({
            'success': True,
            'environment': {
                'id': env.id,
                'name': env.name,
                'status': env.status,
                'occupant': env.occupant
            }
        })
        
    except Exception as e:
        logger.error(f"释放环境失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_environment_usage(request):
    """获取环境占用记录"""
    from .models import EnvironmentUsage
    
    try:
        env_name = request.GET.get('env_name', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        usages = EnvironmentUsage.objects.all()
        
        if env_name:
            usages = usages.filter(env_name=env_name)
        
        usages = usages[:limit].values(
            'id', 'env_name', 'occupant', 
            'occupy_time', 'release_time', 'is_manual_release',
            'created_at'
        )
        
        return JsonResponse({
            'success': True,
            'usages': list(usages)
        })
    except Exception as e:
        logger.error(f"获取占用记录失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)