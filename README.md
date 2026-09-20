# 🛍️ Smart E-commerce Agent

基于 **LLM + Agent + RAG** 构建的电商售后智能客服系统，面向订单查询、物流查询、售后政策咨询、售后争议处理等场景，提供从自然语言对话到业务数据查询、知识检索和售后工单创建的一体化解决方案。

项目采用 **FastAPI + LangChain/LangGraph + DeepSeek + MySQL + Milvus + BGE-M3 + Redis + Vue 3** 架构，并提供完整的 Web 前端与 SSE 流式对话能力。

---

## ✨ 项目特点

- 🤖 **LLM + Agent**：基于 LangChain / LangGraph 构建智能客服 Agent，根据用户问题自主选择合适的业务工具。
- 🧾 **订单查询**：根据订单号查询商品、下单时间、订单金额、订单状态和物流单号。
- 🚚 **物流查询**：根据订单号查询物流单号及完整物流轨迹。
- 📚 **售后政策 RAG**：使用本地 BGE-M3 对售后问题进行向量化，通过 Milvus 检索相关售后政策。
- 📝 **售后工单**：当用户明确要求人工处理或出现需要进一步处理的售后争议时，Agent 可以创建售后工单并生成工单号。
- 💾 **MySQL 业务数据**：订单、物流和售后工单等业务数据统一存储在 MySQL。
- ⚡ **Redis 高频问题联想**：缓存售后高频问题，为前端提供首页快捷问题和输入联想。
- 🧠 **会话记忆**：使用 LangGraph `InMemorySaver` 按 `session_id` / `thread_id` 保存会话上下文。
- 🌊 **SSE 流式输出**：Agent 回复通过 FastAPI SSE 持续推送到前端，实现类似实时打字的聊天体验。
- 🖥️ **完整 Web UI**：Vue 3 + Element Plus 构建客服页面，同时展示聊天、订单和售后工单信息。
- 🔎 **LangSmith 可选追踪**：支持 LangSmith 对 Agent 调用链路进行调试和追踪。

---

## 🏗️ 系统架构

```text
                         ┌──────────────────────┐
                         │      Vue 3 前端       │
                         │ Element Plus + Axios │
                         └──────────┬───────────┘
                                    │ HTTP / SSE
                                    ▼
                         ┌──────────────────────┐
                         │     FastAPI 后端      │
                         │       REST API       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    LangChain Agent    │
                         │     LangGraph         │
                         │  Memory + Tool Call   │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼──────────────────────┐
              │                     │                      │
              ▼                     ▼                      ▼
       ┌─────────────┐      ┌─────────────┐       ┌─────────────┐
       │ query_order │      │ query_track │       │search_policy│
       └──────┬──────┘      └──────┬──────┘       └──────┬──────┘
              │                    │                     │
              └────────────┬───────┘                     ▼
                           ▼                      ┌─────────────┐
                      ┌─────────┐                 │  BGE-M3     │
                      │  MySQL  │                 └──────┬──────┘
                      │ orders  │                        │
                      │ tracks  │                        ▼
                      │ tickets │                 ┌─────────────┐
                      └─────────┘                 │   Milvus    │
                                                  └─────────────┘

                       ┌─────────────────┐
                       │ create_ticket   │
                       └────────┬────────┘
                                │
                                ▼
                         MySQL / tickets

                       ┌─────────────────┐
                       │ Redis FAQ       │
                       │ 高频问题/联想    │
                       └─────────────────┘
```

---

## 🧰 技术栈

| 技术 | 用途 |
|---|---|
| Python | 后端与 Agent 开发语言 |
| LangChain | LLM、Tools 与 Agent 集成 |
| LangGraph | Agent 编排与会话记忆 |
| DeepSeek V4 Flash | 核心大语言模型，通过 SiliconFlow OpenAI-compatible API 调用 |
| FastAPI | 后端 REST API 与 SSE 服务 |
| Uvicorn | ASGI 服务运行 |
| MySQL | 订单、物流、售后工单等业务数据存储 |
| BGE-M3 | 售后政策文本向量化 |
| Milvus | 售后政策向量数据库 |
| Redis | 高频售后问题缓存与联想 |
| Vue 3 | Web 前端 |
| Element Plus | 前端 UI 组件库 |
| Axios | 前端 HTTP 请求 |
| Vite | 前端开发与构建 |
| LangSmith | Agent 调试与链路追踪（可选） |

---

## 📁 项目结构

