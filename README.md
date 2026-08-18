# ✨ AI智能取名助手

一个基于大语言模型的智能取名应用，结合传统诗词文化，
帮助用户生成具有文化内涵和美好寓意的名字。


## 📌 项目介绍

本项目面向家长用户，通过输入宝宝姓氏、性别、名字长度、
个性化要求等信息，利用 AI 大模型生成多个候选名字。

用户可以注册账号、登录系统，并获取个性化取名服务。


## 🛠 技术栈


### 后端 Backend

- Python
- FastAPI
- SQLAlchemy
- MySQL
- JWT身份认证
- Pydantic


### 前端 Frontend

- Vue3
- UniApp


### AI

- DeepSeek API
- LangChain
- Agent


## ✨ 当前功能


### 用户系统

- [x] 用户注册
- [x] 邮箱验证码
- [x] 用户登录
- [x] JWT Token认证


### AI取名

- [x] 根据姓氏生成名字
- [x] 根据性别生成名字
- [x] 根据需求生成名字


### 后续计划

- [ ] 增加历史取名记录
- [ ] 增加名字收藏功能
- [ ] 接入诗词知识库
- [ ] Agent调用知识库
- [ ] 项目部署上线



## 📂 项目结构

ai-name-assistant

├── backend
│ └── FastAPI 后端代码
│
├── frontend
│ └── UniApp 前端代码
│
└── README.md


## 🚀 项目运行


### 后端启动


进入：backend/xh-ainame



安装依赖：pip install -r requirements.txt



启动：uvicorn main:app --reload



### 前端启动


使用 HBuilderX 打开：frontend/ai取名

运行项目即可。

## 📷 项目截图

后续添加。


## 👨‍💻 作者

wangxihong-dev


