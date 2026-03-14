#!/usr/bin/env python3
"""
突突 Tutu LLM 启动脚本
"""

import os
import sys

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║                   突突 Tutu LLM                         ║
║                 自主学习AI v1.0                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 创建目录
    dirs = ["knowledge", "checkpoints"]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"✓ 创建目录: {d}/")
    
    # 检查依赖
    print("\n检查依赖...")
    
    try:
        import flask
        print(f"✓ flask {flask.__version__}")
    except ImportError:
        print("✗ 缺少 flask，请运行: pip install flask flask-cors")
        return
    
    try:
        import requests
        print(f"✓ requests {requests.__version__}")
    except ImportError:
        print("✗ 缺少 requests，请运行: pip install requests")
        return
    
    try:
        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4")
    except ImportError:
        print("⚠ 缺少 beautifulsoup4，将使用简单爬虫")
    
    # 启动
    print("\n启动突突...")
    print("  - 自动爬虫: 每5分钟爬取一次")
    print("  - 自动学习: 每10分钟学习一次")
    print("  - API端口: 8080")
    print()
    
    from api.server import create_app
    from config import TutuConfig
    
    config = TutuConfig.from_env()
    app = create_app(config)
    app.run(host="0.0.0.0", port=config.api.port)


if __name__ == "__main__":
    main()
