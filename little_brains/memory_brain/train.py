#!/usr/bin/env python3
"""
记忆脑 Memory Brain - 存储和调用知识

功能：
1. 存储知识（问答对）
2. 快速检索知识
3. 关联相关知识
4. 遗忘不重要的知识

训练目标：
- 能够记住1000+条知识
- 检索准确率 > 90%
- 响应时间 < 100ms

大小目标：~5MB
"""

import os
import sys
import json
import time
import pickle
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import re


class MemoryBrain:
    """记忆脑"""
    
    def __init__(self):
        # 知识存储
        self.knowledge: Dict[str, Dict] = {}
        
        # 索引
        self.keyword_index: Dict[str, List[str]] = defaultdict(list)
        self.category_index: Dict[str, List[str]] = defaultdict(list)
        
        # 统计
        self.stats = {
            "total_knowledge": 0,
            "total_queries": 0,
            "successful_queries": 0
        }
    
    def remember(self, question: str, answer: str, category: str = "general", 
                 keywords: List[str] = None, importance: float = 1.0):
        """记住一条知识"""
        # 生成ID
        kid = hashlib.md5(question.encode()).hexdigest()[:12]
        
        # 提取关键词
        if keywords is None:
            keywords = self._extract_keywords(question + " " + answer)
        
        # 存储
        self.knowledge[kid] = {
            "id": kid,
            "question": question,
            "answer": answer,
            "category": category,
            "keywords": keywords,
            "importance": importance,
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }
        
        # 更新索引
        for kw in keywords:
            if kid not in self.keyword_index[kw]:
                self.keyword_index[kw].append(kid)
        
        if kid not in self.category_index[category]:
            self.category_index[category].append(kid)
        
        self.stats["total_knowledge"] += 1
        
        return kid
    
    def recall(self, query: str, top_k: int = 3) -> List[Dict]:
        """回忆知识"""
        self.stats["total_queries"] += 1
        
        # 提取查询关键词
        query_keywords = self._extract_keywords(query)
        
        # 计算相关度
        scores: Dict[str, float] = defaultdict(float)
        
        for kw in query_keywords:
            if kw in self.keyword_index:
                for kid in self.keyword_index[kw]:
                    # 基础分数
                    scores[kid] += 1.0
                    # 重要性加成
                    if kid in self.knowledge:
                        scores[kid] += self.knowledge[kid]["importance"] * 0.5
        
        # 排序
        sorted_kids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:top_k]
        
        # 返回结果
        results = []
        for kid in sorted_kids:
            if kid in self.knowledge:
                item = self.knowledge[kid].copy()
                item["score"] = scores[kid]
                item["access_count"] += 1
                results.append(item)
        
        if results:
            self.stats["successful_queries"] += 1
        
        return results
    
    def forget(self, kid: str):
        """遗忘知识"""
        if kid not in self.knowledge:
            return
        
        item = self.knowledge[kid]
        
        # 从索引移除
        for kw in item.get("keywords", []):
            if kid in self.keyword_index[kw]:
                self.keyword_index[kw].remove(kid)
        
        if kid in self.category_index.get(item.get("category", ""), []):
            self.category_index[item["category"]].remove(kid)
        
        # 删除知识
        del self.knowledge[kid]
        self.stats["total_knowledge"] -= 1
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 中文分词（简单版）
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+|[0-9]+', text.lower())
        
        # 过滤停用词
        stopwords = {"的", "是", "在", "了", "和", "与", "或", "但", "这", "那", "有", "为"}
        words = [w for w in words if w not in stopwords and len(w) > 1]
        
        return list(set(words))[:10]
    
    def get_by_category(self, category: str) -> List[Dict]:
        """按类别获取知识"""
        kids = self.category_index.get(category, [])
        return [self.knowledge[kid] for kid in kids if kid in self.knowledge]
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            **self.stats,
            "success_rate": self.stats["successful_queries"] / max(1, self.stats["total_queries"]),
            "categories": len(self.category_index),
            "keywords": len(self.keyword_index)
        }
    
    def save(self, path: str):
        """保存"""
        data = {
            "knowledge": self.knowledge,
            "keyword_index": dict(self.keyword_index),
            "category_index": dict(self.category_index),
            "stats": self.stats
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        
        # 同时保存JSON版本（可读）
        json_path = path.replace('.pkl', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "knowledge": self.knowledge,
                "stats": self.stats
            }, f, ensure_ascii=False, indent=2)
    
    def load(self, path: str):
        """加载"""
        if not os.path.exists(path):
            return
        
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.knowledge = data.get("knowledge", {})
        self.keyword_index = defaultdict(list, data.get("keyword_index", {}))
        self.category_index = defaultdict(list, data.get("category_index", {}))
        self.stats = data.get("stats", self.stats)


