"""
突突知识库

功能：
1. 存储爬取的知识
2. 快速检索
3. 自动去重
4. 持久化存储
"""

import os
import json
import hashlib
import threading
from datetime import datetime
from typing import List, Dict, Optional
from collections import Counter


class KnowledgeBase:
    """知识库"""
    
    def __init__(self, knowledge_dir: str = "./knowledge", max_knowledge: int = 100000):
        self.knowledge_dir = knowledge_dir
        self.max_knowledge = max_knowledge
        
        # 知识存储
        self.knowledge: Dict[str, Dict] = {}
        
        # 索引
        self.keyword_index: Dict[str, List[str]] = {}
        self.category_index: Dict[str, List[str]] = {}
        
        # 锁
        self._lock = threading.Lock()
        
        # 加载
        self._load()
    
    def _load(self):
        """加载知识库"""
        if not os.path.exists(self.knowledge_dir):
            os.makedirs(self.knowledge_dir)
            return
        
        for filename in os.listdir(self.knowledge_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.knowledge_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        for item in data:
                            self._add_to_memory(item)
                    elif isinstance(data, dict):
                        self._add_to_memory(data)
                except Exception as e:
                    print(f"加载失败 {filename}: {e}")
        
        print(f"✓ 知识库加载: {len(self.knowledge)} 条")
    
    def _save(self, knowledge: Dict):
        """保存单条知识"""
        kid = knowledge.get("id", hashlib.md5(str(knowledge).encode()).hexdigest()[:12])
        
        filepath = os.path.join(self.knowledge_dir, f"{kid}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, ensure_ascii=False, indent=2)
    
    def _add_to_memory(self, knowledge: Dict):
        """添加到内存"""
        kid = knowledge.get("id", hashlib.md5(str(knowledge).encode()).hexdigest()[:12])
        knowledge["id"] = kid
        
        self.knowledge[kid] = knowledge
        
        # 更新关键词索引
        for keyword in knowledge.get("keywords", []):
            keyword = keyword.lower()
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = []
            if kid not in self.keyword_index[keyword]:
                self.keyword_index[keyword].append(kid)
        
        # 更新分类索引
        category = knowledge.get("category", "其他")
        if category not in self.category_index:
            self.category_index[category] = []
        if kid not in self.category_index[category]:
            self.category_index[category].append(kid)
    
    def add(self, knowledge: Dict) -> str:
        """添加知识"""
        with self._lock:
            # 生成ID
            kid = hashlib.md5(
                (knowledge.get("title", "") + knowledge.get("content", "")).encode()
            ).hexdigest()[:12]
            
            # 检查重复
            if kid in self.knowledge:
                return kid
            
            knowledge["id"] = kid
            knowledge["added_at"] = datetime.now().isoformat()
            
            # 添加到内存
            self._add_to_memory(knowledge)
            
            # 保存到文件
            self._save(knowledge)
            
            # 检查容量
            if len(self.knowledge) > self.max_knowledge:
                self._cleanup()
            
            return kid
    
    def get(self, kid: str) -> Optional[Dict]:
        """获取知识"""
        return self.knowledge.get(kid)
    
    def get_all(self) -> List[Dict]:
        """获取所有知识"""
        return list(self.knowledge.values())
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索知识"""
        # 分词
        words = query.lower().split()
        
        # 统计相关度
        scores: Counter = Counter()
        
        for word in words:
            if word in self.keyword_index:
                for kid in self.keyword_index[word]:
                    scores[kid] += 1
        
        # 返回结果
        results = []
        for kid, score in scores.most_common(top_k):
            if kid in self.knowledge:
                item = self.knowledge[kid].copy()
                item["score"] = score
                results.append(item)
        
        return results
    
    def get_by_category(self, category: str) -> List[Dict]:
        """按分类获取"""
        kids = self.category_index.get(category, [])
        return [self.knowledge[kid] for kid in kids if kid in self.knowledge]
    
    def _cleanup(self):
        """清理旧知识"""
        # 删除最旧的10%
        to_remove = int(len(self.knowledge) * 0.1)
        
        # 按时间排序
        sorted_knowledge = sorted(
            self.knowledge.items(),
            key=lambda x: x[1].get("added_at", "")
        )
        
        # 删除
        for kid, _ in sorted_knowledge[:to_remove]:
            self.remove(kid)
    
    def remove(self, kid: str):
        """删除知识"""
        if kid not in self.knowledge:
            return
        
        knowledge = self.knowledge[kid]
        
        # 从索引移除
        for keyword in knowledge.get("keywords", []):
            keyword = keyword.lower()
            if keyword in self.keyword_index and kid in self.keyword_index[keyword]:
                self.keyword_index[keyword].remove(kid)
        
        category = knowledge.get("category", "其他")
        if category in self.category_index and kid in self.category_index[category]:
            self.category_index[category].remove(kid)
        
        # 从内存移除
        del self.knowledge[kid]
        
        # 删除文件
        filepath = os.path.join(self.knowledge_dir, f"{kid}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total": len(self.knowledge),
            "by_category": {
                cat: len(kids) for cat, kids in self.category_index.items()
            },
            "total_keywords": len(self.keyword_index),
            "max_knowledge": self.max_knowledge
        }


if __name__ == "__main__":
    print("测试知识库...")
    
    kb = KnowledgeBase("./test_knowledge")
    
    # 添加知识
    kb.add({
        "title": "Python编程",
        "content": "Python是一种流行的编程语言",
        "category": "科技",
        "keywords": ["Python", "编程", "语言"]
    })
    
    kb.add({
        "title": "机器学习",
        "content": "机器学习是AI的核心技术",
        "category": "科技",
        "keywords": ["AI", "机器学习", "技术"]
    })
    
    # 搜索
    results = kb.search("Python")
    print(f"搜索 'Python': {[r['title'] for r in results]}")
    
    # 统计
    print(f"统计: {kb.get_stats()}")
