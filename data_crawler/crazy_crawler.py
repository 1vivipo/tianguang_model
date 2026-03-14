#!/usr/bin/env python3
"""
疯狂爬虫系统 - 10万只虫子，30秒一把

安全范围内的最大配置：
- 10万只虫子（关键词池）
- 每把500只同时出击
- 30秒间隔（避免被封）
- 预计每小时 6000-18000 条数据

使用方法：
    python crazy_crawler.py --hours 8  # 跑8小时
    python crazy_crawler.py --rounds 100  # 抓100把
"""

import os
import sys
import time
import json
import random
import threading
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import gc

# ==================== 配置 ====================

NUM_CRAWLERS = 100000   # 10万只虫子！
MAX_WORKERS = 500       # 每把500只同时出击
CRAWL_INTERVAL = 30     # 30秒间隔
BATCH_SIZE = 500        # 每把500只

DATA_DIR = "/home/z/tianguang_model/collected_data"
REPO_DIR = "/home/z/tianguang_model"

# ==================== 10万关键词 ====================

def generate_100k_keywords():
    """生成10万个关键词"""
    keywords = []
    
    # 基础领域词
    base = [
        # 科技
        "人工智能", "机器学习", "深度学习", "神经网络", "GPT", "ChatGPT", "AI", "AGI",
        "Python", "Java", "JavaScript", "C++", "Go", "Rust", "TypeScript", "PHP",
        "前端", "后端", "全栈", "移动开发", "游戏开发", "小程序", "APP开发",
        "React", "Vue", "Angular", "Node.js", "Django", "Flask", "Spring",
        "Docker", "Kubernetes", "Linux", "Git", "GitHub", "数据库", "Redis",
        "云计算", "大数据", "区块链", "比特币", "以太坊", "Web3", "元宇宙",
        "网络安全", "黑客", "加密", "隐私", "信息安全",
        
        # 财经
        "股票", "基金", "债券", "期货", "外汇", "投资", "理财", "金融",
        "A股", "美股", "港股", "创业板", "科创板", "新三板",
        "银行", "保险", "信贷", "贷款", "信用卡", "支付宝", "微信支付",
        "经济", "宏观", "微观", "GDP", "通胀", "利率", "汇率",
        
        # 健康
        "健康", "医疗", "养生", "健身", "营养", "中医", "西医",
        "疾病", "症状", "治疗", "药物", "医院", "医生", "护士",
        "心理健康", "抑郁", "焦虑", "压力", "睡眠", "失眠",
        "减肥", "增肌", "饮食", "运动", "瑜伽", "跑步",
        
        # 教育
        "教育", "学习", "考试", "培训", "课程", "学校", "大学",
        "高考", "考研", "考公", "留学", "英语", "日语", "韩语",
        "数学", "物理", "化学", "生物", "历史", "地理", "政治",
        "编程", "设计", "美术", "音乐", "舞蹈", "体育",
        
        # 生活
        "美食", "旅游", "汽车", "房产", "家居", "装修", "家电",
        "购物", "网购", "海淘", "比价", "优惠", "折扣", "团购",
        "宠物", "养猫", "养狗", "婚恋", "育儿", "亲子", "家庭",
        "时尚", "穿搭", "美妆", "护肤", "发型", "美容",
        
        # 文化
        "历史", "文学", "艺术", "哲学", "宗教", "文化", "传统",
        "书法", "绘画", "音乐", "电影", "电视剧", "综艺", "动漫",
        "小说", "诗歌", "散文", "故事", "传说", "神话",
        "博物馆", "展览", "收藏", "古董", "文物",
        
        # 科学
        "物理", "化学", "生物", "数学", "天文", "地理", "科学",
        "宇宙", "黑洞", "星系", "行星", "卫星", "火箭", "航天",
        "基因", "DNA", "进化", "生态", "环境", "气候", "能源",
        "材料", "纳米", "量子", "原子", "分子", "元素",
        
        # 社会
        "法律", "法规", "政策", "制度", "政治", "军事", "外交",
        "社会", "民生", "就业", "创业", "职场", "管理", "领导",
        "新闻", "热点", "事件", "人物", "观点", "评论",
    ]
    
    keywords.extend(base)
    
    # 生成变体
    for word in base:
        keywords.append(f"什么是{word}")
        keywords.append(f"如何{word}")
        keywords.append(f"为什么{word}")
        keywords.append(f"{word}是什么")
        keywords.append(f"{word}怎么")
        keywords.append(f"{word}教程")
        keywords.append(f"{word}入门")
        keywords.append(f"{word}学习")
        keywords.append(f"{word}方法")
        keywords.append(f"{word}技巧")
    
    # 添加数字编号
    for i in range(1000):
        for word in base[:100]:
            keywords.append(f"{word}_{i}")
    
    # 去重并填充到10万
    keywords = list(set(keywords))
    
    while len(keywords) < NUM_CRAWLERS:
        idx = len(keywords) % len(base)
        keywords.append(f"{base[idx]}_扩展_{len(keywords)}")
    
    return keywords[:NUM_CRAWLERS]


