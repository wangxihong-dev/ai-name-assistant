# =============================================
# 后端镜像：FastAPI + 依赖 + BGE 向量模型
# =============================================
FROM python:3.13-slim

WORKDIR /app

# 国内加速：PyPI 走清华镜像
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 第一步只复制依赖清单并安装（利用 Docker 层缓存：改代码不会重复装依赖）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 预下载 BGE 向量模型（构建时下载一次并打进镜像，运行时离线使用，不依赖外网）
ENV HF_ENDPOINT=https://hf-mirror.com
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-base-zh-v1.5')"
ENV HF_HUB_OFFLINE=1

# 复制后端代码
COPY . .

EXPOSE 8000

# 容器内监听所有网卡，供 Nginx 转发
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
