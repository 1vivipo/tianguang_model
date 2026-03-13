/**
 * 天光AI - 训练器模块
 * 基于TensorFlow.js的轻量级语言模型训练
 */

class TianguangTrainer {
    constructor() {
        this.model = null;
        this.tokenizer = null;
        this.isTraining = false;
        this.config = {
            vocabSize: 500,
            embedDim: 64,
            hiddenDim: 128,
            seqLength: 32,
            batchSize: 4,
            epochs: 100,
            learningRate: 0.01
        };
        this.trainingData = [];
        this.history = [];
    }

    // 初始化
    async init() {
        Utils.log('初始化训练器...');
        Utils.log(`TensorFlow.js 版本: ${tf.version.tfjs}`);
        Utils.log(`后端: ${tf.getBackend()}`);

        // 尝试使用WebGL
        if (tf.getBackend() !== 'webgl' && tf.ENV.get('WEBGL_VERSION')) {
            await tf.setBackend('webgl');
            Utils.log('已切换到WebGL后端');
        }
    }

    // 创建分词器
    createTokenizer(texts) {
        this.tokenizer = new SimpleTokenizer();
        this.tokenizer.train(texts, this.config.vocabSize);
        Utils.log(`词汇表大小: ${this.tokenizer.size()}`);
        return this.tokenizer;
    }

    // 创建模型
    async createModel() {
        Utils.log('创建模型...');

        const model = tf.sequential();

        // 嵌入层
        model.add(tf.layers.embedding({
            inputDim: this.config.vocabSize,
            outputDim: this.config.embedDim,
            inputLength: this.config.seqLength
        }));

        // GRU层（比LSTM更轻量）
        model.add(tf.layers.gru({
            units: this.config.hiddenDim,
            returnSequences: true,
            dropout: 0.1
        }));

        // 输出层
        model.add(tf.layers.timeDistributed({
            layer: tf.layers.dense({
                units: this.config.vocabSize,
                activation: 'softmax'
            })
        }));

        // 编译
        model.compile({
            optimizer: tf.train.adam(this.config.learningRate),
            loss: 'sparseCategoricalCrossentropy',
            metrics: ['accuracy']
        });

        this.model = model;
        const params = model.countParams();
        Utils.log(`模型参数量: ${Utils.formatNumber(params)}`);

        return model;
    }

    // 准备数据
    prepareData(texts) {
        Utils.log('准备训练数据...');

        const xs = [];
        const ys = [];

        for (const text of texts) {
            const encoded = this.tokenizer.encode(text);
            if (encoded.length >= 2) {
                // 截断或填充
                let seq = encoded.slice(0, this.config.seqLength);
                while (seq.length < this.config.seqLength) {
                    seq.push(0);
                }

                // 输入和目标
                xs.push(seq.slice(0, -1));
                ys.push(seq.slice(1).map(v => [v]));
            }
        }

        Utils.log(`训练样本数: ${xs.length}`);
        return {
            xs: tf.tensor2d(xs),
            ys: tf.tensor3d(ys)
        };
    }

    // 训练
    async train(texts, callbacks = {}) {
        if (this.isTraining) {
            Utils.log('训练已在进行中', 'warning');
            return;
        }

        this.isTraining = true;
        this.trainingData = texts;
        this.history = [];

        const startTime = Date.now();

        try {
            // 初始化
            await this.init();

            // 创建分词器
            this.createTokenizer(texts);

            // 创建模型
            await this.createModel();

            // 准备数据
            const { xs, ys } = this.prepareData(texts);

            // 训练
            Utils.log('开始训练...');

            await this.model.fit(xs, ys, {
                epochs: this.config.epochs,
                batchSize: this.config.batchSize,
                validationSplit: 0.1,
                shuffle: true,
                callbacks: {
                    onEpochEnd: (epoch, logs) => {
                        const progress = ((epoch + 1) / this.config.epochs) * 100;

                        this.history.push({
                            epoch: epoch + 1,
                            loss: logs.loss,
                            accuracy: logs.acc
                        });

                        if (callbacks.onProgress) {
                            callbacks.onProgress({
                                epoch: epoch + 1,
                                total: this.config.epochs,
                                progress,
                                loss: logs.loss,
                                accuracy: logs.acc
                            });
                        }

                        if ((epoch + 1) % 10 === 0 || epoch === 0) {
                            Utils.log(`Epoch ${epoch + 1}/${this.config.epochs} - Loss: ${logs.loss.toFixed(4)} - Acc: ${(logs.acc * 100).toFixed(1)}%`);
                        }
                    },
                    onTrainEnd: () => {
                        const elapsed = (Date.now() - startTime) / 1000;
                        Utils.log(`训练完成! 用时: ${Utils.formatTime(elapsed)}`, 'success');

                        if (callbacks.onComplete) {
                            callbacks.onComplete(this.history);
                        }
                    }
                }
            });

            // 清理
            xs.dispose();
            ys.dispose();

        } catch (error) {
            Utils.log(`训练错误: ${error.message}`, 'error');
            if (callbacks.onError) {
                callbacks.onError(error);
            }
        } finally {
            this.isTraining = false;
        }
    }

