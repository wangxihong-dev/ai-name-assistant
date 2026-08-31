import asyncio
from models import AsyncSessionFactory
from repository.milvus_repository import MilvusRepo
from repository.poetry_reposityory import PoetryRepo
from core.milvus import milvus_client
from service.embedding_service import EmbeddingService
from models import engine


async def main():
    # ========== 1. 连接 Milvus 并创建数据访问对象 ==========
    # milvus_client() 从 core/milvus.py 读取环境变量 MILVUS_URI
    # 本地默认 localhost:19530，容器内由 docker-compose 注入 http://milvus:19530
    client = milvus_client()
    milvus_repo = MilvusRepo(client)

    async with AsyncSessionFactory() as session:
        # ========== 2. 从 MySQL 读取全部诗词 ==========
        poetry_repo = PoetryRepo(session)
        poetry_list = await poetry_repo.get_all()
        # 调试时可先只导前 20 首验证流程：
        # poetry_list = poetry_list[:20]

        # ========== 3. 加载 BGE 向量模型（只在第一次实例化时真正加载） ==========
        embed_service = EmbeddingService()

        # ========== 4. 重建 Milvus 集合（保证从头开始，数据干净） ==========
        # 脚本可反复运行：每次都先删旧集合，再建新集合
        if client.has_collection("poetry_vectors"):
            client.drop_collection("poetry_vectors")
        milvus_repo.create_collection()

        # ========== 5. 逐首诗词：切行 -> 向量化 -> 插入 Milvus ==========
        success = 0      # 成功导入的诗词数
        skipped = 0      # 因单首出错被跳过的诗词数
        total = len(poetry_list)

        for poetry in poetry_list:
            try:
                # 5.1 把一首诗按行切分，去掉空行
                #     content 在导入时用 "\n" 拼接，所以按行切 = 一句/一联一个 chunk
                lines = []
                for text in poetry.content.split("\n"):
                    if text.strip():
                        lines.append(text.strip())

                # 5.2 这一首的所有行一次性批量生成向量（比逐行快）
                vectors = embed_service.embed_texts(lines)

                # 5.3 组装成 Milvus 实体：一行 = 一个 chunk，字段与 Collection 严格对应
                data = []
                for i, (line, vector) in enumerate(zip(lines, vectors)):
                    data.append({
                        "chunk_id": f"{poetry.id}_{i}",      # 主键：诗id_行号，保证唯一
                        "poetry_id": poetry.id,              # 关联 MySQL poetry.id
                        "vector": vector,                    # 768 维向量
                        "chunk_index": i,                    # 第几行
                        "text": line,                        # 诗句原文
                        "metadata": {                        # 检索结果直接可用
                            "title": poetry.title,
                            "author": poetry.author,
                            "dynasty": poetry.dynasty,
                            "source": poetry.source,
                        },
                    })

                # 5.4 这一首的全部 chunk 一次插入
                # Milvus 建索引时可能短暂无响应导致"连接失败"，
                # 所以失败重试 3 次（间隔 5 秒），仍失败才交给外层跳过
                for attempt in range(3):
                    try:
                        milvus_repo.batch_insert(
                            collection_name="poetry_vectors",
                            data=data
                        )
                        break  # 插入成功，跳出重试循环
                    except Exception as e:
                        if attempt == 2:  # 第 3 次仍失败，抛出给外层 try 处理
                            raise
                        print(f"  插入失败，5 秒后重试 {attempt + 1}/3：{e}", flush=True)
                        await asyncio.sleep(5)

                success += 1
                print(f"成功导入 {success}/{total}", flush=True)

            except Exception as e:
                # ========== 容错：单首出错只跳过，不中断整个导入 ==========
                # 之前没有这层保护：某一首诗出错（数据异常/连接抖动）会让整个脚本退出，
                # 导致白跑几十分钟。现在跳过并记录，继续下一首。
                skipped += 1
                print(f"[跳过] 第 {success + skipped} 首 诗词ID={poetry.id} 标题={poetry.title} 原因: {e}", flush=True)

        # ========== 6. 汇总结果 ==========
        print(f"全部完成：成功 {success}，跳过 {skipped}，总 {total}", flush=True)

        # 可选的检索验证（临时调试用）：
        # query_vector = embed_service.embed_text("明月")
        # result = milvus_repo.search(
        #     collection_name="poetry_vectors",
        #     data=[query_vector],
        #     limit=10,
        # )
        # print(result)

    # 关闭数据库连接池（脚本结束前释放资源）
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

