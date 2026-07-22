# 小鲁班开发指南

## 技术栈

- **框架**：Django 4.2
- **数据库**：PostgreSQL
- **API**：RESTful API
- **认证**：无（内部工具）

## 项目结构

```
backend/
├── manage.py                      # Django 管理脚本
├── requirements.txt               # Python 依赖
├── xiaoluban_project/            # Django 项目配置
│   ├── __init__.py
│   ├── settings.py               # 项目配置
│   ├── urls.py                   # 根 URL 路由
│   ├── wsgi.py                   # WSGI 入口
│   └── asgi.py                   # ASGI 入口
├── xiaoluban_api/                # API 应用
│   ├── __init__.py
│   ├── apps.py                   # 应用配置
│   ├── models.py                 # 数据模型
│   ├── views.py                  # API 视图
│   ├── urls.py                   # URL 路由
│   ├── migrations/               # 数据库迁移
│   └── management/               # 管理命令
│       └── commands/
│           └── check_db_schema.py  # Schema 检查工具
├── docs/                         # 文档
│   ├── API.md                    # API 文档
│   └── DEPLOYMENT.md             # 部署指南
└── scripts/                      # 脚本目录
```

## 开发流程

### 1. 环境搭建

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

```bash
# 设置环境变量
export DB_NAME=xiaoluban
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_HOST=localhost
export DB_PORT=5432
```

### 3. 启动开发服务器

```bash
python manage.py runserver
```

访问：http://localhost:8000/api/environments

### 4. 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest xiaoluban_api/tests/test_views.py
```

## 编码规范

### 1. 代码风格

- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 函数和变量使用 snake_case
- 类使用 PascalCase

### 2. 注释规范

```python
def execute_command(request):
    """
    执行 shell 命令
    
    Args:
        request: HTTP 请求对象
        
    Returns:
        JsonResponse: 包含执行结果的响应
    """
    pass
```

### 3. 错误处理

```python
try:
    # 业务逻辑
    pass
except Exception as e:
    logger.error(f"操作失败: {str(e)}")
    return JsonResponse({
        'success': False,
        'error': str(e)
    }, status=500)
```

## 添加新功能

### 1. 添加新 API 端点

**views.py:**
```python
@require_http_methods(["GET"])
def new_endpoint(request):
    """新端点描述"""
    return JsonResponse({'success': True})
```

**urls.py:**
```python
path('new-endpoint', views.new_endpoint, name='new_endpoint'),
```

### 2. 添加新模型

**models.py:**
```python
class NewModel(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'xiaoluban_new_table'
        managed = False
```

### 3. 添加管理命令

创建 `management/commands/new_command.py`:

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = '新命令描述'
    
    def handle(self, *args, **options):
        self.stdout.write('命令执行完成')
```

## 调试技巧

### 1. 查看 SQL 查询

```python
# settings.py
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        },
    },
}
```

### 2. Django Shell

```bash
python manage.py shell
```

```python
from xiaoluban_api.models import Environment
Environment.objects.all()
```

### 3. 检查数据库连接

```bash
python manage.py check_db_schema
```

---

## 常用命令

| 命令 | 说明 |
|------|------|
| `python manage.py runserver` | 启动开发服务器 |
| `python manage.py shell` | 进入 Django Shell |
| `python manage.py check_db_schema` | 检查数据库 schema |
| `python manage.py check_db_schema --fix` | 修复数据库 schema |
| `pytest` | 运行测试 |
| `pip install -r requirements.txt` | 安装依赖 |

---

## 参考资料

- [Django 官方文档](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)