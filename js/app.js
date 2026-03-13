/**
 * 天光AI - 应用主模块（修复版）
 */

class TianguangApp {
    constructor() {
        this.trainer = new TianguangTrainer();
        this.styleGenerator = null;
        this.currentStyle = 'feilu';
        this.loadedDataCount = 0;
        this.customTrainingData = []; // 用户添加的训练数据
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
        
        // 加载保存的自定义数据
        this.loadCustomData();
        
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
        document.getElementById('saveDataBtn')?.addEventListener('click', () => this.saveCustomData());
        document.getElementById('clearDataBtn')?.addEventListener('click', () => this.clearCustomData());

        // 测试
        document.getElementById('testBtn')?.addEventListener('click', () => this.runTest());

        // 结果纠正
        document.getElementById('addCorrectionBtn')?.addEventListener('click', () => this.addCorrection());

        // 聊天
        document.getElementById('sendChatBtn')?.addEventListener('click', () => this.sendChat());
        document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendChat();
        });

        // 导出导入
        document.getElementById('exportModelBtn')?.addEventListener('click', () => this.exportModel());
        document.getElementById('importModelBtn')?.addEventListener('click', () => document.getElementById('modelInput').click());
        document.getElementById('modelInput')?.addEventListener('change', (e) => this.importModel(e));

        // 文件上传
        document.getElementById('uploadFileBtn')?.addEventListener('click', () => document.getElementById('fileInput').click());
        document.getElementById('fileInput')?.addEventListener('change', (e) => this.uploadFile(e));
    }

    // 显示页面
    showPage(pageName) {
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === pageName);
        });

        document.querySelectorAll('.page').forEach(page => {
            page.classList.toggle('active', page.id === `page-${pageName}`);
        });

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

    // 加载保存的自定义数据
    loadCustomData() {
        try {
            const saved = localStorage.getItem('tianguang_custom_data');
            if (saved) {
                this.customTrainingData = JSON.parse(saved);
                console.log(`加载了 ${this.customTrainingData.length} 条自定义数据`);
            }
        } catch (e) {
            console.error('加载自定义数据失败', e);
        }
    }

    // 保存自定义数据到本地
    saveCustomDataToStorage() {
        try {
            localStorage.setItem('tianguang_custom_data', JSON.stringify(this.customTrainingData));
        } catch (e) {
            console.error('保存自定义数据失败', e);
        }
    }

    // 加载全部数据
    loadAllData() {
        if (typeof TrainingData === 'undefined') {
            this.showNotification('数据模块未加载', 'error');
            return;
        }

        let allData = TrainingData.getAllData();
        
        // 加上飞卢风格数据
        if (typeof BUILTIN_DATA !== 'undefined' && BUILTIN_DATA.feilu_style) {
            allData = allData.concat(BUILTIN_DATA.feilu_style);
        }
        
        // 加上自定义数据
        if (this.customTrainingData.length > 0) {
            allData = allData.concat(this.customTrainingData);
        }
        
        this.loadedDataCount = allData.length;
        
        const preview = document.getElementById('dataPreview');
        if (preview) {
            preview.innerHTML = allData.slice(0, 20).map(d => 
                `<div class="data-item">${this.escapeHtml(d.substring(0, 50))}...</div>`
            ).join('');
        }

        document.getElementById('loadedData').textContent = allData.length;
        
        // 显示自定义数据数量
        if (this.customTrainingData.length > 0) {
            this.showNotification(`已加载 ${allData.length} 条数据（含 ${this.customTrainingData.length} 条自定义数据）`);
        } else {
            this.showNotification(`已加载 ${allData.length} 条数据`);
        }
    }

    // 加载随机数据
    loadRandomData(count) {
        if (typeof TrainingData === 'undefined') {
            this.showNotification('数据模块未加载', 'error');
            return;
        }

        let allData = TrainingData.getAllData();
        
        // 加上飞卢风格数据
        if (typeof BUILTIN_DATA !== 'undefined' && BUILTIN_DATA.feilu_style) {
            allData = allData.concat(BUILTIN_DATA.feilu_style);
        }
        
        // 加上自定义数据（全部保留）
        if (this.customTrainingData.length > 0) {
            allData = allData.concat(this.customTrainingData);
        }
        
        const shuffled = [...allData].sort(() => Math.random() - 0.5);
        const selected = shuffled.slice(0, count);
        
        this.loadedDataCount = selected.length;
        
        const preview = document.getElementById('dataPreview');
        if (preview) {
            preview.innerHTML = selected.slice(0, 20).map(d => 
                `<div class="data-item">${this.escapeHtml(d.substring(0, 50))}...</div>`
            ).join('');
        }

        document.getElementById('loadedData').textContent = selected.length;
        this.showNotification(`已随机加载 ${selected.length} 条数据`);
    }

    // 保存自定义数据
    saveCustomData() {
        const textarea = document.getElementById('dataInput');
        const text = textarea?.value.trim();
        
        if (!text) {
            this.showNotification('请输入数据', 'error');
            return;
        }
        
        const lines = text.split('\n').filter(l => l.trim());
        this.customTrainingData = this.customTrainingData.concat(lines);
        this.saveCustomDataToStorage();
        
        textarea.value = '';
        this.showNotification(`已添加 ${lines.length} 条数据，共 ${this.customTrainingData.length} 条自定义数据。请重新训练模型！`, 'success');
        
        // 显示提示
        this.showRetrainTip();
    }

    // 清空自定义数据
    clearCustomData() {
        if (confirm('确定要清空所有自定义数据吗？')) {
            this.customTrainingData = [];
            this.saveCustomDataToStorage();
            this.showNotification('已清空自定义数据');
        }
    }

    // 上传文件
    uploadFile(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const text = e.target.result;
            const lines = text.split('\n').filter(l => l.trim());
            
            this.customTrainingData = this.customTrainingData.concat(lines);
            this.saveCustomDataToStorage();
            
            this.showNotification(`已从文件添加 ${lines.length} 条数据，共 ${this.customTrainingData.length} 条自定义数据。请重新训练模型！`, 'success');
            this.showRetrainTip();
        };
        reader.readAsText(file);
    }

    // 添加纠正数据
    addCorrection() {
        const textarea = document.getElementById('correctionInput');
        const text = textarea?.value.trim();
        
        if (!text) {
            this.showNotification('请输入正确的回复内容', 'error');
            return;
        }
        
        // 添加到自定义训练数据
        this.customTrainingData.push(text);
        this.saveCustomDataToStorage();
        
        textarea.value = '';
        
        // 显示明显的提示
        this.showNotification('✅ 已添加到训练数据！请重新训练模型才能生效！', 'success');
        
        // 显示重新训练提示
        this.showRetrainTip();
    }

    // 显示重新训练提示
    showRetrainTip() {
        const tip = document.createElement('div');
        tip.className = 'retrain-tip';
        tip.innerHTML = `
            <div class="tip-content">
                <span class="tip-icon">⚠️</span>
                <span class="tip-text">数据已更新，需要重新训练模型才能生效！</span>
                <button class="tip-btn" onclick="app.goToTrain()">去训练</button>
                <button class="tip-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        document.body.appendChild(tip);
        
        // 5秒后自动消失
        setTimeout(() => tip.remove(), 10000);
    }

    // 跳转到训练页面
    goToTrain() {
        this.showPage('train');
        document.querySelector('.retrain-tip')?.remove();
    }

    // 开始训练
    async startTraining() {
        // 获取数据
        let data = [];
        if (typeof TrainingData !== 'undefined') {
            data = TrainingData.getAllData();
        }
        
        // 加上飞卢风格数据
        if (typeof BUILTIN_DATA !== 'undefined' && BUILTIN_DATA.feilu_style) {
            data = data.concat(BUILTIN_DATA.feilu_style);
        }
        
        // 加上自定义数据
        if (this.customTrainingData.length > 0) {
            data = data.concat(this.customTrainingData);
            console.log(`包含 ${this.customTrainingData.length} 条自定义数据`);
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
            
            // 检查是否乱码
            let displayResult = result;
            if (this.isGarbled(result)) {
                displayResult = `[输出异常，请检查训练数据是否包含中文]\n原始输出: ${result}`;
            }
            
            resultDiv.innerHTML = `
                <div class="generated-text">
                    <div class="prompt">${this.escapeHtml(prompt)}</div>
                    <div class="result">${this.escapeHtml(displayResult)}</div>
                </div>
            `;
        } catch (error) {
            resultDiv.innerHTML = `<p class="error">生成失败: ${error.message}</p>`;
        }
    }

    // 检查是否乱码
    isGarbled(text) {
        if (!text) return false;
        // 检查是否有过多不可打印字符
        const printable = text.replace(/[\x00-\x1F\x7F-\x9F]/g, '');
        return printable.length < text.length * 0.8;
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
                <div class="message-content">${this.escapeHtml(message)}</div>
            </div>
        `;

        input.value = '';

        // 生成回复
        try {
            const response = await this.styleGenerator.generate(message, 100);
            
            container.innerHTML += `
                <div class="chat-message assistant">
                    <div class="message-content">${this.escapeHtml(response)}</div>
                </div>
            `;
        } catch (error) {
            container.innerHTML += `
                <div class="chat-message assistant">
                    <div class="message-content">抱歉，生成回复时出错了。请确保模型已训练。</div>
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

    // HTML转义
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // 显示通知
    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        if (notification) {
            notification.textContent = message;
            notification.className = `notification show ${type}`;
            setTimeout(() => {
                notification.classList.remove('show');
            }, 5000);
        }
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    window.app = new TianguangApp();
    window.app.init();
});
