"""
突突自动爬虫系统

功能：
1. 24/7自动爬取网页
2. 提取正文内容
3. 过滤广告和垃圾
4. 自动存入知识库
"""

import os
import re
import time
import random
import threading
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import json
import hashlib

# 尝试导入可选依赖
try:
    import requests
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


@dataclass
class CrawledPage:
    """爬取的页面"""
    url: str
    title: str
    content: str
    category: str = "未分类"
    keywords: List[str] = None
    crawled_at: str = ""
    
    def __post_init__(self):
        if not self.crawled_at:
            self.crawled_at = datetime.now().isoformat()
        if self.keywords is None:
            self.keywords = []
    
    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "keywords": self.keywords,
            "crawled_at": self.crawled_at
        }


class SimpleCrawler:
    """简单爬虫（无依赖版）"""
    
    def __init__(self, user_agent: str = ""):
        self.headers = {'User-Agent': user_agent or 'Mozilla/5.0'}
    
    def fetch(self, url: str, timeout: int = 10) -> Optional[str]:
        """获取网页"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"爬取失败 {url}: {e}")
            return None
    
    def extract_text(self, html: str) -> Tuple[str, str]:
        """提取标题和正文"""
        # 提取标题
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "无标题"
        
        # 移除脚本和样式
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # 提取正文
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 截取前2000字
        if len(text) > 2000:
            text = text[:2000] + "..."
        
        return title, text


class BSCrawler:
    """BeautifulSoup爬虫（功能更强）"""
    
    def __init__(self, user_agent: str = ""):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch(self, url: str, timeout: int = 10) -> Optional[str]:
        """获取网页"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"爬取失败 {url}: {e}")
            return None
    
    def extract_text(self, html: str, url: str = "") -> Tuple[str, str]:
        """提取标题和正文"""
        soup = BeautifulSoup(html, 'lxml')
        
        # 提取标题
        title = ""
        if soup.title:
            title = soup.title.string or ""
        title = title.strip() or "无标题"
        
        # 移除不需要的元素
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'ads']):
            tag.decompose()
        
        # 提取正文
        # 尝试找到主要内容区域
        main_content = None
        for selector in ['article', 'main', '.content', '.article', '.post', '#content']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            text = soup.get_text(separator='\n', strip=True)
        
        # 清理
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        # 截取
        if len(text) > 3000:
            text = text[:3000] + "..."
        
        return title, text


class AutoCrawler:
    """自动爬虫 - 24/7自动爬取"""
    
    def __init__(self, config, knowledge_base=None):
        self.config = config
        self.knowledge_base = knowledge_base
        
        # 选择爬虫
        if HAS_BS4:
            self.crawler = BSCrawler(config.user_agent)
            print("✓ 使用BeautifulSoup爬虫")
        else:
            self.crawler = SimpleCrawler(config.user_agent)
            print("✓ 使用简单爬虫")
        
        # 状态
        self.is_running = False
        self.crawl_count = 0
        self.last_crawl = None
        
        # 线程
        self._thread = None
        self._stop_event = threading.Event()
    
    def crawl_url(self, url: str) -> Optional[CrawledPage]:
        """爬取单个URL"""
        html = self.crawler.fetch(url)
        if not html:
            return None
        
        title, content = self.crawler.extract_text(html, url)
        
        if len(content) < 100:  # 内容太短
            return None
        
        page = CrawledPage(
            url=url,
            title=title,
            content=content
        )
        
        return page
    
    def crawl_news(self) -> List[CrawledPage]:
        """爬取新闻"""
        pages = []
        
        # 新闻源
        news_urls = [
            "https://news.baidu.com",
            "https://www.36kr.com",
            "https://www.jiqizhixin.com",
        ]
        
        for url in news_urls:
            try:
                page = self.crawl_url(url)
                if page:
                    pages.append(page)
                    print(f"  ✓ 爬取: {page.title[:30]}...")
            except Exception as e:
                print(f"  ✗ 爬取失败 {url}: {e}")
        
        return pages
    
    def crawl_keywords(self, keywords: List[str]) -> List[CrawledPage]:
        """根据关键词爬取"""
        pages = []
        
        for keyword in keywords[:3]:  # 每次最多3个关键词
            try:
                # 使用DuckDuckGo搜索
                search_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(keyword)}&format=json"
                
                req = urllib.request.Request(search_url, headers={'User-Agent': self.config.user_agent})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
                
                # 提取摘要
                if data.get('AbstractText'):
                    page = CrawledPage(
                        url=data.get('AbstractURL', ''),
                        title=keyword,
                        content=data['AbstractText']
                    )
                    pages.append(page)
                    print(f"  ✓ 关键词 '{keyword}': {data['AbstractText'][:50]}...")
                
                time.sleep(1)  # 避免被封
                
            except Exception as e:
                print(f"  ✗ 关键词 '{keyword}' 失败: {e}")
        
        return pages
    
    def crawl_wikipedia(self) -> List[CrawledPage]:
        """爬取维基百科"""
        pages = []
        
        # 随机获取维基百科文章
        try:
            url = "https://zh.wikipedia.org/api/rest_v1/page/random/summary"
            req = urllib.request.Request(url, headers={'User-Agent': self.config.user_agent})
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            if data.get('extract'):
                page = CrawledPage(
                    url=data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    title=data.get('title', '维基百科'),
                    content=data['extract']
                )
                pages.append(page)
                print(f"  ✓ 维基: {page.title}")
        
        except Exception as e:
            print(f"  ✗ 维基百科失败: {e}")
        
        return pages
    
    def crawl_once(self) -> List[CrawledPage]:
        """执行一次爬取"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 开始爬取...")
        
        all_pages = []
        
        # 1. 爬取新闻
        print("  爬取新闻...")
        all_pages.extend(self.crawl_news())
        
        # 2. 爬取关键词
        print("  爬取关键词...")
        all_pages.extend(self.crawl_keywords(self.config.keywords))
        
        # 3. 爬取维基百科
        print("  爬取维基百科...")
        all_pages.extend(self.crawl_wikipedia())
        
        # 更新统计
        self.crawl_count += len(all_pages)
        self.last_crawl = datetime.now().isoformat()
        
        print(f"  本次爬取: {len(all_pages)} 页, 累计: {self.crawl_count} 页")
        
        return all_pages
    
    def start(self):
        """启动自动爬取"""
        if self.is_running:
            print("爬虫已在运行")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        def run():
            print(f"\n🚀 自动爬虫启动，间隔: {self.config.crawl_interval}秒")
            
            while not self._stop_event.is_set():
                try:
                    # 执行爬取
                    pages = self.crawl_once()
                    
                    # 存入知识库
                    if self.knowledge_base and pages:
                        for page in pages:
                            self.knowledge_base.add(page.to_dict())
                        print(f"  ✓ 存入知识库: {len(pages)} 条")
                    
                except Exception as e:
                    print(f"爬取出错: {e}")
                
                # 等待下次爬取
                self._stop_event.wait(self.config.crawl_interval)
            
            print("爬虫已停止")
        
        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
    
    def stop(self):
        """停止爬取"""
        self._stop_event.set()
        self.is_running = False
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "is_running": self.is_running,
            "crawl_count": self.crawl_count,
            "last_crawl": self.last_crawl,
            "interval": self.config.crawl_interval
        }


if __name__ == "__main__":
    print("测试自动爬虫...")
    
    from config import default_config
    
    crawler = AutoCrawler(default_config.crawler)
    pages = crawler.crawl_once()
    
    print(f"\n爬取结果:")
    for p in pages:
        print(f"  - {p.title}: {p.content[:50]}...")
