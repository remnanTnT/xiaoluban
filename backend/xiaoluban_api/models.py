"""
Xiaoluban API Models

参考 llm-router 的 unmanaged 模型设计，所有表都是 managed=False。
"""
from django.db import models


class Environment(models.Model):
    """环境配置表"""
    STATUS_IDLE = 'idle'
    STATUS_OCCUPIED = 'occupied'
    STATUS_CHOICES = [
        (STATUS_IDLE, '空闲'),
        (STATUS_OCCUPIED, '占用'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IDLE)
    occupant = models.CharField(max_length=100, blank=True, null=True)
    queued_users = models.TextField(blank=True, null=True)
    is_used = models.BooleanField(default=True)
    offline_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'xiaoluban_environments'
        managed = False
        verbose_name = '环境'
        verbose_name_plural = '环境列表'

    def __str__(self):
        return self.name


class History(models.Model):
    """操作历史表"""
    id = models.BigAutoField(primary_key=True)
    env_id = models.BigIntegerField(null=True, blank=True)
    action = models.CharField(max_length=50)
    command = models.TextField(blank=True, null=True)
    user = models.CharField(max_length=100, default='anonymous')
    success = models.BooleanField(default=False)
    output = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'xiaoluban_history'
        managed = False
        ordering = ['-timestamp']
        verbose_name = '历史记录'
        verbose_name_plural = '历史记录列表'

    def __str__(self):
        return f"{self.action} - {self.timestamp}"


class EnvironmentUsage(models.Model):
    """环境占用记录表"""
    RELEASE_AUTO = 'auto'
    RELEASE_MANUAL = 'manual'
    RELEASE_CHOICES = [
        (RELEASE_AUTO, '自动释放'),
        (RELEASE_MANUAL, '手动释放'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    env_name = models.CharField(max_length=100)
    occupant = models.CharField(max_length=100)
    occupy_time = models.DateTimeField()
    release_time = models.DateTimeField(null=True, blank=True)
    is_manual_release = models.CharField(max_length=10, choices=RELEASE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'xiaoluban_environment_usage'
        managed = False
        ordering = ['-occupy_time']
        verbose_name = '环境占用记录'
        verbose_name_plural = '环境占用记录列表'

    def __str__(self):
        return f"{self.env_name} - {self.occupant} - {self.occupy_time}"