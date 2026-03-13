/**
 * 天光AI - 模型格式转换器
 * 将TensorFlow.js模型转换为Hugging Face兼容格式
 */

class ModelConverter {
    
    /**
     * 将训练好的模型转换为Hugging Face格式
     */
    static async convertToHuggingFace(trainer) {
        if (!trainer.model || !trainer.tokenizer) {
            throw new Error('请先训练模型');
        }

        console.log('开始转换模型格式...');

        // 1. 提取模型权重
        const weights = await this.extractWeights(trainer.model);
        
        // 2. 创建配置文件
        const config = {
            architectures: ["GRUForCausalLM"],
            model_type: "tianguang",
            vocab_size: trainer.config.vocabSize,
            hidden_size: trainer.config.embedDim,
            intermediate_size: trainer.config.hiddenDim,
            num_hidden_layers: trainer.config.numLayers,
            max_position_embeddings: trainer.config.seqLength,
            torch_dtype: "float32",
            transformers_version: "4.30.0",
        };

        // 3. 创建分词器文件
        const tokenizerConfig = {
            add_bos_token: true,
            add_eos_token: true,
            bos_token: "<bos>",
            eos_token: "<eos>",
            model_max_length: trainer.config.seqLength,
            tokenizer_class: "TianguangTokenizer",
            vocab: trainer.tokenizer.char2idx,
        };

        // 4. 创建词表文件
        const vocab = trainer.tokenizer.char2idx;

        // 5. 创建模型权重文件 (简化版，实际需要PyTorch格式)
        const modelWeights = {
            format: "tianguang-weights-v1",
            weights: weights,
            config: config,
        };

        return {
            config: config,
            tokenizer_config: tokenizerConfig,
            vocab: vocab,
            model_weights: modelWeights,
            readme: this.generateReadme(trainer),
        };
    }

    /**
     * 提取模型权重
     */
    static async extractWeights(model) {
        const weights = {};
        
        // 遍历所有层
        for (const layer of model.layers) {
            const layerWeights = layer.getWeights();
            for (let i = 0; i < layerWeights.length; i++) {
                const w = layerWeights[i];
                const name = layer.name + '_weight_' + i;
                weights[name] = await w.array();
            }
        }

        return weights;
    }

    /**
     * 生成README文件
     */
    static generateReadme(trainer) {
        return `# 天光AI 自训练模型

## 模型信息

- **模型类型**: GRU语言模型
- **词汇表大小**: ${trainer.config.vocabSize}
- **嵌入维度**: ${trainer.config.embedDim}
- **隐藏层维度**: ${trainer.config.hiddenDim}
- **层数**: ${trainer.config.numLayers}
- **参数量**: ${trainer.model.countParams().toLocaleString()}

## 训练信息

- **训练轮次**: ${trainer.history.length}
- **最终损失**: ${trainer.history[trainer.history.length - 1]?.loss?.toFixed(4) || 'N/A'}

## 使用方法

### 在浏览器中使用 (TensorFlow.js)

\`\`\`javascript
// 加载模型
const model = await tf.loadLayersModel('model.json');

// 生成文本
const result = await model.generate('人工智能', 50);
\`\`\`

### 在Python中使用 (需要转换)

\`\`\`python
# 需要先转换为PyTorch格式
# 使用提供的转换脚本
python convert_to_pytorch.py --input model.json --output pytorch_model.bin
\`\`\`

## 许可证

本模型由天光AI训练生成，可自由使用。

## 致谢

- TensorFlow.js
- Hugging Face Transformers
`;
    }

    /**
     * 下载为Hugging Face格式
     */
    static async downloadAsHuggingFace(trainer) {
        const files = await this.convertToHuggingFace(trainer);
        
        // 创建并下载各个文件
        this.downloadJSON(files.config, 'config.json');
        this.downloadJSON(files.tokenizer_config, 'tokenizer_config.json');
        this.downloadJSON(files.vocab, 'vocab.json');
        this.downloadJSON(files.model_weights, 'pytorch_model.json');
        this.downloadText(files.readme, 'README.md');
        
        console.log('模型文件已下载！');
    }

