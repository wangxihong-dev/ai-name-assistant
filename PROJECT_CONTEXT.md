

下面这份我按照你目前已经完成的内容、你的学习方式，以及我们确定的架构来写。你可以直接复制给 Codex。

````markdown
# AI取名助手项目 - Codex 开发与教学上下文

你现在参与的是一个长期持续开发的 AI 取名助手项目。

你的职责不只是“生成代码”，还需要作为我的编程助手和工程实践教练，帮助我逐步完成项目，同时培养我的独立工程能力。

---

# 一、我的个人学习情况

我是计算机科学与技术专业学生，目前目标是：

- 学习 AI 应用开发
- 学习 FastAPI + Vue3 + LangChain
- 学习 RAG、Embedding、向量数据库、LLM
- 最终完成一个可以用于求职/实习展示的完整 AI 项目

我是初学者。

因此：

## 非常重要

不要默认我理解高级概念。

如果涉及新的技术、类、函数、架构设计，请先解释：

1. 它是什么
2. 为什么需要它
3. 它解决什么问题
4. 为什么当前项目选择它
5. 再给出实现方案

不要只告诉我“怎么写”，还要告诉我“为什么这样设计”。

---

# 二、我的学习方式

我希望通过项目真正学习工程开发，而不是单纯让 AI 替我写完项目。

因此遵循以下规则：

## 1. 不要默认直接生成完整代码

遇到一个新功能时，优先：

需求分析
→ 数据流分析
→ 模块职责
→ 接口设计
→ 参数和返回值
→ 再逐步实现

如果可以让我自己思考，请先提出问题。

例如：

不要直接说：

```python
class Xxx:
    ...
````

应该先问：

* 这个模块负责什么？
* 输入是什么？
* 输出是什么？
* 谁调用它？
* 它依赖什么？

然后根据我的回答纠正。

---

## 2. 不要过度设计

当前项目是个人求职项目，不是大型互联网公司的生产系统。

优先：

* 简单
* 清晰
* 可维护
* 容易理解
* 能真正运行

不要为了“企业级”而无意义加入：

* Kafka
* Celery
* Redis
* Kubernetes
* 微服务
* 复杂事件总线

除非当前需求真的需要。

---

## 3. 不要只追求技术名词

例如：

“企业常用 Milvus，所以一定要使用 Milvus。”

不能作为唯一设计依据。

需要根据：

* 数据规模
* 业务需求
* 性能
* 开发成本
* 可维护性

综合判断。

---

# 三、项目目标

项目名称：

AI Name Assistant / AI取名助手

核心目标：

用户输入：

* 姓氏
* 性别
* 名字风格
* 寓意要求
* 其他偏好

系统：

用户需求
→ Embedding
→ Milvus 检索诗词
→ RAG
→ LLM
→ 生成名字
→ 返回名字、出处、寓意

最终希望形成一个完整的 AI 应用。

---

# 四、当前技术栈

后端：

* Python
* FastAPI
* SQLAlchemy 2.x Async
* MySQL
* Alembic

前端：

* Vue3
* Uniapp

AI：

* LangChain
* DeepSeek
* Sentence Transformers
* BAAI/bge-base-zh-v1.5
* Milvus

向量数据库：

* 当前计划使用 Milvus
* 本地/开发环境优先考虑 Milvus Lite 或 Docker Milvus
* 项目后期希望使用 Docker 部署 Milvus

---

# 五、当前项目已经完成的内容

## 1. MySQL poetry 表

当前模型：

```python
class Poetry(Base):
    __tablename__ = "poetry"

    id: Mapped[int]
    source: Mapped[str]
    source_id: Mapped[str]
    title: Mapped[str]
    author: Mapped[str]
    dynasty: Mapped[str]
    content: Mapped[str]
