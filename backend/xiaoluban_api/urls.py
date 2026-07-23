"""
Xiaoluban API URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # 登录认证
    path('login', views.login, name='login'),
    
    # 命令执行
    path('execute', views.execute_command, name='execute'),
    
    # 环境管理
    path('environments', views.get_environments, name='environments'),
    path('environments/add', views.add_environment, name='add_environment'),
    path('environments/update', views.update_environment, name='update_environment'),
    path('environments/remove', views.remove_environment, name='remove_environment'),
    path('environments/occupy', views.occupy_environment, name='occupy_environment'),
    path('environments/release', views.release_environment, name='release_environment'),
    path('environments/usage', views.get_environment_usage, name='environment_usage'),
    
    # 历史记录
    path('history', views.get_history, name='history'),
]