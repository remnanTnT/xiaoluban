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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IDLE)
    occupant = models.CharField(max_length=100, blank=True, null=True)
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