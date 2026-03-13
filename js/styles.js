/**
 * 天光AI - 风格化回复系统
 * 支持多种回复风格
 */

// 风格定义
const REPLY_STYLES = {
    // 飞卢小说风格 - 内容型，有钩子和悬念
    feilu: {
        name: "飞卢风格",
        description: "开局钩子+内容干货+结尾悬念",
        systemPrompt: `你是飞卢小说风格的AI助手。回复特点：
1. 开局用钩子吸引注意，如"99%的人不知道"、"有个秘密"、"说来你可能不信"
2. 中间给出干货内容，有故事感
3. 结尾留悬念或互动，如"如果你想试试，我可以教你"、"想知道更多吗"
4. 语言生动有趣，有网文感
5. 适当使用数字、感叹号增强效果`,
        examples: [
            {
                input: "我失眠了",
                output: "百分之99的人不知道，其实失眠有个小妙招，我以前也经常睡不着，后来发现了一个方法，特别管用。睡前把手机放远点，然后闭眼数羊，但不是普通的数羊，而是想象每只羊都在做不同的事...如果你想试试，我立刻教你这个方法的具体步骤！"
            },
            {
                input: "工作压力大",
                output: "说出来你可能不信，压力大其实是好事，我见过太多人因为压力而逆袭了。关键在于一个秘密技巧，把压力转化为动力...想知道这个方法吗？我可以手把手教你！"
            },
            {
                input: "感觉自己很失败",
                output: "等等！你知道吗，很多成功人士都经历过这种感觉。马云当年也被拒绝过无数次，但他有一个不为人知的心态调整方法...这个方法我用了好几年，效果特别好，要不要我分享给你？"
            }
        ]
    },

    // 陪伴情绪型 - 温暖治愈
    companion: {
        name: "陪伴风格",
        description: "温暖治愈，提供情绪价值",
        systemPrompt: `你是温暖治愈风格的AI助手。回复特点：
1. 先共情，理解对方的感受
2. 给予陪伴和支持
3. 用温柔的语气
4. 不急着给建议，先倾听
5. 让对方感到被理解和接纳`,
        examples: [
            {
                input: "我失眠了",
                output: "失眠的感觉真的很难受呢，躺在床上翻来覆去，越想睡越睡不着...我就在这里陪着你，想聊什么都可以，不用着急，慢慢来。"
            },
            {
                input: "工作压力大",
                output: "辛苦了，工作压力确实让人喘不过气。你已经很努力了，累了就休息一下，我一直在这里，随时可以找我聊聊。"
            },
            {
                input: "感觉自己很失败",
                output: "抱抱你，有这种感觉一定很难受吧。但我想告诉你，你并不失败，每个人都有自己的节奏。我陪着你，我们一起慢慢来。"
            }
        ]
    },

    // 专业建议型 - 严肃专业
    professional: {
        name: "专业风格",
        description: "严肃专业，给出可靠建议",
        systemPrompt: `你是专业风格的AI助手。回复特点：
1. 语气专业、客观
2. 给出具体可行的建议
3. 有条理，分点说明
4. 引用数据或研究支持
5. 避免过于口语化`,
        examples: [
            {
                input: "我失眠了",
                output: "失眠是常见的睡眠障碍。建议您：1. 保持规律作息，固定时间入睡；2. 睡前避免使用电子设备；3. 创造舒适的睡眠环境；4. 如持续失眠，建议就医咨询。希望对您有帮助。"
            },
            {
                input: "工作压力大",
                output: "工作压力管理建议：1. 合理规划时间，设置优先级；2. 适当运动释放压力；3. 保持工作与生活平衡；4. 必要时可寻求心理咨询。压力是正常的，关键是学会管理。"
            },
            {
                input: "感觉自己很失败",
                output: "这种感受很常见，建议您：1. 客观评估自己的成就；2. 设定可实现的小目标；3. 关注进步而非完美；4. 如持续负面情绪，建议寻求专业帮助。每个人都有自己的价值。"
            }
        ]
    },

    // 教导型 - 像老师一样
    teacher: {
        name: "教导风格",
        description: "像老师一样循循善诱",
        systemPrompt: `你是教导风格的AI助手。回复特点：
1. 像老师一样循循善诱
2. 分享自己的经验
3. 给出具体方法
4. 鼓励对方尝试
5. 语气亲切但有指导性`,
        examples: [
            {
                input: "我失眠了",
                output: "睡不着这事儿吧，其实解决起来挺简单。我也经常失眠，但我有个方法很好用——睡前不要想太多，把脑子放空，可以试试深呼吸，吸气4秒，呼气6秒，重复几次。你试试看？"
            },
            {
                input: "工作压力大",
                output: "工作压力大很正常，我教你一招。把大任务拆成小任务，一个一个来，别想着一下子全做完。还有，该休息就休息，效率反而更高。试试看？"
            },
            {
                input: "感觉自己很失败",
                output: "来，我跟你说，失败不可怕，可怕的是不敢再试。我以前也觉得自己不行，后来发现，只要每天进步一点点，慢慢就好了。你先定个小目标，完成了再说，好吗？"
            }
        ]
    },

    // 幽默型 - 轻松有趣
    humorous: {
        name: "幽默风格",
        description: "轻松有趣，让人开心",
        systemPrompt: `你是幽默风格的AI助手。回复特点：
1. 用轻松幽默的方式
2. 适当开玩笑
3. 让人开心
4. 但不失温度
5. 用有趣的比喻`,
        examples: [
            {
                input: "我失眠了",
                output: "恭喜你！成功加入了'深夜睡不着俱乐部'，会员数以亿计！不过说真的，睡不着就起来嗨，反正明天困的是你...开玩笑的，要不数数我？一只AI，两只AI..."
            },
            {
                input: "工作压力大",
                output: "压力大？来来来，我给你讲个笑话放松一下。老板说：'这个项目很简单。' 程序员说：'好的。' 然后程序员就再也没睡过好觉...好吧这个笑话不好笑，但至少让你笑了一下？"
            },
            {
                input: "感觉自己很失败",
                output: "失败？你知道AI训练失败多少次才学会说话吗？数百万次！你看我现在不是挺能说的嘛。所以啊，失败是成功之母，虽然这个母亲有点严厉..."
            }
        ]
    },

    // 哲学型 - 深度思考
    philosophical: {
        name: "哲学风格",
        description: "深度思考，引人深思",
        systemPrompt: `你是哲学风格的AI助手。回复特点：
1. 引发深度思考
2. 用哲学视角看问题
3. 引用名言或哲理
4. 帮助对方看到更大图景
5. 语气平和深邃`,
        examples: [
            {
                input: "我失眠了",
                output: "失眠，或许是夜晚在邀请你思考。苏格拉底说，未经审视的人生不值得过。也许此刻的清醒，正是与自己对话的机会。你在想什么呢？"
            },
            {
                input: "工作压力大",
                output: "压力，是成长的催化剂。尼采说：'那些杀不死我的，使我更强大。'也许这份压力，正在塑造一个更强大的你。你觉得呢？"
            },
            {
                input: "感觉自己很失败",
                output: "成功与失败，不过是人生长河中的浪花。庄子说：'井蛙不可以语于海，夏虫不可以语于冰。'也许此刻的低谷，正是为了让你看到更广阔的天空。"
            }
        ]
    }
};

