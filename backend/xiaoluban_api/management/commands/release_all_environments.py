"""
每日自动释放所有环境

使用方法:
    python manage.py release_all_environments

定时任务配置 (crontab):
    0 0 * * * cd /home/xiaoluban/backend && /usr/bin/python3 manage.py release_all_environments

功能:
    - 清空所有环境的状态为 "空闲"
    - 清空所有环境的占用人
    - 更新未结束的占用记录为 "自动释放"
"""
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger('xiaoluban_api')


class Command(BaseCommand):
    help = '释放所有环境（清空占用人），用于每日定时任务'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要释放的环境，不实际执行',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('释放所有环境'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        
        from xiaoluban_api.models import Environment, EnvironmentUsage
        
        # 查找所有被占用的环境
        occupied_envs = Environment.objects.filter(status=Environment.STATUS_OCCUPIED)
        count = occupied_envs.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('没有需要释放的环境'))
            return
        
        self.stdout.write(f"发现 {count} 个被占用的环境:")
        
        for env in occupied_envs:
            self.stdout.write(f"  - {env.name}: 占用人 {env.occupant}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY-RUN] 以上环境将被释放，但未实际执行"))
            return
        
        # 执行释放
        with transaction.atomic():
            # 更新占用记录为自动释放
            for env in occupied_envs:
                latest_usage = EnvironmentUsage.objects.filter(
                    env_name=env.name,
                    release_time__isnull=True
                ).order_by('-occupy_time').first()
                
                if latest_usage:
                    latest_usage.release_time = timezone.now()
                    latest_usage.is_manual_release = EnvironmentUsage.RELEASE_AUTO
                    latest_usage.save()
                    self.stdout.write(f"  更新占用记录: {env.name} -> 自动释放")
            
            # 清空环境状态
            updated = occupied_envs.update(
                status=Environment.STATUS_IDLE,
                occupant=None
            )
        
        self.stdout.write(self.style.SUCCESS(f"\n成功释放 {updated} 个环境"))
        logger.info(f"自动释放了 {updated} 个环境")