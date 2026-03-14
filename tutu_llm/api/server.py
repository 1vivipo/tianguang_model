"""
突突 Tutu LLM API服务

功能：
1. 对话接口
2. 知识检索
3. 状态监控
4. 手动触发学习
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict

from flask import Flask, request, jsonify
from flask_cors import CORS

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TutuConfig, default_config


class TutuEngine:
    """突突引擎"""
    
    def __init__(self, config: TutuConfig = None):
        self.config = config or default_config
        
        # 初始化组件
        self._init_components()
    
    def _init_components(self):
        """初始化组件"""
        print("\n" + "="*50)
        print("  突突 Tutu LLM 初始化")
        print("="*50)
        
        # 1. 知识库
        print("\n[1/4] 加载知识库...")
        from memory.knowledge_base import KnowledgeBase
        self.knowledge_base = KnowledgeBase(
            knowledge_dir=self.config.memory.knowledge_dir,
            max_knowledge=self.config.memory.max_knowledge
        )
        
        # 2. 分类器
        print("[2/4] 加载分类器...")
        from brain.classifier import KnowledgeClassifier
        self.classifier = KnowledgeClassifier(
            categories=self.config.classifier.categories
        )
        
        # 3. 自动爬虫
        print("[3/4] 启动自动爬虫...")
        from crawler.auto_crawler import AutoCrawler
        self.crawler = AutoCrawler(
            config=self.config.crawler,
            knowledge_base=self.knowledge_base
        )
        if self.config.crawler.enabled:
            self.crawler.start()
        
        # 4. 自动学习器
        print("[4/4] 启动自动学习器...")
        from brain.auto_learner import AutoLearner
        self.learner = AutoLearner(
            config=self.config.learner,
            knowledge_base=self.knowledge_base
        )
        if self.config.learner.enabled:
            self.learner.start()
        
        print("\n" + "="*50)
        print("  ✓ 突突初始化完成！")
        print("  ✓ 自动爬虫: 运行中")
        print("  ✓ 自动学习: 运行中")
        print("  ✓ 知识库: {} 条".format(len(self.knowledge_base.knowledge)))
        print("="*50 + "\n")
    
    def chat(self, message: str) -> Dict:
        """对话"""
        start_time = time.time()
        
        # 搜索知识库
        results = self.knowledge_base.search(message, top_k=3)
        
        # 生成回答
        if results:
            answer_parts = ["根据我的知识库："]
            for i, r in enumerate(results, 1):
                answer_parts.append(f"\n{i}. 【{r.get('category', '未分类')}】{r.get('title', '')}")
                answer_parts.append(f"   {r.get('content', '')[:200]}...")
            answer = "\n".join(answer_parts)
        else:
            answer = f"关于「{message}」，我目前了解的信息有限。让我继续学习，下次会更好！"
        
        elapsed = time.time() - start_time
        
        return {
            "answer": answer,
            "sources": len(results),
            "elapsed_ms": int(elapsed * 1000)
        }
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "crawler": self.crawler.get_stats(),
            "learner": self.learner.get_stats(),
            "knowledge": self.knowledge_base.get_stats(),
            "uptime": datetime.now().isoformat()
        }
    
    def trigger_crawl(self) -> Dict:
        """手动触发爬取"""
        pages = self.crawler.crawl_once()
        
        # 处理并存入知识库
        added = 0
        for page in pages:
            processed = self.classifier.process(page.to_dict())
            self.knowledge_base.add(processed)
            added += 1
        
        return {
            "crawled": len(pages),
            "added": added
        }
    
    def trigger_learn(self) -> Dict:
        """手动触发学习"""
        return self.learner.learn_once()
    
    def shutdown(self):
        """关闭"""
        print("\n正在关闭突突...")
        self.crawler.stop()
        self.learner.stop()
        print("✓ 突突已关闭")


def create_app(config: TutuConfig = None) -> Flask:
    """创建Flask应用"""
    config = config or default_config
    
    app = Flask(__name__)
    CORS(app)
    
    # 初始化引擎
    engine = TutuEngine(config)
    
    @app.route('/')
    def index():
        return jsonify({
            "name": "突突 Tutu LLM",
            "version": "1.0.0",
            "model": config.api.model_name,
            "status": "running",
            "features": [
                "🚀 自动爬取 - 24/7自动获取知识",
                "🧠 自动学习 - 后台持续训练",
                "📚 自动分类 - 智能整理知识",
                "🔄 持续进化 - 越来越聪明"
            ],
            "api_key": config.api.api_key,
            "endpoints": {
                "chat": "POST /api/chat",
                "status": "GET /api/status",
                "crawl": "POST /api/crawl",
                "learn": "POST /api/learn"
            }
        })
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        # 鉴权
        key = request.headers.get('X-API-KEY', '')
        if key != config.api.api_key:
            return jsonify({"error": "Invalid API key"}), 401
        
        data = request.get_json() or {}
        message = data.get('message', '') or data.get('query', '')
        
        if not message:
            return jsonify({"error": "No message"}), 400
        
        result = engine.chat(message)
        
        return jsonify({
            "answer": result["answer"],
            "status": "success",
            "sources": result["sources"],
            "elapsed_ms": result["elapsed_ms"]
        })
    
    @app.route('/api/status', methods=['GET'])
    def status():
        """获取状态"""
        return jsonify(engine.get_status())
    
    @app.route('/api/crawl', methods=['POST'])
    def trigger_crawl():
        """手动触发爬取"""
        key = request.headers.get('X-API-KEY', '')
        if key != config.api.api_key:
            return jsonify({"error": "Invalid API key"}), 401
        
        result = engine.trigger_crawl()
        return jsonify(result)
    
    @app.route('/api/learn', methods=['POST'])
    def trigger_learn():
        """手动触发学习"""
        key = request.headers.get('X-API-KEY', '')
        if key != config.api.api_key:
            return jsonify({"error": "Invalid API key"}), 401
        
        result = engine.trigger_learn()
        return jsonify(result)
    
    @app.route('/api/knowledge', methods=['GET'])
    def get_knowledge():
        """获取知识列表"""
        category = request.args.get('category', '')
        
        if category:
            items = engine.knowledge_base.get_by_category(category)
        else:
            items = engine.knowledge_base.get_all()[:20]
        
        return jsonify({
            "count": len(items),
            "items": items
        })
    
    return app


if __name__ == "__main__":
    config = TutuConfig.from_env()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                   突突 Tutu LLM                         ║
║                 自主学习AI v1.0                          ║
╠══════════════════════════════════════════════════════════╣
║  🚀 自动爬取 - 24/7自动获取知识                          ║
║  🧠 自动学习 - 后台持续训练                              ║
║  📚 自动分类 - 智能整理知识                              ║
║  🔄 持续进化 - 越来越聪明                                ║
╠══════════════════════════════════════════════════════════╣
║  API Key: {config.api.api_key:<42} ║
║  Port:    {config.api.port:<42} ║
╚══════════════════════════════════════════════════════════╝
""")
    
    app = create_app(config)
    app.run(host="0.0.0.0", port=config.api.port)
