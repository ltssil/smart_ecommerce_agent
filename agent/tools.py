# -*- coding: utf-8 -*-

"""
tools.py —— Agent 工具

当前阶段只实现一个工具：

    query_order(order_no)

作用：
    根据订单号查询订单信息。

数据来源：
    MySQL -> smart_ecommerce_agent.orders
"""

import os
from langchain_huggingface import HuggingFaceEmbeddings
from pymilvus import MilvusClient
from langchain.tools import tool
from agent.db import get_connection

from pydantic import BaseModel, Field

class CreateTicketInput(BaseModel):
    """创建售后工单的输入参数"""

    order_no: str = Field(
        ...,
        description="要创建售后工单的订单号，例如 ORD202609180001",
        min_length=1,
        max_length=64,
    )

    issue: str = Field(
        ...,
        description="用户需要人工处理的售后问题，例如退货运费争议",
        min_length=1,
        max_length=500,
    )

@tool
def query_order(order_no: str) -> dict:
    """
    根据订单号查询订单信息。

    当用户询问订单状态、订单金额、下单时间、物流单号等订单信息时使用。

    如果订单不存在，必须明确返回订单不存在，不能编造订单信息。
    """

    order_no = order_no.strip()

    if not order_no:
        return {
            "found": False,
            "message": "订单号不能为空。"
        }

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
                WHERE order_no = %s
            """

            cursor.execute(sql, (order_no,))
            order = cursor.fetchone()

        if order is None:
            return {
                "found": False,
                "order_no": order_no,
                "message": f"未找到订单 {order_no}。"
            }

        order["order_time"] = order["order_time"].strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        order["amount"] = float(order["amount"])

        return {
            "found": True,
            "order": order
        }

    finally:
        connection.close()

@tool
def query_track(order_no: str) -> dict:
    """
    根据订单号查询物流轨迹。

    使用订单号先查询对应的物流单号，
    再根据物流单号查询物流轨迹。

    如果订单不存在、订单尚未发货或没有物流轨迹，
    都必须明确返回对应信息，不能编造物流数据。
    """

    order_no = order_no.strip()

    if not order_no:
        return {
            "found": False,
            "message": "订单号不能为空。"
        }

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            # 1. 根据订单号查询物流单号
            sql_order = """
                SELECT
                    order_no,
                    status,
                    tracking_no
                FROM orders
                WHERE order_no = %s
            """

            cursor.execute(sql_order, (order_no,))
            order = cursor.fetchone()

            # 2. 订单不存在
            if order is None:
                return {
                    "found": False,
                    "order_no": order_no,
                    "message": f"未找到订单 {order_no}。"
                }

            # 3. 订单存在，但是还没有物流单号
            if not order["tracking_no"]:
                return {
                    "found": False,
                    "order_no": order_no,
                    "status": order["status"],
                    "tracking_no": None,
                    "message": "该订单暂时没有物流单号，可能尚未发货。"
                }

            tracking_no = order["tracking_no"]

            # 4. 根据物流单号查询物流轨迹
            sql_track = """
                SELECT
                    track_time,
                    node,
                    description
                FROM tracks
                WHERE tracking_no = %s
                ORDER BY track_time ASC
            """

            cursor.execute(sql_track, (tracking_no,))
            tracks = cursor.fetchall()

        # 5. 没有找到物流轨迹
        if not tracks:
            return {
                "found": False,
                "order_no": order_no,
                "tracking_no": tracking_no,
                "status": order["status"],
                "message": "暂未查询到该订单的物流轨迹。"
            }

        # 6. 转换时间类型，保证可以直接交给 Agent
        for track in tracks:
            track["track_time"] = track["track_time"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        # 7. 返回完整物流信息
        return {
            "found": True,
            "order_no": order_no,
            "tracking_no": tracking_no,
            "status": order["status"],
            "tracks": tracks
        }

    finally:
        connection.close()

# ============================================================
# 全局单例：BGE-M3 嵌入模型 / Milvus 客户端
# ============================================================

_embeddings = None
_milvus_client = None

def get_embeddings() -> HuggingFaceEmbeddings:
    """获取 BGE-M3 嵌入模型，全局只加载一次。"""
    global _embeddings

    if _embeddings is None:
        device = os.getenv("MODEL_DEVICE", "").strip()

        model_kwargs = {
            "device": device
        } if device else {}

        _embeddings = HuggingFaceEmbeddings(
            model=os.getenv("MODEL_PATH"),
            model_kwargs=model_kwargs,
            encode_kwargs={
                "normalize_embeddings": True
            },
        )

    return _embeddings


def get_milvus_client() -> MilvusClient:
    """获取 Milvus 客户端，全局只创建一次。"""
    global _milvus_client

    if _milvus_client is None:
        _milvus_client = MilvusClient(
            uri=os.getenv(
                "MILVUS_URI",
                "http://localhost:19530"
            ),
            token=os.getenv("MILVUS_TOKEN", ""),
            db_name=os.getenv(
                "MILVUS_DATABASE",
                "default"
            ),
        )

    return _milvus_client

def preload_rag_resources():
    """启动时预加载 BGE-M3 和 Milvus。"""

    collection_name = os.getenv(
        "MILVUS_COLLECTION",
        "after_sales_policies"
    )

    # 1. 加载 BGE-M3
    embeddings = get_embeddings()

    # 2. 预热模型，避免第一次正式请求时才进行模型计算初始化
    embeddings.embed_query("售后政策预热")

    # 3. 创建 Milvus 客户端
    client = get_milvus_client()

    # 4. 检查 Collection 是否存在
    if not client.has_collection(collection_name):
        raise RuntimeError(
            f"Milvus Collection 不存在：{collection_name}"
        )

    # 5. 加载 Collection
    client.load_collection(collection_name)

    # 6. 等待 Collection 真正进入 Loaded 状态
    import time

    for _ in range(30):
        state = str(
            client.get_load_state(collection_name)
        )

        if (
            "Loaded" in state
            and "NotLoad" not in state
        ):
            print(
                f"Milvus Collection 已加载："
                f"{collection_name}"
            )
            return

        time.sleep(0.2)

    raise RuntimeError(
        f"Milvus Collection 加载超时：{collection_name}"
    )

@tool
def search_policy(question: str) -> list[dict]:
    """
    根据用户的售后问题，检索最相关的售后政策。

    适用于：
    - 退货
    - 换货
    - 退货期限
    - 运费承担
    - 商品质量问题
    - 二次销售
    - 待发货取消等售后政策问题

    这里只负责检索政策，不直接判断用户是否一定可以退货或换货。
    最终处理结论需要结合订单信息和具体政策进行判断。
    """

    question = question.strip()

    if not question:
        return [
            {
                "found": False,
                "message": "售后问题不能为空。"
            }
        ]

    collection_name = os.getenv(
        "MILVUS_COLLECTION",
        "after_sales_policies"
    )

    embeddings = get_embeddings()
    client = get_milvus_client()

    query_vector = embeddings.embed_query(question)

    results = client.search(
        collection_name=collection_name,
        data=[query_vector],
        anns_field="vector",
        output_fields=["text"],
        limit=3,
    )

    if not results or not results[0]:
        return [
            {
                "found": False,
                "message": "暂未检索到相关售后政策。"
            }
        ]

    policies = []

    for hit in results[0]:
        text = hit["entity"]["text"]

        policies.append(
            {
                "found": True,
                "policy": text,
                "distance": float(hit["distance"]),
            }
        )

    return policies

@tool(
    args_schema=CreateTicketInput,
    description="创建售后工单。当用户的问题需要人工处理或存在争议时使用。必须提供真实存在的订单号和具体问题描述。"
)
def create_ticket(order_no: str, issue: str) -> dict:
    """
    创建售后工单。

    使用场景：
    1. 用户与售后政策产生争议。
    2. 用户明确要求转人工处理。
    3. 当前问题无法仅通过订单、物流和政策直接解决。

    创建工单前会先检查订单是否存在。
    不存在的订单不能创建工单。
    """

    order_no = order_no.strip()
    issue = issue.strip()

    # 参数再次校验
    if not order_no:
        return {
            "success": False,
            "message": "订单号不能为空。",
        }

    if not issue:
        return {
            "success": False,
            "message": "售后问题不能为空。",
        }

    if len(order_no) > 64:
        return {
            "success": False,
            "message": "订单号长度不能超过64个字符。",
        }

    if len(issue) > 500:
        return {
            "success": False,
            "message": "售后问题描述长度不能超过500个字符。",
        }

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            # 1. 先检查订单是否真实存在
            cursor.execute(
                """
                SELECT order_no
                FROM orders
                WHERE order_no = %s
                LIMIT 1
                """,
                (order_no,),
            )

            order = cursor.fetchone()

            if not order:
                return {
                    "success": False,
                    "message": f"订单 {order_no} 不存在，无法创建售后工单。",
                    "order_no": order_no,
                }

            # 2. 先生成一个临时工单号
            #    最终正式工单号会根据 tickets.id 生成
            import uuid

            temp_ticket_no = uuid.uuid4().hex

            cursor.execute(
                """
                INSERT INTO tickets
                    (ticket_no, order_no, issue, status)
                VALUES
                    (%s, %s, %s, %s)
                """,
                (
                    temp_ticket_no,
                    order_no,
                    issue,
                    "待处理",
                ),
            )

            # 3. 获取刚刚插入的自增 id
            ticket_id = cursor.lastrowid

            # 4. 使用 id 生成正式工单号
            ticket_no = f"TK-{ticket_id:06d}"

            cursor.execute(
                """
                UPDATE tickets
                SET ticket_no = %s
                WHERE id = %s
                """,
                (
                    ticket_no,
                    ticket_id,
                ),
            )

            # 5. 提交事务
            connection.commit()

            # 6. 查询刚创建的工单
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
                WHERE id = %s
                """,
                (ticket_id,),
            )

            ticket = cursor.fetchone()

            if ticket:
                ticket["created_at"] = str(ticket["created_at"])

            return {
                "success": True,
                "message": "售后工单创建成功。",
                "ticket": ticket,
            }

    except Exception as error:
        connection.rollback()

        return {
            "success": False,
            "message": "创建售后工单失败。",
            "error": f"{type(error).__name__}: {error}",
        }

    finally:
        connection.close()

ALL_TOOLS = [
    query_order,
    query_track,
    search_policy,
    create_ticket,
]