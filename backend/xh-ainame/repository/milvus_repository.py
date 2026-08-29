from typing import Dict

from pymilvus import FieldSchema,CollectionSchema,MilvusClient,DataType


class MilvusRepo:
    def __init__(self, client):
        self.client = client


    def create_collection(self):
        # 第1步：创建空的 schema（相当于一张空白表）
        schema = self.client.create_schema()

        schema.add_field(field_name="chunk_id",datatype=DataType.VARCHAR,max_length=64,is_primary=True)
        schema.add_field(field_name="poetry_id",datatype=DataType.INT64)
        schema.add_field(field_name="chunk_index",datatype=DataType.INT64)
        schema.add_field(field_name="text",datatype=DataType.VARCHAR,max_length=512)
        schema.add_field(field_name="vector",datatype=DataType.FLOAT_VECTOR,dim=768)
        schema.add_field(field_name="metadata",datatype=DataType.JSON)

        # 第3步：给 vector 字段建索引（向量字段必须有索引才能搜索）
        index_params=self.client.prepare_index_params()
        index_params.add_index(field_name="vector",index_type="HNSW",metric_type="COSINE")

        # 第4步：把"表"和"索引"一起交给 create_collection
        self.client.create_collection(
            collection_name="poetry_vectors",
            schema=schema,
            index_params=index_params
        )

    def \
            batch_insert(self, collection_name,data) ->Dict:
        result=self.client.insert(collection_name=collection_name,data=data)
        return result


    def search(self,collection_name, data,limit):
        result=self.client.search(
            collection_name=collection_name,data=data,limit=limit,
            output_fields=["text","metadata"]
        )
        return result