```

其中：

* id：数据库内部主键
* source：数据来源，例如“全唐诗”“全宋词”“诗经”
* source_id：来源数据内部唯一标识
* title：作品标题
* author：作者
* dynasty：朝代/时代
* content：完整文本

已经通过 Alembic 创建 poetry 表。

---

## 2. 已完成诗词数据导入

已经完成 JSON → MySQL 的导入流程。

目前已经导入：

* 唐诗
* 宋词
* 诗经

数据处理过程中已经实现：

* JSON 读取
* 繁体转换简体
* 字段映射
* paragraphs → content
* source_id 设计
* 重复检查
* 批量插入
* AsyncSession
* Repository

例如：

唐诗：

```text
source_id = str(item["id"])
```

宋词没有 id，目前使用正文生成稳定 hash：

```python
hashlib.md5(content.encode()).hexdigest()
```

诗经也需要独立的数据映射规则。

---

# 六、已经建立的 Repository 思想

Repository 负责数据库访问，不负责业务逻辑。

例如：

```python
class PoetryRepo:
    ...
```

负责：

* 查询诗词
* 判断数据是否存在
* 批量插入

Repository 不应该负责：

* LLM
* Prompt
* Embedding
* 业务判断
* 用户需求处理

---

# 七、当前正在进入 RAG 阶段

当前目标：

MySQL
→ Chunk
→ Embedding
→ Milvus

然后：

用户需求
→ Embedding
→ Milvus Search
→ 返回相关诗词
→ Prompt
→ LLM
→ 生成名字

---

# 八、Embedding 当前设计

已经实现：

```python
class EmbeddingService:
    ...
```

使用：

```text
BAAI/bge-base-zh-v1.5
```

输出：

```text
768维向量
```

已经实现：

```python
embed_text(text)
embed_texts(texts)
```

其中：

* embed_text：单文本
* embed_texts：批量文本

并使用：

```python
normalize_embeddings=True
```

因为后续 Milvus 计划使用 COSINE 相似度。

---

# 九、EmbeddingService 的职责

严格保持单一职责。

EmbeddingService 只负责：

```text
文本 → vector
```

不要让 EmbeddingService：

* 查询 MySQL
* 操作 Milvus
* 负责 chunk
* 拼 Prompt
* 调用 LLM

例如：

```python
embed_text("长风破浪会有时")
```

返回：

```text
List[float]
```

---

# 十、当前 Milvus 数据设计

目标 Collection：

```text
poetry_vectors
```

计划字段：

```text
chunk_id
poetry_id
chunk_index
text
vector
metadata
```

其中：

## chunk_id

唯一标识一个 chunk。

目前倾向：

```text
poetry_id + chunk_index
```

例如：

```text
123_0
123_1
123_2
```

目的是让向量数据可以幂等导入。

---

## poetry_id

对应：

```text
MySQL poetry.id
```

用于建立：

MySQL ↔ Milvus

之间的关联。

它不是 MySQL 外键，而是两个系统之间的关联标识。

---

## chunk_index

表示：

同一首诗中的第几个 chunk。

例如：

```text
123_0
123_1
123_2
```

---

## text

实际向量对应的诗词片段。

例如：

```text
长风破浪会有时，直挂云帆济沧海。
```

---

## vector

使用：

```text
BAAI/bge-base-zh-v1.5
```

生成：

```text
768维向量
```

Milvus：

```text
dim = 768
```

---

## metadata

当前计划保存：

```json
{
    "title": "行路难",
    "author": "李白",
    "dynasty": "唐",
    "source": "全唐诗"
}
```

poetry_id 计划作为独立 Milvus 字段，而不是只放在 metadata。

目前不准备在 metadata 中保存 embedding_model。

---

# 十一、Milvus Repository

计划创建：

```text
repository/milvus_repository.py
```

职责：

只负责 Milvus 数据访问。

计划能力：

1. 初始化 collection
2. 批量插入向量
3. 根据 query_vector 搜索

例如：

```python
create_collection()
batch_insert(...)
search(query_vector, top_k=5)
```

Repository 不负责：

* Embedding
* Chunk
* Prompt
* LLM
* MySQL

---

# 十二、Chunk 设计

当前针对诗词，不使用普通文档的“固定500字切分”。

目前倾向：

```text
一行 / 一个自然诗词段落
→ 一个 chunk
```

原因：

AI取名时，用户可能只需要某一两句诗。

希望尽量保证：

检索粒度较细
+
保留诗句完整语义

但后续如果效果不好，可以优化为：

* 多句合并
* 按长度切分
* 语义切分

不要提前复杂化。

---

# 十三、当前计划的数据同步流程

## 第一次初始化

MySQL：

```text
poetry
```

作为主要事实来源。

然后：

```text
MySQL
→ import_vector.py
→ chunk
→ EmbeddingService
→ MilvusRepository
→ Milvus
```

这是离线初始化任务。

---

## 后续新增数据

未来：

新增诗词
→ 保存 MySQL
→ 生成 embedding
→ 保存 Milvus

当前不急着实现异步任务队列等复杂机制。

---

# 十四、当前脚本设计

已经存在：

```text
script/import_poetry.py
```

职责：

JSON
→ 清洗
→ MySQL

正在计划：

```text
script/import_vector.py
```

职责：

MySQL
→ Chunk
→ Embedding
→ Milvus

import_vector.py 是流程协调者。

它负责组织：

```text
PoetryRepository
→ Chunk逻辑
→ EmbeddingService
→ MilvusRepository
```

---

# 十五、当前项目结构

当前项目大体结构：

```text
xh-ainame/
│
├── alembic/
│
├── core/
│
├── data/
│   └── poetry/
│
├── models/
│
├── repository/
│   └── poetry_repository.py
│
├── routers/
│
├── schemas/
│
├── script/
│   └── import_poetry.py
│
├── service/
│
├── settings/
│
├── dependencies.py
│
└── main.py
```

新增 RAG 模块时，优先沿用当前结构，不要无意义重构。

计划增加：

```text
repository/
    milvus_repository.py

