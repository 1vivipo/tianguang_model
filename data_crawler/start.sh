#!/bin/bash
# Plan B - 快速启动脚本

echo "╔══════════════════════════════════════════════════════════╗"
echo "║            Plan B - 本地数据收集系统                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要Python3"
    exit 1
fi

echo "✓ Python3 已安装"

# 检查依赖
echo ""
echo "检查依赖..."

pip3 install requests flask flask-cors -q 2>/dev/null

echo "✓ 依赖已安装"

# 运行时间
HOURS=${1:-8}

echo ""
echo "运行时间: $HOURS 小时"
echo ""
echo "开始收集数据..."
echo ""

cd /home/z/tianguang_model/data_crawler
python3 run_all_crawlers.py --hours $HOURS
