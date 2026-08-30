import asyncio
import json
from zhconv import convert
from models.poetry import Poetry
from typing import List
from repository.poetry_reposityory import PoetryRepo
from models import AsyncSessionFactory,engine
import hashlib
from pathlib import Path


def read_json(filename: str) -> List[dict]:
    with open(filename, 'r',encoding="utf-8") as f:
        return json.load(f)

#唐诗
def process_item(item: dict,source:str,dynasty:str) ->dict:

    poetry = {
        "source_id":str(item['id']),
        "source":source,
        "dynasty":dynasty,
        "content":convert("\n".join(item["paragraphs"]),"zh-cn"),
        "author":convert(item['author'],"zh-cn"),
        "title":convert(item['title'],"zh-cn")
    }
    return poetry

#宋词
def process_item_song(item: dict,source:str,dynasty:str) ->dict:
    content = convert("\n".join(item["paragraphs"]),"zh-cn")
    poetry = {
        "source_id":hashlib.md5(content.encode()).hexdigest(),
        "source":source,
        "dynasty":dynasty,
        "content":content,
        "author":convert(item['author'],"zh-cn"),
        "title":convert(item['rhythmic'],"zh-cn")
    }
    return poetry

#诗经
def process_item_shijing(item: dict,source:str,dynasty:str) ->dict:
    content = convert("\n".join(item["content"]),"zh-cn")
    poetry = {
        "source_id":hashlib.md5(content.encode()).hexdigest(),
        "source":source,
        "dynasty":dynasty,
        "content":content,
        "author":"佚名",
        "title":convert(item['title'],"zh-cn")
    }
    return poetry


def create_poetry(item: dict) -> Poetry:
    poetry = Poetry(**item)
    return poetry

async def main():
    success=0
    duplicate=0
    failed=0
    batch_list = []

    async with AsyncSessionFactory() as session:
        poetry_data = Path(__file__).resolve().parent.parent / "data" / "poetry" / "ci.song.11000.json"
    raw_data = read_json(str(poetry_data))
        poetry_repo=PoetryRepo(session)

        for i, item in enumerate(raw_data):
            try:
                #导入唐诗(source="全唐诗",dynasty="唐")
                #poetry_dict=process_item(item,source="全唐诗",dynasty="唐")

                #导入宋词(source="宋词",dynasty="宋")
                poetry_dict=process_item_song(item,source="宋词",dynasty="宋")

                #导入诗经(source="诗经",dynasty="春秋中期")
                # poetry_dict=process_item_shijing(item,source="诗经",dynasty="春秋中期")

                result=await poetry_repo.poetry_is_exist(source=poetry_dict.get("source"),source_id=poetry_dict.get("source_id"))

                if result:
                    duplicate+=1
                    continue


                batch=create_poetry(poetry_dict)
                batch_list.append(batch)
                if len(batch_list)>=100:
                    await poetry_repo.batch_insert(batch_list)
                    await session.commit()
                    success+=len(batch_list)
                    batch_list.clear()

            except Exception as e:
                failed+=1
                print(f"第 {i + 1} 条失败: {e}")

            if i % 100 == 0:
                print(f"已经处理{i+1}/{len(raw_data)}")

        if batch_list :
            await poetry_repo.batch_insert(batch_list)
            await session.commit()
            success+=len(batch_list)
            batch_list.clear()

    await session.close()
    await engine.dispose()


    print(f"成功了{success}条\n失败了{failed}\n重复了{duplicate}")



if __name__ == '__main__':

    asyncio.run(main())





