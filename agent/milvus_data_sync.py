# -*- coding: utf-8 -*-

"""
milvus_data_sync.py —— 售后政策向量同步脚本

流程：

    MySQL policies
        ↓
    拼成自然语言
        ↓
    BGE-M3
        ↓
    1024 维向量
        ↓
    Milvus after_sales_policies
"""

import os
import time

from dotenv import load_dotenv

from agent.db import get_connection
from agent.tools import get_embeddings, get_milvus_client


load_dotenv()


COLLECTION_NAME = os.getenv(
    "MILVUS_COLLECTION",
    "after_sales_policies"
)

def query_all_policies() -> list[dict]:
    """从 MySQL 查询全部售后政策。"""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    policy_id,
                    scenario,
                    rule,
                    basis
                FROM policies
                ORDER BY policy_id
            """

            cursor.execute(sql)

            return cursor.fetchall()

    finally:
        connection.close()

def build_policy_text(policy: dict) -> str:
    return (
        f"售后场景：{policy['scenario']}。"
        f"售后规则：{policy['rule']}"
        f"规则依据：{policy['basis']}。"
    )

def data_sync():
    """MySQL → 文本 → BGE-M3 → Milvus。"""

    # ========================================================
    # 1. 从 MySQL 读取政策
    # ========================================================

    policies = query_all_policies()

    print(
        f"[1/4] 从 MySQL 读取到 "
        f"{len(policies)} 条售后政策"
    )

    if not policies:
        raise RuntimeError(
            "policies 表中没有数据，无法同步。"
        )

    # ========================================================
    # 2. 拼接自然语言
    # ========================================================

    policy_texts = [
        build_policy_text(policy)
        for policy in policies
    ]
    print("[2/4] 政策文本准备完成")
    print("      示例：")
    print(
        "      "
        + policy_texts[0]
    )

    # ========================================================
    # 3. BGE-M3 编码
    # ========================================================

    print(
        "[3/4] 使用 BGE-M3 转换为向量"
    )
    embeddings = get_embeddings()
    vectors = embeddings.embed_documents(
        policy_texts
    )
    print(
        f"      向量数量：{len(vectors)}"
    )
    print(
        f"      向量维度：{len(vectors[0])}"
    )
    # ========================================================
    # 4. 写入 Milvus
    # ========================================================
    client = get_milvus_client()

    if client.has_collection(
        COLLECTION_NAME
    ):
        print(
            f"      删除旧 Collection："
            f"{COLLECTION_NAME}"
        )

        client.drop_collection(
            COLLECTION_NAME
        )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=len(vectors[0])
    )

    rows = []

    for policy, vector, text in zip(
        policies,
        vectors,
        policy_texts
    ):
        rows.append(
            {
                "id": policy["policy_id"],
                "vector": vector,
                "text": text
            }
        )
    result = client.insert(
        collection_name=COLLECTION_NAME,
        data=rows
    )
    print(
        f"[4/4] Milvus 写入完成：{result}"
    )

    # ========================================================
    # 5. 加载 Collection
    # ========================================================

    client.load_collection(
        COLLECTION_NAME
    )

    # load 是异步过程，等待真正进入 Loaded 状态。
    for _ in range(30):
        state = str(
            client.get_load_state(
                COLLECTION_NAME
            )
        )
        if (
            "Loaded" in state
            and "NotLoad" not in state
        ):
            break
        time.sleep(0.2)

    print(
        f"      Collection 已加载："
        f"{COLLECTION_NAME}"
    )
    return len(policies)


if __name__ == "__main__":
    total = data_sync()
    print()
    print("=" * 60)
    print(
        f"完成：{total} 条售后政策"
        f"已经写入 Milvus"
    )
    print("=" * 60)