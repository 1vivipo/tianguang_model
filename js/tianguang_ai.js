/**
 * 天光AI - 整合版应用
 * 
 * 设计原则：
 * - 体积可以小，逻辑必须硬
 * - 见识可以少，判断必须准
 * - 话可以不多，每句都要解决问题
 * - 永远把「怎么思考」放在「知道什么」前面
 */

class TianguangAI {
    constructor() {
        // 核心组件
        this.trainer = new TianguangTrainer();
        this.reasoning = new ReasoningEngine();
        this.memory = new ConversationMemory(10);
        this.styleGenerator = null;
        
        // 配置
        this.config = {
            version: '2.0.0',
            mode: 'quick',  // quick, balanced, full
            style: 'feilu'  // 飞卢风格
        };
        
        // 数据
        this.customData = [];
        this.isInitialized = false;
    }

    /**
     * 初始化
     */
    async init() {
        console.log('=== 天光AI v2.0 初始化 ===');
        console.log('设计理念：逻辑优先，数据为辅');
        
        // 加载保存的数据
        this.loadSavedData();
        
        // 初始化风格生成器
        if (typeof StyleGenerator !== 'undefined') {
            this.styleGenerator = new StyleGenerator(this.trainer);
        }
        
        this.isInitialized = true;
        console.log('初始化完成');
        
        return true;
    }

    /**
     * 核心对话方法
     */
    async chat(userInput) {
        console.log('\n=== 开始对话 ===');
        console.log('用户输入:', userInput);
        
        // Step 1: 推理分析
        const reasoning = await this.reasoning.reason(userInput);
        console.log('推理结果:', reasoning);
        
        // Step 2: 获取上下文
        const context = this.memory.getContext(userInput);
        console.log('上下文:', context);
        
        // Step 3: 生成回复
        let reply;
        
        if (this.trainer.model) {
            // 有模型，使用模型生成
            reply = await this.generateWithModel(userInput, reasoning, context);
        } else {
            // 没有模型，使用规则生成
            reply = this.generateWithRules(userInput, reasoning, context);
        }
        
        // Step 4: 保存对话
        this.memory.addTurn(userInput, reply);
        
        // Step 5: 保存数据
        this.saveData();
        
        console.log('回复:', reply);
        return reply;
    }

    /**
     * 使用模型生成回复
     */
    async generateWithModel(input, reasoning, context) {
        try {
            // 构建带上下文的提示
            const prompt = this.memory.buildPromptWithContext(input);
            
            // 生成
            let output = await this.trainer.generate(prompt, 100, 0.8);
            
            // 后处理
            output = this.postProcess(output, reasoning);
            
            return output;
        } catch (error) {
            console.error('模型生成失败:', error);
            return this.generateWithRules(input, reasoning, context);
        }
    }

    /**
     * 使用规则生成回复（无模型时的后备方案）
     */
    generateWithRules(input, reasoning, context) {
        const { type, intent, emotion } = reasoning.understanding || {};
        
        // 根据问题类型生成回复
        const templates = {
            'how': this.getHowTemplate(input, reasoning),
            'what': this.getWhatTemplate(input, reasoning),
            'why': this.getWhyTemplate(input, reasoning),
            'help': this.getHelpTemplate(input, reasoning)
        };
        
        let reply = templates[type] || this.getGeneralTemplate(input, reasoning);
        
        // 根据情绪调整
        if (emotion && emotion !== '平静') {
            reply = this.adjustForEmotion(reply, emotion);
        }
        
        return reply;
    }

    /**
     * 获取"怎么做"类型的模板
     */
    getHowTemplate(input, reasoning) {
        return `关于"${input}"，我来帮你分析一下：

【问题拆解】
首先，我们需要搞清楚几个问题：
1. 现状是什么？
2. 目标是什么？
3. 差距在哪里？

【解决思路】
1. 先确认具体问题
2. 分析可能的原因
3. 制定可行的方案
4. 分步骤执行

告诉我具体情况，我给你更具体的建议？`;
    }

    /**
     * 获取"是什么"类型的模板
     */
    getWhatTemplate(input, reasoning) {
        return `让我来解释一下：

【核心概念】
这个问题涉及到...

【关键要点】
1. 第一点...
2. 第二点...
3. 第三点...

【实际应用】
简单来说就是...

还有什么想了解的吗？`;
    }

    /**
     * 获取"为什么"类型的模板
     */
    getWhyTemplate(input, reasoning) {
        return `关于原因，我们来分析一下：

【可能的原因】
1. 表面原因：...
2. 深层原因：...

【分析思路】
要找到真正的原因，需要问几个问题：
- 什么时候开始的？
- 有什么变化？
- 还有其他相关因素吗？

告诉我更多细节，我帮你分析？`;
    }

