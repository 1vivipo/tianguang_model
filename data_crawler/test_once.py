#!/usr/bin/env python3
"""
快速测试 - 收集一次数据看看效果
"""

import os
import sys

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_all_crawlers import DataCollector

def test():
    print("=" * 50)
    print("  快速测试 - 收集一次数据")
    print("=" * 50)
    
    collector = DataCollector()
    
    # 收集一次
    count = collector.collect_once()
    
    # 保存
    collector.save_data()
    
    print(f"\n✅ 测试完成!")
    print(f"   收集数据: {count} 条")
    print(f"   总数据: {len(collector.all_data)} 条")

if __name__ == "__main__":
    test()