```text
smart_ecommerce_agent/
│
├── agent/                         # Agent 核心代码
│   ├── agent_builder.py           # Agent 构建、LLM、Memory
│   ├── config.py                  # Agent 配置
│   ├── db.py                      # MySQL 数据库连接
│   ├── milvus_data_sync.py        # 售后政策同步到 Milvus
│   ├── redis_service.py           # Redis 高频问题服务
│   ├── stream_agent.py            # Agent SSE 流式处理
│   ├── tools.py                   # Agent 业务工具
│   └── prompts/
│       └── system_prompt.txt      # Agent 系统提示词
│
├── api/
│   └── main.py                    # FastAPI 接口层
│
├── ui/                            # Vue 3 前端
│   ├── src/
│   │   ├── App.vue                # 主页面
│   │   ├── main.js                # 前端入口
│   │   └── api/index.js           # API 请求封装
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── tables/                        # MySQL 建表 SQL
│   ├── agent_test.sql
│   ├── orders.sql
│   ├── tracks.sql
│   ├── policies.sql
│   └── tickets.sql
│
├── chat_cli.py                    # 命令行聊天入口
├── check_llm.py                   # LLM 连接检查
├── init_redis_faq.py              # 初始化 Redis 高频问题
├── main.py                        # Agent / 项目入口
├── run.py                         # FastAPI 启动入口
├── test_db.py                     # MySQL 测试
├── test_memory.py                 # Agent Memory 测试
├── test_milvus_bge.py             # BGE-M3 + Milvus 测试
├── test_pocily_search.py          # 政策检索测试
├── test_policy_db.py              # 政策数据库测试
├── test_policy_tool.py            # 政策工具测试
├── test_redis_faq.py              # Redis FAQ 测试
├── test_stream.py                 # SSE 流式测试
├── test_ticket_tool.py            # 工单工具测试
├── test_tools.py                  # Agent Tools 测试
├── test_track.py                  # 物流查询测试
├── .env_example                   # 环境变量模板
├── .gitignore
└── README.md
```

---

## 🔄 核心业务流程

### 1. 用户对话

```text
用户输入问题
      ↓
Vue 3 前端
      ↓
POST /chat
      ↓
FastAPI
      ↓
LangGraph Agent
      ↓
DeepSeek 判断是否需要调用工具
      ↓
执行业务工具
      ↓
Agent 综合工具结果生成回答
      ↓
SSE 流式返回
      ↓
Vue 实时展示回答
```

### 2. 订单查询

```text
用户提供订单号
      ↓
query_order
      ↓
MySQL.orders
      ↓
订单信息
      ↓
Agent 整理并回答
```

查询内容包括：

- 订单号
- 商品名称
- 下单时间
- 订单金额
- 订单状态
- 物流单号

如果订单不存在，工具会明确返回订单不存在，不生成虚假订单信息。

### 3. 物流查询

```text
订单号
  ↓
查询 orders
  ↓
获取 tracking_no
  ↓
查询 tracks
  ↓
按 track_time 升序返回物流轨迹
  ↓
Agent 整理回答
```

如果订单不存在、没有物流单号或没有物流轨迹，系统会分别返回对应状态。

### 4. 售后政策 RAG

```text
用户售后问题
      ↓
BGE-M3 Embedding
      ↓
Milvus 向量检索
      ↓
返回 Top 3 相关政策
      ↓
Agent 结合订单信息与政策
      ↓
生成售后处理建议
```

`search_policy` 只负责检索相关政策，不直接替代业务判断。Agent 会结合具体订单信息和政策适用条件进行回答。

### 5. 售后工单

当用户明确要求进一步人工处理、对售后处理产生明确争议，或者当前问题无法仅通过订单、物流和政策解决时，Agent 可以调用 `create_ticket`。

```text
确认订单号
    ↓
确认订单真实存在
    ↓
整理用户售后问题
    ↓
create_ticket
    ↓
写入 MySQL.tickets
    ↓
生成 TK-xxxxxx 工单号
    ↓
返回工单号 + 订单号 + 工单状态
```

当前系统的“创建工单”表示**将问题写入售后工单表并生成工单号**，不等同于已经接通真实人工客服。

### 6. Redis 高频问题联想

项目使用 Redis 保存售后高频问题，通过两个接口支持前端：

- `/faq/hot`：获取首页快捷问题
- `/faq/suggest`：根据用户输入进行问题联想

前端输入至少两个字符后，会延迟请求 Redis 联想接口，并避免旧请求覆盖新结果。

---

## 🔌 后端 API

启动 FastAPI 后，可以访问：

```text
http://127.0.0.1:8000/docs
```

### `POST /chat`

智能客服核心接口，通过 SSE 流式返回 Agent 回复。

请求：

```json
{
  "query": "帮我查一下订单 ORD202609180001 的物流",
  "session_id": "customer_123"
}
```

SSE 数据示例：

```text
data: {"content":"您好","type":"token"}

data: {"content":"，我帮您查询一下。","type":"token"}
```

### `GET /health`

