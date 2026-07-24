#!/bin/bash
# 验证修复是否生效

echo "=================================================="
echo "验证时间修复"
echo "=================================================="

echo ""
echo "【1】检查代码版本："
cd /home/xiaoluban/backend
git log --oneline -3
echo ""

echo "【2】检查后端进程是否使用最新代码："
ps aux | grep "manage.py runserver" | grep -v grep
echo ""

echo "【3】运行诊断脚本："
python3 diagnose_time.py 2>&1
echo ""

echo "【4】测试API返回的时间格式："
echo "环境列表："
curl -s http://localhost:6000/api/environments | python3 -m json.tool | grep -A 5 "occupy_time\|release_time" | head -20
echo ""

echo "占用记录："
curl -s "http://localhost:6000/api/environments/usage?limit=2" | python3 -m json.tool
echo ""

echo "【5】当前系统时间："
date '+%Y-%m-%d %H:%M:%S %Z'
echo ""

echo "=================================================="