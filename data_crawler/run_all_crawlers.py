#!/usr/bin/env python3
"""
Plan B - 本地数据爬虫和对话收集系统

目标：
1. 10-20个爬虫脚本，爬取不同领域数据
2. 10-20个科普对话机器人，收集问答数据
3. 实时推送到GitHub仓库
4. 跑一晚上积累大量数据

使用方法：
    python run_all_crawlers.py --hours 8  # 跑8小时
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
from concurrent.futures import ThreadPoolExecutor

# 配置
CRAWL_INTERVAL = 60  # 每分钟爬一次
SAVE_INTERVAL = 300  # 每5分钟保存一次
PUSH_INTERVAL = 1800  # 每30分钟推送到GitHub

# 数据目录
DATA_DIR = "/home/z/tianguang_model/collected_data"
REPO_DIR = "/home/z/tianguang_model"

# 领域配置
DOMAINS = {
    "人工智能": ["AI", "人工智能", "机器学习", "深度学习", "神经网络", "GPT", "ChatGPT"],
    "编程": ["Python", "Java", "JavaScript", "编程", "代码", "开发", "软件"],
    "科技": ["科技", "互联网", "数码", "手机", "电脑", "芯片"],
    "财经": ["股票", "基金", "投资", "理财", "经济", "金融"],
    "健康": ["健康", "医疗", "养生", "健身", "营养", "疾病"],
    "教育": ["教育", "学习", "考试", "培训", "留学", "考研"],
    "历史": ["历史", "古代", "朝代", "历史人物", "历史事件"],
    "科学": ["物理", "化学", "生物", "数学", "天文", "科学"],
    "文化": ["文化", "艺术", "文学", "哲学", "传统文化"],
    "生活": ["美食", "旅游", "家居", "汽车", "宠物"],
}

# 科普问答模板
QA_TEMPLATES = {
    "人工智能": [
        ("什么是人工智能？", "人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统，如学习、推理、问题解决和语言理解。"),
        ("机器学习和深度学习有什么区别？", "机器学习是AI的子集，使用算法从数据中学习。深度学习是机器学习的子集，使用多层神经网络来学习数据的复杂模式。"),
        ("什么是神经网络？", "神经网络是一种模仿人脑结构的计算系统，由相互连接的节点（神经元）组成，可以通过训练来识别模式和做出决策。"),
        ("GPT是什么？", "GPT（Generative Pre-trained Transformer）是一种大型语言模型，通过在海量文本数据上预训练，能够生成类似人类的文本。"),
        ("AI有哪些应用？", "AI应用广泛，包括：语音助手、图像识别、自动驾驶、医疗诊断、金融分析、智能客服、内容生成等。"),
    ],
    "编程": [
        ("Python适合初学者吗？", "Python非常适合初学者，语法简洁清晰，接近自然语言，学习曲线平缓，且有丰富的库和社区支持。"),
        ("什么是面向对象编程？", "面向对象编程（OOP）是一种编程范式，使用'对象'来设计软件，对象包含数据（属性）和代码（方法），支持封装、继承和多态。"),
        ("如何学习编程？", "建议：1.选择一门语言（如Python）2.学习基础语法 3.做小项目练习 4.阅读他人代码 5.参与开源项目 6.持续学习新技术。"),
        ("什么是API？", "API（应用程序编程接口）是一组定义和协议，用于构建和集成应用软件，允许不同软件系统之间进行通信。"),
        ("前端和后端有什么区别？", "前端是用户看到和交互的部分（网页界面），后端是服务器端的逻辑和数据处理部分，两者通过API通信。"),
    ],
    "科技": [
        ("什么是5G？", "5G是第五代移动通信技术，比4G快10-100倍，延迟更低，支持更多设备连接，将推动物联网、自动驾驶等发展。"),
        ("什么是物联网？", "物联网（IoT）是指通过互联网连接各种物理设备，使它们能够收集和交换数据，实现智能化识别和管理。"),
        ("什么是区块链？", "区块链是一种分布式账本技术，数据以区块形式存储，每个区块链接到前一个区块，具有去中心化、不可篡改的特点。"),
        ("什么是云计算？", "云计算是通过互联网提供计算服务（服务器、存储、数据库、软件等），用户按需使用，无需自己维护硬件。"),
        ("芯片是怎么制造的？", "芯片制造包括：设计、硅片制备、光刻、蚀刻、掺杂、金属化、封装测试等步骤，需要高度精密的设备和洁净环境。"),
    ],
    "财经": [
        ("什么是股票？", "股票是公司所有权的凭证，购买股票成为公司股东，可分享公司利润（分红）和资产增值，但也承担风险。"),
        ("基金和股票哪个风险小？", "基金风险通常比股票小，因为基金由专业经理管理，投资多只股票分散风险，但收益也可能较低。"),
        ("什么是复利？", "复利是指利息产生利息，投资收益再投资产生更多收益，长期下来财富会指数级增长，被称为'世界第八大奇迹'。"),
        ("如何开始投资？", "建议：1.建立应急基金 2.了解风险承受能力 3.学习基础知识 4.从指数基金开始 5.分散投资 6.长期持有。"),
        ("什么是通货膨胀？", "通货膨胀是货币购买力下降，物价普遍上涨的现象。适度通胀有利于经济，但高通胀会侵蚀财富。"),
    ],
    "健康": [
        ("每天应该睡几个小时？", "成年人建议每天睡7-9小时。睡眠不足会影响免疫力、记忆力和情绪，长期睡眠不足增加多种疾病风险。"),
        ("如何保持健康？", "健康生活方式包括：均衡饮食、规律运动、充足睡眠、心理健康、定期体检、戒烟限酒、保持社交。"),
        ("什么是健康饮食？", "健康饮食包括：多吃蔬菜水果、全谷物、优质蛋白；少吃加工食品、高糖高盐食品；控制总热量摄入。"),
        ("运动多久合适？", "建议每周至少150分钟中等强度有氧运动，或75分钟高强度运动，加上每周2次力量训练。"),
        ("如何缓解压力？", "缓解压力方法：运动、冥想、深呼吸、充足睡眠、社交活动、培养爱好、寻求专业帮助。"),
    ],
    "教育": [
        ("如何高效学习？", "高效学习方法：主动学习、间隔重复、费曼技巧、思维导图、番茄工作法、及时复习、教授他人。"),
        ("在线教育有什么优势？", "在线教育优势：时间灵活、地点自由、资源丰富、可重复学习、成本较低、个性化学习进度。"),
        ("如何培养阅读习惯？", "培养阅读习惯：选择感兴趣的书、设定每天阅读时间、创造安静环境、做读书笔记、加入读书社群。"),
        ("什么是终身学习？", "终身学习是指贯穿一生的持续学习过程，适应快速变化的社会，保持竞争力和个人成长。"),
        ("如何提高记忆力？", "提高记忆力方法：充足睡眠、规律运动、健康饮食、联想记忆、重复复习、教授他人、减少压力。"),
    ],
    "历史": [
        ("中国历史有多少年？", "中国有约5000年的文明史，有文字记载的历史约3500年（从商朝甲骨文开始），是世界上历史最悠久的文明之一。"),
        ("四大发明是什么？", "中国四大发明：造纸术、印刷术、火药、指南针，对世界文明发展产生了深远影响。"),
        ("秦始皇做了什么？", "秦始皇统一六国，建立中央集权制度，统一文字、货币、度量衡，修建长城，是中国历史上第一位皇帝。"),
        ("丝绸之路是什么？", "丝绸之路是古代连接中国和西方的贸易路线，不仅传播商品，还传播了文化、宗教和技术。"),
        ("工业革命有什么影响？", "工业革命从18世纪英国开始，机器取代手工，工厂制度建立，城市化加速，深刻改变了社会结构和生活方式。"),
    ],
    "科学": [
        ("什么是相对论？", "相对论是爱因斯坦提出的物理学理论，包括狭义相对论（时间空间相对性）和广义相对论（引力是时空弯曲）。"),
        ("DNA是什么？", "DNA（脱氧核糖核酸）是遗传信息的载体，双螺旋结构，由四种碱基组成，决定了生物的遗传特征。"),
        ("光速有多快？", "光速约每秒30万公里，是宇宙中最快的速度。光从太阳到地球约需8分钟。"),
        ("什么是黑洞？", "黑洞是引力极强的天体，连光都无法逃逸。当大质量恒星坍缩时可能形成黑洞。"),
        ("进化论是什么？", "进化论是达尔文提出的理论，认为物种通过自然选择逐渐演化，适应环境的个体更容易生存繁衍。"),
    ],
    "文化": [
        ("什么是传统文化？", "传统文化是一个民族世代相传的文化遗产，包括思想、艺术、习俗、节日等，是民族身份的重要标志。"),
        ("四大名著是哪些？", "中国四大名著：《红楼梦》《西游记》《水浒传》《三国演义》，是中国古典文学的巅峰之作。"),
        ("书法有什么特点？", "中国书法是独特的艺术形式，通过毛笔书写汉字，讲究笔法、结构、章法，体现书写者的修养和情感。"),
        ("京剧是什么？", "京剧是中国传统戏曲剧种，融合唱、念、做、打，角色分行当（生旦净丑），是中国文化的瑰宝。"),
        ("茶文化有什么内涵？", "茶文化包括种茶、制茶、泡茶、品茶的技艺和精神，讲究'和、敬、清、寂'，是中国传统文化的重要组成部分。"),
    ],
    "生活": [
        ("如何做一道简单的菜？", "番茄炒蛋：1.番茄切块，鸡蛋打散 2.热油炒蛋盛出 3.炒番茄出汁 4.加入鸡蛋翻炒 5.调味即可。"),
        ("如何规划旅行？", "旅行规划：确定目的地和时间、预订交通住宿、了解当地文化、制定行程、准备必需品、购买保险。"),
        ("如何养宠物？", "养宠物需要：提供适当食物和水、定期体检和疫苗、足够运动空间、清洁的生活环境、足够的陪伴时间。"),
        ("如何选购二手车？", "选购二手车：检查外观和内饰、试驾感受、查看保养记录、检查事故历史、请专业人士评估、议价。"),
        ("如何布置小户型？", "小户型布置：选择多功能家具、利用垂直空间、浅色系增加空间感、保持整洁、合理分区、增加收纳。"),
    ],
}


class SimpleCrawler:
    """简单爬虫"""
    
    def __init__(self, domain: str, keywords: List[str]):
        self.domain = domain
        self.keywords = keywords
        self.crawled_count = 0
    
    def crawl(self) -> List[Dict]:
        """爬取数据"""
        results = []
        
        for keyword in self.keywords[:2]:  # 每次最多2个关键词
            try:
                # 使用DuckDuckGo API
                url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(keyword)}&format=json&no_html=1"
                
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
                
                if data.get('AbstractText'):
                    results.append({
                        "domain": self.domain,
                        "title": keyword,
                        "content": data['AbstractText'],
                        "source": data.get('AbstractURL', ''),
                        "type": "knowledge",
                        "crawled_at": datetime.now().isoformat()
                    })
                    self.crawled_count += 1
                
                # 相关主题
                for topic in data.get('RelatedTopics', [])[:3]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        results.append({
                            "domain": self.domain,
                            "title": topic.get('FirstURL', '').split('/')[-1] if topic.get('FirstURL') else self.domain,
                            "content": topic['Text'],
                            "source": topic.get('FirstURL', ''),
                            "type": "knowledge",
                            "crawled_at": datetime.now().isoformat()
                        })
                        self.crawled_count += 1
                
                time.sleep(0.5)  # 避免被封
                
            except Exception as e:
                print(f"  [{self.domain}] 爬取 {keyword} 失败: {e}")
        
        return results


class DialogueGenerator:
    """对话数据生成器"""
    
    def __init__(self, domain: str, qa_pairs: List[tuple]):
        self.domain = domain
        self.qa_pairs = qa_pairs
        self.generated_count = 0
    
    def generate(self) -> List[Dict]:
        """生成对话数据"""
        results = []
        
        for question, answer in self.qa_pairs:
            # 原始问答
            results.append({
                "domain": self.domain,
                "question": question,
                "answer": answer,
                "type": "dialogue",
                "generated_at": datetime.now().isoformat()
            })
            self.generated_count += 1
            
            # 变体问题
            variants = self._generate_variants(question, answer)
            for var_q, var_a in variants:
                results.append({
                    "domain": self.domain,
                    "question": var_q,
                    "answer": var_a,
                    "type": "dialogue",
                    "generated_at": datetime.now().isoformat()
                })
                self.generated_count += 1
        
        return results
    
    def _generate_variants(self, question: str, answer: str) -> List[tuple]:
        """生成问题变体"""
        variants = []
        
        # 添加不同问法
        prefixes = ["请问", "我想知道", "能告诉我", "请教一下"]
        for prefix in prefixes:
            if not question.startswith(prefix):
                variants.append((f"{prefix}{question}", answer))
        
        # 简化问题
        if len(question) > 10:
            short_q = question.replace("什么是", "").replace("如何", "怎么").replace("为什么", "为啥")
            variants.append((short_q, answer))
        
        return variants[:3]  # 最多3个变体


class DataCollector:
    """数据收集器"""
    
    def __init__(self):
        self.all_data = []
        self.crawlers = []
        self.generators = []
        self.is_running = False
        
        # 创建爬虫
        for domain, keywords in DOMAINS.items():
            crawler = SimpleCrawler(domain, keywords)
            self.crawlers.append(crawler)
        
        # 创建对话生成器
        for domain, qa_pairs in QA_TEMPLATES.items():
            generator = DialogueGenerator(domain, qa_pairs)
            self.generators.append(generator)
        
        print(f"✓ 创建了 {len(self.crawlers)} 个爬虫")
        print(f"✓ 创建了 {len(self.generators)} 个对话生成器")
    
    def collect_once(self) -> int:
        """收集一次数据"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 开始收集数据...")
        
        count = 0
        
        # 爬取知识
        print("  爬取知识数据...")
        for crawler in self.crawlers:
            try:
                data = crawler.crawl()
                self.all_data.extend(data)
                count += len(data)
            except Exception as e:
                print(f"    [{crawler.domain}] 错误: {e}")
        
        # 生成对话
        print("  生成对话数据...")
        for generator in self.generators:
            try:
                data = generator.generate()
                self.all_data.extend(data)
                count += len(data)
            except Exception as e:
                print(f"    [{generator.domain}] 错误: {e}")
        
        print(f"  ✓ 本次收集: {count} 条, 累计: {len(self.all_data)} 条")
        
        return count
    
    def save_data(self):
        """保存数据"""
        if not self.all_data:
            return
        
        # 按类型分类
        knowledge_data = [d for d in self.all_data if d.get('type') == 'knowledge']
        dialogue_data = [d for d in self.all_data if d.get('type') == 'dialogue']
        
        # 保存知识数据
        if knowledge_data:
            knowledge_file = os.path.join(DATA_DIR, f"knowledge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
            print(f"  ✓ 保存知识数据: {len(knowledge_data)} 条 -> {knowledge_file}")
        
        # 保存对话数据
        if dialogue_data:
            dialogue_file = os.path.join(DATA_DIR, f"dialogue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(dialogue_file, 'w', encoding='utf-8') as f:
                json.dump(dialogue_data, f, ensure_ascii=False, indent=2)
            print(f"  ✓ 保存对话数据: {len(dialogue_data)} 条 -> {dialogue_file}")
        
        # 同时保存到黑洞知识库目录
        blackhole_dir = os.path.join(REPO_DIR, "blackhole_llm", "blackhole_knowledge")
        os.makedirs(blackhole_dir, exist_ok=True)
        
        all_file = os.path.join(blackhole_dir, f"collected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(all_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_data, f, ensure_ascii=False, indent=2)
        print(f"  ✓ 保存到黑洞知识库: {all_file}")
    
    def push_to_github(self):
        """推送到GitHub"""
        print("\n推送到GitHub...")
        
        os.chdir(REPO_DIR)
        
        # git add
        os.system("git add collected_data/")
        os.system("git add blackhole_llm/blackhole_knowledge/")
        
        # git commit
        commit_msg = f"data: 自动收集数据 {datetime.now().strftime('%Y-%m-%d %H:%M')} - {len(self.all_data)}条"
        os.system(f'git commit -m "{commit_msg}"')
        
        # git push
        result = os.system("git push origin main")
        
        if result == 0:
            print("  ✓ 推送成功!")
        else:
            print("  ✗ 推送失败，稍后重试")
    
    def run(self, hours: float = 8):
        """运行收集"""
        self.is_running = True
        
        total_seconds = hours * 3600
        start_time = time.time()
        
        print(f"""
╔══════════════════════════════════════════════════════════╗
║            Plan B - 本地数据收集系统                    ║
╠══════════════════════════════════════════════════════════╣
║  爬虫数量: {len(self.crawlers):<42} ║
║  对话生成器: {len(self.generators):<40} ║
║  运行时间: {hours}小时{' '*36} ║
║  爬取间隔: {CRAWL_INTERVAL}秒{' '*41} ║
║  保存间隔: {SAVE_INTERVAL}秒{' '*41} ║
║  推送间隔: {PUSH_INTERVAL}秒{' '*40} ║
╚══════════════════════════════════════════════════════════╝
""")
        
        last_save = time.time()
        last_push = time.time()
        
        while self.is_running and (time.time() - start_time) < total_seconds:
            # 收集数据
            self.collect_once()
            
            # 检查是否需要保存
            if time.time() - last_save >= SAVE_INTERVAL:
                self.save_data()
                last_save = time.time()
            
            # 检查是否需要推送
            if time.time() - last_push >= PUSH_INTERVAL:
                self.push_to_github()
                last_push = time.time()
            
            # 等待下次收集
            time.sleep(CRAWL_INTERVAL)
        
        # 最后保存和推送
        self.save_data()
        self.push_to_github()
        
        print(f"\n✅ 数据收集完成!")
        print(f"   总数据: {len(self.all_data)} 条")
        print(f"   运行时间: {(time.time() - start_time)/3600:.1f} 小时")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Plan B - 本地数据收集")
    parser.add_argument("--hours", type=float, default=8, help="运行时间（小时）")
    
    args = parser.parse_args()
    
    # 创建数据目录
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 运行收集
    collector = DataCollector()
    collector.run(hours=args.hours)


if __name__ == "__main__":
    main()
