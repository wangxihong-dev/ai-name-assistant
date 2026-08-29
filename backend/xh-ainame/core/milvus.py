from pymilvus import MilvusClient


def milvus_client() :
    client = MilvusClient(
        uri="http://localhost:19530"
    )
    return client