# -*- coding: utf-8 -*-

from agent.tools import search_policy


def main():
    queries = [
        "我的商品还能退吗？",
        "超过七天还能退货吗？",
        "质量有问题退货谁承担运费？",
        "我想换一个新的可以吗？",
        "商品还没发货怎么办？",
    ]

    print("=" * 60)
    print("search_policy 工具测试")
    print("=" * 60)

    for query in queries:
        print()
        print("-" * 60)
        print(f"查询：{query}")
        print("-" * 60)

        result = search_policy.invoke(
            {
                "question": query
            }
        )

        for index, item in enumerate(
            result,
            start=1
        ):
            print(f"\n第 {index} 条")
            print(f"距离：{item.get('distance', '-')}")
            print(f"政策：{item.get('policy', item.get('message'))}")


if __name__ == "__main__":
    main()