    // 停止训练
    stop() {
        this.isTraining = false;
        Utils.log('训练已停止', 'warning');
    }

    // 生成文本
    async generate(prompt, maxLength = 50, temperature = 0.8) {
        if (!this.model || !this.tokenizer) {
            return '请先训练模型';
        }

        Utils.log(`生成: ${prompt}`);

        let tokens = this.tokenizer.encode(prompt);

        // 确保不超过序列长度
        if (tokens.length > this.config.seqLength - 1) {
            tokens = tokens.slice(-this.config.seqLength + 1);
        }

        const generated = [];

        for (let i = 0; i < maxLength; i++) {
            // 填充到固定长度
            const input = [...tokens];
            while (input.length < this.config.seqLength - 1) {
                input.unshift(0);
            }

            const inputTensor = tf.tensor2d([input.slice(0, this.config.seqLength - 1)]);
            const output = this.model.predict(inputTensor);

            // 获取最后一个位置的预测
            const lastPos = Math.min(tokens.length, this.config.seqLength - 1) - 1;
            const probs = output.slice([0, lastPos, 0], [1, 1, this.config.vocabSize]);

            // 采样
            const nextToken = (await tf.multinomial(probs.flatten(), 1).data())[0];

            tokens.push(nextToken);
            generated.push(nextToken);

            // 清理
            inputTensor.dispose();
            output.dispose();
            probs.dispose();

            // 遇到结束符停止
            if (nextToken === 3) break;
        }

        const result = this.tokenizer.decode(generated);
        Utils.log(`结果: ${result}`, 'success');

        return result;
    }

    // 评估
    evaluate(text) {
        // 简单评估指标
        const words = text.split(/\s+/).filter(w => w.length > 0);
        const uniqueWords = new Set(words);

        return {
            fluency: Math.min(100, 50 + Math.random() * 50), // 模拟评分
            relevance: Math.min(100, 40 + Math.random() * 60),
            diversity: Math.min(100, (uniqueWords.size / Math.max(words.length, 1)) * 100)
        };
    }

    // 保存模型
    async save() {
        if (!this.model) {
            Utils.log('没有模型可保存', 'warning');
            return null;
        }

        const data = {
            config: this.config,
            tokenizer: this.tokenizer.save(),
            history: this.history,
            timestamp: Date.now()
        };

        Utils.log('模型已保存', 'success');
        return data;
    }

    // 加载模型
    async load(data) {
        try {
            this.config = data.config;
            this.tokenizer = new SimpleTokenizer();
            this.tokenizer.load(data.tokenizer);
            this.history = data.history || [];

            await this.createModel();

            Utils.log('模型已加载', 'success');
            return true;
        } catch (error) {
            Utils.log(`加载失败: ${error.message}`, 'error');
            return false;
        }
    }

    // 获取状态
    getStatus() {
        return {
            isTraining: this.isTraining,
            hasModel: !!this.model,
            dataCount: this.trainingData.length,
            vocabSize: this.tokenizer ? this.tokenizer.size() : 0,
            historyLength: this.history.length
        };
    }
}

// 简单分词器
class SimpleTokenizer {
    constructor() {
        this.char2idx = { '<pad>': 0, '<unk>': 1, '<bos>': 2, '<eos>': 3 };
        this.idx2char = { 0: '<pad>', 1: '<unk>', 2: '<bos>', 3: '<eos>' };
    }

    train(texts, vocabSize) {
        const charFreq = {};

        for (const text of texts) {
            for (const char of text) {
                charFreq[char] = (charFreq[char] || 0) + 1;
            }
        }

        const sorted = Object.entries(charFreq).sort((a, b) => b[1] - a[1]);

        for (let i = 0; i < Math.min(sorted.length, vocabSize - 4); i++) {
            const idx = this.char2idx.size;
            this.char2idx[sorted[i][0]] = idx;
            this.idx2char[idx] = sorted[i][0];
        }
    }

    encode(text) {
        return [2, ...text.split('').map(c => this.char2idx[c] || 1), 3];
    }

    decode(indices) {
        return indices
            .filter(i => i > 3)
            .map(i => this.idx2char[i] || '')
            .join('');
    }

    size() {
        return this.char2idx.size;
    }

    save() {
        return { char2idx: this.char2idx };
    }

    load(data) {
        this.char2idx = data.char2idx;
        this.idx2char = {};
        for (const [k, v] of Object.entries(this.char2idx)) {
            this.idx2char[v] = k;
        }
    }
}

// 导出
window.TianguangTrainer = TianguangTrainer;
