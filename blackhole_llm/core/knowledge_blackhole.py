"""
黑洞知识核心 - 吞噬所有知识

功能：
1. 吸收所有虫子爬取的知识
2. 自动分类整理
3. 知识融合
4. 快速检索
"""

import os
import json
import hashlib
import threading
import time
from datetime import datetime
from typing import List, Dict, Optional
from collections import Counter
import random


class KnowledgeBlackhole:
    """知识黑洞 - 吞噬所有知识"""
    
    def __init__(self, config):
        self.config = config
        
        # 知识存储
        self.knowledge: Dict[str, Dict] = {}
        
        # 领域索引
        self.domain_index: Dict[str, List[str]] = {}
        
        # 关键词索引
        self.keyword_index: Dict[str, List[str]] = {}
        
        # 统计
        self.total_absorbed = 0
        self.last_absorb = None
        
        # 锁
        self._lock = threading.Lock()
        
        # 加载
        self._load()
    
    def _load(self):
        """加载知识"""
        if not os.path.exists(self.config.knowledge_dir):
            os.makedirs(self.config.knowledge_dir)
            return
        
        for filename in os.listdir(self.config.knowledge_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.config.knowledge_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        for item in data:
                            self._add_to_memory(item)
                except:
                    pass
        
        print(f"✓ 知识黑洞加载: {len(self.knowledge)} 条知识")
    
    def _add_to_memory(self, item: Dict):
        """添加到内存"""
        kid = item.get("id", hashlib.md5(str(item).encode()).hexdigest()[:12])
        item["id"] = kid
        
        self.knowledge[kid] = item
        
        # 更新领域索引
        domain = item.get("domain", "其他")
        if domain not in self.domain_index:
            self.domain_index[domain] = []
        if kid not in self.domain_index[domain]:
            self.domain_index[domain].append(kid)
        
        # 更新关键词索引
        for keyword in item.get("keywords", []):
            keyword = keyword.lower()
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = []
            if kid not in self.keyword_index[keyword]:
                self.keyword_index[keyword].append(kid)
    
    def absorb(self, knowledge_list: List[Dict]) -> int:
        """吞噬知识"""
        with self._lock:
            absorbed = 0
            
            for item in knowledge_list:
                # 生成ID
                content = item.get("content", "")
                kid = hashlib.md5(content.encode()).hexdigest()[:12]
                
                # 检查重复
                if kid in self.knowledge:
                    continue
                
                item["id"] = kid
                item["absorbed_at"] = datetime.now().isoformat()
                
                # 添加到内存
                self._add_to_memory(item)
                
                # 保存到文件
                self._save_item(item)
                
                absorbed += 1
            
            self.total_absorbed += absorbed
            self.last_absorb = datetime.now().isoformat()
            
            return absorbed
    
    def _save_item(self, item: Dict):
        """保存单条知识"""
        kid = item["id"]
        filepath = os.path.join(self.config.knowledge_dir, f"{kid}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(item, f, ensure_ascii=False)
    
    def sample(self, n: int = 100) -> List[Dict]:
        """随机采样知识"""
        if len(self.knowledge) <= n:
            return list(self.knowledge.values())
        
        return random.sample(list(self.knowledge.values()), n)
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
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
    
    def get_by_domain(self, domain: str) -> List[Dict]:
        """按领域获取"""
        kids = self.domain_index.get(domain, [])
        return [self.knowledge[kid] for kid in kids if kid in self.knowledge]
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total_knowledge": len(self.knowledge),
            "total_absorbed": self.total_absorbed,
            "last_absorb": self.last_absorb,
            "domains": {
                domain: len(kids) 
                for domain, kids in sorted(
                    self.domain_index.items(), 
                    key=lambda x: len(x[1]), 
                    reverse=True
                )[:20]
            },
            "keywords_count": len(self.keyword_index)
        }


if __name__ == "__main__":
    print("测试知识黑洞...")
    
    from config import default_config
    
    blackhole = KnowledgeBlackhole(default_config.blackhole)
    
    # 吞噬知识
    test_knowledge = [
        {"domain": "科技", "title": "AI", "content": "人工智能是...", "keywords": ["AI"]},
        {"domain": "财经", "title": "股票", "content": "股票是...", "keywords": ["股票"]},
    ]
    
    absorbed = blackhole.absorb(test_knowledge)
    print(f"吞噬: {absorbed} 条")
    
    # 搜索
    results = blackhole.search("AI")
    print(f"搜索 'AI': {[r['title'] for r in results]}")
    
    # 统计
    print(f"统计: {blackhole.get_stats()}")
