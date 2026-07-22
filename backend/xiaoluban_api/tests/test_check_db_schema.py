"""
测试 check_db_schema 命令

运行: python manage.py test xiaoluban_api.tests.test_check_db_schema
"""
from django.test import TestCase
from django.core.management import call_command
from io import StringIO


class CheckDbSchemaCommandTest(TestCase):
    """测试 check_db_schema 管理命令"""
    
    def test_check_without_fix(self):
        """测试检查命令（不修复）"""
        out = StringIO()
        call_command('check_db_schema', stdout=out)
        output = out.getvalue()
        self.assertIn('数据库 Schema 检查', output)
    
    def test_generate_ddl_method(self):
        """测试 generate_ddl 方法"""
        from xiaoluban_api.management.commands.check_db_schema import Command
        
        cmd = Command()
        cmd.schema_issues = [
            '表 test_table 不存在',
            '表 xiaoluban_environments 缺少列 status',
            '表 xiaoluban_history 缺少列 user',
        ]
        
        ddl = cmd.generate_ddl()
        
        # 验证 DDL 语句
        self.assertEqual(len(ddl), 3)
        
        # 验证表创建语句
        self.assertIn('CREATE TABLE "test_table"', ddl[0])
        
        # 验证添加列语句（使用双引号）
        self.assertIn('ALTER TABLE "xiaoluban_environments"', ddl[1])
        self.assertIn('"status"', ddl[1])
        
        # 验证保留关键字 user 被正确引用
        self.assertIn('ALTER TABLE "xiaoluban_history"', ddl[2])
        self.assertIn('"user"', ddl[2])
    
    def test_reserved_keyword_quoting(self):
        """测试保留关键字被正确引用"""
        from xiaoluban_api.management.commands.check_db_schema import Command
        
        cmd = Command()
        cmd.schema_issues = ['表 xiaoluban_history 缺少列 user']
        
        ddl = cmd.generate_ddl()
        
        # user 是 PostgreSQL 保留关键字，必须用双引号
        self.assertIn('"user"', ddl[0])
        self.assertNotIn(' ADD COLUMN user ', ddl[0])
