"""
黑洞虫群系统 - 100只虫子并行爬取

每只虫子负责一个领域：
- 虫子1: 人工智能
- 虫子2: 机器学习
- 虫子3: 深度学习
- ...
- 虫子100: 社会热点

并行工作，同时爬取！
"""

import os
import re
import time
import json
import random
import threading
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue


@dataclass
class CrawlerAgent:
    """单只虫子"""
    id: int
    domain: str
    keywords: List[str]
    sources: List[str]
    
    def __post_init__(self):
        self.crawl_count = 0
        self.last_crawl = None
        self.status = "idle"


class CrawlerSwarm:
    """虫群 - 100只虫子并行爬取"""
    
    def __init__(self, config, knowledge_blackhole=None):
        self.config = config
        self.knowledge_blackhole = knowledge_blackhole
        
        # 创建虫群
        self.agents: List[CrawlerAgent] = []
        self._create_swarm()
        
        # 状态
        self.is_running = False
        self.total_crawled = 0
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent)
        
        # 任务队列
        self.task_queue = queue.Queue()
        
        # 停止信号
        self._stop_event = threading.Event()
    
    def _create_swarm(self):
        """创建虫群"""
        domains = self.config.domains[:self.config.num_crawlers]
        
        for i, domain in enumerate(domains):
            # 为每个领域生成关键词
            keywords = self._generate_keywords(domain)
            
            # 为每个领域生成数据源
            sources = self._generate_sources(domain)
            
            agent = CrawlerAgent(
                id=i + 1,
                domain=domain,
                keywords=keywords,
                sources=sources
            )
            self.agents.append(agent)
        
        print(f"✓ 虫群创建完成: {len(self.agents)} 只虫子")
    
    def _generate_keywords(self, domain: str) -> List[str]:
        """为领域生成关键词"""
        # 领域相关关键词映射
        domain_keywords = {
            "人工智能": ["AI", "人工智能", "机器智能", "智能系统", "AGI"],
            "机器学习": ["机器学习", "ML", "监督学习", "无监督学习", "强化学习"],
            "深度学习": ["深度学习", "神经网络", "CNN", "RNN", "Transformer"],
            "自然语言处理": ["NLP", "自然语言", "文本分析", "语言模型", "GPT"],
            "计算机视觉": ["计算机视觉", "图像识别", "目标检测", "图像分割"],
            "区块链": ["区块链", "比特币", "以太坊", "智能合约", "Web3"],
            "云计算": ["云计算", "AWS", "阿里云", "容器", "Kubernetes"],
            "大数据": ["大数据", "数据分析", "数据挖掘", "Hadoop", "Spark"],
            "股票": ["股票", "股市", "A股", "美股", "港股"],
            "基金": ["基金", "公募基金", "私募基金", "ETF", "定投"],
            # ... 更多领域关键词
        }
        
        return domain_keywords.get(domain, [domain])
    
    def _generate_sources(self, domain: str) -> List[str]:
        """为领域生成数据源"""
        # 通用数据源
        base_sources = [
            f"https://www.baidu.com/s?wd={urllib.parse.quote(domain)}",
            f"https://www.zhihu.com/search?q={urllib.parse.quote(domain)}",
        ]
        
        # 领域特定数据源
        if domain in ["人工智能", "机器学习", "深度学习"]:
            base_sources.extend([
                "https://www.jiqizhixin.com",
                "https://www.36kr.com",
            ])
        elif domain in ["股票", "基金", "财经"]:
            base_sources.extend([
                "https://finance.sina.com.cn",
                "https://xueqiu.com",
            ])
        
        return base_sources
    
    def crawl_with_agent(self, agent: CrawlerAgent) -> List[Dict]:
        """单只虫子爬取"""
        results = []
        
        try:
            agent.status = "crawling"
            
            # 爬取关键词相关内容
            for keyword in agent.keywords[:2]:  # 每次最多2个关键词
                try:
                    # 使用DuckDuckGo搜索
                    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(keyword)}&format=json&no_html=1"
                    
                    req = urllib.request.Request(
                        url, 
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        data = json.loads(response.read().decode())
                    
                    if data.get('AbstractText'):
                        results.append({
                            "domain": agent.domain,
                            "title": keyword,
                            "content": data['AbstractText'],
                            "source": data.get('AbstractURL', ''),
                            "agent_id": agent.id,
                            "crawled_at": datetime.now().isoformat()
                        })
                    
                    time.sleep(0.5)  # 避免被封
                    
                except Exception as e:
                    pass
            
            agent.crawl_count += len(results)
            agent.last_crawl = datetime.now().isoformat()
            agent.status = "idle"
            
        except Exception as e:
            agent.status = "error"
        
        return results
    
    def crawl_all_parallel(self) -> List[Dict]:
        """所有虫子并行爬取"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🕷️ 虫群出击！{len(self.agents)}只虫子并行爬取...")
        
        all_results = []
        futures = []
        
        # 提交所有任务
        for agent in self.agents:
            future = self.executor.submit(self.crawl_with_agent, agent)
            futures.append(future)
        
        # 收集结果
        completed = 0
        for future in as_completed(futures):
            try:
                results = future.result()
                all_results.extend(results)
                completed += 1
                
                if completed % 20 == 0:
                    print(f"  进度: {completed}/{len(self.agents)} 只虫子完成")
                    
            except Exception as e:
                pass
        
        # 更新统计
        self.total_crawled += len(all_results)
        
        print(f"  ✓ 本次爬取: {len(all_results)} 条知识, 累计: {self.total_crawled} 条")
        
        return all_results
    
    def start(self):
        """启动虫群"""
        if self.is_running:
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        def run():
            print(f"\n🕷️ 虫群启动！{len(self.agents)}只虫子，间隔{self.config.crawl_interval}秒")
            
            while not self._stop_event.is_set():
                try:
                    # 并行爬取
                    results = self.crawl_all_parallel()
                    
                    # 存入知识黑洞
                    if self.knowledge_blackhole and results:
                        self.knowledge_blackhole.absorb(results)
                    
                except Exception as e:
                    print(f"虫群错误: {e}")
                
                self._stop_event.wait(self.config.crawl_interval)
            
            print("虫群已停止")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def stop(self):
        """停止虫群"""
        self._stop_event.set()
        self.is_running = False
    
    def get_stats(self) -> Dict:
        """获取统计"""
        active = sum(1 for a in self.agents if a.status == "crawling")
        
        return {
            "is_running": self.is_running,
            "total_agents": len(self.agents),
            "active_agents": active,
            "total_crawled": self.total_crawled,
            "top_domains": sorted(
                [(a.domain, a.crawl_count) for a in self.agents],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }


if __name__ == "__main__":
    print("测试虫群系统...")
    
    from config import default_config
    
    swarm = CrawlerSwarm(default_config.swarm)
    
    # 测试一次爬取
    results = swarm.crawl_all_parallel()
    
    print(f"\n爬取结果:")
    for r in results[:5]:
        print(f"  [{r['domain']}] {r['title']}: {r['content'][:50]}...")
    
    print(f"\n统计: {swarm.get_stats()}")