@dataclass
class CrazyCrawler:
    """疯狂爬虫"""
    id: int
    keyword: str
    
    def crawl(self) -> List[Dict]:
        """爬取"""
        results = []
        
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(self.keyword)}&format=json&no_html=1"
            
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
            
            if data.get('AbstractText'):
                results.append({
                    "id": f"crazy_{self.id}",
                    "keyword": self.keyword,
                    "content": data['AbstractText'],
                    "source": data.get('AbstractURL', ''),
                    "crawled_at": datetime.now().isoformat()
                })
            
            for topic in data.get('RelatedTopics', [])[:2]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        "id": f"crazy_{self.id}_{len(results)}",
                        "keyword": self.keyword,
                        "content": topic['Text'],
                        "source": topic.get('FirstURL', ''),
                        "crawled_at": datetime.now().isoformat()
                    })
        
        except:
            pass
        
        return results


class CrazyCrawlerSystem:
    """疯狂爬虫系统"""
    
    def __init__(self):
        print("生成10万关键词...")
        self.keywords = generate_100k_keywords()
        print(f"✓ 关键词池: {len(self.keywords)} 个")
        
        self.all_data = []
        self.round_count = 0
        self.total_crawled = 0
        
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
        
        print(f"✓ 并发数: {MAX_WORKERS}")
        print(f"✓ 间隔: {CRAWL_INTERVAL}秒")
    
    def crawl_round(self) -> int:
        """抓一把"""
        self.round_count += 1
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"  第 {self.round_count} 把 - {BATCH_SIZE} 只虫子出击！")
        print(f"{'='*60}")
        
        # 随机选择
        batch_keywords = random.sample(self.keywords, BATCH_SIZE)
        
        # 并行爬取
        futures = []
        for i, keyword in enumerate(batch_keywords):
            crawler = CrazyCrawler(id=i, keyword=keyword)
            future = self.executor.submit(crawler.crawl)
            futures.append(future)
        
        # 收集结果
        count = 0
        for future in as_completed(futures):
            try:
                results = future.result()
                self.all_data.extend(results)
                count += len(results)
            except:
                pass
        
        self.total_crawled += count
        elapsed = time.time() - start_time
        
        print(f"  ✓ 本次: {count} 条")
        print(f"  ✓ 累计: {self.total_crawled} 条")
        print(f"  ✓ 用时: {elapsed:.1f} 秒")
        
        # 定期清理内存
        if self.round_count % 10 == 0:
            gc.collect()
        
        return count
    
    def save(self):
        """保存"""
        if not self.all_data:
            return
        
        filename = f"crazy_round{self.round_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ 保存: {filepath} ({len(self.all_data)} 条)")
        
        # 同步到黑洞
        blackhole_dir = os.path.join(REPO_DIR, "blackhole_llm", "blackhole_knowledge")
        os.makedirs(blackhole_dir, exist_ok=True)
        
        import shutil
        shutil.copy(filepath, os.path.join(blackhole_dir, filename))
    
    def run(self, rounds: int = None, hours: float = None):
        """运行"""
        if hours:
            rounds = int(hours * 3600 / CRAWL_INTERVAL)
        
        print(f"""
╔══════════════════════════════════════════════════════════╗
║            疯狂爬虫系统 - 10万只虫子                    ║
╠══════════════════════════════════════════════════════════╣
║  关键词池: {len(self.keywords):<42} ║
║  每把并发: {BATCH_SIZE}只{' '*38} ║
║  抓取轮数: {rounds}把{' '*40} ║
║  间隔时间: {CRAWL_INTERVAL}秒{' '*41} ║
║  预计数据: {rounds * 1500}+条{' '*37} ║
╚══════════════════════════════════════════════════════════╝
""")
        
        for i in range(rounds):
            self.crawl_round()
            
            # 每10把保存一次
            if (i + 1) % 10 == 0:
                self.save()
            
            if i < rounds - 1:
                time.sleep(CRAWL_INTERVAL)
        
        # 最后保存
        self.save()
        
        print(f"\n{'='*60}")
        print(f"  完成！总数据: {self.total_crawled} 条")
        print(f"{'='*60}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="疯狂爬虫系统")
    parser.add_argument("--rounds", type=int, default=10, help="抓取轮数")
    parser.add_argument("--hours", type=float, default=0, help="运行时间（小时）")
    
    args = parser.parse_args()
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    system = CrazyCrawlerSystem()
    
    if args.hours > 0:
        system.run(hours=args.hours)
    else:
        system.run(rounds=args.rounds)


if __name__ == "__main__":
    main()
