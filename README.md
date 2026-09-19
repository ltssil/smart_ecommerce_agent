# 🛍️ Smart E-commerce Agent

基于大语言模型（LLM）与 Agent 技术构建的**电商售后智能客服系统**。

项目围绕真实电商售后场景，将大模型、工具调用、会话记忆、MySQL 数据查询、Milvus 向量检索以及 FastAPI 服务结合起来，让用户可以通过自然语言查询订单、物流信息，并检索相关售后政策。

## ✨ 项目特点

- 🤖 **LLM + Agent**：使用 LangChain / LangGraph 相关能力构建智能体，让模型根据用户问题自主选择工具。
- 🔍 **订单查询**：根据订单号查询商品、下单时间、金额、订单状态和物流单号。
- 🚚 **物流查询**：根据订单号查询对应物流单号及完整物流轨迹。
- 📚 **售后政策检索**：使用 BGE-M3 生成向量，通过 Milvus 检索相关售后政策。
- 🧠 **会话记忆**：基于 LangGraph `InMemorySaver` 保存当前进程中的会话上下文，不同 `session_id` 相互隔离。
- ⚡ **流式输出**：通过 FastAPI + SSE 将 Agent 的回答以流式方式返回。
- 🌐 **REST API**：提供 `/chat`、`/health`、`/order/list`、`/ticket/list` 等 HTTP 接口。
- 📊 **LangSmith 可选追踪**：支持配置 LangSmith，对 Agent 执行过程进行追踪和调试。

## 🏗️ 系统架构

```text
用户
 │
 ▼
FastAPI
 │
 │ POST /chat
 ▼
Agent
 │
 ├── LLM（DeepSeek / OpenAI-compatible API）
 │
 ├── 会话记忆
 │
 └── Tools
      │
      ├── query_order ──────► MySQL
      │
      ├── query_track ──────► MySQL
      │
      └── search_policy ────► BGE-M3 ───► Milvus
```

## 🧰 技术栈

| 技术 | 用途 |
|---|---|
| Python | 项目主要开发语言 |
| LangChain | LLM 与 Agent 能力集成 |
| LangGraph | Agent 编排与会话记忆 |
| DeepSeek | 大语言模型，通过 OpenAI-compatible API 调用 |
| FastAPI | 后端 HTTP API |
| Uvicorn | ASGI 服务运行 |
| MySQL | 订单、物流等业务数据存储 |
| Milvus | 售后政策向量检索 |
| BGE-M3 | 文本向量化 |
| LangSmith | Agent 调试与链路追踪（可选） |

## 📁 项目结构

```text
smart_ecommerce_agent/
├── agent/
│   ├── agent_builder.py       # Agent 构建与会话记忆
│   ├── config.py              # Agent 相关配置
│   ├── db.py                  # MySQL 数据库连接
│   ├── milvus_data_sync.py    # 数据同步到 Milvus
│   ├── stream_agent.py        # Agent 流式处理
│   ├── tools.py               # Agent 工具：订单、物流、售后政策
│   └── prompts/
│       └── system_prompt.txt  # Agent 系统提示词
│
├── api/
│   └── main.py                # FastAPI 接口层
│
├── chat_cli.py                # 命令行对话入口
├── check_llm.py               # LLM 连接检查
├── run.py                     # FastAPI 服务启动入口
├── test_db.py                 # 数据库测试
├── test_memory.py             # 会话记忆测试
├── test_milvus_bge.py         # BGE-M3 / Milvus 测试
├── test_pocily_search.py      # 售后政策检索测试
├── test_policy_db.py          # 售后政策数据库测试
├── test_policy_tool.py        # 售后政策工具测试
├── test_stream.py             # 流式输出测试
├── .env_example               # 环境变量配置示例
└── README.md
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/ltssil/smart_ecommerce_agent.git
cd smart_ecommerce_agent
```

### 2. 创建 Python 虚拟环境

建议使用 Conda：

```bash
conda create -n sog python=3.13
conda activate sog
```

### 3. 安装依赖

根据项目当前代码安装所需依赖，例如：

```bash
pip install fastapi uvicorn python-dotenv pymysql
pip install langchain langgraph langchain-openai langchain-huggingface
pip install pymilvus
```

如果本地使用 BGE-M3，还需要根据实际运行环境安装对应的 PyTorch、Transformers 等依赖。

### 4. 配置环境变量

复制 `.env_example` 为 `.env`：

```bash
copy .env_example .env
```

Linux / macOS：

```bash
cp .env_example .env
```

然后填写自己的配置。项目当前示例包含以下配置项：

