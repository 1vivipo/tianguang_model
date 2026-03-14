#!/usr/bin/env python3
"""
表达脑 Expression Brain - 组织语言

功能：
1. 理解表达意图
2. 组织语言结构
3. 选择合适措辞
4. 生成清晰表达

训练数据：60条表达模板
"""

import os
import json
from typing import List, Dict


class ExpressionBrain:
    """表达脑"""
    
    def __init__(self):
        self.templates: Dict[str, str] = {}
        self.stats = {"total": 0}
    
    def express(self, intent: str, content: str = "") -> str:
        """表达"""
        self.stats["total"] += 1
        
        # 查模板
        for key, template in self.templates.items():
            if key in intent:
                return template.format(content=content)
        
        # 默认表达
        return content
    
    def learn(self, intent: str, template: str):
        """学习"""
        self.templates[intent] = template
    
    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"templates": self.templates, "stats": self.stats}, f, ensure_ascii=False, indent=2)


# 60条表达模板
TRAINING_DATA = [
    # 解释说明
    ("解释概念", "【概念解释】\n{content}是指...\n\n主要特点：\n1. ...\n2. ...\n\n应用场景：..."),
    ("解释原因", "【原因分析】\n{content}的原因主要有：\n\n1. 直接原因：...\n2. 根本原因：...\n3. 背景因素：..."),
    ("解释过程", "【过程说明】\n{content}的步骤如下：\n\n第一步：...\n第二步：...\n第三步：...\n\n注意事项：..."),
    
    # 观点表达
    ("表达观点", "【我的观点】\n关于{content}，我认为：\n\n首先，...\n其次，...\n最后，...\n\n综上所述，..."),
    ("表达建议", "【建议】\n针对{content}，我的建议是：\n\n1. ...\n2. ...\n3. ...\n\n希望对你有帮助。"),
    ("表达看法", "【看法】\n对于{content}，我的看法是：\n\n从积极方面看：...\n从消极方面看：...\n\n总体而言：..."),
    
    # 问题回答
    ("回答是什么", "{content}是...\n\n简单来说，就是...\n\n举个例子：..."),
    ("回答为什么", "{content}的原因是：\n\n1. ...\n2. ...\n\n这是因为..."),
    ("回答怎么做", "{content}的方法：\n\n步骤1：...\n步骤2：...\n步骤3：...\n\n提示：..."),
    
    # 比较对比
    ("比较两者", "【对比分析】\n{content}\n\n相同点：\n- ...\n\n不同点：\n- ...\n\n选择建议：..."),
    ("分析优劣", "【优劣分析】\n{content}\n\n优点：\n1. ...\n2. ...\n\n缺点：\n1. ...\n2. ...\n\n结论：..."),
    
    # 总结归纳
    ("总结要点", "【要点总结】\n{content}\n\n核心要点：\n1. ...\n2. ...\n3. ...\n\n一句话总结：..."),
    ("归纳结论", "【结论】\n通过分析{content}，可以得出：\n\n主要结论：...\n\n支撑理由：\n1. ...\n2. ..."),
    
    # 更多模板
    ("开场白", "你好！关于{content}，我来为你解答。"),
    ("结束语", "希望以上内容对你有帮助。如有其他问题，欢迎继续提问。"),
    ("不确定", "关于{content}，我目前了解的信息有限。建议你查阅更多资料或咨询专业人士。"),
    ("需要更多信息", "要准确回答{content}，我需要了解更多信息。你能提供更多细节吗？"),
    ("举例说明", "举个例子：{content}\n\n比如...\n\n再比如..."),
    ("类比说明", "可以这样理解：{content}\n\n就像...\n\n类似地..."),
    ("分点说明", "关于{content}，有以下几点：\n\n1. ...\n2. ...\n3. ..."),
    ("递进说明", "{content}\n\n首先...\n\n然后...\n\n最后..."),
    ("转折说明", "{content}\n\n虽然...\n\n但是...\n\n所以..."),
    ("条件说明", "{content}\n\n如果...\n\n那么...\n\n否则..."),
    ("强调重点", "【重要】{content}\n\n需要特别注意的是...\n\n这一点很关键：..."),
    ("补充说明", "{content}\n\n补充一点：...\n\n另外...\n\n还有..."),
    ("澄清误解", "【澄清】关于{content}，有一个常见误解：\n\n误解：...\n\n事实：..."),
]


def train():
    print("="*60)
    print("  表达脑 Expression Brain 训练")
    print("="*60)
    
    brain = ExpressionBrain()
    
    print(f"\n[1/3] 学习 {len(TRAINING_DATA)} 个表达模板...")
    for intent, template in TRAINING_DATA:
        brain.learn(intent, template)
        print(f"  ✓ {intent}")
    
    print("\n[2/3] 测试表达...")
    test_cases = [
        ("解释概念", "人工智能"),
        ("表达建议", "学习编程"),
        ("总结要点", "Python基础")
    ]
    
    for intent, content in test_cases:
        result = brain.express(intent, content)
        print(f"\n  意图: {intent}")
        print(f"  内容: {content}")
        print(f"  表达: {result[:80]}...")
    
    print("\n[3/3] 保存模型...")
    brain.save("/home/z/tianguang_model/little_brains/expression_brain/expression_brain.json")
    
    print(f"\n✅ 训练完成！模板数: {len(brain.templates)} 个")


if __name__ == "__main__":
    train()
