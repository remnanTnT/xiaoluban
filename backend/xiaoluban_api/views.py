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
    """获取环境列表（只返回 is_used=True 的环境）"""
    from .models import Environment
    from django.db.models import Q
    
    try:
        environments = Environment.objects.filter(
            Q(is_used=True) | Q(is_used__iexact='true') | Q(is_used__iexact='t')
        ).values(
            'id', 'name', 'description', 'status', 'occupant', 
            'is_used', 'offline_time', 'created_at', 'updated_at'
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
        
        # 检查是否存在（包括已下线的）
        existing_env = Environment.objects.filter(name=name).first()
        
        if existing_env:
            if existing_env.is_used:
                return JsonResponse({
                    'success': False,
                    'error': f'环境 "{name}" 已存在'
                }, status=400)
            # 恢复已下线的环境
            existing_env.is_used = True
            existing_env.offline_time = None
            existing_env.description = description
            existing_env.save()
            
            logger.info(f"恢复环境: {name}")
            
            return JsonResponse({
                'success': True,
                'environment': {
                    'id': existing_env.id,
                    'name': existing_env.name,
                    'description': existing_env.description,
                    'is_used': existing_env.is_used
                },
                'message': f'环境 "{name}" 已恢复'
            })
        
        # 创建新环境
        env = Environment(name=name, description=description, is_used=True)
        env.save()
        
        logger.info(f"添加环境: {name}")
        
        return JsonResponse({
            'success': True,
            'environment': {
                'id': env.id,
                'name': env.name,
                'description': env.description,
                'is_used': env.is_used
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
    """移除环境（软删除）"""
    import json
    from datetime import datetime
    from .models import Environment
    
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        
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
        
        if not env.is_used:
            return JsonResponse({
                'success': False,
                'error': f'环境 "{name}" 已下线'
            }, status=400)
        
        env.is_used = False
        env.offline_time = datetime.now()
        env.status = Environment.STATUS_IDLE
        env.occupant = None
        env.save()
        
        logger.info(f"下线环境: {name}")
        
        return JsonResponse({
            'success': True,
            'message': f'环境 "{name}" 已下线'
        })
        
    except Exception as e:
        logger.error(f"下线环境失败: {str(e)}")
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


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    import json
    import shutil
    from pathlib import Path
    
    try:
        data = json.loads(request.body)
        uid = data.get('uid', '').strip()
        password = data.get('password', '')
        
        if not uid or not password:
            return JsonResponse({
                'success': False,
                'error': '账号和密码不能为空'
            }, status=400)
        
        cli_path = settings.W3_VERIFY_CLI_PATH
        if not Path(cli_path).exists():
            logger.error(f"w3-verify CLI 不存在: {cli_path}")
            return JsonResponse({
                'success': False,
                'error': 'W3 校验服务不可用'
            }, status=503)
        
        if not shutil.which('node'):
            logger.error("Node.js 未安装")
            return JsonResponse({
                'success': False,
                'error': 'W3 校验服务不可用'
            }, status=503)
        
        try:
            result = subprocess.run(
                ['node', cli_path, '--uid', uid],
                input=password,
                capture_output=True,
                text=True,
                timeout=settings.W3_VERIFY_TIMEOUT
            )
        except subprocess.TimeoutExpired:
            logger.warning(f"登录校验超时: uid={uid}")
            return JsonResponse({
                'success': False,
                'error': '登录校验超时'
            }, status=408)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                verify_result = json.loads(result.stdout.strip())
                if verify_result.get('success'):
                    logger.info(f"登录成功: uid={uid}, statusCode={verify_result.get('statusCode')}")
                    logger.info(f"w3-verify 返回: {verify_result}")
                    return JsonResponse({
                        'success': True,
                        'uid': uid
                    })
                else:
                    error_msg = verify_result.get('error', '账号或密码错误')
                    logger.warning(f"登录失败: uid={uid}, error={error_msg}")
                    return JsonResponse({
                        'success': False,
                        'error': '账号或密码错误'
                    }, status=401)
            except json.JSONDecodeError:
                logger.error(f"w3-verify 输出解析失败: {result.stdout}")
                return JsonResponse({
                    'success': False,
                    'error': '登录校验失败'
                }, status=500)
        else:
            logger.warning(f"登录失败: uid={uid}, returncode={result.returncode}")
            return JsonResponse({
                'success': False,
                'error': '账号或密码错误'
            }, status=401)
        
    except Exception as e:
        logger.error(f"登录异常: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)