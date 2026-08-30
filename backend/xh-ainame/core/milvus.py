import os
from pymilvus import MilvusClient

# Milvus 地址：默认本地；部署时通过环境变量 MILVUS_URI 指向容器内的 milvus 服务
MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")


def milvus_client():
    client = MilvusClient(
        uri=MILVUS_URI
    )
    return client
