#!/bin/bash
# 超级爬虫 - 快速启动

echo "╔══════════════════════════════════════════════════════════╗"
echo "║            超级爬虫系统 - 10000只虫子                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

ROUNDS=${1:-10}

echo "抓取轮数: $ROUNDS 把"
echo "每把: 1000只虫子"
echo "预计数据: $((ROUNDS * 2000))+ 条"
echo ""
echo "开始抓取！"
echo ""

cd /home/z/tianguang_model/data_crawler
python3 super_crawler.py --rounds $ROUNDS
