"""
天光AI - API服务
将模型部署为REST API
"""

import os
import sys
import json
import time
from typing import Optional

import torch

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from model import TianguangModel
from tokenizer import TianguangTokenizer

# FastAPI
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("请安装FastAPI: pip install fastapi uvicorn")
    sys.exit(1)


# 请求模型
class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 100
    temperature: float = 0.8
    top_k: int = 50
    top_p: float = 0.9


class GenerateResponse(BaseModel):
    text: str
    prompt: str
    generated_tokens: int
    time_ms: float


# 全局变量
model = None
tokenizer = None
device = None


def load_model(model_path: str):
    """加载模型"""
    global model, tokenizer, device
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    print(f"加载模型: {model_path}")
    model = TianguangModel.from_pretrained(model_path)
    model = model.to(device)
    model.eval()
    
    tokenizer = TianguangTokenizer.from_pretrained(model_path)
    
    print("模型加载完成！")


# 创建应用
app = FastAPI(
    title="天光AI API",
    description="天光AI语言模型API服务",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """启动时加载模型"""
    model_path = os.environ.get("MODEL_PATH", "models/tianguang_model")
    load_model(model_path)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "天光AI API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """生成文本"""
    global model, tokenizer, device
    
    if model is None:
        raise HTTPException(status_code=503, detail="模型未加载")
    
    start_time = time.time()
    
    # 编码
    input_ids = torch.tensor([tokenizer.encode(request.prompt, add_bos=True, add_eos=False)]).to(device)
    
    # 生成
    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p,
            do_sample=True
        )
    
    # 解码
    output_text = tokenizer.decode(output_ids[0].tolist(), skip_special_tokens=True)
    
    # 计算时间
    elapsed_ms = (time.time() - start_time) * 1000
    
    return GenerateResponse(
        text=output_text,
        prompt=request.prompt,
        generated_tokens=output_ids.shape[1] - input_ids.shape[1],
        time_ms=elapsed_ms
    )


@app.post("/chat")
async def chat(request: GenerateRequest):
    """对话接口"""
    response = await generate(request)
    return {
        "response": response.text,
        "time_ms": response.time_ms
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="天光AI API服务")
    parser.add_argument("--model", type=str, default="models/tianguang_model", help="模型路径")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="主机")
    parser.add_argument("--port", type=int, default=8000, help="端口")
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ["MODEL_PATH"] = args.model
    
    print(f"启动API服务: http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