# ==================== 训练数据 ====================

TRAINING_DATA = [
    # 编程基础
    {"q": "什么是变量？", "a": "变量是存储数据的容器，可以保存各种类型的值，并在程序中使用。", "category": "编程基础"},
    {"q": "什么是函数？", "a": "函数是一段可重复使用的代码块，用于执行特定任务，可以接收参数并返回结果。", "category": "编程基础"},
    {"q": "什么是循环？", "a": "循环是一种控制结构，用于重复执行某段代码，直到满足特定条件为止。", "category": "编程基础"},
    {"q": "什么是条件判断？", "a": "条件判断是根据条件真假执行不同代码分支的结构，如if-else语句。", "category": "编程基础"},
    {"q": "什么是数组？", "a": "数组是一种数据结构，用于存储多个相同类型的元素，可以通过索引访问。", "category": "编程基础"},
    
    # Python
    {"q": "Python是什么？", "a": "Python是一种高级编程语言，以简洁易读著称，广泛应用于Web开发、数据分析、AI等领域。", "category": "Python"},
    {"q": "Python如何定义变量？", "a": "Python中直接使用变量名赋值即可定义变量，如：x = 10，name = 'hello'。", "category": "Python"},
    {"q": "Python如何定义函数？", "a": "使用def关键字定义函数，如：def my_func(param): return param * 2。", "category": "Python"},
    {"q": "Python如何循环？", "a": "Python使用for和while进行循环，如：for i in range(10): print(i)。", "category": "Python"},
    {"q": "Python如何条件判断？", "a": "使用if-elif-else进行条件判断，如：if x > 0: print('正数')。", "category": "Python"},
    
    # AI基础
    {"q": "什么是人工智能？", "a": "人工智能(AI)是计算机科学分支，致力于创建能执行人类智能任务的系统。", "category": "AI"},
    {"q": "什么是机器学习？", "a": "机器学习是AI核心技术，通过算法让计算机从数据中自动学习和改进。", "category": "AI"},
    {"q": "什么是深度学习？", "a": "深度学习是机器学习子集，使用多层神经网络学习数据的复杂模式。", "category": "AI"},
    {"q": "什么是神经网络？", "a": "神经网络是模仿人脑结构的计算系统，由神经元连接组成，可学习模式。", "category": "AI"},
    {"q": "什么是自然语言处理？", "a": "自然语言处理(NLP)是AI分支，让计算机理解、处理和生成人类语言。", "category": "AI"},
    
    # 数据结构
    {"q": "什么是链表？", "a": "链表是一种线性数据结构，元素通过指针连接，插入删除效率高但随机访问慢。", "category": "数据结构"},
    {"q": "什么是栈？", "a": "栈是一种后进先出(LIFO)的数据结构，只能在栈顶进行插入和删除操作。", "category": "数据结构"},
    {"q": "什么是队列？", "a": "队列是一种先进先出(FIFO)的数据结构，在一端插入，另一端删除。", "category": "数据结构"},
    {"q": "什么是树？", "a": "树是一种非线性数据结构，由节点和边组成，有一个根节点，每个节点可有多个子节点。", "category": "数据结构"},
    {"q": "什么是图？", "a": "图是由节点和边组成的数据结构，可表示复杂关系，如社交网络、地图等。", "category": "数据结构"},
    
    # 算法
    {"q": "什么是排序算法？", "a": "排序算法是将数据按特定顺序排列的算法，如冒泡排序、快速排序、归并排序等。", "category": "算法"},
    {"q": "什么是搜索算法？", "a": "搜索算法是在数据中查找特定元素的算法，如线性搜索、二分搜索等。", "category": "算法"},
    {"q": "什么是递归？", "a": "递归是函数调用自身的编程技术，通过将问题分解为更小的子问题来解决。", "category": "算法"},
    {"q": "什么是动态规划？", "a": "动态规划是将复杂问题分解为子问题并存储结果的优化技术，避免重复计算。", "category": "算法"},
    {"q": "什么是贪心算法？", "a": "贪心算法在每一步选择局部最优解，期望得到全局最优解的算法策略。", "category": "算法"},
    
    # Web开发
    {"q": "什么是HTML？", "a": "HTML是超文本标记语言，用于创建网页结构，定义网页内容的含义和结构。", "category": "Web"},
    {"q": "什么是CSS？", "a": "CSS是层叠样式表，用于描述HTML元素的显示方式，控制网页的视觉表现。", "category": "Web"},
    {"q": "什么是JavaScript？", "a": "JavaScript是一种脚本语言，用于实现网页的交互功能，是前端开发的核心技术。", "category": "Web"},
    {"q": "什么是API？", "a": "API是应用程序编程接口，定义了软件组件之间交互的规则和协议。", "category": "Web"},
    {"q": "什么是数据库？", "a": "数据库是有组织的数据集合，通过数据库管理系统进行存储、管理和检索。", "category": "Web"},
    
    # 生活常识
    {"q": "如何保持健康？", "a": "保持健康需要：均衡饮食、规律运动、充足睡眠、心理健康、定期体检。", "category": "生活"},
    {"q": "如何提高效率？", "a": "提高效率的方法：制定计划、设置优先级、避免干扰、适当休息、使用工具。", "category": "生活"},
    {"q": "如何学习新技能？", "a": "学习新技能：设定目标、分解步骤、刻意练习、及时反馈、持续改进。", "category": "生活"},
    {"q": "如何管理时间？", "a": "时间管理技巧：列出任务、估算时间、设置截止日期、避免拖延、定期回顾。", "category": "生活"},
    {"q": "如何解决问题？", "a": "解决问题步骤：明确问题、分析原因、提出方案、评估选择、执行验证。", "category": "生活"},
]


