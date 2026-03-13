/**
 * 天光AI - 训练器模块（修复中文输出版）
 */

class TianguangTrainer {
    constructor() {
        this.model = null;
        this.tokenizer = null;
        this.isTraining = false;
        this.shouldStop = false;
        
        this.config = {
            vocabSize: 500,
            embedDim: 32,
            hiddenDim: 64,
            seqLength: 16,
            batchSize: 8,
            epochs: 20,
            learningRate: 0.02,
            maxDataSize: 500
        };
        
        this.trainingData = [];
        this.history = [];
    }

    setMode(mode) {
        switch(mode) {
            case 'quick':
                this.config = {
                    ...this.config,
                    embedDim: 32,
                    hiddenDim: 64,
                    seqLength: 16,
                    epochs: 20,
                    learningRate: 0.02,
                    maxDataSize: 500
                };
                Utils.log('已切换到快速模式');
                break;
            case 'balanced':
                this.config = {
                    ...this.config,
                    embedDim: 48,
                    hiddenDim: 96,
                    seqLength: 24,
                    epochs: 30,
                    learningRate: 0.015,
                    maxDataSize: 1000
                };
                Utils.log('已切换到平衡模式');
                break;
            case 'full':
                this.config = {
                    ...this.config,
                    embedDim: 64,
                    hiddenDim: 128,
                    seqLength: 32,
                    epochs: 50,
                    learningRate: 0.01,
                    maxDataSize: 2000
                };
                Utils.log('已切换到完整模式');
                break;
        }
    }

    async init() {
        Utils.log('初始化训练器...');
        Utils.log(`TensorFlow.js 版本: ${tf.version.tfjs}`);
        Utils.log(`后端: ${tf.getBackend()}`);

        if (tf.getBackend() !== 'webgl' && tf.ENV.get('WEBGL_VERSION')) {
            await tf.setBackend('webgl');
            Utils.log('已切换到WebGL后端');
        }
    }

    createTokenizer(texts) {
        this.tokenizer = new SimpleTokenizer();
        this.tokenizer.train(texts, this.config.vocabSize);
        Utils.log(`词汇表大小: ${this.tokenizer.size()}`);
        
        // 验证中文支持
        const testText = "测试中文";
        const encoded = this.tokenizer.encode(testText);
        const decoded = this.tokenizer.decode(encoded);
        Utils.log(`分词器测试: "${testText}" -> [${encoded.slice(0,6)}...] -> "${decoded}"`);
        
        return this.tokenizer;
    }