```env
OPENAI_API_KEY=你的模型API_KEY
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DATABASE=smart_ecommerce_agent
```

如果需要使用 LangSmith，可以继续配置：

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=你的LangSmith_API_KEY
LANGSMITH_PROJECT=smart_ecommerce_agent
```

> ⚠️ `.env` 中包含 API Key 和数据库密码等敏感信息，不要提交到 GitHub。项目已经提供 `.env_example` 作为配置模板。

### 5. 准备 MySQL

项目的订单查询和物流查询工具依赖 MySQL 数据库。

主要涉及的数据包括：

- `orders`：订单信息
- `tracks`：物流轨迹

数据库连接参数通过 `.env` 配置。

### 6. 准备 Milvus 与 BGE-M3

售后政策检索使用 BGE-M3 对用户问题进行向量化，再通过 Milvus 检索相关政策。

相关环境变量可以配置为：

```env
MODEL_PATH=你的BGE-M3模型路径
MODEL_DEVICE=cpu

MILVUS_URI=http://localhost:19530
MILVUS_TOKEN=
MILVUS_DATABASE=default
MILVUS_COLLECTION=after_sales_policies
```

在正式进行政策检索前，需要确保 Milvus 服务已经启动，并完成售后政策数据的向量化与同步。

## ▶️ 运行项目

### 启动 FastAPI 后端

```bash
python run.py
```

启动成功后：

```text
http://localhost:8000
```

FastAPI 自动生成的接口文档：

```text
http://localhost:8000/docs
```

也可以直接使用 Uvicorn：

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## 🔌 API 接口

### `POST /chat`

智能客服对话接口，通过 SSE 流式返回 Agent 回复。

请求示例：

```json
{
  "query": "帮我查一下订单 ORD10001 的物流",
  "session_id": "sid_123"
}
```

### `GET /health`

健康检查接口。

返回示例：

```json
{
  "status": "ok",
  "service": "smart-ecommerce-agent"
}
```

### `GET /order/list`

查询订单列表，为前端“我的订单”区域提供数据。

### `GET /ticket/list`

售后工单接口。目前接口已经预留，但工单数据暂未接入真实 `tickets` 表。

## 🧠 Agent 工具

当前 Agent 注册了三个主要工具：

### 1. `query_order`

根据订单号查询：

- 商品名称
- 下单时间
- 订单金额
- 订单状态
- 物流单号

如果订单不存在，会明确返回“订单不存在”，不会生成虚假订单信息。

### 2. `query_track`

根据订单号查询物流信息：

```text
订单号
  ↓
查询物流单号
  ↓
查询 tracks 表
  ↓
按时间升序返回物流轨迹
```

如果订单不存在、尚未发货或暂无物流轨迹，会返回对应状态信息。

### 3. `search_policy`

用于检索售后政策，例如：

- 退货期限
- 换货规则
- 运费承担
- 商品质量问题
- 二次销售
- 待发货取消

该工具负责**检索相关政策**，最终的售后处理结论由 Agent 结合订单信息和政策内容进行回答。

## 💬 使用示例

启动服务后，可以在 `/docs` 中测试接口，也可以使用 PowerShell：

```powershell
$body = '{"query":"帮我查一下订单 ORD10001 的物流","session_id":"sid_123"}'
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -ContentType "application/json" -Body $body
```

也可以运行项目中的命令行客户端：

```bash
python chat_cli.py
```

## 🧪 测试

项目提供了多个测试脚本，用于分别验证不同模块：

```bash
python test_db.py
python test_memory.py
python test_milvus_bge.py
python test_pocily_search.py
python test_policy_db.py
python test_policy_tool.py
python test_stream.py
```

## 🔐 安全说明

- 不要将真实 API Key、数据库密码等敏感配置提交到 Git。
- 使用 `.env` 保存本地配置，提交时使用 `.env_example` 作为模板。
- Agent 查询订单和物流时以数据库实际返回结果为准，不应编造订单或物流信息。
- 售后政策检索结果用于提供相关政策依据，具体业务规则应以实际业务系统配置为准。

## 📌 项目状态

当前项目重点完成了电商售后智能客服的核心 Agent 能力，包括：

- LLM 接入
- Agent 构建
- 会话记忆
- 订单查询工具
- 物流查询工具
- BGE-M3 + Milvus 售后政策检索
- FastAPI 接口
- SSE 流式输出

`/ticket/list` 当前为接口预留，后续可以继续接入真实售后工单系统。

## 📄 License

本项目主要用于学习、课程实践与 AI Agent 应用开发研究。