def train_memory_brain():
    """训练记忆脑"""
    print("""
╔══════════════════════════════════════════════════════════╗
║            记忆脑 Memory Brain 训练                    ║
╠══════════════════════════════════════════════════════════╣
║  目标：存储和调用知识                                  ║
║  大小：~5MB                                            ║
║  数据：{} 条知识                                       ║
╚══════════════════════════════════════════════════════════╝
""".format(len(TRAINING_DATA)))
    
    brain = MemoryBrain()
    
    # 学习知识
    print("\n[1/3] 学习知识...")
    for item in TRAINING_DATA:
        brain.remember(
            question=item["q"],
            answer=item["a"],
            category=item.get("category", "general")
        )
        print(f"  ✓ 记住: {item['q'][:30]}...")
    
    # 测试检索
    print("\n[2/3] 测试检索...")
    test_queries = [
        "什么是Python？",
        "如何学习？",
        "什么是算法？",
        "变量是什么？"
    ]
    
    for query in test_queries:
        results = brain.recall(query)
        print(f"\n  查询: {query}")
        if results:
            print(f"  找到: {results[0]['answer'][:50]}...")
        else:
            print(f"  未找到")
    
    # 保存
    print("\n[3/3] 保存模型...")
    brain.save("/home/z/tianguang_model/little_brains/memory_brain/memory_brain.pkl")
    
    # 统计
    stats = brain.get_stats()
    print(f"\n✅ 训练完成！")
    print(f"   知识量: {stats['total_knowledge']} 条")
    print(f"   分类数: {stats['categories']} 个")
    print(f"   关键词: {stats['keywords']} 个")
    
    return brain


if __name__ == "__main__":
    train_memory_brain()
