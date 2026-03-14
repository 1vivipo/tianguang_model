# 天光AI MetaBrain V3.1 - 云端部署版
# 精简版，适合云端部署

import os
import re
import json
import hashlib
import logging
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional

# Flask
from flask import Flask, request, jsonify
from flask_cors import CORS

# 尝试导入可选依赖
try:
    import jieba
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ==================== 配置 ====================

PORT = int(os.environ.get("PORT", 8080))
API_KEY = os.environ.get("API_KEY", "sk-tianguang-2024-metabrain-v31")
API_SECRET = os.environ.get("API_SECRET", "tianguang-secret-key-2024")
MODEL_NAME = os.environ.get("MODEL_NAME", "metabrain-v3.1")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MetaBrain")

# ==================== 内置知识库 ====================

DEFAULT_FACTS = [
    {"id": "fact_001", "tags": ["天气", "降温", "寒冷"], "content": "近期全国大范围降温，单日降温幅度达8-10度，伴随大风、雨雪天气"},
    {"id": "fact_002", "tags": ["健康", "感冒", "防护"], "content": "突然降温会导致呼吸道免疫力下降，易引发感冒、支气管炎，老人小孩需重点防护"},
    {"id": "fact_003", "tags": ["保暖", "穿搭", "技巧"], "content": "洋葱式穿搭最有效：内层透气、中层保暖、外层防风"},
    {"id": "fact_004", "tags": ["人工智能", "AI", "技术"], "content": "人工智能是模拟人类智能的技术，包括机器学习、深度学习、自然语言处理等"},
    {"id": "fact_005", "tags": ["编程", "学习", "技能"], "content": "学习编程建议从Python开始，语法简单，应用广泛，适合初学者"},
]

DEFAULT_STYLES = {
    "default": "关于{query}，给你几个实用的建议：\n{content}\n\n希望对你有帮助！",
    "professional": "【专业解答】\n\n问题：{query}\n\n{content}\n\n以上信息仅供参考。",
    "friendly": "你好！关于{query}，我帮你整理了这些信息：\n\n{content}\n\n还有什么想了解的吗？",
    "brief": "{content}"
}

# ==================== 搜索引擎 ====================

class SimpleSearcher:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    
    def search(self, query: str, max_results: int = 3) -> List[Dict]:
        if not HAS_REQUESTS:
            return []
        results = []
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
            resp = requests.get(url, headers=self.headers, timeout=10)
            data = resp.json()
            if data.get('AbstractText'):
                results.append({'title': '摘要', 'content': data['AbstractText'], 'url': data.get('AbstractURL', '')})
            for topic in data.get('RelatedTopics', [])[:max_results]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({'title': '相关', 'content': topic['Text'], 'url': topic.get('FirstURL', '')})
        except Exception as e:
            logger.error(f"搜索失败: {e}")
        return results

# ==================== 知识库 ====================

class SimpleKnowledgeBase:
    def __init__(self):
        self.facts = {f['id']: f for f in DEFAULT_FACTS}
        self.searcher = SimpleSearcher() if HAS_REQUESTS else None
    
    def search_local(self, query: str) -> List[Dict]:
        results = []
        query_lower = query.lower()
        for fact in self.facts.values():
            score = sum(10 for tag in fact['tags'] if tag.lower() in query_lower)
            if any(word in fact['content'] for word in query_lower.split()):
                score += 5
            if score > 0:
                results.append({**fact, 'score': score, 'source': 'local'})
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def search(self, query: str, use_web: bool = True) -> List[Dict]:
        results = self.search_local(query)
        if use_web and self.searcher and len(results) < 2:
            web_results = self.searcher.search(query)
            for r in web_results:
                r['source'] = 'web'
                r['id'] = f"web_{hash(r['content']) % 10000}"
            results.extend(web_results)
        return results[:5]

# ==================== 生成器 ====================

class SimpleGenerator:
    def __init__(self):
        self.styles = DEFAULT_STYLES
    
    def generate(self, query: str, facts: List[Dict], style: str = "default") -> str:
        if not facts:
            return f"抱歉，没有找到关于{query}的相关信息。请尝试其他问题。"
        content_parts = []
        for i, fact in enumerate(facts, 1):
            src = "【本地】" if fact.get('source') == 'local' else "【网络】"
            content_parts.append(f"{i}. {src} {fact['content']}")
        content = "\n".join(content_parts)
        template = self.styles.get(style, self.styles["default"])
        return template.format(query=query, content=content)

# ==================== Flask应用 ====================

kb = SimpleKnowledgeBase()
gen = SimpleGenerator()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({
        "name": "天光AI - MetaBrain",
        "version": "3.1.0",
        "model": MODEL_NAME,
        "status": "running",
        "api_key": API_KEY,
        "endpoints": {
            "openai": "POST /v1/chat/completions",
            "simple": "POST /api/chat",
            "health": "GET /health"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "model": MODEL_NAME, "timestamp": datetime.now().isoformat()})

@app.route('/v1/chat/completions', methods=['POST'])
def openai_chat():
    auth = request.headers.get('Authorization', '')
    key = auth[7:] if auth.startswith('Bearer ') else request.headers.get('X-API-KEY', '')
    if key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401
    
    data = request.get_json() or {}
    messages = data.get('messages', [])
    user_message = ""
    for msg in reversed(messages):
        if msg.get('role') == 'user':
            user_message = msg.get('content', '')
            break
    
    if not user_message:
        return jsonify({"error": "No user message"}), 400
    
    facts = kb.search(user_message)
    answer = gen.generate(user_message, facts)
    
    return jsonify({
        "id": f"chatcmpl-{int(datetime.now().timestamp())}",
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": MODEL_NAME,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": answer}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": len(user_message), "completion_tokens": len(answer), "total_tokens": len(user_message) + len(answer)}
    })

@app.route('/v1/models', methods=['GET'])
def list_models():
    return jsonify({"object": "list", "data": [{"id": MODEL_NAME, "object": "model", "owned_by": "tianguang"}]})

@app.route('/api/chat', methods=['POST'])
def simple_chat():
    key = request.headers.get('X-API-KEY', '')
    if key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401
    
    data = request.get_json() or {}
    query = data.get('query', '')
    style = data.get('style', 'default')
    use_web = data.get('enable_online_search', True)
    
    if not query:
        return jsonify({"error": "No query"}), 400
    
    facts = kb.search(query, use_web)
    answer = gen.generate(query, facts, style)
    
    return jsonify({"answer": answer, "status": "success", "model": MODEL_NAME, "sources": len(facts)})

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "No query"}), 400
    results = kb.search(query)
    return jsonify({"query": query, "results": results, "count": len(results)})

if __name__ == "__main__":
    print(f"\n天光AI - MetaBrain V3.1\nAPI Key: {API_KEY}\nPort: {PORT}\n")
    app.run(host="0.0.0.0", port=PORT)
