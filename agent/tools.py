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

ALL_TOOLS = [
    query_order,
    query_track,

]