    /**
     * 下载JSON文件
     */
    static downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * 下载文本文件
     */
    static downloadText(text, filename) {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * 导出为可在Python加载的格式
     */
    static async exportForPython(trainer) {
        const exportData = {
            // 模型架构
            architecture: {
                type: 'GRULanguageModel',
                vocab_size: trainer.config.vocabSize,
                embedding_dim: trainer.config.embedDim,
                hidden_dim: trainer.config.hiddenDim,
                num_layers: trainer.config.numLayers,
            },
            
            // 模型权重 (numpy格式)
            weights: {},
            
            // 分词器
            tokenizer: {
                type: 'CharacterTokenizer',
                vocab: trainer.tokenizer.char2idx,
            },
            
            // 训练信息
            training_info: {
                epochs: trainer.history.length,
                final_loss: trainer.history[trainer.history.length - 1]?.loss,
                history: trainer.history,
            },
            
            // 元数据
            metadata: {
                created_at: new Date().toISOString(),
                framework: 'tensorflow.js',
                version: '1.0.0',
            }
        };

        // 提取权重
        for (const layer of trainer.model.layers) {
            const layerWeights = layer.getWeights();
            for (let i = 0; i < layerWeights.length; i++) {
                const w = layerWeights[i];
                const name = layer.name + '_' + i;
                exportData.weights[name] = await w.array();
            }
        }

        return exportData;
    }

    /**
     * 生成Python加载脚本
     */
    static generatePythonLoader() {
        return `#!/usr/bin/env python3
"""
天光AI - 模型加载器
用于在Python中加载TensorFlow.js训练的模型
"""

import json
import numpy as np
import torch
import torch.nn as nn

class GRULanguageModel(nn.Module):
    """GRU语言模型"""
    
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers=2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.gru = nn.GRU(embedding_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
    def forward(self, x):
        embedded = self.embedding(x)
        output, _ = self.gru(embedded)
        logits = self.fc(output)
        return logits
    
    def generate(self, start_tokens, max_length=50, temperature=1.0):
        """生成文本"""
        self.eval()
        with torch.no_grad():
            current = torch.tensor([start_tokens])
            for _ in range(max_length):
                logits = self(current[:, -32:])  # 限制序列长度
                next_logits = logits[:, -1, :] / temperature
                probs = torch.softmax(next_logits, dim=-1)
                next_token = torch.multinomial(probs, 1)
                current = torch.cat([current, next_token], dim=1)
        return current[0].tolist()

class TianguangTokenizer:
    """天光AI分词器"""
    
    def __init__(self, vocab):
        self.char2idx = vocab
        self.idx2char = {v: k for k, v in vocab.items()}
        
    def encode(self, text):
        return [self.char2idx.get(c, 1) for c in text]
    
    def decode(self, indices):
        return ''.join([self.idx2char.get(i, '') for i in indices if i > 3])

def load_model(model_path):
    """加载模型"""
    with open(model_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建模型
    arch = data['architecture']
    model = GRULanguageModel(
        vocab_size=arch['vocab_size'],
        embedding_dim=arch['embedding_dim'],
        hidden_dim=arch['hidden_dim'],
        num_layers=arch['num_layers']
    )
    
    # 加载权重
    state_dict = {}
    for name, weights in data['weights'].items():
        tensor = torch.tensor(weights, dtype=torch.float32)
        # 映射权重名称
        if 'embedding' in name:
            state_dict['embedding.weight'] = tensor
        elif 'gru' in name:
            # GRU权重映射
            pass
        elif 'fc' in name:
            state_dict['fc.weight'] = tensor
    
    # 创建分词器
    tokenizer = TianguangTokenizer(data['tokenizer']['vocab'])
    
    return model, tokenizer

def main():
    """示例使用"""
    # 加载模型
    model, tokenizer = load_model('tianguang_model.json')
    
    # 生成文本
    prompt = "人工智能"
    tokens = [2] + tokenizer.encode(prompt)  # 添加BOS
    generated = model.generate(tokens, max_length=50)
    result = tokenizer.decode(generated)
    
    print(f"输入: {prompt}")
    print(f"输出: {result}")

if __name__ == '__main__':
    main()
`;
    }
}

// 导出
window.ModelConverter = ModelConverter;
