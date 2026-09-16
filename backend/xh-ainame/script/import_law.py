import json
from models.law_clause import LawClause
from models.law_version import LawVersion
from models import engine,AsyncSessionFactory
from repository.law_repository import LawRepo
import asyncio
from datetime import date
from pathlib import Path

DATA_DIR=Path(__file__).resolve().parent.parent  /"data"/"law"
files=sorted(DATA_DIR.glob("*.json"))
print(f"目录 {DATA_DIR} 找到 {len(files)} 个文件")
if not files:
    raise SystemExit("一个文件都没找到，路径错了")


def read_json(file_name) -> dict:
    with open(file_name,"r",encoding="utf-8") as f:
        return json.load(f)

def to_date(value:str|None) -> date|None:
    if value is None:
        return None
    return date.fromisoformat(value)

async def import_law_clause():
    async with AsyncSessionFactory() as session:
        law_repo=LawRepo(session)
        count = 0
        async with session.begin():

            for file in list(files):
                law_dict=read_json(file)
                law_exist=await law_repo.law_is_exist(law_dict["law_name"],law_dict["version_name"])
                if not law_exist :
                    version=await law_repo.insert_law_version(LawVersion(
                        law_name=law_dict["law_name"],
                        version_name=law_dict["version_name"]   ,
                        enforcement_date=to_date(law_dict["enforcement_date"]),
                        expiry_date=to_date(law_dict["expiry_date"])
                    ))
                else:
                    print("已存在，跳过")
                    version=await law_repo.get_law_version(law_dict["law_name"],law_dict["version_name"])

                for i,item in enumerate(law_dict["clauses"],1):
                    await law_repo.insert_law_clause(LawClause(
                        version_id=version.id,
                        clause_number=item["clause_number"],
                        clause_original=item["clause_original"],
                        risk_grade=item["risk_grade"],
                    ))
                    count += 1

        print(f"条款 {count} 条，已提交")

    await engine.dispose()



asyncio.run(import_law_clause())