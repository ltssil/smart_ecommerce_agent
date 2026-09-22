# -*- coding: utf-8 -*-
"""
main.py —— 电商售后智能客服 FastAPI 接口层

第03讲：
    把第02讲只能在命令行运行的智能客服，
    变成浏览器可以访问的HTTP服务。

本阶段真正实现：
    POST /chat

提前占位：
    GET /order/list
    GET /ticket/list
    GET /health
"""

from typing import List, Optional  # 导入类型声明

from dotenv import load_dotenv  # 导入环境变量加载函数
from fastapi import FastAPI  # 导入FastAPI
from pydantic import BaseModel  # 导入Pydantic请求响应模型
from starlette.responses import StreamingResponse  # 导入流式响应

from agent.stream_agent import assistant_query  # 导入Agent流式处理函数
from agent.db import get_connection  # 导入数据库连接
from agent.redis_service import get_faqs, suggest_faq # 导入redis联想函数
from contextlib import asynccontextmanager
from agent.agent_builder import construct_agent
from agent.tools import preload_rag_resources
from agent.redis_service import get_redis_client

load_dotenv()  # 加载.env文件

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 启动时预加载项目依赖。"""

    print("=" * 60)
    print("      系统启动初始化")
    print("=" * 60)

    try:
        # 1. 提前构建 Agent
        await construct_agent()
        print("✅ Agent 初始化完成")

        # 2. 提前加载 BGE-M3 和 Milvus
        preload_rag_resources()
        print("✅ BGE-M3 + Milvus 初始化完成")

        # 3. 提前建立 Redis 连接
        redis_client = get_redis_client()
        redis_client.ping()
        print("✅ Redis 连接正常")

        print("=" * 60)
        print("      所有核心资源初始化完成")
        print("=" * 60)

    except Exception as error:
        print(
            f"❌ 启动初始化失败："
            f"{type(error).__name__}: {error}"
        )
        raise

    yield

# ============================================================
# 1. 创建FastAPI应用
# ============================================================

app = FastAPI(
    title="电商售后智能客服",
    description="基于 LangChain + LangGraph + DeepSeek 的电商售后智能客服系统",
    lifespan=lifespan,
)

# ============================================================
# 2. 请求 / 响应模型
# ============================================================

class ChatRequest(BaseModel):
    """POST /chat 请求体"""
    query: str  # 用户的问题
    session_id: str = "sid_123"  # 当前会话编号


class HealthResponse(BaseModel):
    """GET /health 响应体"""
    status: str  # 服务状态
    service: str  # 服务名称

class FaqResponse(BaseModel):
    success: bool
    query: str
    suggestions: list[str]

class FaqHotResponse(BaseModel):
    success: bool
    suggestions: list[str]
    count: int

class OrderItem(BaseModel):
    """订单信息"""
    order_no: str  # 订单编号
    product_name: str  # 商品名称
    order_time: str  # 下单时间
    amount: float  # 订单金额
    status: str  # 订单状态
    tracking_no: Optional[str] = None  # 物流单号

class OrderListResponse(BaseModel):
    """GET /order/list 响应体"""
    success: bool  # 请求是否成功
    orders: List[OrderItem]  # 订单列表
    count: int  # 订单数量
    message: str  # 返回说明

class TicketItem(BaseModel):
    """售后工单信息"""
    ticket_no: str  # 售后工单编号
    order_no: str  # 关联订单编号
    issue: str  # 售后问题
    status: str  # 工单状态
    created_at: Optional[str] = None  # 创建时间

class TicketListResponse(BaseModel):
    """GET /ticket/list 响应体"""
    success: bool  # 请求是否成功
    tickets: List[TicketItem]  # 工单列表
    count: int  # 工单数量
    message: str  # 返回说明

# ============================================================
# 3. POST /chat —— 智能对话
# ============================================================

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    接收用户问题，通过SSE流式返回Agent回答。
    """
    return StreamingResponse(
        content=assistant_query(
            request.query,
            request.session_id,
        ),
        media_type="text/event-stream",
    )


# ============================================================
# 4. GET /health —— 健康检查
# ============================================================

@app.get("/health", response_model=HealthResponse)
async def health_endpoint():
    """检查后端服务是否正常运行。"""

    return HealthResponse(
        status="ok",
        service="smart-ecommerce-agent",
    )


# ============================================================
# 5. GET /order/list —— 我的订单
# ============================================================

@app.get("/order/list", response_model=OrderListResponse)
async def order_list_endpoint():
    """查询全部订单，提供给前端“我的订单”区域。"""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    order_no,
                    product_name,
                    order_time,
                    amount,
                    status,
                    tracking_no
                FROM orders
                ORDER BY order_time DESC
            """

            cursor.execute(sql)
            rows = cursor.fetchall()

        orders = []

        for row in rows:
            orders.append(
                OrderItem(
                    order_no=row["order_no"],
                    product_name=row["product_name"],
                    order_time=row["order_time"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    amount=float(row["amount"]),
                    status=row["status"],
                    tracking_no=row["tracking_no"],
                )
            )

        return OrderListResponse(
            success=True,
            orders=orders,
            count=len(orders),
            message="success",
        )

    finally:
        connection.close()

# ============================================================
# 6. GET /ticket/list —— 售后工单
# ============================================================

@app.get("/ticket/list", response_model=TicketListResponse)
async def ticket_list_endpoint():
    """查询售后工单列表。"""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    ticket_no,
                    order_no,
                    issue,
                    status,
                    created_at
                FROM tickets
                ORDER BY id DESC
                """
            )

            rows = cursor.fetchall()

        tickets = []

        for row in rows:
            item = dict(row)

            if item.get("created_at"):
                item["created_at"] = str(item["created_at"])

            tickets.append(item)

        return TicketListResponse(
            success=True,
            tickets=tickets,
            count=len(tickets),
            message="售后工单查询成功。",
        )

    except Exception as error:
        return TicketListResponse(
            success=False,
            tickets=[],
            count=0,
            message=f"查询售后工单失败：{type(error).__name__}: {error}",
        )

    finally:
        connection.close()

@app.get("/faq/suggest", response_model=FaqResponse)
async def faq_suggest_endpoint(
    query: str = "",
    limit: int = 5,
):
    """根据用户输入，从 Redis 返回售后高频问题联想。"""

    query = query.strip()

    # 限制联想数量，避免前端一次显示太多内容
    limit = max(1, min(limit, 10))

    suggestions = suggest_faq(
        keyword=query,
        limit=limit,
    )

    return FaqResponse(
        success=True,
        query=query,
        suggestions=suggestions,
    )

@app.get("/faq/hot", response_model=FaqHotResponse)
async def faq_hot_endpoint(limit: int = 5):
    # 限制最多返回 10 个问题
    limit = max(1, min(limit, 10))

    # 从 Redis 获取全部高频问题
    faqs = get_faqs()

    # 只取前面的几个作为首页快捷问题
    suggestions = faqs[:limit]

    return FaqHotResponse(
        success=True,
        suggestions=suggestions,
        count=len(suggestions)
    )