import asyncio
from models import AsyncSessionFactory
from repository.milvus_repository import MilvusRepo
from repository.poetry_reposityory import PoetryRepo
from core.milvus import milvus_client
from service.embedding_service import EmbeddingService
from models import engine

async def main():
    client = milvus_client()
    milvus_repo=MilvusRepo(client)

    async with AsyncSessionFactory() as session:

        poetry_repo=PoetryRepo(session)
        poetry_list=await poetry_repo.get_all()
       # poetry_list=poetry_list[:20]
        embed_service = EmbeddingService()

        if client.has_collection("poetry_vectors"):
            client.drop_collection("poetry_vectors")
        milvus_repo.create_collection()
        x=0
        for poetry in poetry_list:
            lines=[]
            for text in poetry.content.split("\n"):
                if text.strip():
                    lines.append(text.strip())

            vectors=embed_service.embed_texts(lines)
            data=[]
            for i,(line,vector) in enumerate(zip(lines,vectors)):

                data.append({
                    "chunk_id":f"{poetry.id}_{i}",
                    "poetry_id":poetry.id,
                    "vector":vector,
                    "chunk_index":i,
                    "text":line,
                    "metadata":{
                        "title":poetry.title,
                        "author":poetry.author,
                        "dynasty":poetry.dynasty,
                        "source":poetry.source
                    }
                })
            milvus_repo.batch_insert(
                collection_name="poetry_vectors",
                data=data
            )
            x+=1
            print(f"成功导入{x}/{len(poetry_list)}")
        print("全部导入完成")
        # query_vector=embed_service.embed_text("明月")
        # result=milvus_repo.search(
        #     collection_name="poetry_vectors",data=[query_vector],limit=10 )
        # print(result,type(result))
    await engine.dispose()


# if __name__ == '__main__':
#已导入全部
#     asyncio.run(main())






