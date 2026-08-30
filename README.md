# ✨ AI智能取名助手

一个基于大语言模型的智能取名应用，结合传统诗词文化，
帮助用户生成具有文化内涵和美好寓意的名字。


## 📌 项目介绍

本项目面向家长用户，通过输入宝宝姓氏、性别、名字长度、
个性化要求等信息，利用 RAG 检索诗词知识库，结合 AI 大模型
生成多个候选名字，并给出诗词出处与寓意解释。

用户可以注册账号、登录系统，获取个性化取名服务，
收藏心仪的名字，所有取名记录自动保存，方便随时回顾对比。


## 🛠 技术栈


### 后端 Backend

- Python
- FastAPI
- SQLAlchemy（异步 ORM）
- Alembic（数据库迁移）
- MySQL
- JWT 身份认证
- Pydantic
- LangChain + DeepSeek API


### 前端 Frontend

- Vue3
- UniApp（跨端，支持 H5 / 小程序 / App）


### AI

- DeepSeek API
- LangChain
- Agent（结构化输出）
- Sentence Transformers（BAAI/bge-base-zh-v1.5 中文向量模型，768 维）
- Milvus 向量数据库（Docker 部署，etcd + MinIO）
- RAG 检索增强生成
- 诗词知识库（唐诗 + 宋词 + 诗经，繁体转简体）


## ✨ 当前功能


### 用户系统

- [x] 用户注册（邮箱验证码）
- [x] 用户登录
- [x] JWT Token 认证（access token + refresh token）
- [x] 邮箱验证码发送


### AI 取名

- [x] 根据姓氏生成名字
- [x] 根据性别生成名字
- [x] 根据名字长度生成名字
- [x] 根据父母寄语生成名字
- [x] 检索诗词知识库，基于真实诗句生成名字出处
- [x] AI 返回名字、出处、寓意
- [x] 结构化输出（Pydantic Schema 约束）


### 历史记录

- [x] 取名后自动保存历史记录
- [x] 查看个人取名历史记录列表
- [x] 点击展开查看当时生成的名字详情
- [x] 按时间倒序排列


### 名字收藏

- [x] 一键收藏喜欢的名字（出处、寓意一并保存）
- [x] 查看我的收藏列表
- [x] 取消收藏


### 诗词 RAG 知识库

- [x] Milvus 向量数据库连接与 Collection 创建（`poetry_vectors`）
- [x] 诗词向量化导入（MySQL → 按行切 chunk → BGE 768 维向量 → Milvus，共 5.7 万+ chunk）
- [x] 向量语义检索（按诗句语义召回相关诗词，并返回标题、作者、出处）
- [x] RAG 接进取名流程（用户需求 → 向量检索 → 构造 Prompt → LLM 生成带出处名字）


### 后续计划

- [ ] 项目部署上线（前端、后端、MySQL、Milvus 全链路容器化）
- [ ] 收藏去重 / 已收藏状态标记（可选优化）


## 📷 项目截图

| 登录页 | 注册页 |
|--------|--------|
| ![登录页](docs/screenshots/login.png) | ![注册页](docs/screenshots/register.png) |

| 取名页 | 我的收藏 |
|--------|----------|
| ![取名页](docs/screenshots/name-input.png) | ![我的收藏](docs/screenshots/favorite.png) |


## 📂 项目结构

```
ai-name-assistant
├── backend
│   └── xh-ainame
│       ├── alembic/                      # 数据库迁移
│       ├── core/                         # 核心模块（认证、邮件、AI Agent）
│       │   └── milvus.py                 # Milvus 连接客户端
│       ├── data/poetry/                  # 原始诗词数据（JSON）
│       ├── models/                       # 数据库模型
│       │   ├── poetry.py                 # 诗词表
│       │   ├── name_history.py           # 取名历史表
│       │   └── name_favorite.py          # 名字收藏表
│       ├── repository/                   # 数据访问层
│       │   ├── poetry_reposityory.py     # MySQL 诗词访问
│       │   ├── milvus_repository.py      # Milvus 访问（建表/插入/搜索）
│       │   └── name_favorite_repository.py # 收藏数据访问
│       ├── routers/                      # 路由层
│       ├── schemas/                      # Pydantic 数据模型
│       ├── script/                       # 工具脚本
│       │   ├── import_poetry.py          # JSON → MySQL 诗词导入
│       │   ├── import_vector.py          # MySQL → chunk → 向量 → Milvus
│       │   └── test_milvus.py            # Milvus 建表/插入/搜索验证
│       ├── service/                      # 业务逻辑层
│       │   ├── embedding_service.py      # BGE 文本向量化
│       │   ├── name_service.py           # 取名 + 历史记录
│       │   └── favorite_service.py       # 名字收藏
│       ├── settings/                     # 配置
│       ├── main.py                       # 应用入口（含 CORS 配置）
│       └── requirements.txt              # 依赖
├── docker
│   └── milvus/
│       ├── docker-compose.yml            # Milvus Standalone（etcd + minio）
│       └── volumes/                      # Milvus 数据目录（git 忽略）
├── frontend
│   └── ai取名                            # UniApp 前端
│       ├── common/api.js                 # 统一请求层（地址/鉴权/错误处理）
│       └── pages/
│           ├── index/                    # 登录页
│           ├── register/                 # 注册页
│           ├── name/                     # 取名页
│           ├── history/                  # 历史记录页
│           └── favorite/                 # 我的收藏页
├── docs
│   └── screenshots/                      # 项目截图
└── README.md
```