服务健康检查。

返回：

```json
{
  "status": "ok",
  "service": "smart-ecommerce-agent"
}
```

### `GET /order/list`

获取订单列表，供前端右侧“我的订单”区域展示。

### `GET /ticket/list`

获取售后工单列表，供前端右侧“售后工单”区域展示。

返回字段包括：

- `ticket_no`
- `order_no`
- `issue`
- `status`
- `created_at`

### `GET /faq/hot`

获取 Redis 中的售后高频问题。

示例：

```text
GET /faq/hot?limit=4
```

### `GET /faq/suggest`

根据关键词获取售后问题联想。

示例：

```text
GET /faq/suggest?query=退货&limit=5
```

---

## 🧠 Agent Tools

当前 Agent 注册了 4 个业务工具。

### `query_order`

查询订单信息。

### `query_track`

查询物流轨迹。

### `search_policy`

通过 BGE-M3 + Milvus 检索相关售后政策。

### `create_ticket`

创建售后工单。

输入参数：

```json
{
  "order_no": "ORD202609180001",
  "issue": "用户对退货运费承担存在争议，需要进一步处理"
}
```

系统会先检查订单是否真实存在，再写入 `tickets` 表并生成正式工单号，例如：

```text
TK-000001
```

---

## 🗄️ 数据库

项目使用 MySQL 保存核心业务数据，SQL 文件位于 `tables/` 目录。

| 数据表 | 作用 |
|---|---|
| `orders` | 订单信息 |
| `tracks` | 物流轨迹 |
| `policies` | 售后政策原始数据 |
| `tickets` | 售后工单 |

其中 `tickets` 表包含：

```text
id
 ticket_no
order_no
issue
status
created_at
```

---

## 🔍 Milvus + BGE-M3

售后政策采用向量检索方式处理。

### 数据同步

`agent/milvus_data_sync.py` 负责将售后政策数据处理后写入 Milvus。

默认配置：

```env
MODEL_PATH=你的BGE-M3本地模型路径
MODEL_DEVICE=cpu

MILVUS_URI=http://localhost:19530
MILVUS_DATABASE=default
MILVUS_COLLECTION=after_sales_policies
MILVUS_TOKEN=
```

检索时：

1. 加载 BGE-M3；
2. 将用户问题转换为向量；
3. 加载 Milvus Collection；
4. 检索最相关的 3 条政策；
5. 将政策文本与距离返回给 Agent。

---

## 🧠 会话记忆

Agent 使用 LangGraph `InMemorySaver` 保存会话上下文。

前端会为当前页面生成一个 `session_id`：

```text
customer_时间戳
```

后端将其作为 LangGraph 的 `thread_id`。

因此同一会话中可以理解类似：

```text
用户：帮我查一下订单 ORD202609180001

AI：查询到该订单……

用户：那它现在到哪里了？

AI：根据当前订单的物流信息……
```

不同 `session_id` 的对话上下文相互隔离。

> 当前使用的是 `InMemorySaver`，因此记忆数据保存在当前 Python 进程内，服务重启后不会持久化。

---

## ⚡ Redis FAQ

Redis 用于保存售后高频问题，例如：

```text
退货需要什么条件？
换货需要承担运费吗？
订单还没发货可以取消吗？
超过退货期限还能申请吗？
```

### 初始化

项目提供：

```bash
python init_redis_faq.py
```

用于初始化 Redis 高频问题数据。

环境变量：

```env
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
```

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/ltssil/smart_ecommerce_agent.git
cd smart_ecommerce_agent
```

### 2. 创建 Python 环境

推荐使用 Conda：

```bash
conda create -n sog python=3.13
conda activate sog
```

### 3. 安装后端依赖

根据项目当前代码安装对应依赖，核心依赖包括：

```bash
pip install fastapi uvicorn python-dotenv pymysql redis
pip install langchain langgraph langchain-openai langchain-huggingface
pip install pymilvus
```

本地使用 BGE-M3 时，还需要安装对应的 PyTorch、Transformers 等模型运行依赖。

### 4. 配置环境变量

复制模板：

Windows：

```powershell
Copy-Item .env_example .env
```

Linux / macOS：

```bash
cp .env_example .env
```

当前 `.env_example` 使用 SiliconFlow 提供的 DeepSeek OpenAI-compatible 接口：

```env
OPENAI_API_KEY=你的API_KEY
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_MODEL=deepseek-ai/DeepSeek-V4-Flash
```

MySQL：

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DATABASE=smart_ecommerce_agent
```

BGE-M3 + Milvus：

```env
MODEL_PATH=D:/Models/bge-m3/models/bge-m3
MODEL_DEVICE=cpu
MILVUS_URI=http://localhost:19530
MILVUS_DATABASE=default
MILVUS_COLLECTION=after_sales_policies
MILVUS_TOKEN=
```

