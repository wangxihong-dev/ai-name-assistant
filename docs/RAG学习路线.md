# RAG 学习路线图（AI 取名助手实战）

> 目标：掌握 RAG（检索增强生成）+ AI 应用开发，能独立完成本项目改造，并具备西安 AI 应用开发实习的面试能力。

## 学习地图总览

```
阶段0 基础自检（已有：Python/FastAPI/SQLAlchemy/Vue）
   ↓
阶段1 Docker 容器化（为什么用容器、镜像/容器/Compose）
   ↓
阶段2 向量数据库 Milvus（概念 + Docker 部署 + 基础操作）
   ↓
阶段3 文本向量化 Embedding（中文模型/API）
   ↓
阶段4 RAG 管线（检索 → 拼 Prompt → LLM 生成 → 引用出处）
   ↓
阶段5 工程化与评估（异步、日志、评测、错误处理）
   ↓
阶段6 部署 + 作品集 + 简历 + 面试（西安实习）
```

## 阶段1：Docker 基础

### 要掌握的概念
- 容器 vs 虚拟机：容器是进程级隔离，共享操作系统内核
- 镜像（Image）：打包好的模板，只读
- 容器（Container）：镜像运行起来的实例
- Dockerfile：构建镜像的说明书
- Docker Compose：用 YAML 一次启动多个容器（我们用来启动 Milvus）
- 端口映射：`-p 宿主机端口:容器端口`
- 数据卷（Volume）：容器删除后数据不丢失

### 常用命令（记住这些）
```bash
docker ps                # 查看运行中的容器
docker ps -a             # 查看所有容器
docker images            # 查看本地镜像
docker pull <镜像名>      # 拉取镜像
docker run <镜像名>       # 运行容器
docker stop/start <容器>  # 停止/启动容器
docker logs <容器>        # 查看容器日志
docker compose up -d     # 按 compose 文件后台启动
docker compose down      # 停止并删除
```

### 本项目的落地任务
1. 启动 Docker Desktop
2. 用 Docker Compose 部署 Milvus Standalone（etcd + minio + milvus 三个容器）
3. 掌握 `docker ps` 查看服务状态

## 阶段2：Milvus 向量数据库

### 要掌握的概念
- 什么是向量：把文本/图片转成一串数字（例如 1024 维）
- 什么是向量检索：找“语义最相似”的向量（余弦相似度/欧氏距离）
- Collection（集合）：类似 MySQL 的表
- Schema（字段结构）：定义 id、向量字段、标量字段
- Index（索引）：加速检索（如 IVF_FLAT、HNSW）
- Metric（距离度量）：COSINE / L2 / IP
- 标量过滤：在检索时加条件（如只搜“宋词”）

### 本项目的落地任务
1. 用 pymilvus 连接 Milvus
2. 创建 poetry 向量集合（id、诗词内容、出处、向量）
3. 写入一批诗词向量
4. 做一次相似度检索，验证结果

## 阶段3：Embedding 向量化

### 要掌握的概念
- Embedding 模型把文本变成向量
- 中文场景常用：BGE-M3、bge-large-zh、text-embedding-v3 等
- API 调用 vs 本地模型：API 简单、本地模型免费但要 GPU/内存
- 向量维度：不同模型维度不同（如 bge-m3 是 1024 维）

### 本项目的落地任务
1. 把 poetry 表里的诗词切分（一首诗/一句词为一个检索单元）
2. 调用 Embedding 接口生成向量
3. 批量写入 Milvus

## 阶段4：RAG 管线（核心）

### RAG 流程
```
用户提问（想取名）
  → 把用户需求转成查询向量
  → 在 Milvus 中检索最相关的诗词（top-k）
  → 把诗词原文拼进 Prompt（上下文）
  → 大模型（DeepSeek）参考诗词生成名字 + 出处
  → 返回名字、寓意、出处
```

### 要掌握的概念
- Query 向量化：用户输入也要转成向量
- Top-K：返回最相似的 K 条
- Prompt 组装：把检索结果作为上下文注入
- 引用溯源：答案里带上诗词出处，增强可信度

### 本项目的落地任务
1. 写 `retriever.py`：输入用户需求 → 输出相关诗词
2. 改造 `core/agent.py`：把检索结果注入 System Prompt
3. 取名结果里展示诗词出处
4. 验证：检索到的诗词确实与取名结果相关

## 阶段5：工程化与评估

- 把检索和生成做成异步、可配置
- 加日志：记录每次检索用时、命中的诗词
- 做评估：准备 10~20 个取名测试用例，人工打分（相关性、寓意、音律）
- 优化：调 Top-K、换 Embedding 模型、加标量过滤

## 阶段6：实习求职准备（西安）

### 作品集要求
- GitHub 仓库 README 写好：项目背景、架构图、技术栈、效果截图、如何运行
- 录一个 3~5 分钟演示视频
- 部署上线（可以用免费云服务器/平台），能给别人演示

### 西安 AI 应用开发实习常见要求
- Python 基础 + FastAPI/Flask 经验
- 大模型 API 调用（DeepSeek/通义/智谱等）
- 了解 RAG、LangChain、向量数据库
- 会 Docker 部署是加分项
- 有真实项目经验 > 刷题

### 面试常见问题
1. 什么是 RAG？为什么要用 RAG？（幻觉、知识时效、私有知识）
2. 向量检索和关键字检索的区别？
3. 为什么选 Milvus？和其他向量库（Faiss、pgvector、Milvus）比？
4. 怎么解决检索不到好诗词的问题？（换模型、调 K、过滤、重排）
5. 大模型幻觉怎么缓解？（引用出处、限制只基于检索内容回答）

## 进度记录

- [x] 阶段0：项目了解
- [x] 阶段1：Docker 部署 Milvus（2026-08-27：Milvus Standalone 已在本机 Docker 运行，三个容器：etcd/minio/milvus）
- [x] 阶段2：Milvus 基础操作（入门脚本 script/milvus_hello.py：建集合/插入/检索已跑通）
- [x] 阶段3：诗词向量化入库（代码已就绪并验证：core/embedding.py + script/import_poetry_vectors.py + script/milvus_search_demo.py；等待配置 EMBEDDING_API_KEY 后导入真实向量）
- [ ] 阶段4：RAG 接入取名 Agent
- [ ] 阶段5：工程化与评估
- [ ] 阶段6：部署与求职


