
from core.milvus import milvus_client
from service.embedding_service import EmbeddingService
from repository.milvus_repository import MilvusRepo

def test_milvus():
    client = milvus_client()

    milvus_repo = MilvusRepo(client)
    embed_service=EmbeddingService()
    vector=embed_service.embed_text("聪慧")

    result=milvus_repo.search(collection_name="poetry_vectors",data=[vector],limit=5)

    #print(result[0])
    #for i, hit in enumerate(result[0],1):
        #print(hit["entity"])
        #print(hit["entity"]["metadata"]["title"])


if __name__=="__main__":
    test_milvus()