Redis：

```env
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
```

LangSmith 为可选配置：

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=你的LangSmith_API_KEY
LANGSMITH_PROJECT=smart_ecommerce_agent
```

> ⚠️ `.env` 包含 API Key、数据库密码等敏感信息，不要提交到 GitHub。仓库中的 `.env_example` 仅作为配置模板。

### 5. 准备 MySQL

创建项目数据库后执行 `tables/` 中的 SQL 文件，例如：

```text
tables/orders.sql
tables/tracks.sql
tables/policies.sql
tables/tickets.sql
```

确保 MySQL 服务正常运行，并与 `.env` 中的连接配置一致。

### 6. 准备 Redis

确保 Redis 服务运行：

```text
127.0.0.1:6379
```

然后初始化高频问题：

```bash
python init_redis_faq.py
```

### 7. 准备 Milvus + BGE-M3

确保 Milvus 服务运行：

```text
http://localhost:19530
```

准备本地 BGE-M3 模型，并根据实际路径配置 `MODEL_PATH`。

首次使用售后政策检索前，根据项目中的数据同步脚本完成政策向量数据准备。

### 8. 启动后端

```bash
python run.py
```

默认后端地址：

```text
http://127.0.0.1:8000
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

### 9. 启动前端

进入前端目录：

```bash
cd ui
```

安装依赖：

```bash
npm install
```

启动开发服务器：

```bash
npm run dev
```

当前 Vite 开发服务器端口为：

```text
http://localhost:3000
```

前端通过 Vite Proxy 将 `/api` 请求转发到：

```text
http://127.0.0.1:8000
```

---

## 🖥️ Web 前端

最终版本提供完整的客服 Web 页面，主要包括：

### 左侧：智能客服对话

- AI 欢迎语
- 用户 / AI 消息气泡
- SSE 流式回复
- 售后高频问题快捷入口
- Redis FAQ 输入联想

### 右侧：我的订单

实时请求 `/order/list`，展示：

- 订单号
- 商品名称
- 订单状态
- 下单时间
- 订单金额
- 物流单号

### 右侧：售后工单

实时请求 `/ticket/list`，展示：

- 工单号
- 关联订单号
- 售后问题
- 工单状态
- 创建时间

Agent 创建新工单后，前端会在本轮对话结束后刷新订单和工单列表。

---

## 💬 使用示例

启动前后端后，可以直接在浏览器访问：

```text
http://localhost:3000
```

例如：

```text
用户：帮我查一下订单 ORD202609180001

用户：这个订单现在到哪里了？

用户：如果商品有质量问题可以退吗？

用户：我不同意这个处理结果，帮我创建售后工单。
```

Agent 会根据不同问题选择：

```text
订单问题      → query_order
物流问题      → query_track
政策问题      → search_policy
明确争议/人工处理 → create_ticket
```

---

## 🧪 测试

项目提供了多个模块测试脚本：

```bash
python test_db.py
python test_memory.py
python test_milvus_bge.py
python test_pocily_search.py
python test_policy_db.py
python test_policy_tool.py
python test_redis_faq.py
python test_stream.py
python test_ticket_tool.py
python test_tools.py
python test_track.py
```

也可以使用：

```bash
python check_llm.py
```

检查模型 API 配置和连接情况。

---

## 🔐 安全与数据真实性

项目在 Agent System Prompt 和 Tools 层面对数据真实性进行了约束：

- 订单信息必须来自 MySQL 查询结果。
- 物流信息必须来自真实物流查询结果。
- 售后政策必须来自 Milvus 检索结果。
- 工单信息必须来自实际工单创建结果。
- 不得虚构订单号、物流节点、售后政策、工单号或处理结果。
- 创建售后工单前必须确认订单真实存在。
- 用户仅进行普通政策咨询时，不应无必要创建工单。
- “创建工单”不等同于已经接通真实人工客服。

---

## 📌 当前版本能力

当前最终版本已经形成较完整的电商售后 Agent 闭环：

```text
自然语言问题
      ↓
      Agent
      ↓
┌─────┼────────┬──────────┐
│     │        │          │
订单  物流    售后政策    工单
│     │        │          │
MySQL MySQL  BGE-M3      MySQL
              +Milvus
│     │        │          │
└─────┴────────┴──────────┘
              ↓
        Agent 综合回答
              ↓
          SSE 流式输出
              ↓
          Vue Web UI
```

同时通过 Redis 提供售后 FAQ 快捷问题与输入联想，并通过 LangGraph Memory 保持多轮对话上下文。

---

## 📄 License

本项目主要用于学习、课程实践和 AI Agent 应用开发实践。