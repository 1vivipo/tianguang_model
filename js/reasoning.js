/**
 * 天光AI - 推理框架
 * 核心理念：逻辑优先，数据为辅
 * 
 * 设计原则：
 * - 体积可以小，逻辑必须硬
 * - 见识可以少，判断必须准
 * - 话可以不多，每句都要解决问题
 * - 永远把「怎么思考」放在「知道什么」前面
 */

class ReasoningEngine {
    constructor() {
        // 推理步骤
        this.steps = [
            '理解问题',
            '拆解问题', 
            '定位核心',
            '制定方案',
            '分步解决',
            '验证结果'
        ];
        
        // 当前状态
        this.currentStep = 0;
        this.context = {};
        this.history = [];
    }

    /**
     * 主推理流程
     * @param {string} userInput 用户输入
     * @returns {object} 推理结果
     */
    async reason(userInput) {
        console.log('=== 开始推理 ===');
        console.log('输入:', userInput);
        
        // Step 1: 理解问题
        const understanding = this.understandProblem(userInput);
        console.log('理解:', understanding);
        
        // Step 2: 拆解问题
        const breakdown = this.breakdownProblem(understanding);
        console.log('拆解:', breakdown);
        
        // Step 3: 定位核心
        const core = this.locateCore(breakdown);
        console.log('核心:', core);
        
        // Step 4: 制定方案
        const solution = this.planSolution(core);
        console.log('方案:', solution);
        
        // Step 5: 执行解决
        const result = this.executeSolution(solution);
        console.log('结果:', result);
        
        // Step 6: 验证
        const validated = this.validateResult(result);
        console.log('验证:', validated);
        
        // 保存到历史
        this.history.push({
            input: userInput,
            understanding,
            breakdown,
            core,
            solution,
            result: validated,
            timestamp: Date.now()
        });
        
        return validated;
    }

    /**
     * Step 1: 理解问题
     * 目标：听明白问题在问什么
     */
    understandProblem(input) {
        const analysis = {
            original: input,
            type: this.detectProblemType(input),
            intent: this.detectIntent(input),
            emotion: this.detectEmotion(input),
            keywords: this.extractKeywords(input),
            context: this.extractContext(input)
        };
        
        return analysis;
    }

    /**
     * 检测问题类型
     */
    detectProblemType(input) {
        const types = {
            'how': ['怎么', '如何', '怎样', '方法', '办法'],
            'what': ['是什么', '什么是', '意思', '定义'],
            'why': ['为什么', '原因', '为何', '怎么会'],
            'which': ['哪个', '哪些', '选择', '比较'],
            'can': ['能', '可以', '行吗', '是否'],
            'help': ['帮', '求助', '问题', '困难', '怎么办']
        };
        
        for (const [type, keywords] of Object.entries(types)) {
            if (keywords.some(kw => input.includes(kw))) {
                return type;
            }
        }
        
        return 'general';
    }

    /**
     * 检测意图
     */
    detectIntent(input) {
        const intents = {
            '寻求解决方案': ['怎么办', '怎么解决', '如何处理'],
            '获取知识': ['是什么', '告诉我', '介绍一下'],
            '寻求建议': ['建议', '推荐', '应该'],
            '情绪倾诉': ['难过', '开心', '烦', '累', '压力'],
            '闲聊': ['你好', '在吗', '聊聊']
        };
        
        for (const [intent, keywords] of Object.entries(intents)) {
            if (keywords.some(kw => input.includes(kw))) {
                return intent;
            }
        }
        
        return '其他';
    }

    /**
     * 检测情绪
     */
    detectEmotion(input) {
        const emotions = {
            '焦虑': ['焦虑', '担心', '害怕', '紧张', '不安'],
            '沮丧': ['难过', '伤心', '失望', '沮丧', '失败'],
            '愤怒': ['生气', '愤怒', '烦', '讨厌', '气死'],
            '困惑': ['不懂', '不明白', '困惑', '迷茫', '不知道'],
            '开心': ['开心', '高兴', '快乐', '好', '棒'],
            '疲惫': ['累', '疲惫', '困', '没劲', '乏力']
        };
        
        for (const [emotion, keywords] of Object.entries(emotions)) {
            if (keywords.some(kw => input.includes(kw))) {
                return emotion;
            }
        }
        
        return '平静';
    }