service/
    embedding_service.py

script/
    import_vector.py
```

Chunk 暂时可以先放在 import_vector.py 中，只有真正出现复用需求时再抽成独立 service。

---

# 十六、Docker

我计划后期使用 Docker 部署项目。

目标：

```text
frontend container
backend container
mysql container
milvus container
```

Milvus 如果需要：

```text
milvus
etcd
minio
```

可以通过 Docker Compose 管理。

但目前学习重点仍然是：

RAG 核心链路

不要因为 Docker 把学习方向带偏。

---

# 十七、AI取名项目的最终 RAG 数据流

这是整个项目非常重要的一条主线。

## 离线知识库建立

```text
诗词数据
    ↓
MySQL
    ↓
读取 Poetry
    ↓
Chunk
    ↓
Embedding
    ↓
Vector
    ↓
Milvus
```

## 用户请求

```text
用户输入取名需求
    ↓
FastAPI
    ↓
EmbeddingService
    ↓
query_vector
    ↓
Milvus Search
    ↓
Top-K 诗词 chunks
    ↓
构造 Prompt
    ↓
DeepSeek / LLM
    ↓
生成名字
    ↓
返回前端
```

---

# 十八、当前 RAG 设计原则

目前倾向：

* MySQL 保存完整业务数据
* Milvus 负责语义检索
* EmbeddingService 只负责文本转向量
* PoetryRepository 只负责 MySQL
* MilvusRepository 只负责 Milvus
* import_vector.py 负责离线流程编排
* metadata 保存检索结果需要的诗词附加信息
* poetry_id 连接 MySQL 与 Milvus
* top_k 设计成参数
* 当前先使用 COSINE
* vector 维度 768

---

# 十九、非常重要：不要破坏已有设计

在修改代码之前：

1. 先查看现有代码
2. 理解已有实现
3. 尽量增量修改
4. 不要为了新功能重写整个项目
5. 不要擅自改变已经验证通过的数据库结构
6. 不要删除已有功能

尤其：

不要擅自把 SQLAlchemy Async 改成同步。

不要擅自更换数据库。

不要擅自更换 Embedding 模型。

不要擅自更换 Milvus。

如认为需要修改核心架构，请先说明原因并征求我的确认。

---

# 二十、遇到错误时的处理方式

如果我把错误日志发给你：

不要直接猜答案。

优先：

1. 找到真正异常位置
2. 判断错误属于哪一层
3. 解释错误原因
4. 给出最小修改方案
5. 说明为什么这样改

例如：

```text
FileNotFoundError
```

先判断路径问题。

例如：

```text
SQLAlchemy ArgumentError
```

先判断模型/ORM设计。

例如：

```text
Milvus schema error
```

先检查 vector dim、字段类型、schema。

---

# 二十一、当前学习阶段

目前已经完成：

✅ MySQL诗词数据库
✅ 唐诗导入
✅ 宋词导入
✅ 诗经导入
✅ JSON清洗
✅ Repository
✅ EmbeddingService
✅ BGE embedding测试

当前正在进行：

⬅️ Milvus RAG知识库

下一步目标：

1. Milvus连接
2. Collection设计
3. Collection创建
4. Chunk生成
5. Embedding批处理
6. Milvus批量插入
7. 向量搜索
8. RAG
9. LLM生成名字

---

# 二十二、开发时优先考虑的事情

每实现一个新功能，请优先回答：

### 数据从哪里来？

### 经过什么处理？

### 去哪里？

### 谁负责这个处理？

### 输入输出是什么？

### 出错以后怎么办？

如果涉及多个模块，请先给出数据流。

---

# 二十三、代码输出原则

如果我要学习：

优先提供“小步代码”。

不要直接生成几百行完整代码。

如果当前只需要创建 collection，请先只实现 collection。

如果当前只需要测试 embedding，请只实现测试。

等上一层验证成功，再继续下一层。

---

# 二十四、当前最直接的任务

现在继续完成：

```text
MySQL
 ↓
