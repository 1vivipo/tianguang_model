/**
 * 天光AI - 主应用
 */

// 全局变量
let trainer = null;
let trainingData = [];

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    // 创建训练器
    trainer = new TianguangTrainer();

    // 加载保存的数据
    loadSavedData();

    // 绑定事件
    bindEvents();

    // 初始化UI
    updateUI();

    Utils.log('系统就绪');
    Utils.log(`后端: ${tf.getBackend()}`);
});

// 绑定事件
function bindEvents() {
    // 菜单切换
    document.getElementById('menuToggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('open');
    });

    // 页面切换
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            switchPage(page);
        });
    });

    // 训练控制
    document.getElementById('startTrainBtn').addEventListener('click', startTraining);
    document.getElementById('stopTrainBtn').addEventListener('click', stopTraining);
    document.getElementById('saveModelBtn').addEventListener('click', saveModel);

    // 数据管理
    document.getElementById('saveDataBtn').addEventListener('click', saveData);
    document.getElementById('uploadFileBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
    document.getElementById('fileInput').addEventListener('change', handleFileUpload);
    document.getElementById('clearDataBtn').addEventListener('click', clearData);

    // 测试
    document.getElementById('testBtn').addEventListener('click', runTest);
    document.getElementById('addCorrectionBtn').addEventListener('click', addCorrection);

    // 聊天
    document.getElementById('sendChatBtn').addEventListener('click', sendChat);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChat();
    });

    // 设置
    document.getElementById('exportModelBtn').addEventListener('click', exportModel);
    document.getElementById('importModelBtn').addEventListener('click', () => {
        document.getElementById('modelInput').click();
    });
    document.getElementById('modelInput').addEventListener('change', importModel);

    // 参数变化
    ['epochs', 'learningRate', 'batchSize', 'seqLength', 'embedDim'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', updateConfig);
        }
    });
}

// 切换页面
function switchPage(page) {
    // 更新菜单
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });

    // 更新页面
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === `page-${page}`);
    });

    // 更新标题
    const titles = {
        train: '模型训练',
        data: '数据管理',
        test: '测试评估',
        chat: '对话测试',
        settings: '系统设置'
    };
    document.getElementById('pageTitle').textContent = titles[page] || page;

    // 关闭侧边栏（移动端）
    document.getElementById('sidebar').classList.remove('open');
}

// 更新配置
function updateConfig() {
    if (!trainer) return;

    trainer.config.epochs = parseInt(document.getElementById('epochs').value) || 100;
    trainer.config.learningRate = parseFloat(document.getElementById('learningRate').value) || 0.01;
    trainer.config.batchSize = parseInt(document.getElementById('batchSize').value) || 4;
    trainer.config.seqLength = parseInt(document.getElementById('seqLength').value) || 32;
    trainer.config.embedDim = parseInt(document.getElementById('embedDim').value) || 64;
}

// 开始训练
async function startTraining() {
    if (trainingData.length < 2) {
        Utils.notify('请先添加至少2条训练数据', 'error');
        return;
    }

    // 更新配置
    updateConfig();

    // 更新UI
    document.getElementById('startTrainBtn').disabled = true;
    document.getElementById('stopTrainBtn').disabled = false;
    document.getElementById('statusBadge').textContent = '训练中';
    document.getElementById('statusBadge').classList.add('training');
    document.getElementById('trainStatus').textContent = '训练中...';

    Utils.clearLog();
    Utils.log('开始训练...');

    // 开始训练
    await trainer.train(trainingData, {
        onProgress: (data) => {
            document.getElementById('currentEpoch').textContent = `${data.epoch} / ${trainer.config.epochs}`;
            document.getElementById('currentLoss').textContent = data.loss.toFixed(4);
            document.getElementById('currentAccuracy').textContent = (data.accuracy * 100).toFixed(1) + '%';
            document.getElementById('trainProgress').style.width = data.progress + '%';
            document.getElementById('progressText').textContent = data.progress.toFixed(1) + '%';
        },
        onComplete: () => {
            document.getElementById('startTrainBtn').disabled = false;
            document.getElementById('stopTrainBtn').disabled = true;
            document.getElementById('saveModelBtn').disabled = false;
            document.getElementById('statusBadge').textContent = '完成';
            document.getElementById('statusBadge').classList.remove('training');
            document.getElementById('trainStatus').textContent = '训练完成';
            Utils.notify('训练完成!', 'success');
        },
        onError: (error) => {
            document.getElementById('startTrainBtn').disabled = false;
            document.getElementById('stopTrainBtn').disabled = true;
            document.getElementById('statusBadge').textContent = '错误';
            document.getElementById('statusBadge').classList.remove('training');
            document.getElementById('trainStatus').textContent = '训练失败';
        }
    });
}

// 停止训练
function stopTraining() {
    trainer.stop();
    document.getElementById('startTrainBtn').disabled = false;
    document.getElementById('stopTrainBtn').disabled = true;
    document.getElementById('statusBadge').textContent = '已停止';
    document.getElementById('statusBadge').classList.remove('training');
    document.getElementById('trainStatus').textContent = '已停止';
}

// 保存模型
async function saveModel() {
    const data = await trainer.save();
    if (data) {
        Utils.storage.set('model', data);
        Utils.notify('模型已保存到本地', 'success');
    }
}

