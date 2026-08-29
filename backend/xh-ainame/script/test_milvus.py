
from core.milvus import milvus_client

from repository.milvus_repository import MilvusRepo

def test_milvus():
    client = milvus_client()

    milvus_repo = MilvusRepo(client)

    if client.has_collection(collection_name="poetry_vectors"):
        client.drop_collection(collection_name="poetry_vectors")
        print("之前存在，已删除")

    milvus_repo.create_collection()
    print("已创建，collection")
    milvus_repo.batch_insert(
        collection_name="poetry_vectors",
        data=[
            {
                "chunk_id":"1001_0",
                "poetry_id":1001,
                "vector":[0.1]*384 + [0.9]*384,
                "chunk_index":0,
                "text":"我是1古诗",
                "metadata":{
                    "title":"王"
                }
            },
            {
                "chunk_id":"1002_1",
                "poetry_id":1002,
                "vector":[0.91]*768,
                "chunk_index":1,
                "text":"我是2古诗",
                "metadata":{
                    "title":"鸿"
                }

            }
        ]
    )
    print("插入成功")
    result=milvus_repo.search(collection_name="poetry_vectors",data=[[0.31]*768],limit=2)
    print(result)

if __name__=="__main__":
    test_milvus()
