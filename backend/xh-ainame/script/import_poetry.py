import asyncio
import json
import hashlib
from pathlib import Path
from typing import List, Tuple

from zhconv import convert
from models import AsyncSessionFactory, engine
from models.poetry import Poetry
from repository.poetry_reposityory import PoetryRepo

# 数据目录：脚本在 script/ 下，向上两级到项目根，再进 data/poetry
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "poetry"

# 文件名 → (来源, 朝代)
FILE_META: dict[str, Tuple[str, str]] = {
    "唐诗三百首.json": ("全唐诗", "唐"),
    "ci.song.11000.json": ("宋词", "宋"),
    "poet.song.1000.json": ("宋诗", "宋"),
    "poet.song.10000.json": ("宋诗", "宋"),
    "shijing.json": ("诗经", "先秦"),
    # 新增文件放这里即可，例如：
    # "ci.song.12000.json": ("宋词", "宋"),
}


def read_json(filename: str) -> List[dict]:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def process_item(item: dict, source: str, dynasty: str) -> dict:
    """统一格式识别：
    - 有 rhythmic → 宋词（无 id，正文 hash 当 source_id，词牌当标题）
    - 有 content 数组（诗经）→ 无作者，填"佚名"
    - 其他（唐诗/宋诗）→ 有 id/title/author
    """
    paragraphs = item.get("paragraphs") or item.get("content") or []
    content = convert("\n".join(paragraphs), "zh-cn")

    if "rhythmic" in item:
        # 宋词
        title = convert(item["rhythmic"], "zh-cn")
        author = convert(item["author"], "zh-cn")
        source_id = hashlib.md5(content.encode()).hexdigest()
    elif "content" in item and "paragraphs" not in item:
        # 诗经
        title = convert(item["title"], "zh-cn")
        author = "佚名"
        source_id = hashlib.md5(content.encode()).hexdigest()
    else:
        # 唐诗 / 宋诗
        title = convert(item["title"], "zh-cn")
        author = convert(item["author"], "zh-cn")
        source_id = str(item["id"])

    return {
        "source_id": source_id,
        "source": source,
        "dynasty": dynasty,
        "content": content,
        "author": author,
        "title": title,
    }


def create_poetry(item: dict) -> Poetry:
    return Poetry(**item)


async def import_file(repo: PoetryRepo, path: Path, source: str, dynasty: str) -> Tuple[int, int, int]:
    """导入单个文件，返回 (成功, 重复, 失败)"""
    success = 0
    duplicate = 0
    failed = 0
    batch_list = []
    raw_data = read_json(str(path))

    for i, item in enumerate(raw_data):
        try:
            poetry_dict = process_item(item, source, dynasty)
            result = await repo.poetry_is_exist(
                source=poetry_dict["source"],
                source_id=poetry_dict["source_id"],
            )
            if result:
                duplicate += 1
                continue

            batch_list.append(create_poetry(poetry_dict))
            if len(batch_list) >= 100:
                await repo.batch_insert(batch_list)
                await repo.session.commit()
                success += len(batch_list)
                batch_list.clear()
        except Exception as e:
            failed += 1
            print(f"  第 {i + 1} 条失败: {e}")

        if (i + 1) % 500 == 0:
            print(f"  已处理 {i + 1}/{len(raw_data)}")

    if batch_list:
        await repo.batch_insert(batch_list)
        await repo.session.commit()
        success += len(batch_list)
        batch_list.clear()

    return success, duplicate, failed


async def main():
    async with AsyncSessionFactory() as session:
        poetry_repo = PoetryRepo(session)

        # 只处理 data/poetry 下 .json，且 FILE_META 里登记过的
        total_success = total_duplicate = total_failed = 0
        for path in sorted(DATA_DIR.glob("*.json")):
            meta = FILE_META.get(path.name)
            if meta is None:
                print(f"跳过未登记文件: {path.name}")
                continue

            source, dynasty = meta
            print(f"开始导入: {path.name}（来源={source}，朝代={dynasty}）")
            success, duplicate, failed = await import_file(poetry_repo, path, source, dynasty)
            total_success += success
            total_duplicate += duplicate
            total_failed += failed
            print(f"完成 {path.name}: 成功 {success}，重复 {duplicate}，失败 {failed}")

        print(f"\n全部完成：成功 {total_success}，重复 {total_duplicate}，失败 {total_failed}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
