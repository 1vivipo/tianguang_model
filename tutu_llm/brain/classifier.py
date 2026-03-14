"""
突突知识分类器

功能：
1. 自动分类知识
2. 提取关键词
3. 生成摘要
4. 去重过滤
"""

import os
import re
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from collections import Counter
from datetime import datetime


class KnowledgeClassifier:
    """知识分类器"""
    
    def __init__(self, categories: List[str] = None):
        self.categories = categories or [
            "科技", "财经", "教育", "娱乐", "体育",
            "健康", "生活", "文化", "政治", "其他"
        ]
        
        # 分类关键词
        self.category_keywords = {
            "科技": ["AI", "人工智能", "机器学习", "深度学习", "编程", "代码", "软件", "硬件", "互联网", "科技", "技术", "Python", "Java", "算法"],
            "财经": ["股票", "基金", "投资", "理财", "金融", "经济", "银行", "财经", "股市", "基金"],
            "教育": ["教育", "学校", "大学", "学习", "考试", "培训", "课程", "老师", "学生"],
            "娱乐": ["娱乐", "明星", "电影", "音乐", "综艺", "游戏", "演员", "歌手"],
            "体育": ["体育", "足球", "篮球", "比赛", "运动员", "奥运", "世界杯", "NBA"],
            "健康": ["健康", "医疗", "医院", "医生", "疾病", "养生", "保健", "疫苗"],
            "生活": ["生活", "美食", "旅游", "购物", "家居", "汽车", "房产"],
            "文化": ["文化", "历史", "艺术", "文学", "书籍", "博物馆", "传统文化"],
            "政治": ["政治", "政府", "政策", "法律", "外交", "国家", "领导人"],
        }
    
    def classify(self, text: str) -> Tuple[str, float]:
        """分类文本"""
        scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            scores[category] = score
        
        if not scores or max(scores.values()) == 0:
            return "其他", 0.0
        
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category] / (sum(scores.values()) + 1)
        
        return best_category, confidence
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """提取关键词"""
        # 简单提取（实际可用jieba）
        # 中文词
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        # 英文词
        english_words = re.findall(r'[A-Za-z]{2,}', text.upper())
        
        all_words = chinese_words + english_words
        
        # 统计频率
        word_freq = Counter(all_words)
        
        # 过滤停用词
        stopwords = {"的", "是", "在", "了", "和", "与", "或", "但", "这", "那", "有", "为", "以", "及"}
        
        keywords = [
            word for word, freq in word_freq.most_common(top_n * 2)
            if word not in stopwords and freq > 1
        ][:top_n]
        
        return keywords
    
    def generate_summary(self, text: str, max_length: int = 100) -> str:
        """生成摘要"""
        # 取前几句
        sentences = re.split(r'[。！？\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        summary = ""
        for sentence in sentences:
            if len(summary) + len(sentence) <= max_length:
                summary += sentence + "。"
            else:
                break
        
        return summary or text[:max_length] + "..."
    
    def process(self, knowledge: Dict) -> Dict:
        """处理知识条目"""
        text = knowledge.get("content", "") + " " + knowledge.get("title", "")
        
        # 分类
        category, confidence = self.classify(text)
        
        # 提取关键词
        keywords = self.extract_keywords(text)
        
        # 生成摘要
        summary = self.generate_summary(knowledge.get("content", ""))
        
        return {
            **knowledge,
            "category": category,
            "confidence": confidence,
            "keywords": keywords,
            "summary": summary,
            "processed_at": datetime.now().isoformat()
        }
    
    def is_duplicate(self, knowledge: Dict, existing: List[Dict], threshold: float = 0.8) -> bool:
        """检查是否重复"""
        new_text = knowledge.get("content", "")
        
        for item in existing:
            existing_text = item.get("content", "")
            
            # 简单相似度检查
            common = len(set(new_text) & set(existing_text))
            total = max(len(set(new_text)), len(set(existing_text)))
            
            if total > 0 and common / total > threshold:
                return True
        
        return False


if __name__ == "__main__":
    print("测试知识分类器...")
    
    classifier = KnowledgeClassifier()
    
    test_texts = [
        {"title": "AI新突破", "content": "人工智能在机器学习领域取得重大突破，深度学习算法性能提升50%。"},
        {"title": "股市动态", "content": "今日股票市场大涨，科技股领涨，投资者信心增强。"},
        {"title": "健康养生", "content": "秋季养生要注意饮食健康，多吃蔬菜水果，保持运动。"},
    ]
    
    for item in test_texts:
        result = classifier.process(item)
        print(f"\n标题: {result['title']}")
        print(f"分类: {result['category']} (置信度: {result['confidence']:.2f})")
        print(f"关键词: {result['keywords']}")
        print(f"摘要: {result['summary']}")
