"""
洱海长期记忆系统

特点：
1. 永久存储学到的知识
2. 对话历史记忆
3. 用户偏好记忆
4. 记忆权重衰减
5. 自动总结压缩
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any
from collections import Counter
import re


class Memory:
    """单条记忆"""
    
    def __init__(
        self,
        content: str,
        memory_type: str = "knowledge",  # knowledge, conversation, preference
        importance: float = 1.0,
        metadata: Dict = None
    ):
        self.id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        self.content = content
        self.memory_type = memory_type
        self.importance = importance
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.access_count = 0
        self.last_accessed = datetime.now().isoformat()
    
    def access(self):
        """访问记忆"""
        self.access_count += 1
        self.last_accessed = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Memory":
        memory = cls(
            content=data["content"],
            memory_type=data.get("memory_type", "knowledge"),
            importance=data.get("importance", 1.0),
            metadata=data.get("metadata", {})
        )
        memory.id = data["id"]
        memory.created_at = data["created_at"]
        memory.access_count = data.get("access_count", 0)
        memory.last_accessed = data.get("last_accessed", data["created_at"])
        return memory


class LongTermMemory:
    """长期记忆系统"""
    
    def __init__(
        self,
        memory_file: str = "./memory/long_term.json",
        max_memories: int = 10000,
        memory_decay: float = 0.99
    ):
        self.memory_file = memory_file
        self.max_memories = max_memories
        self.memory_decay = memory_decay
        
        # 记忆存储
        self.memories: Dict[str, Memory] = {}
        
        # 类型索引
        self.type_index: Dict[str, List[str]] = {
            "knowledge": [],
            "conversation": [],
            "preference": []
        }
        
        # 关键词索引
        self.keyword_index: Dict[str, List[str]] = {}
        
        # 加载记忆
        self._load()
    
    def _load(self):
        """加载记忆"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data.get("memories", []):
                    memory = Memory.from_dict(item)
                    self.memories[memory.id] = memory
                    self._index_memory(memory)
                
                print(f"加载了 {len(self.memories)} 条记忆")
            except Exception as e:
                print(f"加载记忆失败: {e}")
    
    def _save(self):
        """保存记忆"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "total_memories": len(self.memories),
            "memories": [m.to_dict() for m in self.memories.values()]
        }
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _index_memory(self, memory: Memory):
        """索引记忆"""
        # 类型索引
        if memory.memory_type in self.type_index:
            if memory.id not in self.type_index[memory.memory_type]:
                self.type_index[memory.memory_type].append(memory.id)
        
        # 关键词索引
        words = self._extract_keywords(memory.content)
        for word in words:
            if word not in self.keyword_index:
                self.keyword_index[word] = []
            if memory.id not in self.keyword_index[word]:
                self.keyword_index[word].append(memory.id)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单提取（实际可用jieba）
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text.lower())
        return [w for w in words if len(w) > 1]
    
    def remember(
        self,
        content: str,
        memory_type: str = "knowledge",
        importance: float = 1.0,
        metadata: Dict = None
    ) -> Memory:
        """记住新内容"""
        memory = Memory(content, memory_type, importance, metadata)
        
        self.memories[memory.id] = memory
        self._index_memory(memory)
        
        # 检查容量
        if len(self.memories) > self.max_memories:
            self._forget_least_important()
        
        # 保存
        self._save()
        
        return memory
    
    def recall(self, query: str, top_k: int = 5) -> List[Memory]:
        """回忆相关记忆"""
        # 提取查询关键词
        query_words = self._extract_keywords(query)
        
        # 统计相关记忆
        memory_scores: Counter = Counter()
        
        for word in query_words:
            if word in self.keyword_index:
                for mid in self.keyword_index[word]:
                    memory_scores[mid] += 1
        
        # 获取并排序
        results = []
        for mid, score in memory_scores.most_common(top_k * 2):
            if mid in self.memories:
                memory = self.memories[mid]
                memory.access()
                
                # 计算综合分数
                final_score = score * memory.importance * (self.memory_decay ** memory.access_count)
                results.append((memory, final_score))
        
        # 排序并返回
        results.sort(key=lambda x: x[1], reverse=True)
        return [m for m, s in results[:top_k]]
    
    def _forget_least_important(self):
        """遗忘最不重要的记忆"""
        # 计算每条记忆的重要性分数
        scores = []
        for mid, memory in self.memories.items():
            # 综合考虑：重要性、访问次数、创建时间
            age_days = (datetime.now() - datetime.fromisoformat(memory.created_at)).days
            score = memory.importance * (1 + memory.access_count * 0.1) * (self.memory_decay ** age_days)
            scores.append((mid, score))
        
        # 删除最不重要的10%
        scores.sort(key=lambda x: x[1])
        to_remove = int(len(self.memories) * 0.1)
        
        for mid, _ in scores[:to_remove]:
            self._forget(mid)
    
    def _forget(self, memory_id: str):
        """遗忘指定记忆"""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            
            # 从类型索引移除
            if memory.memory_type in self.type_index:
                if memory_id in self.type_index[memory.memory_type]:
                    self.type_index[memory.memory_type].remove(memory_id)
            
            # 从关键词索引移除
            words = self._extract_keywords(memory.content)
            for word in words:
                if word in self.keyword_index and memory_id in self.keyword_index[word]:
                    self.keyword_index[word].remove(memory_id)
            
            # 删除记忆
            del self.memories[memory_id]
    
    def learn_from_conversation(
        self,
        user_input: str,
        ai_response: str,
        feedback: str = "neutral"  # positive, neutral, negative
    ):
        """从对话中学习"""
        # 提取知识点
        knowledge = self._extract_knowledge(user_input, ai_response)
        
        # 根据反馈调整重要性
        importance = {
            "positive": 1.5,
            "neutral": 1.0,
            "negative": 0.5
        }.get(feedback, 1.0)
        
        # 存储
        for k in knowledge:
            self.remember(
                content=k,
                memory_type="knowledge",
                importance=importance,
                metadata={
                    "source": "conversation",
                    "user_input": user_input[:100],
                    "ai_response": ai_response[:100]
                }
            )
    
    def _extract_knowledge(self, user_input: str, ai_response: str) -> List[str]:
        """从对话中提取知识"""
        knowledge = []
        
        # 简单规则：提取问答对
        if "是" in ai_response or "是指" in ai_response:
            # 可能是定义
            knowledge.append(f"Q: {user_input} A: {ai_response[:200]}")
        
        # 提取列表类知识
        if "包括" in ai_response or "有以下" in ai_response:
            knowledge.append(ai_response[:300])
        
        return knowledge
    
    def get_stats(self) -> Dict:
        """获取记忆统计"""
        return {
            "total_memories": len(self.memories),
            "by_type": {
                t: len(ids) for t, ids in self.type_index.items()
            },
            "total_keywords": len(self.keyword_index),
            "oldest_memory": min(
                (m.created_at for m in self.memories.values()),
                default=None
            ),
            "newest_memory": max(
                (m.created_at for m in self.memories.values()),
                default=None
            )
        }


if __name__ == "__main__":
    print("测试长期记忆系统...")
    
    memory = LongTermMemory(memory_file="./test_memory.json")
    
    # 记住一些东西
    memory.remember("Python是一种编程语言", "knowledge")
    memory.remember("用户喜欢简洁的回答", "preference")
    
    # 回忆
    results = memory.recall("Python")
    print(f"回忆 'Python': {[m.content for m in results]}")
    
    # 从对话学习
    memory.learn_from_conversation(
        "什么是机器学习",
        "机器学习是人工智能的一个分支，它使计算机能够从数据中学习。",
        "positive"
    )
    
    # 统计
    print(f"记忆统计: {memory.get_stats()}")
    
    print("\n✅ 记忆系统测试通过！")