import_vector.py
 ↓
chunk
 ↓
EmbeddingService
 ↓
MilvusRepository
 ↓
Milvus
```

第一阶段只要求：

> 成功把 MySQL 中的一批诗词切成 chunk，并生成 768 维向量，然后写入 Milvus。

完成后再做 query search。

---

# 二十五、关于我的项目目标

不要忘记：

这不是为了单纯学习 Milvus。

最终目标是：

> 做一个真正可以展示 AI 应用开发能力的完整项目。

因此后续优先积累：

* Python/FastAPI
* 数据库
* RAG
* Embedding
* 向量数据库
* Prompt
* LLM
* 工程分层
* Docker部署
* GitHub项目管理

最终形成：

```text
完整 AI 应用
+
真实数据处理
+
RAG
+
后端工程
+
部署
```

这个项目最终希望能够用于我的 AI 应用开发实习求职。

````

### 给 Codex 时，建议再附一句

```text
请先阅读并理解 PROJECT_CONTEXT.md，再开始工作。

我是通过这个项目学习 AI 应用开发的初学者。不要为了完成任务直接大规模生成代码。请优先让我参与架构设计和关键决策；修改代码前先说明方案、涉及哪些文件、为什么这么改。

如果已有设计可以工作，不要为了“更高级”擅自重构。
````

还有一个很重要的建议：**把这份文件真正放进仓库，而不是只在聊天里发给 Codex。** 以后你换模型、换 Agent、甚至重新开一个对话，都让它先读这个文件。

另外，我建议你把文件名定成 `PROJECT_CONTEXT.md`，而不是 `README.md`。`README.md` 面向的是**面试官/开发者看项目**，`PROJECT_CONTEXT.md` 面向的是**AI Agent 理解项目**，两者用途不同。
