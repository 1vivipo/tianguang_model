FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY app.py .

# 环境变量
ENV PORT=8080
ENV API_KEY=sk-tianguang-2024-metabrain-v31
ENV API_SECRET=tianguang-secret-key-2024
ENV MODEL_NAME=metabrain-v3.1

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "2"]
