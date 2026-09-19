# -*- coding: utf-8 -*-

import os

from dotenv import load_dotenv

from agent.tools import (
    get_embeddings,
    get_milvus_client,
)


load_dotenv()


COLLECTION_NAME = os.getenv(
    "MILVUS_COLLECTION",
    "after_sales_policies"
)


def search_policy(query: str, limit: int = 3):
    """使用 BGE-M3 + Milvus 检索最相关的售后政策。"""

    embeddings = get_embeddings()
    client = get_milvus_client()

    # Milvus 服务重启后，Collection 可能处于 released 状态。
    # 检索前主动 load，保证 Collection 可以正常搜索。
    client.load_collection(COLLECTION_NAME)

    query_vector = embeddings.embed_query(query)

    results = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        anns_field="vector",
        output_fields=["text"],
        limit=limit,
    )

    return results[0] if results else []


def main():
    print("=" * 60)
    print("售后政策语义检索测试")
    print("=" * 60)

    queries = [
        "我的商品还能退吗？",
        "超过七天还能退货吗？",
        "质量有问题退货谁承担运费？",
        "我想换一个新的可以吗？",
        "商品还没发货怎么办？",
    ]

    for query in queries:
        print()
        print("-" * 60)
        print(f"查询：{query}")
        print("-" * 60)

        results = search_policy(query, limit=3)

        if not results:
            print("没有检索到相关政策")
            continue

        for rank, hit in enumerate(results, start=1):
            text = hit["entity"]["text"]
            distance = hit["distance"]

            print(f"\n第 {rank} 条")
            print(f"距离：{distance:.4f}")
            print(f"政策：{text}")


if __name__ == "__main__":
    main()