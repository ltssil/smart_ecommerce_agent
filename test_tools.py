# -*- coding: utf-8 -*-

from agent.tools import query_order


def main():
    print("=" * 60)
    print("测试 1：查询存在的订单")
    print("=" * 60)

    result = query_order.invoke(
        {
            "order_no": "ORD202609180001"
        }
    )

    print(result)

    print()
    print("=" * 60)
    print("测试 2：查询不存在的订单")
    print("=" * 60)

    result = query_order.invoke(
        {
            "order_no": "ORD999999999999"
        }
    )

    print(result)


if __name__ == "__main__":
    main()