    async createModel() {
        Utils.log('创建模型...');
        Utils.log(`配置: embed=${this.config.embedDim}, hidden=${this.config.hiddenDim}, seqLen=${this.config.seqLength}`);

        const model = tf.sequential();

        model.add(tf.layers.embedding({
            inputDim: this.config.vocabSize,
            outputDim: this.config.embedDim,
            inputLength: this.config.seqLength
        }));

        model.add(tf.layers.gru({
            units: this.config.hiddenDim,
            returnSequences: true,
            dropout: 0.1,
            recurrentInitializer: 'glorotNormal'
        }));

        model.add(tf.layers.timeDistributed({
            layer: tf.layers.dense({
                units: this.config.vocabSize,
                activation: 'softmax'
            })
        }));

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

    prepareData(texts) {
        Utils.log('准备训练数据...');
        
        let limitedTexts = texts;
        if (texts.length > this.config.maxDataSize) {
            limitedTexts = this.shuffleArray([...texts]).slice(0, this.config.maxDataSize);
            Utils.log(`数据采样: ${texts.length} → ${limitedTexts.length} 条`);
        }

        const xs = [];
        const ys = [];
        const seqLen = this.config.seqLength;
        let skippedCount = 0;

        for (const text of limitedTexts) {
            const encoded = this.tokenizer.encode(text);
            
            if (encoded.length < 2) {
                skippedCount++;
                continue;
            }

            let seq;
            if (encoded.length > seqLen + 1) {
                seq = encoded.slice(0, seqLen + 1);
            } else if (encoded.length < seqLen + 1) {
                seq = [...encoded];
                while (seq.length < seqLen + 1) {
                    seq.push(0);
                }
            } else {
                seq = encoded;
            }

            const inputSeq = seq.slice(0, seqLen);
            const targetSeq = seq.slice(1, seqLen + 1);

            xs.push(inputSeq);
            ys.push(targetSeq.map(v => [v]));
        }

        Utils.log(`训练样本数: ${xs.length}`);
        if (skippedCount > 0) {
            Utils.log(`跳过过短样本: ${skippedCount}`);
        }

        return {
            xs: tf.tensor2d(xs),
            ys: tf.tensor3d(ys)
        };
    }

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    async train(texts, callbacks = {}) {
        if (this.isTraining) {
            Utils.log('训练已在进行中', 'warning');
            return;
        }

        this.isTraining = true;
        this.shouldStop = false;
        this.trainingData = texts;
        this.history = [];

        const startTime = Date.now();

        try {
            await this.init();
            this.createTokenizer(texts);
            await this.createModel();
            
            const { xs, ys } = this.prepareData(texts);

            Utils.log('开始训练...');
            Utils.log(`预计时间: ${this.estimateTime(xs.shape[0])}`);

            await this.model.fit(xs, ys, {
                epochs: this.config.epochs,
                batchSize: this.config.batchSize,
                validationSplit: 0.1,
                shuffle: true,
                callbacks: {
                    onEpochEnd: (epoch, logs) => {
                        if (this.shouldStop) {
                            this.model.stopTraining = true;
                            return;
                        }

                        const progress = ((epoch + 1) / this.config.epochs) * 100;
                        const elapsed = (Date.now() - startTime) / 1000;
                        const eta = (elapsed / (epoch + 1)) * (this.config.epochs - epoch - 1);

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
                                accuracy: logs.acc,
                                elapsed,
                                eta
                            });
                        }

                        if ((epoch + 1) % 5 === 0 || epoch === 0) {
                            Utils.log(`Epoch ${epoch + 1}/${this.config.epochs} - Loss: ${logs.loss.toFixed(4)} - Acc: ${(logs.acc * 100).toFixed(1)}% - ETA: ${Utils.formatTime(eta)}`);
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

            xs.dispose();
            ys.dispose();

        } catch (error) {
            Utils.log(`训练错误: ${error.message}`, 'error');
            console.error(error);
            if (callbacks.onError) {
                callbacks.onError(error);
            }
        } finally {
            this.isTraining = false;
        }
    }

    estimateTime(sampleCount) {
        const timePerSample = 0.001;
        const totalTime = sampleCount * this.config.epochs * timePerSample / this.config.batchSize;
        return Utils.formatTime(totalTime);
    }

    stop() {
        this.shouldStop = true;
        Utils.log('正在停止训练...', 'warning');
    }

    // 生成文本（修复中文输出）
    async generate(prompt, maxLength = 50, temperature = 0.8) {
        if (!this.model || !this.tokenizer) {
            return '请先训练模型';
        }

        Utils.log(`生成提示: "${prompt}"`);

        let tokens = this.tokenizer.encode(prompt);
        Utils.log(`编码后: [${tokens.slice(0, 10)}...] (长度: ${tokens.length})`);

        if (tokens.length > this.config.seqLength - 1) {
            tokens = tokens.slice(-this.config.seqLength + 1);
        }

        const generated = [];

        for (let i = 0; i < maxLength; i++) {
            const input = [...tokens];
            while (input.length < this.config.seqLength) {
                input.push(0);
            }
            
            const inputSeq = input.slice(0, this.config.seqLength);
            
            const inputTensor = tf.tensor2d([inputSeq]);
            const output = this.model.predict(inputTensor);

            const lastPos = Math.min(tokens.length, this.config.seqLength) - 1;
            const probs = output.slice([0, lastPos, 0], [1, 1, this.config.vocabSize]);

            // 应用温度
            const probsData = await probs.data();
            const scaledProbs = new Float32Array(probsData.length);
            const maxProb = Math.max(...probsData);
            let sum = 0;
            for (let j = 0; j < probsData.length; j++) {
                scaledProbs[j] = Math.exp((probsData[j] - maxProb) / temperature);
                sum += scaledProbs[j];
            }
            for (let j = 0; j < scaledProbs.length; j++) {
                scaledProbs[j] /= sum;
            }

            // 采样
            let nextToken = 0;
            const rand = Math.random();
            let cumProb = 0;
            for (let j = 0; j < scaledProbs.length; j++) {
                cumProb += scaledProbs[j];
                if (rand < cumProb) {
                    nextToken = j;
                    break;
                }
            }

            tokens.push(nextToken);
            generated.push(nextToken);

            inputTensor.dispose();
            output.dispose();
            probs.dispose();

            // 遇到结束符或PAD停止
            if (nextToken === 3 || nextToken === 0) break;
        }

        Utils.log(`生成了 ${generated.length} 个token`);
        
        // 解码
        const result = this.tokenizer.decode(generated);
        Utils.log(`解码结果: "${result}"`);

        return result;
    }

    async save() {
        if (!this.model) return null;
        return {
            config: this.config,
            tokenizer: this.tokenizer.save(),
            history: this.history,
            timestamp: Date.now()
        };
    }

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

// 简单分词器（修复中文支持）
class SimpleTokenizer {
    constructor() {
        this.char2idx = { '<pad>': 0, '<unk>': 1, '<bos>': 2, '<eos>': 3 };
        this.idx2char = { 0: '<pad>', 1: '<unk>', 2: '<bos>', 3: '<eos>' };
    }

    train(texts, vocabSize) {
        const charFreq = {};
        
        // 统计字符频率
        for (const text of texts) {
            if (!text) continue;
            for (const char of text) {
                // 确保正确处理中文字符
                charFreq[char] = (charFreq[char] || 0) + 1;
            }
        }

        // 按频率排序
        const sorted = Object.entries(charFreq).sort((a, b) => b[1] - a[1]);

        // 构建词表
        let idx = 4; // 从4开始，0-3是特殊token
        for (let i = 0; i < Math.min(sorted.length, vocabSize - 4); i++) {
            const char = sorted[i][0];
            this.char2idx[char] = idx;
            this.idx2char[idx] = char;
            idx++;
        }

        console.log(`词表构建完成，共 ${idx} 个token`);
        
        // 验证中文支持
        const chineseChars = Object.keys(this.char2idx).filter(c => /[\u4e00-\u9fa5]/.test(c));
        console.log(`词表包含 ${chineseChars.length} 个中文字符`);
    }

    encode(text) {
        if (!text) return [2, 3]; // BOS, EOS
        
        const tokens = [2]; // BOS
        
        for (const char of text) {
            const idx = this.char2idx[char];
            if (idx !== undefined) {
                tokens.push(idx);
            } else {
                tokens.push(1); // UNK
            }
        }
        
        tokens.push(3); // EOS
        return tokens;
    }

    decode(indices) {
        if (!indices || indices.length === 0) return '';
        
        const chars = [];
        
        for (const idx of indices) {
            // 跳过特殊token
            if (idx <= 3) continue;
            
            const char = this.idx2char[idx];
            if (char && char !== '<unk>') {
                chars.push(char);
            } else if (char === '<unk>') {
                // UNK token，跳过或用占位符
                // chars.push('□'); // 可选：用占位符表示未知字符
            }
        }
        
        return chars.join('');
    }

    size() {
        return Object.keys(this.char2idx).length;
    }

    save() {
        return { 
            char2idx: this.char2idx,
            idx2char: this.idx2char 
        };
    }

    load(data) {
        this.char2idx = data.char2idx;
        this.idx2char = data.idx2char || {};
        
        // 如果没有idx2char，重建它
        if (Object.keys(this.idx2char).length === 0) {
            this.idx2char = {};
            for (const [k, v] of Object.entries(this.char2idx)) {
                this.idx2char[v] = k;
            }
        }
    }
}

window.TianguangTrainer = TianguangTrainer;
window.SimpleTokenizer = SimpleTokenizer;
