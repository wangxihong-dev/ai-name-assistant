import os
from pymilvus import MilvusClient

# Milvus 地址：默认本地；部署时通过环境变量 MILVUS_URI 指向容器内的 milvus 服务
MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")

# 超时时间（秒）：Milvus 在 2 核小机器上建索引时会很忙，
# 默认超时太短会被误报"连接失败"，所以放宽到 120 秒
MILVUS_TIMEOUT = int(os.getenv("MILVUS_TIMEOUT", "120"))


def milvus_client():
    client = MilvusClient(
        uri=MILVUS_URI,
        timeout=MILVUS_TIMEOUT,
    )
    return client
