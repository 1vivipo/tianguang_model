"""
天光AI - 模型导出脚本
导出为ONNX格式，可在各种平台部署
"""

import os
import sys
import argparse

import torch
import torch.onnx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from model import TianguangModel
from tokenizer import TianguangTokenizer


def export_onnx(model_path: str, output_path: str, seq_length: int = 64):
    """导出为ONNX格式"""
    
    print(f"加载模型: {model_path}")
    model = TianguangModel.from_pretrained(model_path)
    model.eval()
    
    # 创建示例输入
    dummy_input = torch.randint(0, model.config.vocab_size, (1, seq_length))
    
    # 导出
    os.makedirs(output_path, exist_ok=True)
    onnx_path = os.path.join(output_path, "model.onnx")
    
    print(f"导出ONNX模型: {onnx_path}")
    
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        input_names=["input_ids"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch", 1: "sequence"},
            "logits": {0: "batch", 1: "sequence"}
        },
        opset_version=14
    )
    
    print("导出完成！")
    
    # 验证
    print("验证ONNX模型...")
    import onnx
    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)
    print("验证通过！")


def export_torchscript(model_path: str, output_path: str, seq_length: int = 64):
    """导出为TorchScript格式"""
    
    print(f"加载模型: {model_path}")
    model = TianguangModel.from_pretrained(model_path)
    model.eval()
    
    # 创建示例输入
    dummy_input = torch.randint(0, model.config.vocab_size, (1, seq_length))
    
    # 导出
    os.makedirs(output_path, exist_ok=True)
    script_path = os.path.join(output_path, "model.pt")
    
    print(f"导出TorchScript模型: {script_path}")
    
    traced_model = torch.jit.trace(model, dummy_input)
    traced_model.save(script_path)
    
    print("导出完成！")


def export_quantized(model_path: str, output_path: str):
    """导出量化模型"""
    
    print(f"加载模型: {model_path}")
    model = TianguangModel.from_pretrained(model_path)
    model.eval()
    
    # 动态量化
    print("量化模型...")
    quantized_model = torch.quantization.quantize_dynamic(
        model,
        {torch.nn.Linear},
        dtype=torch.qint8
    )
    
    # 保存
    os.makedirs(output_path, exist_ok=True)
    quant_path = os.path.join(output_path, "model_quantized.pt")
    
    print(f"保存量化模型: {quant_path}")
    torch.save(quantized_model.state_dict(), quant_path)
    
    # 比较大小
    original_size = sum(p.numel() * p.element_size() for p in model.parameters())
    quantized_size = sum(p.numel() * p.element_size() for p in quantized_model.parameters())
    
    print(f"原始模型大小: {original_size / 1024 / 1024:.2f} MB")
    print(f"量化模型大小: {quantized_size / 1024 / 1024:.2f} MB")
    print(f"压缩比: {original_size / quantized_size:.2f}x")


def main():
    parser = argparse.ArgumentParser(description="天光AI模型导出脚本")
    parser.add_argument("--model", type=str, default="models/tianguang_model", help="模型路径")
    parser.add_argument("--output", type=str, default="models/exported", help="输出路径")
    parser.add_argument("--format", type=str, default="onnx", choices=["onnx", "torchscript", "quantized"])
    parser.add_argument("--seq_length", type=int, default=64, help="序列长度")
    
    args = parser.parse_args()
    
    if args.format == "onnx":
        export_onnx(args.model, args.output, args.seq_length)
    elif args.format == "torchscript":
        export_torchscript(args.model, args.output, args.seq_length)
    elif args.format == "quantized":
        export_quantized(args.model, args.output)


if __name__ == "__main__":
    main()