    /**
     * 获取"求助"类型的模板
     */
    getHelpTemplate(input, reasoning) {
        return `我理解你的困扰。让我们一步步来解决：

【第一步：确认问题】
具体是什么情况？

【第二步：分析原因】
可能的原因有哪些？

【第三步：制定方案】
根据情况，我建议...

告诉我更多细节，我给你具体的解决方案。`;
    }

    /**
     * 获取通用模板
     */
    getGeneralTemplate(input, reasoning) {
        return `我收到你的问题了。让我想想...

【我的理解】
你是在问关于"${input}"的问题，对吗？

【我的想法】
这个问题可以从几个角度来看...

告诉我更多，我帮你分析？`;
    }

    /**
     * 根据情绪调整回复
     */
    adjustForEmotion(reply, emotion) {
        const emotionPrefix = {
            '焦虑': '我感觉到你有些焦虑，先深呼吸一下。焦虑的时候，我们更需要冷静地分析问题。\n\n',
            '沮丧': '我能感受到你现在的低落情绪，这很正常。每个人都会有低谷期。\n\n',
            '愤怒': '我理解你的愤怒，这种情绪很正常。让我们先冷静下来，再解决问题。\n\n',
            '困惑': '困惑是思考的开始，说明你在认真想问题。让我们一起来理清思路。\n\n',
            '疲惫': '你辛苦了。在解决问题之前，先照顾好自己。\n\n'
        };
        
        return (emotionPrefix[emotion] || '') + reply;
    }

    /**
     * 后处理
     */
    postProcess(output, reasoning) {
        // 确保输出不为空
        if (!output || output.trim() === '') {
            return '这个问题我需要更多信息才能回答，能详细说说吗？';
        }
        
        // 检查是否乱码
        if (this.isGarbled(output)) {
            return '抱歉，我刚才的回答出了点问题。能再说一遍你的问题吗？';
        }
        
        return output;
    }

    /**
     * 检查是否乱码
     */
    isGarbled(text) {
        if (!text) return true;
        const printable = text.replace(/[\x00-\x1F\x7F-\x9F]/g, '');
        return printable.length < text.length * 0.7;
    }

    /**
     * 训练模型
     */
    async train(callbacks = {}) {
        // 收集所有数据
        let allData = [];
        
        // 基础数据
        if (typeof TrainingData !== 'undefined') {
            allData = allData.concat(TrainingData.getAllData());
        }
        
        // 思考型数据
        if (typeof BUILTIN_DATA !== 'undefined') {
            if (BUILTIN_DATA.thinking_formatted) {
                allData = allData.concat(BUILTIN_DATA.thinking_formatted);
            }
            if (BUILTIN_DATA.feilu_style) {
                allData = allData.concat(BUILTIN_DATA.feilu_style);
            }
        }
        
        // 自定义数据
        if (this.customData.length > 0) {
            allData = allData.concat(this.customData);
        }
        
        console.log(`训练数据总量: ${allData.length} 条`);
        
        // 设置训练模式
        this.trainer.setMode(this.config.mode);
        
        // 开始训练
        await this.trainer.train(allData, callbacks);
    }

    /**
     * 添加训练数据
     */
    addTrainingData(data) {
        if (Array.isArray(data)) {
            this.customData = this.customData.concat(data);
        } else {
            this.customData.push(data);
        }
        this.saveData();
        
        return {
            success: true,
            message: `已添加数据，当前共 ${this.customData.length} 条自定义数据。请重新训练模型。`
        };
    }

    /**
     * 保存数据到本地
     */
    saveData() {
        try {
            localStorage.setItem('tianguang_custom_data', JSON.stringify(this.customData));
            localStorage.setItem('tianguang_memory', JSON.stringify(this.memory.export()));
        } catch (e) {
            console.error('保存数据失败:', e);
        }
    }

    /**
     * 加载保存的数据
     */
    loadSavedData() {
        try {
            const customData = localStorage.getItem('tianguang_custom_data');
            if (customData) {
                this.customData = JSON.parse(customData);
            }
            
            const memoryData = localStorage.getItem('tianguang_memory');
            if (memoryData) {
                this.memory.import(JSON.parse(memoryData));
            }
        } catch (e) {
            console.error('加载数据失败:', e);
        }
    }

    /**
     * 获取状态
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            hasModel: !!this.trainer.model,
            customDataCount: this.customData.length,
            conversationTurns: this.memory.conversations.length,
            mode: this.config.mode
        };
    }
}

// 导出
window.TianguangAI = TianguangAI;
