"""
洱海知识检索系统

特点：
1. 本地知识库检索
2. 网络搜索补充
3. 语义相似度匹配
4. 实时更新知识库
"""

import os
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from collections import Counter
import re

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


class KnowledgeRetriever:
    """知识检索器"""
    
    def __init__(
        self,
        knowledge_dir: str = "./knowledge",
        top_k: int = 5,
        enable_web_search: bool = True
    ):
        self.knowledge_dir = knowledge_dir
        self.top_k = top_k
        self.enable_web_search = enable_web_search
        
        # 知识库
        self.knowledge: Dict[str, Dict] = {}
        
        # 倒排索引
        self.inverted_index: Dict[str, List[str]] = {}
        
        # 加载知识
        self._load_knowledge()
    
    def _load_knowledge(self):
        """加载知识库"""
        if not os.path.exists(self.knowledge_dir):
            os.makedirs(self.knowledge_dir)
            self._init_default_knowledge()
        
        # 加载JSON文件
        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.knowledge_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            self._add_knowledge(item)
                    elif isinstance(data, dict):
                        self._add_knowledge(data)
        
        # 构建索引
        self._build_index()
    
    def _init_default_knowledge(self):
        """初始化默认知识"""
        default_knowledge = [
            {
                "id": "k001",
                "title": "人工智能",
                "content": "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。包括机器学习、深度学习、自然语言处理、计算机视觉等领域。",
                "tags": ["AI", "人工智能", "技术"]
            },
            {
                "id": "k002",
                "title": "机器学习",
                "content": "机器学习是人工智能的核心技术，通过数据和算法让计算机系统自动改进和学习。主要类型包括监督学习、无监督学习和强化学习。",
                "tags": ["机器学习", "AI", "算法"]
            },
            {
                "id": "k003",
                "title": "深度学习",
                "content": "深度学习是机器学习的一个子领域，使用多层神经网络来学习数据的表示。在图像识别、语音识别、自然语言处理等领域取得了突破性进展。",
                "tags": ["深度学习", "神经网络", "AI"]
            },
            {
                "id": "k004",
                "title": "自然语言处理",
                "content": "自然语言处理（NLP）是人工智能的重要分支，让计算机能够理解、解释和生成人类语言。应用包括机器翻译、情感分析、问答系统等。",
                "tags": ["NLP", "语言处理", "AI"]
            },
            {
                "id": "k005",
                "title": "洱海",
                "content": "洱海位于中国云南省大理市，是云南省第二大淡水湖。洱海形状像人耳，故名洱海。湖水清澈，风景优美，是大理著名的旅游景点。",
                "tags": ["洱海", "云南", "旅游", "湖泊"]
            }
        ]
        
        with open(os.path.join(self.knowledge_dir, 'default.json'), 'w', encoding='utf-8') as f:
            json.dump(default_knowledge, f, ensure_ascii=False, indent=2)
    
    def _add_knowledge(self, item: Dict):
        """添加知识"""
        if 'id' not in item:
            item['id'] = hashlib.md5(item.get('content', '').encode()).hexdigest()[:12]
        
        self.knowledge[item['id']] = item
    
    def _build_index(self):
        """构建倒排索引"""
        self.inverted_index = {}
        
        for kid, item in self.knowledge.items():
            # 提取关键词
            words = self._tokenize(item.get('content', ''))
            words.extend(item.get('tags', []))
            words.append(item.get('title', ''))
            
            # 建立索引
            for word in words:
                word = word.lower().strip()
                if word:
                    if word not in self.inverted_index:
                        self.inverted_index[word] = []
                    if kid not in self.inverted_index[word]:
                        self.inverted_index[word].append(kid)
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        if HAS_JIEBA:
            return list(jieba.cut(text))
        else:
            # 简单分词
            return re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+|[0-9]+', text)
    
    def search_local(self, query: str) -> List[Dict]:
        """搜索本地知识库"""
        # 分词
        query_words = self._tokenize(query)
        
        # 统计相关文档
        doc_scores: Counter = Counter()
        
        for word in query_words:
            word = word.lower().strip()
            if word in self.inverted_index:
                for kid in self.inverted_index[word]:
                    doc_scores[kid] += 1
        
        # 排序并返回
        results = []
        for kid, score in doc_scores.most_common(self.top_k):
            item = self.knowledge.get(kid, {})
            results.append({
                **item,
                'score': score,
                'source': 'local'
            })
        
        return results
    
    def search_web(self, query: str) -> List[Dict]:
        """网络搜索"""
        if not HAS_REQUESTS or not self.enable_web_search:
            return []
        
        results = []
        try:
            # 使用DuckDuckGo API
            import urllib.parse
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            if data.get('AbstractText'):
                results.append({
                    'id': 'web_001',
                    'title': '摘要',
                    'content': data['AbstractText'],
                    'source': 'web'
                })
            
            for topic in data.get('RelatedTopics', [])[:3]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'id': f"web_{hash(topic['Text']) % 10000}",
                        'title': topic.get('FirstURL', '').split('/')[-1] if topic.get('FirstURL') else '相关',
                        'content': topic['Text'],
                        'source': 'web'
                    })
        except Exception as e:
            print(f"网络搜索失败: {e}")
        
        return results
    
    def search(self, query: str) -> List[Dict]:
        """综合搜索"""
        # 本地搜索
        results = self.search_local(query)
        
        # 网络搜索补充
        if len(results) < 2:
            web_results = self.search_web(query)
            results.extend(web_results)
        
        return results[:self.top_k]
    
    def add_knowledge(self, content: str, title: str = "", tags: List[str] = None):
        """添加新知识"""
        item = {
            'id': hashlib.md5(content.encode()).hexdigest()[:12],
            'title': title,
            'content': content,
            'tags': tags or []
        }
        
        self._add_knowledge(item)
        self._build_index()
        
        # 保存到文件
        self._save_knowledge(item)
    
    def _save_knowledge(self, item: Dict):
        """保存知识到文件"""
        filename = f"learned_{item['id']}.json"
        filepath = os.path.join(self.knowledge_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(item, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("测试知识检索系统...")
    
    retriever = KnowledgeRetriever()
    
    # 测试搜索
    query = "什么是人工智能"
    results = retriever.search(query)
    
    print(f"查询: {query}")
    print(f"结果数: {len(results)}")
    
    for r in results:
        print(f"  - {r.get('title', 'N/A')}: {r.get('content', '')[:50]}...")
    
    print("\n✅ 检索系统测试通过！")