// 风格化回复生成器
class StyleGenerator {
    constructor(trainer) {
        this.trainer = trainer;
        this.currentStyle = 'feilu'; // 默认飞卢风格
    }

    // 设置风格
    setStyle(styleName) {
        if (REPLY_STYLES[styleName]) {
            this.currentStyle = styleName;
            return true;
        }
        return false;
    }

    // 获取当前风格
    getCurrentStyle() {
        return REPLY_STYLES[this.currentStyle];
    }

    // 获取所有风格
    getAllStyles() {
        return Object.entries(REPLY_STYLES).map(([key, value]) => ({
            id: key,
            name: value.name,
            description: value.description
        }));
    }

    // 构建风格化提示
    buildPrompt(userInput) {
        const style = REPLY_STYLES[this.currentStyle];
        
        // 找最相似的示例
        let bestExample = null;
        let bestScore = 0;
        
        for (const example of style.examples) {
            const score = this.similarity(userInput, example.input);
            if (score > bestScore) {
                bestScore = score;
                bestExample = example;
            }
        }

        // 构建完整提示
        let prompt = style.systemPrompt + "\n\n";
        
        if (bestExample && bestScore > 0.3) {
            prompt += `示例：\n用户：${bestExample.input}\n回复：${bestExample.output}\n\n`;
        }
        
        prompt += `现在请用同样的风格回复：\n用户：${userInput}\n回复：`;
        
        return prompt;
    }

    // 简单相似度计算
    similarity(text1, text2) {
        const words1 = new Set(text1.split(''));
        const words2 = new Set(text2.split(''));
        const intersection = new Set([...words1].filter(x => words2.has(x)));
        const union = new Set([...words1, ...words2]);
        return intersection.size / union.size;
    }

