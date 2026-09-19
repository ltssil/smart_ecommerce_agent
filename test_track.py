# -*- coding: utf-8 -*-

from agent.tools import query_track


def main():
    print("=" * 60)
    print("测试 1：查询已签收订单的物流")
    print("=" * 60)

    result = query_track.invoke(
        {"order_no": "ORD202609180001"}
    )
    print(result)

    print()
    print("=" * 60)
    print("测试 2：查询运输中的订单")
    print("=" * 60)

    result = query_track.invoke(
        {"order_no": "ORD202609180002"}
    )
    print(result)

    print()
    print("=" * 60)
    print("测试 3：查询待发货订单")
    print("=" * 60)

    result = query_track.invoke(
        {"order_no": "ORD202609180004"}
    )
    print(result)

    print()
    print("=" * 60)
    print("测试 4：查询不存在的订单")
    print("=" * 60)

    result = query_track.invoke(
        {"order_no": "ORD999999999999"}
    )
    print(result)


if __name__ == "__main__":
    main()