## 🚀 项目运行


### 后端启动

1. 进入目录：
```bash
cd backend/xh-ainame
```

2. 创建虚拟环境并安装依赖：
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. 配置环境变量：
复制 `.env.example` 为 `.env`，填写数据库连接、邮箱配置、AI API Key。

4. 执行数据库迁移：
```bash
alembic upgrade head
```

5. 导入诗词数据（可选，RAG 功能需要）：
```bash
python script/import_poetry.py
```
脚本会自动将 `data/poetry/` 目录下的诗词 JSON 文件导入数据库，支持繁体转简体、重复跳过。

6. 启动 Milvus 向量数据库（RAG 功能需要）：
```bash
cd docker/milvus
docker compose up -d
```
首次启动会拉取镜像（etcd、MinIO、Milvus Standalone），等待健康检查通过后即可连接 `localhost:19530`。

7. 导入诗词向量（将 MySQL 中的诗词切分并向量化写入 Milvus）：
```bash
cd backend/xh-ainame
python -m script.import_vector
```
脚本按行切分诗词为 chunk，用 BGE 模型生成 768 维向量，写入 `poetry_vectors` Collection。
模型已下载到本地缓存时可离线运行（设置环境变量 `HF_HUB_OFFLINE=1`）。

8. 启动服务：
```bash
uvicorn main:app --reload
```

API 文档：http://127.0.0.1:8000/docs


### 前端启动

1. 使用 HBuilderX 打开 `frontend/ai取名`
2. 后端 API 地址统一在 `common/api.js` 的 `BASE_URL` 中配置（默认 `http://127.0.0.1:8000`）
3. 运行到浏览器或模拟器


## 📝 开发记录

### 2026-08-22 新增历史取名记录功能

- 新增 `NameHistory` 模型，关联用户表
- Alembic 迁移创建 `name_history` 表
- 新增 `NameHistoryRepository` 数据访问层
- 新增 `NameService` 业务逻辑层（取名 + 保存历史 + 查询历史）
- 新增 `GET /name/history` 接口
- 取名接口 `POST /name/` 增加自动保存历史逻辑
- 前端新增历史记录页面，支持列表展示和展开详情
- 前端取名页增加历史记录入口和保存成功提示

### 2026-08-26 新增诗词数据导入功能

- 新增 `Poetry` 模型，存储诗词原文（宋诗 + 宋词）
- Alembic 迁移创建 `poetry` 表
- 新增 `PoetryRepository` 数据访问层
- 新增 `script/import_poetry.py` 数据导入脚本
- 支持繁体转简体、批量导入、重复数据自动跳过
- 包含 1000 首宋诗和 11000 首宋词原始数据
- 为后续 RAG 检索增强生成功能做数据准备

### 2026-08-29 新增 Milvus RAG 知识库

- 新增 `core/milvus.py`：Milvus 连接客户端
- 新增 `repository/milvus_repository.py`：Milvus 数据访问层（建表 / 批量插入 / 向量搜索）
- 新增 `service/embedding_service.py`：BGE 中文向量模型封装（768 维，余弦归一化）
- 新增 `script/import_vector.py`：MySQL → chunk → 向量 → Milvus 导入脚本
- 新增 `script/test_milvus.py`：Milvus 建表 / 插入 / 搜索验证脚本
- 新增 `docker/milvus/docker-compose.yml`：Milvus Standalone（etcd + MinIO）Docker 编排
- 完成诗词语义检索验证（示例：搜索「明月」可召回相关诗句并返回出处）

### 2026-08-30 RAG 接进取名流程 + 名字收藏功能 + 前端全面改版

- RAG 接进取名：取名时先向量检索诗词，诗句拼入 Prompt，LLM 生成带真实出处的名字
- 新增 `NameFavorite` 模型与 Alembic 迁移，收藏数据入库
- 新增 `NameFavoriteRepository`、`FavoritesService` 分层实现
- 新增接口：`POST /name/favorite`、`GET /name/favorites`、`DELETE /name/delete/{id}`
- 前端新增「我的收藏」页面，取名结果支持一键收藏 / 取消收藏
- 前端统一设计系统（暖色渐变 + 卡片 + 动效），全面改版登录 / 注册 / 取名 / 历史页面
- 优化等待体验（分阶段加载动画、骨架屏）与页面性能（统一请求层、防重复提交、入场动画）
- 后端增加 CORS 配置，支持 H5 前端跨域调用


## 👨‍💻 作者

wangxihong-dev
