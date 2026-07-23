"""
Django settings for xiaoluban project.

基于 llm-router 架构，支持前后端分离部署。
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,7.197.65.7').split(',')

# CORS 配置 - 允许前端跨域访问
CORS_ALLOW_ALL_ORIGINS = DEBUG  # 开发环境允许所有来源
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173'
).split(',') if not DEBUG else []

# Application definition
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'corsheaders',
    'xiaoluban_api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'xiaoluban_project.urls'

# Database
# 使用 PostgreSQL（参考 llm-router）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '123456'),
        'HOST': os.environ.get('DB_HOST', '7.197.65.7'),
        'PORT': os.environ.get('DB_PORT', '5430'),
    }
}

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# API 配置
API_PREFIX = '/api'

EXECUTE_TIMEOUT = int(os.environ.get('EXECUTE_TIMEOUT', '300'))
EXECUTE_MAX_BUFFER = int(os.environ.get('EXECUTE_MAX_BUFFER', str(1024 * 1024 * 10)))

W3_VERIFY_CLI_PATH = os.environ.get(
    'W3_VERIFY_CLI_PATH', 
    str(BASE_DIR / 'w3-verify' / 'src' / 'cli.js')
)
W3_VERIFY_TIMEOUT = int(os.environ.get('W3_VERIFY_TIMEOUT', '20'))

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'xiaoluban_api': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}