import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
from sentence_transformers import SentenceTransformer
from typing import List


class EmbeddingService:
    _model = None

    def __init__(self):
        if self._model is None:
            print("运行中请等侯。。。")
            EmbeddingService._model=SentenceTransformer("BAAI/bge-base-zh-v1.5")
            print("模型加载成功")



    def embed_text(self, text:str) -> List[float]:
        vector=self._model.encode(text,normalize_embeddings=True).tolist()
        return vector


    def embed_texts(self, texts:List[str]) -> List[List[float]]:
        vectors=self._model.encode(texts,normalize_embeddings=True).tolist()
        return vectors