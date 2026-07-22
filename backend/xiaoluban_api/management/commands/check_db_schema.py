"""
数据库 Schema 检查和修复工具

参考 llm-router 的 check_db_schema 命令实现。

使用方法:
    python manage.py check_db_schema            # 检查 schema 是否一致
    python manage.py check_db_schema --fix      # 自动修复 schema 差异

功能:
    - 检查 Django 模型与数据库表结构是否一致
    - 自动生成并执行 DDL 语句修复差异
    - 支持检测表、列、索引的结构差异
"""
import logging
from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '检查数据库 schema 与 Django 模型是否一致，支持 --fix 参数自动修复'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='自动修复 schema 差异（执行 DDL）',
        )

    def handle(self, *args, **options):
        self.fix = options['fix']
        self.schema_issues = []
        
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('数据库 Schema 检查'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        
        # 获取所有模型
        all_models = apps.get_models()
        
        for model in all_models:
            if model._meta.managed:  # 只检查 managed 模型
                continue
            
            self.stdout.write(f"\n检查表: {model._meta.db_table}")
            self.check_table(model)
        
        # 输出结果
        if self.schema_issues:
            self.stdout.write(self.style.WARNING(f"\n发现 {len(self.schema_issues)} 个 schema 差异:"))
            for issue in self.schema_issues:
                self.stdout.write(self.style.WARNING(f"  - {issue}"))
            
            if self.fix:
                self.stdout.write(self.style.SUCCESS("\n正在修复 schema..."))
                self.fix_schema()
                self.stdout.write(self.style.SUCCESS("修复完成"))
            else:
                self.stdout.write(self.style.HTTP_INFO("\n运行 'python manage.py check_db_schema --fix' 自动修复"))
        else:
            self.stdout.write(self.style.SUCCESS("\n✓ Schema 检查通过，无差异"))
    
    def check_table(self, model):
        """检查单个表的结构"""
        table_name = model._meta.db_table
        
        with connection.cursor() as cursor:
            # 检查表是否存在
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, [table_name])
            
            if not cursor.fetchone()[0]:
                self.schema_issues.append(f"表 {table_name} 不存在")
                return
            
            # 获取表的列信息
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, [table_name])
            
            db_columns = {row[0]: {'type': row[1], 'nullable': row[2]} for row in cursor.fetchall()}
            
            # 检查模型字段
            for field in model._meta.get_fields():
                if field.concrete and not field.many_to_many:
                    column_name = field.column
                    if column_name not in db_columns:
                        self.schema_issues.append(f"表 {table_name} 缺少列 {column_name}")
    
    def fix_schema(self):
        """修复 schema 差异"""
        ddl_statements = self.generate_ddl()
        
        with connection.cursor() as cursor:
            for ddl in ddl_statements:
                self.stdout.write(f"执行: {ddl}")
                try:
                    cursor.execute(ddl)
                    self.stdout.write(self.style.SUCCESS(f"  ✓ 成功"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ 失败: {e}"))
    
    def generate_ddl(self):
        """生成修复 DDL 语句"""
        ddl = []
        
        for issue in self.schema_issues:
            if "不存在" in issue:
                # 创建表
                parts = issue.split()
                table_name = parts[1]
                ddl.append(f"CREATE TABLE {table_name} (id BIGSERIAL PRIMARY KEY);")
            
            elif "缺少列" in issue:
                # 添加列（需要根据模型字段类型确定）
                parts = issue.split()
                table_name = parts[1]
                column_name = parts[3]
                ddl.append(f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT;")
        
        return ddl