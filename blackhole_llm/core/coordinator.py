"""
黑洞协调器 - 统一调度虫群和神经群

功能：
1. 协调虫群爬取
2. 协调神经训练
3. 知识融合
4. 状态监控
"""

import time
import threading
from datetime import datetime
from typing import Dict, List


class Coordinator:
    """协调器 - 统一调度"""
    
    def __init__(self, swarm, neural_cluster, knowledge_blackhole):
        self.swarm = swarm
        self.neural_cluster = neural_cluster
        self.knowledge_blackhole = knowledge_blackhole
        
        # 状态
        self.is_running = False
        self.cycle_count = 0
        
        # 停止信号
        self._stop_event = threading.Event()
    
    def run_cycle(self):
        """执行一个周期"""
        self.cycle_count += 1
        
        print(f"\n{'='*50}")
        print(f"  黑洞周期 #{self.cycle_count}")
        print(f"{'='*50}")
        
        # 1. 虫群爬取
        print("\n[1/3] 虫群爬取...")
        crawled = self.swarm.crawl_all_parallel()
        
        # 2. 吞噬知识
        print("\n[2/3] 吞噬知识...")
        absorbed = self.knowledge_blackhole.absorb(crawled)
        print(f"  ✓ 吞噬: {absorbed} 条知识")
        
        # 3. 神经训练
        print("\n[3/3] 神经训练...")
        trained = self.neural_cluster.train_all_parallel()
        
        # 打印状态
        self._print_status()
    
    def _print_status(self):
        """打印状态"""
        stats = self.get_stats()
        
        print(f"\n{'─'*50}")
        print(f"  黑洞状态")
        print(f"{'─'*50}")
        print(f"  知识总量: {stats['knowledge']['total_knowledge']:,}")
        print(f"  爬取总数: {stats['swarm']['total_crawled']:,}")
        print(f"  训练总数: {stats['neural']['total_trained']:,}")
        print(f"  运行周期: {self.cycle_count}")
        print(f"{'─'*50}")
    
    def start(self):
        """启动协调器"""
        if self.is_running:
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # 启动虫群
        self.swarm.start()
        
        # 启动神经群
        self.neural_cluster.start()
        
        print("\n" + "="*50)
        print("  🕳️ 黑洞协调器启动！")
        print("="*50)
        print(f"  虫群: {len(self.swarm.agents)} 只")
        print(f"  神经: {len(self.neural_cluster.networks)} 条")
        print("="*50 + "\n")
    
    def stop(self):
        """停止协调器"""
        self._stop_event.set()
        self.swarm.stop()
        self.neural_cluster.stop()
        self.is_running = False
        
        print("\n黑洞协调器已停止")
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "is_running": self.is_running,
            "cycle_count": self.cycle_count,
            "swarm": self.swarm.get_stats(),
            "neural": self.neural_cluster.get_stats(),
            "knowledge": self.knowledge_blackhole.get_stats()
        }


if __name__ == "__main__":
    print("测试协调器...")
    
    from config import default_config
    from swarm.crawler_swarm import CrawlerSwarm
    from neural.neural_cluster import NeuralCluster
    from knowledge_blackhole import KnowledgeBlackhole
    
    blackhole = KnowledgeBlackhole(default_config.blackhole)
    swarm = CrawlerSwarm(default_config.swarm, blackhole)
    neural = NeuralCluster(default_config.neural, blackhole)
    
    coordinator = Coordinator(swarm, neural, blackhole)
    
    # 测试一个周期
    coordinator.run_cycle()
    
    print(f"\n统计: {coordinator.get_stats()}")
