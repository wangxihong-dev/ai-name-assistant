import json
from models.forbidden_word import ForbiddenWord,WordKindClause
from models import engine,AsyncSessionFactory
from repository.forbidden_word_repo import ForbiddenWordRepo
import asyncio
from pathlib import Path
from datetime import date
from repository.law_repository import LawRepo

DATA_DIR=Path(__file__).resolve().parent.parent  /"data"/"forbidden_word"
files=sorted(DATA_DIR.glob("*.json"))
print(f"目录 {DATA_DIR} 找到 {len(files)} 个文件")
if not files:
    raise SystemExit("一个文件都没找到，路径错了")


def read_json(file_name) -> dict:
    with open(file_name,"r",encoding="utf-8") as f:
        return json.load(f)


async def import_forbidden_words():
    async with AsyncSessionFactory() as session:
        forbidden_repo = ForbiddenWordRepo(session)
        count = 0
        async with session.begin():

            for file in list(files):
                forbidden_dict=read_json(file)
                forbidden_list=forbidden_dict["forbidden_word"]
                for item in forbidden_list:
                    forbidden_exist=await forbidden_repo.forbidden_is_exists(item["word"],item["word_kind"])
                    if not forbidden_exist:
                        forbidden=await forbidden_repo.insert_forbidden_word(ForbiddenWord(
                            word=item["word"],
                            word_kind=item["word_kind"],
                        ))
                        count += 1
                        print(f'词汇：{item["word"]} 禁用种类：{item["word_kind"]}保存成功')
                    else:
                        print(f"词汇：{item["word"]} 禁用种类：{item["word_kind"]}已存在，跳过")


        print(f"条款 {count} 条，已提交")

    await engine.dispose()


async def import_word_kind_clause():
    async with AsyncSessionFactory() as session:
        word_kind_repo=ForbiddenWordRepo(session)
        law_repo=LawRepo(session)
        count = 0
        async with session.begin():
            for file in list(files):
                wordclause_dict=read_json(file)
                wordclause_list=wordclause_dict["word_kind_clause"][0]

                version=await law_repo.get_law_version(wordclause_list["version_name"],wordclause_list["law_name"])
                if not version:
                    raise SystemExit(f"law_version 表里查不到法律：law_name={wordclause_list['law_name']!r},"
                                     f"版本={wordclause_list['version_name']!r}")

                for item in wordclause_list["kinds"]:
                    wordclause_exist=await word_kind_repo.word_kind_is_exists(item["word_kind"],version.id)
                    if not wordclause_exist:
                        clause=await law_repo.get_law_clause(version.id,item["clause_number"])
                        if not clause:
                            raise SystemExit(f"law_clause 表里查不到条款：clause_number={item['clause_number']!r}"
                                             f"（version_id={version.id}）")
                        wordclause=await word_kind_repo.insert_word_kind_clause(WordKindClause(
                            word_kind=item["word_kind"],
                            version_id=version.id,
                            clause_id=clause.id,
                        ))
                        print(f"{item['word_kind']}保存成功")
                        count += 1
                    else:
                        print(f"禁用种类：{item["word_kind"]}已存在，跳过")
        print(f"条款 {count} 条，已提交")
    await engine.dispose()


async def verify_forbidden_words():
    async with AsyncSessionFactory() as session:
        forbidden_repo=ForbiddenWordRepo(session)
        law_repo=LawRepo(session)

        today = date.today()
        version=await law_repo.get_law_version_by_date(today)
        if not version:
            raise SystemExit("数据库没有该日期的version对象")

        forbidden_list=await forbidden_repo.get_all_forbidden_words()

        word_kind_clause_list=await forbidden_repo.get_all_wordkindsclause(version_id=version.id)
        kinds_a={w.word_kind for w in forbidden_list}
        kinds_b={w.word_kind for w in word_kind_clause_list}

        missing = kinds_a - kinds_b
        if missing:
            raise SystemExit(f"以下类别在映射表里没有对应行：{[repr(k) for k in sorted(missing)]}")
        print(f"校验通过：{len(kinds_a)} 个类别全部有映射")
        print(f"生效时间:{version.enforcement_date} 失效时间:{version.expiry_date}  今日时间:{date.today()}")



    await engine.dispose()

asyncio.run(import_word_kind_clause())
asyncio.run(import_forbidden_words())
asyncio.run(verify_forbidden_words())
