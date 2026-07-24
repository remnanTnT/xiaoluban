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
from django.utils import timezone

logger = logging.getLogger('xiaoluban_api')


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
    
    from django.utils.timezone import localtime, make_aware
    from django.conf import settings
    import pytz
    from datetime import datetime
    
    # 调试日志
    logger.debug(f"serialize_datetime输入: {dt}, tzinfo={dt.tzinfo if hasattr(dt, 'tzinfo') else 'N/A'}")
    
    # timezone-aware：转换为本地时间
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
        local_dt = localtime(dt)
        result = local_dt.strftime('%Y-%m-%d %H:%M:%S')
        logger.debug(f"timezone-aware转换: {dt} -> {local_dt} -> {result}")
        return result
    
    # naive datetime的处理策略：
    # 在USE_TZ=True且数据库为timestamp without time zone的情况下：
    # - 新数据：用timezone.now()写入UTC时间，读取后Django会自动标记为UTC-aware
    # - 历史数据：用datetime.now()写入本地时间，读取后是naive
    
    # 如果到这里说明是naive，可能是：
    # 1. 历史数据（本地时间）
    # 2. Django没有正确处理时区
    
    # 策略：假设naive是UTC时间（符合Django USE_TZ=True的预期）
    # 然后转换为本地时间
    utc_tz = pytz.UTC
    dt_utc = utc_tz.localize(dt)
    local_dt = localtime(dt_utc)
    result = local_dt.strftime('%Y-%m-%d %H:%M:%S')
    logger.debug(f"naive转UTC再转本地: {dt} -> {dt_utc} -> {local_dt} -> {result}")
    return result
    
    # timezone-aware：转换为本地时间
    local_dt = localtime(dt)
    return local_dt.strftime('%Y-%m-%d %H:%M:%S')


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
    from django.utils.timezone import now, make_aware
    
    try:
        environments = Environment.objects.filter(is_used=True)
        
        env_list = []
        for env in environments:
            queued_users = []
            if env.queued_users:
                queued_users = [u.strip() for u in env.queued_users.split(',') if u.strip()]
            
            # 计算创建天数
            created_days = 0
            if env.created_at:
                # 处理naive datetime（历史数据）
                created_at = env.created_at
                if created_at.tzinfo is None:
                    # naive datetime，假设为本地时间，转换为aware
                    created_at = make_aware(created_at)
                
                delta = now() - created_at
                created_days = delta.days
            
            env_list.append({
                'id': env.id,
                'name': env.name,
                'description': env.description,
                'type': env.type,
                'status': env.status,
                'occupant': env.occupant,
                'queued_users': queued_users,
                'is_used': env.is_used,
                'offline_time': serialize_datetime(env.offline_time),
                'created_at': serialize_datetime(env.created_at),
                'updated_at': serialize_datetime(env.updated_at),
                'created_days': created_days
            })
        
        return JsonResponse({
            'success': True,
            'environments': env_list
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
        env_type = data.get('type', '')
        
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
            existing_env.type = env_type if env_type else None
            existing_env.save()
            
            logger.info(f"恢复环境: {name}")
            
            return JsonResponse({
                'success': True,
                'environment': {
                    'id': existing_env.id,
                    'name': existing_env.name,
                    'description': existing_env.description,
                    'type': existing_env.type,
                    'is_used': existing_env.is_used
                },
                'message': f'环境 "{name}" 已恢复'
            })
        
        # 创建新环境
        env = Environment(name=name, description=description, type=env_type if env_type else None, is_used=True)
        env.save()
        
        logger.info(f"添加环境: {name}")
        
        return JsonResponse({
            'success': True,
            'environment': {
                'id': env.id,
                'name': env.name,
                'description': env.description,
                'type': env.type,
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
        env.offline_time = timezone.now()
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


@csrf_exempt
@require_http_methods(["POST"])
def update_environment(request):
    """更新环境信息"""
    import json
    from .models import Environment
    
    try:
        data = json.loads(request.body)
        env_id = data.get('id')
        new_name = data.get('name', '').strip()
        new_description = data.get('description', '')
        new_type = data.get('type', '')
        
        if not env_id:
            return JsonResponse({
                'success': False,
                'error': '环境ID不能为空'
            }, status=400)
        
        if not new_name:
            return JsonResponse({
                'success': False,
                'error': '环境名称不能为空'
            }, status=400)
        
        try:
            env = Environment.objects.get(id=env_id)
        except Environment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'环境ID {env_id} 不存在'
            }, status=404)
        
        # 检查新名称是否与其他环境冲突
        if new_name != env.name:
            existing = Environment.objects.filter(name=new_name).exclude(id=env_id).first()
            if existing:
                return JsonResponse({
                    'success': False,
                    'error': f'环境名称 "{new_name}" 已存在'
                }, status=400)
        
        old_name = env.name
        env.name = new_name
        env.description = new_description
        env.type = new_type if new_type else None
        env.save()
        
        logger.info(f"更新环境: {old_name} -> {new_name}")
        
        return JsonResponse({
            'success': True,
            'message': '环境信息已更新',
            'environment': {
                'id': env.id,
                'name': env.name,
                'description': env.description,
                'type': env.type,
                'status': env.status,
                'occupant': env.occupant
            }
        })
        
    except Exception as e:
        logger.error(f"更新环境失败: {str(e)}")
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
    """占用环境或排队"""
    import json
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
        
        # 如果环境空闲，直接占用
        if env.status == Environment.STATUS_IDLE:
            env.status = Environment.STATUS_OCCUPIED
            env.occupant = occupant
            env.queued_users = None
            env.save()
            
            usage = EnvironmentUsage(
                env_name=name,
                occupant=occupant,
                occupy_time=timezone.now()
            )
            usage.save()
            
            logger.info(f"环境 {name} 被 {occupant} 占用")
            
            return JsonResponse({
                'success': True,
                'action': 'occupied',
                'environment': {
                    'id': env.id,
                    'name': env.name,
                    'status': env.status,
                    'occupant': env.occupant
                }
            })
        
        # 环境已被占用，检查是否已在排队
        queued_list = []
        if env.queued_users:
            queued_list = [u.strip() for u in env.queued_users.split(',') if u.strip()]
        
        # 如果当前用户已在排队，取消排队
        if occupant in queued_list:
            queued_list.remove(occupant)
            env.queued_users = ','.join(queued_list) if queued_list else None
            env.save()
            
            logger.info(f"用户 {occupant} 取消排队环境 {name}")
            
            return JsonResponse({
                'success': True,
                'action': 'queue_cancelled',
                'environment': {
                    'id': env.id,
                    'name': env.name,
                    'status': env.status,
                    'occupant': env.occupant,
                    'queued_users': queued_list
                }
            })
        
        # 添加到排队列表
        queued_list.append(occupant)
        env.queued_users = ','.join(queued_list)
        env.save()
        
        logger.info(f"用户 {occupant} 排队环境 {name}，当前排队人数: {len(queued_list)}")
        
        return JsonResponse({
            'success': True,
            'action': 'queued',
            'queue_position': len(queued_list),
            'environment': {
                'id': env.id,
                'name': env.name,
                'status': env.status,
                'occupant': env.occupant,
                'queued_users': queued_list
            }
        })
        
    except Exception as e:
        logger.error(f"占用/排队环境失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def release_environment(request):
    """释放环境"""
    import json
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
        
        # 更新占用记录（使用update确保只修改release_time）
        latest_usage = EnvironmentUsage.objects.filter(
            env_name=name, 
            release_time__isnull=True
        ).order_by('-occupy_time').first()
        
        if latest_usage:
            # 使用update()而不是save()，确保只修改release_time和is_manual_release
            # 绝对不会影响occupy_time
            EnvironmentUsage.objects.filter(id=latest_usage.id).update(
                release_time=timezone.now(),
                is_manual_release=EnvironmentUsage.RELEASE_MANUAL if is_manual else EnvironmentUsage.RELEASE_AUTO
            )
        
        # 检查是否有排队用户
        next_occupant = None
        if env.queued_users:
            queued_list = [u.strip() for u in env.queued_users.split(',') if u.strip()]
            if queued_list:
                next_occupant = queued_list[0]
                queued_list = queued_list[1:]
        
        if next_occupant:
            # 排队第一人自动占用
            prev_occupant = env.occupant  # 记录前一个占用人
            
            env.occupant = next_occupant
            env.queued_users = ','.join(queued_list) if queued_list else None
            env.save()
            
            usage = EnvironmentUsage(
                env_name=name,
                occupant=next_occupant,
                occupy_time=timezone.now()
            )
            usage.save()
            
            logger.info(f"环境 {name} 已释放，排队用户 {next_occupant} 自动占用")
            
            # 发送通知给新的占用人
            try:
                from send_msg import send_msg
                
                # 构造消息内容
                message_content = f"{prev_occupant} 已释放环境【{name}】，现在轮到您使用了。"
                
                # 发送消息
                send_msg(message_content, next_occupant)
                
                logger.info(f"已发送通知给 {next_occupant}: {message_content}")
            except Exception as e:
                # 通知发送失败不影响主流程
                logger.error(f"发送通知失败: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'action': 'transferred',
                'environment': {
                    'id': env.id,
                    'name': env.name,
                    'status': env.status,
                    'occupant': next_occupant,
                    'queued_users': queued_list
                }
            })
        else:
            # 没有排队用户，设置为空闲
            env.status = Environment.STATUS_IDLE
            env.occupant = None
            env.queued_users = None
            env.save()
            
            logger.info(f"环境 {name} 已释放，无排队用户")
            
            return JsonResponse({
                'success': True,
                'action': 'released',
                'environment': {
                    'id': env.id,
                    'name': env.name,
                    'status': env.status,
                    'occupant': None,
                    'queued_users': []
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