// 保存数据
function saveData() {
    const input = document.getElementById('dataInput').value;
    const lines = input.split('\n').filter(l => l.trim());

    if (lines.length === 0) {
        Utils.notify('请输入训练数据', 'error');
        return;
    }

    trainingData = lines;
    Utils.storage.set('trainingData', trainingData);
    updateDataPreview();
    Utils.notify(`已保存 ${lines.length} 条数据`, 'success');
}

// 加载保存的数据
function loadSavedData() {
    const saved = Utils.storage.get('trainingData');
    if (saved && Array.isArray(saved)) {
        trainingData = saved;
        document.getElementById('dataInput').value = trainingData.join('\n');
        updateDataPreview();
    }
}

// 更新数据预览
function updateDataPreview() {
    const preview = document.getElementById('dataPreview');
    const count = document.getElementById('dataCount');

    if (trainingData.length === 0) {
        preview.innerHTML = '<p class="empty-hint">暂无数据，请添加训练数据</p>';
        count.textContent = '0';
        return;
    }

    preview.innerHTML = trainingData.map((item, i) => 
        `<div class="data-item">${i + 1}. ${item}</div>`
    ).join('');

    count.textContent = trainingData.length;
}

// 处理文件上传
async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    try {
        const content = await Utils.readFile(file);
        let lines = [];

        if (file.name.endsWith('.json')) {
            const data = JSON.parse(content);
            if (Array.isArray(data)) {
                lines = data.map(d => typeof d === 'string' ? d : d.text || d.content || '');
            }
        } else {
            lines = content.split('\n').filter(l => l.trim());
        }

        trainingData = [...trainingData, ...lines.filter(l => l.trim())];
        document.getElementById('dataInput').value = trainingData.join('\n');
        Utils.storage.set('trainingData', trainingData);
        updateDataPreview();
        Utils.notify(`已导入 ${lines.length} 条数据`, 'success');
    } catch (error) {
        Utils.notify('文件读取失败', 'error');
    }

    e.target.value = '';
}

// 清空数据
function clearData() {
    if (confirm('确定要清空所有数据吗？')) {
        trainingData = [];
        document.getElementById('dataInput').value = '';
        Utils.storage.remove('trainingData');
        updateDataPreview();
        Utils.notify('数据已清空', 'success');
    }
}

// 运行测试
async function runTest() {
    const prompt = document.getElementById('testPrompt').value || '人工智能';
    const length = parseInt(document.getElementById('generateLength').value) || 50;

    document.getElementById('testResult').innerHTML = '<p>生成中...</p>';

    try {
        const result = await trainer.generate(prompt, length);
        document.getElementById('testResult').textContent = result;

        // 评估
        const scores = trainer.evaluate(result);
        updateScores(scores);
    } catch (error) {
        document.getElementById('testResult').textContent = '生成失败: ' + error.message;
    }
}

// 更新评分
function updateScores(scores) {
    document.getElementById('fluencyScore').style.width = scores.fluency + '%';
    document.getElementById('fluencyValue').textContent = scores.fluency.toFixed(0);

    document.getElementById('relevanceScore').style.width = scores.relevance + '%';
    document.getElementById('relevanceValue').textContent = scores.relevance.toFixed(0);

    document.getElementById('diversityScore').style.width = scores.diversity + '%';
    document.getElementById('diversityValue').textContent = scores.diversity.toFixed(0);
}

// 添加纠正
function addCorrection() {
    const correction = document.getElementById('correctionInput').value.trim();
    if (!correction) {
        Utils.notify('请输入纠正内容', 'error');
        return;
    }

    trainingData.push(correction);
    document.getElementById('dataInput').value = trainingData.join('\n');
    Utils.storage.set('trainingData', trainingData);
    updateDataPreview();
    document.getElementById('correctionInput').value = '';
    Utils.notify('已添加到训练数据', 'success');
}

// 发送聊天
async function sendChat() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // 添加用户消息
    addChatMessage(message, 'user');
    input.value = '';

    // 生成回复
    try {
        const response = await trainer.generate(message, 50);
        addChatMessage(response, 'assistant');
    } catch (error) {
        addChatMessage('生成失败，请确保已训练模型', 'system');
    }
}

// 添加聊天消息
function addChatMessage(content, role) {
    const container = document.getElementById('chatContainer');
    const msg = document.createElement('div');
    msg.className = `chat-message ${role}`;
    msg.innerHTML = `<div class="message-content">${content}</div>`;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
}

// 导出模型
async function exportModel() {
    const data = await trainer.save();
    if (data) {
        Utils.downloadJSON(data, `tianguang-model-${Date.now()}.json`);
        Utils.notify('模型已导出', 'success');
    }
}

// 导入模型
async function importModel(e) {
    const file = e.target.files[0];
    if (!file) return;

    try {
        const content = await Utils.readFile(file);
        const data = JSON.parse(content);
        await trainer.load(data);
        Utils.notify('模型已导入', 'success');
        updateUI();
    } catch (error) {
        Utils.notify('导入失败', 'error');
    }

    e.target.value = '';
}

// 更新UI
function updateUI() {
    const status = trainer.getStatus();

    document.getElementById('dataCount').textContent = trainingData.length;
    document.getElementById('vocabSize').textContent = status.vocabSize || 0;

    if (status.hasModel) {
        document.getElementById('saveModelBtn').disabled = false;
        document.getElementById('modelInfo').innerHTML = `
            <p><strong>模型状态:</strong> 已加载</p>
            <p><strong>参数量:</strong> ${Utils.formatNumber(trainer.model?.countParams() || 0)}</p>
            <p><strong>训练轮次:</strong> ${status.historyLength}</p>
        `;
    }
}
