"""
Xiaoluban API URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # 命令执行
    path('execute', views.execute_command, name='execute'),
    
    # 环境管理
    path('environments', views.get_environments, name='environments'),
    path('environments/add', views.add_environment, name='add_environment'),
    path('environments/remove', views.remove_environment, name='remove_environment'),
    
    # 历史记录
    path('history', views.get_history, name='history'),
]