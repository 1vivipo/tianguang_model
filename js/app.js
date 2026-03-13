/**
 * 天光AI - 应用主模块
 */

class TianguangApp {
    constructor() {
        this.trainer = new TianguangTrainer();
        this.styleGenerator = null;
        this.currentStyle = 'feilu';
        this.loadedDataCount = 0;
    }

    // 初始化
    async init() {
        console.log('天光AI 初始化...');
        
        // 绑定事件
        this.bindEvents();
        
        // 加载数据统计
        this.loadDataStats();
        
        // 初始化风格生成器
        this.styleGenerator = new StyleGenerator(this.trainer);
        
        console.log('初始化完成');
    }

    // 绑定事件
    bindEvents() {
        // 导航
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                this.showPage(page);
            });
        });

        // 移动端菜单
        const menuToggle = document.getElementById('menuToggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                document.getElementById('sidebar').classList.toggle('open');
            });
        }

        // 训练控制
        document.getElementById('startTrainBtn')?.addEventListener('click', () => this.startTraining());
        document.getElementById('stopTrainBtn')?.addEventListener('click', () => this.stopTraining());
        document.getElementById('saveModelBtn')?.addEventListener('click', () => this.saveModel());

        // 数据管理
        document.getElementById('loadAllDataBtn')?.addEventListener('click', () => this.loadAllData());
        document.getElementById('loadRandomBtn')?.addEventListener('click', () => this.loadRandomData(500));

        // 测试
        document.getElementById('testBtn')?.addEventListener('click', () => this.runTest());

        // 聊天
        document.getElementById('sendChatBtn')?.addEventListener('click', () => this.sendChat());
        document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendChat();
        });

        // 导出导入
        document.getElementById('exportModelBtn')?.addEventListener('click', () => this.exportModel());
        document.getElementById('importModelBtn')?.addEventListener('click', () => document.getElementById('modelInput').click());
        document.getElementById('modelInput')?.addEventListener('change', (e) => this.importModel(e));
    }

    // 显示页面
    showPage(pageName) {
        // 更新菜单
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === pageName);
        });

        // 更新页面
        document.querySelectorAll('.page').forEach(page => {
            page.classList.toggle('active', page.id === `page-${pageName}`);
        });

        // 更新标题
        const titles = {
            train: '模型训练',
            data: '数据管理',
            test: '测试评估',
            chat: '对话测试',
            settings: '系统设置'
        };
        document.getElementById('pageTitle').textContent = titles[pageName] || pageName;
    }

    // 加载数据统计
    loadDataStats() {
        if (typeof TrainingData !== 'undefined') {
            const stats = TrainingData.getStats();
            document.getElementById('totalData').textContent = stats.total;
        }
    }

    // 加载全部数据
    loadAllData() {
        if (typeof TrainingData === 'undefined') {
            this.showNotification('数据模块未加载', 'error');
            return;
        }

        const allData = TrainingData.getAllData();
        this.loadedDataCount = allData.length;
        
        // 显示预览
        const preview = document.getElementById('dataPreview');
        if (preview) {
            preview.innerHTML = allData.slice(0, 20).map(d => 
                `<div class="data-item">${d.substring(0, 50)}...</div>`
            ).join('');
        }

        // 更新统计
        document.getElementById('loadedData').textContent = allData.length;
        
        // 更新分类统计
        const categories = TrainingData.getCategories();
        const categoriesDiv = document.getElementById('dataCategories');
        if (categoriesDiv) {
            categoriesDiv.innerHTML = Object.entries(categories).map(([name, count]) => 
                `<div class="category-item">
                    <span class="category-name">${name}</span>
                    <span class="category-count">${count}</span>
                </div>`
            ).join('');
        }

        this.showNotification(`已加载 ${allData.length} 条数据`);
    }

    // 加载随机数据
    loadRandomData(count) {
        if (typeof TrainingData === 'undefined') {
            this.showNotification('数据模块未加载', 'error');
            return;
        }

        const allData = TrainingData.getAllData();
        const shuffled = [...allData].sort(() => Math.random() - 0.5);
        const selected = shuffled.slice(0, count);
        
        this.loadedDataCount = selected.length;
        
        const preview = document.getElementById('dataPreview');
        if (preview) {
            preview.innerHTML = selected.slice(0, 20).map(d => 
                `<div class="data-item">${d.substring(0, 50)}...</div>`
            ).join('');
        }

        document.getElementById('loadedData').textContent = selected.length;
        this.showNotification(`已随机加载 ${selected.length} 条数据`);
    }

    // 开始训练
    async startTraining() {
        // 获取数据
        let data = [];
        if (typeof TrainingData !== 'undefined') {
            data = TrainingData.getAllData();
        }
        
        // 也加上用户自定义数据
        const customData = document.getElementById('dataInput')?.value || '';
        if (customData.trim()) {
            data = data.concat(customData.split('\n').filter(l => l.trim()));
        }

        if (data.length === 0) {
            this.showNotification('请先加载数据', 'error');
            return;
        }

        // 获取训练模式
        const mode = document.querySelector('input[name="trainMode"]:checked')?.value || 'quick';
        this.trainer.setMode(mode);

        // 获取参数
        const epochs = parseInt(document.getElementById('epochs')?.value) || 20;
        const learningRate = parseFloat(document.getElementById('learningRate')?.value) || 0.02;
        const batchSize = parseInt(document.getElementById('batchSize')?.value) || 8;

        this.trainer.config.epochs = epochs;
        this.trainer.config.learningRate = learningRate;
        this.trainer.config.batchSize = batchSize;

        // 更新UI
        document.getElementById('startTrainBtn').disabled = true;
        document.getElementById('stopTrainBtn').disabled = false;
        document.getElementById('trainStatus').textContent = '训练中...';
        document.getElementById('trainLog').innerHTML = '';

        // 开始训练
        try {
            await this.trainer.train(data, {
                onProgress: (info) => {
                    document.getElementById('currentEpoch').textContent = `${info.epoch}/${info.total}`;
                    document.getElementById('currentLoss').textContent = info.loss.toFixed(4);
                    document.getElementById('currentAccuracy').textContent = `${(info.accuracy * 100).toFixed(1)}%`;
                    document.getElementById('trainProgress').style.width = `${info.progress}%`;
                    document.getElementById('progressText').textContent = `${info.progress.toFixed(1)}%`;
                    document.getElementById('elapsedTime').textContent = Utils.formatTime(info.elapsed);
                    
                    if (info.eta) {
                        document.getElementById('trainLog').innerHTML += 
                            `<div>Epoch ${info.epoch}: Loss=${info.loss.toFixed(4)}, ETA=${Utils.formatTime(info.eta)}</div>`;
                    }
                },
                onComplete: (history) => {
                    document.getElementById('trainStatus').textContent = '训练完成';
                    document.getElementById('startTrainBtn').disabled = false;
                    document.getElementById('stopTrainBtn').disabled = true;
                    document.getElementById('saveModelBtn').disabled = false;
                    this.showNotification('训练完成！', 'success');
                },
                onError: (error) => {
                    document.getElementById('trainStatus').textContent = '训练失败';
                    document.getElementById('startTrainBtn').disabled = false;
                    document.getElementById('stopTrainBtn').disabled = true;
                    this.showNotification(`训练失败: ${error.message}`, 'error');
                }
            });
        } catch (error) {
            console.error(error);
            this.showNotification(`训练出错: ${error.message}`, 'error');
        }
    }

    // 停止训练
    stopTraining() {
        this.trainer.stop();
        document.getElementById('trainStatus').textContent = '已停止';
        document.getElementById('startTrainBtn').disabled = false;
        document.getElementById('stopTrainBtn').disabled = true;
    }

    // 保存模型
    async saveModel() {
        const data = await this.trainer.save();
        if (!data) {
            this.showNotification('没有模型可保存', 'error');
            return;
        }

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tianguang-model-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('模型已保存', 'success');
    }

    // 运行测试
    async runTest() {
        const prompt = document.getElementById('testPrompt')?.value || '人工智能';
        const length = parseInt(document.getElementById('generateLength')?.value) || 50;
        const temperature = parseFloat(document.getElementById('temperature')?.value) || 0.8;

        const resultDiv = document.getElementById('testResult');
        resultDiv.innerHTML = '<p>生成中...</p>';

        try {
            const result = await this.trainer.generate(prompt, length, temperature);
            resultDiv.innerHTML = `<div class="generated-text">${prompt}${result}</div>`;
        } catch (error) {
            resultDiv.innerHTML = `<p class="error">生成失败: ${error.message}</p>`;
        }
    }

    // 发送聊天
    async sendChat() {
        const input = document.getElementById('chatInput');
        const message = input?.value.trim();
        
        if (!message) return;

        const container = document.getElementById('chatContainer');
        
        // 添加用户消息
        container.innerHTML += `
            <div class="chat-message user">
                <div class="message-content">${message}</div>
            </div>
        `;

        input.value = '';

        // 生成回复
        try {
            const response = await this.styleGenerator.generate(message, 100);
            
            container.innerHTML += `
                <div class="chat-message assistant">
                    <div class="message-content">${response}</div>
                </div>
            `;
        } catch (error) {
            container.innerHTML += `
                <div class="chat-message assistant">
                    <div class="message-content">抱歉，生成回复时出错了。</div>
                </div>
            `;
        }

        // 滚动到底部
        container.scrollTop = container.scrollHeight;
    }

    // 导出模型
    async exportModel() {
        await this.saveModel();
    }

    // 导入模型
    async importModel(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (e) => {
            try {
                const data = JSON.parse(e.target.result);
                await this.trainer.load(data);
                this.showNotification('模型已加载', 'success');
                document.getElementById('modelInfo').innerHTML = `
                    <p>模型已加载</p>
                    <p>词表大小: ${data.config.vocabSize}</p>
                    <p>训练轮次: ${data.history?.length || 0}</p>
                `;
            } catch (error) {
                this.showNotification('加载失败', 'error');
            }
        };
        reader.readAsText(file);
    }

    // 显示通知
    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        if (notification) {
            notification.textContent = message;
            notification.className = `notification show ${type}`;
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TianguangApp();
    window.app.init();
});
