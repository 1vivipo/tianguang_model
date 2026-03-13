/**
 * 天光AI - 多轮对话记忆系统
 * 支持上下文记忆，实现连贯对话
 */

class ConversationMemory {
    constructor(maxTurns = 10) {
        this.maxTurns = maxTurns;
        this.conversations = [];  // 对话历史
        this.userProfile = {};    // 用户画像
        this.topicHistory = [];   // 话题历史
    }

    /**
     * 添加一轮对话
     */
    addTurn(userInput, assistantReply, metadata = {}) {
        const turn = {
            role: 'user',
            content: userInput,
            timestamp: Date.now(),
            ...metadata
        };
        
        this.conversations.push(turn);
        
        this.conversations.push({
            role: 'assistant',
            content: assistantReply,
            timestamp: Date.now()
        });
        
        // 保持最大轮次限制
        if (this.conversations.length > this.maxTurns * 2) {
            this.conversations = this.conversations.slice(-this.maxTurns * 2);
        }
        
        // 更新用户画像
        this.updateUserProfile(userInput);
        
        // 更新话题历史
        this.updateTopicHistory(userInput);
    }

    /**
     * 获取上下文
     */
    getContext(currentInput) {
        return {
            recentHistory: this.getRecentHistory(3),
            userProfile: this.userProfile,
            relevantTopics: this.getRelevantTopics(currentInput),
            summary: this.getConversationSummary()
        };
    }

    /**
     * 获取最近的对话历史
     */
    getRecentHistory(turns = 3) {
        const recent = this.conversations.slice(-turns * 2);
        return recent.map(turn => ({
            role: turn.role,
            content: turn.content
        }));
    }

    /**
     * 更新用户画像
     */
    updateUserProfile(input) {
        // 提取用户特征
        const features = this.extractUserFeatures(input);
        
        // 合并到用户画像
        for (const [key, value] of Object.entries(features)) {
            if (!this.userProfile[key]) {
                this.userProfile[key] = [];
            }
            this.userProfile[key].push(value);
            
            // 保持最近10个
            if (this.userProfile[key].length > 10) {
                this.userProfile[key] = this.userProfile[key].slice(-10);
            }
        }
    }

    /**
     * 提取用户特征
     */
    extractUserFeatures(input) {
        const features = {};
        
        // 情绪特征
        const emotions = ['焦虑', '难过', '开心', '愤怒', '困惑', '疲惫'];
        for (const emotion of emotions) {
            if (input.includes(emotion)) {
                features.emotion = emotion;
                break;
            }
        }
        
        // 问题类型
        const problemTypes = {
            '工作': ['工作', '加班', '领导', '同事', '项目'],
            '学习': ['学习', '考试', '成绩', '作业'],
            '感情': ['恋爱', '分手', '喜欢', '对象'],
            '健康': ['失眠', '生病', '身体', '医院'],
            '人际': ['朋友', '家人', '关系', '社交']
        };
        
        for (const [type, keywords] of Object.entries(problemTypes)) {
            if (keywords.some(kw => input.includes(kw))) {
                features.problemType = type;
                break;
            }
        }
        
        return features;
    }

    /**
     * 更新话题历史
     */
    updateTopicHistory(input) {
        const topic = this.extractTopic(input);
        if (topic) {
            this.topicHistory.push({
                topic,
                timestamp: Date.now()
            });
            
            // 保持最近20个话题
            if (this.topicHistory.length > 20) {
                this.topicHistory = this.topicHistory.slice(-20);
            }
        }
    }

    /**
     * 提取话题
     */
    extractTopic(input) {
        // 简单的话题提取
        const topicKeywords = {
            '失眠': ['失眠', '睡不着', '睡眠'],
            '工作压力': ['工作', '压力', '加班'],
            '学习': ['学习', '考试', '成绩'],
            '感情': ['恋爱', '分手', '喜欢'],
            '迷茫': ['迷茫', '不知道', '方向']
        };
        
        for (const [topic, keywords] of Object.entries(topicKeywords)) {
            if (keywords.some(kw => input.includes(kw))) {
                return topic;
            }
        }
        
        return null;
    }

    /**
     * 获取相关话题
     */
    getRelevantTopics(currentInput) {
        const currentTopic = this.extractTopic(currentInput);
        
        if (!currentTopic) return [];
        
        // 找到相关的历史话题
        return this.topicHistory
            .filter(t => t.topic === currentTopic)
            .slice(-3);
    }

    /**
     * 获取对话摘要
     */
    getConversationSummary() {
        if (this.conversations.length === 0) {
            return '新对话';
        }
        
        // 统计
        const userTurns = this.conversations.filter(t => t.role === 'user').length;
        const topics = [...new Set(this.topicHistory.map(t => t.topic))];
        
        return {
            turnCount: userTurns,
            mainTopics: topics.slice(-5),
            userEmotions: this.userProfile.emotion || []
        };
    }

    /**
     * 构建带上下文的提示
     */
    buildPromptWithContext(currentInput) {
        const context = this.getContext(currentInput);
        
        let prompt = '';
        
        // 添加对话历史
        if (context.recentHistory.length > 0) {
            prompt += '[历史对话]\n';
            for (const turn of context.recentHistory) {
                prompt += `${turn.role === 'user' ? '用户' : 'AI'}: ${turn.content}\n`;
            }
            prompt += '\n';
        }
        
        // 添加用户画像
        if (context.userProfile.problemType) {
            prompt += `[用户情况] 问题类型: ${context.userProfile.problemType}\n`;
        }
        if (context.userProfile.emotion) {
            prompt += `[用户情绪] ${context.userProfile.emotion}\n`;
        }
        
        // 添加当前输入
        prompt += `[当前输入] ${currentInput}\n`;
        prompt += `[请回答]`;
        
        return prompt;
    }

    /**
     * 清空记忆
     */
    clear() {
        this.conversations = [];
        this.topicHistory = [];
        // 保留用户画像
    }

    /**
     * 完全重置
     */
    reset() {
        this.conversations = [];
        this.userProfile = {};
        this.topicHistory = [];
    }

    /**
     * 导出记忆
     */
    export() {
        return {
            conversations: this.conversations,
            userProfile: this.userProfile,
            topicHistory: this.topicHistory
        };
    }

    /**
     * 导入记忆
     */
    import(data) {
        this.conversations = data.conversations || [];
        this.userProfile = data.userProfile || {};
        this.topicHistory = data.topicHistory || [];
    }
}

// 导出
window.ConversationMemory = ConversationMemory;