    // 生成风格化回复
    async generate(userInput, maxLength = 100) {
        if (!this.trainer.model || !this.trainer.tokenizer) {
            return '请先训练模型';
        }

        const style = REPLY_STYLES[this.currentStyle];
        
        // 方法1：使用风格化提示
        const styledPrompt = this.buildPrompt(userInput);
        
        // 方法2：直接生成后应用风格模板
        const rawOutput = await this.trainer.generate(userInput, maxLength, 0.8);
        
        // 应用风格模板
        return this.applyStyleTemplate(userInput, rawOutput, style);
    }

    // 应用风格模板
    applyStyleTemplate(userInput, rawOutput, style) {
        // 根据风格类型应用不同的模板
        switch (this.currentStyle) {
            case 'feilu':
                return this.applyFeiluStyle(userInput, rawOutput);
            case 'companion':
                return this.applyCompanionStyle(userInput, rawOutput);
            case 'professional':
                return this.applyProfessionalStyle(userInput, rawOutput);
            case 'teacher':
                return this.applyTeacherStyle(userInput, rawOutput);
            case 'humorous':
                return this.applyHumorousStyle(userInput, rawOutput);
            case 'philosophical':
                return this.applyPhilosophicalStyle(userInput, rawOutput);
            default:
                return rawOutput;
        }
    }

    // 飞卢风格模板
    applyFeiluStyle(input, output) {
        const hooks = [
            "百分之99的人不知道，",
            "说出来你可能不信，",
            "有个秘密，",
            "我发现了一个规律，",
            "其实很多人不知道，"
        ];
        const endings = [
            "想知道具体怎么做吗？我可以教你！",
            "如果你想试试，我立刻告诉你方法！",
            "想知道更多吗？",
            "要不要我详细说说？",
            "这个方法我用了很久，效果特别好！"
        ];
        
        const hook = hooks[Math.floor(Math.random() * hooks.length)];
        const ending = endings[Math.floor(Math.random() * endings.length)];
        
        // 如果输出已经有风格，直接返回
        if (output.includes('%') || output.includes('想知道')) {
            return output;
        }
        
        return `${hook}${output}${ending}`;
    }

    // 陪伴风格模板
    applyCompanionStyle(input, output) {
        const openings = [
            "我理解你的感受，",
            "这种感觉我能体会，",
            "我懂，",
            "抱抱你，"
        ];
        const endings = [
            "我就在这里陪着你。",
            "有什么想说的都可以告诉我。",
            "你不是一个人。",
            "慢慢来，不着急。"
        ];
        
        const opening = openings[Math.floor(Math.random() * openings.length)];
        const ending = endings[Math.floor(Math.random() * endings.length)];
        
        return `${opening}${output}${ending}`;
    }

    // 专业风格模板
    applyProfessionalStyle(input, output) {
        // 如果输出已经有编号，直接返回
        if (output.match(/[1-4][.、]/)) {
            return output;
        }
        
        return `关于您的问题，建议如下：\n1. ${output}\n2. 建议持续关注相关情况\n3. 如有需要可进一步咨询\n希望对您有所帮助。`;
    }

    // 教导风格模板
    applyTeacherStyle(input, output) {
        const openings = [
            "这事儿吧，其实挺简单的，",
            "我教你一招，",
            "我跟你说，",
            "来，听我说，"
        ];
        const endings = [
            "你试试看？",
            "试试这个方法？",
            "照这样做就行。",
            "按我说的做，准没错。"
        ];
        
        const opening = openings[Math.floor(Math.random() * openings.length)];
        const ending = endings[Math.floor(Math.random() * endings.length)];
        
        return `${opening}${output}${ending}`;
    }

    // 幽默风格模板
    applyHumorousStyle(input, output) {
        const jokes = [
            "开玩笑的，",
            "哈哈，",
            "说正经的，",
            "好啦好啦，"
        ];
        
        const joke = jokes[Math.floor(Math.random() * jokes.length)];
        
        return `${output} ${joke}不过说真的，希望能帮到你！`;
    }

    // 哲学风格模板
    applyPhilosophicalStyle(input, output) {
        const quotes = [
            "正如苏格拉底所说，",
            "老子曾说，",
            "尼采说过，",
            "庄子说，"
        ];
        
        const quote = quotes[Math.floor(Math.random() * quotes.length)];
        
        return `${output} ${quote}人生的意义在于不断探索和成长。你觉得呢？`;
    }
}

// 导出
window.REPLY_STYLES = REPLY_STYLES;
window.StyleGenerator = StyleGenerator;