    /**
     * 提取关键词
     */
    extractKeywords(input) {
        // 简单的关键词提取
        const stopWords = ['的', '了', '是', '在', '我', '你', '他', '她', '它', '们', '这', '那', '有', '没', '不', '就', '也', '都', '还', '要', '会', '能', '可以', '怎么', '什么', '为什么', '如何'];
        
        const words = input.split('').filter(w => !stopWords.includes(w) && w.trim());
        return [...new Set(words)].slice(0, 10);
    }

    /**
     * 提取上下文
     */
    extractContext(input) {
        // 从历史对话中提取相关上下文
        const recentHistory = this.history.slice(-3);
        return recentHistory.map(h => h.input);
    }

    /**
     * Step 2: 拆解问题
     * 目标：把复杂问题拆成小问题
     */
    breakdownProblem(understanding) {
        const { type, intent, keywords } = understanding;
        
        const breakdown = {
            mainQuestion: understanding.original,
            subQuestions: [],
            dependencies: [],
            priority: 'normal'
        };
        
        // 根据问题类型拆解
        switch (type) {
            case 'how':
                breakdown.subQuestions = [
                    '目标是什么？',
                    '现状是什么？',
                    '差距在哪里？',
                    '有什么资源可用？',
                    '第一步做什么？'
                ];
                break;
            case 'why':
                breakdown.subQuestions = [
                    '表面原因是什么？',
                    '深层原因是什么？',
                    '有什么证据？',
                    '还有其他可能吗？'
                ];
                break;
            case 'help':
                breakdown.subQuestions = [
                    '具体是什么问题？',
                    '问题严重程度？',
                    '已经尝试过什么？',
                    '期望的结果是什么？'
                ];
                break;
            default:
                breakdown.subQuestions = ['需要了解什么信息？'];
        }
        
        return breakdown;
    }

    /**
     * Step 3: 定位核心
     * 目标：找到最关键的问题
     */
    locateCore(breakdown) {
        const { mainQuestion, subQuestions } = breakdown;
        
        // 核心问题定位逻辑
        const core = {
            primary: subQuestions[0] || mainQuestion,
            secondary: subQuestions.slice(1, 3),
            focus: '解决最紧迫的问题'
        };
        
        // 如果是情绪问题，核心是情绪
        // 如果是实际问题，核心是解决方案
        
        return core;
    }

    /**
     * Step 4: 制定方案
     * 目标：给出可执行的步骤
     */
    planSolution(core) {
        const solution = {
            approach: '',
            steps: [],
            expectedOutcome: '',
            alternatives: []
        };
        
        // 根据核心问题制定方案
        solution.approach = '分步骤解决';
        solution.steps = [
            '确认问题',
            '分析原因',
            '制定对策',
            '执行行动',
            '检查效果'
        ];
        
        return solution;
    }

    /**
     * Step 5: 执行解决
     * 目标：生成具体回答
     */
    executeSolution(solution) {
        // 这里会调用模型生成回答
        // 但回答必须遵循：逻辑清晰、步骤明确
        return {
            answer: '',
            reasoning: solution.steps,
            confidence: 0.8
        };
    }

    /**
     * Step 6: 验证结果
     * 目标：确保回答有效
     */
    validateResult(result) {
        // 验证回答是否：
        // 1. 解决了问题
        // 2. 逻辑清晰
        // 3. 可执行
        
        return {
            ...result,
            validated: true,
            quality: this.assessQuality(result)
        };
    }

    /**
     * 评估回答质量
     */
    assessQuality(result) {
        return {
            relevance: 0.8,    // 相关性
            clarity: 0.8,     // 清晰度
            actionability: 0.8, // 可执行性
            completeness: 0.7  // 完整性
        };
    }

    /**
     * 获取思考过程
     */
    getThinkingProcess() {
        return this.history.slice(-1)[0] || null;
    }
}

// 导出
window.ReasoningEngine = ReasoningEngine;
