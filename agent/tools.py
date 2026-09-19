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