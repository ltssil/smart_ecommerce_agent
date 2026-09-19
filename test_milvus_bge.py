# -*- coding: utf-8 -*-

import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from pymilvus import MilvusClient


load_dotenv()


def main():
    print("=" * 60)
    print("第五讲前置环境检查")
    print("=" * 60)

    # 1. 检查 BGE-M3 路径
    model_path = os.getenv("MODEL_PATH")

    print("\n[1] BGE-M3 模型")
    print("模型路径：", model_path)

    if not model_path:
        print("❌ MODEL_PATH 未配置")
        return

    if not os.path.isdir(model_path):
        print("❌ 模型路径不存在")
        return

    print("✅ 模型路径存在")

    # 2. 加载 BGE-M3
    print("\n[2] 加载 BGE-M3")

    device = os.getenv("MODEL_DEVICE", "").strip()
    model_kwargs = {"device": device} if device else {}

    embeddings = HuggingFaceEmbeddings(
        model=model_path,
        model_kwargs=model_kwargs,
        encode_kwargs={
            "normalize_embeddings": True
        },
    )

    vector = embeddings.embed_query("我的商品可以退货吗？")

    print("✅ BGE-M3 加载成功")
    print("向量维度：", len(vector))

    # 3. 检查 Milvus
    print("\n[3] 连接 Milvus")

    uri = os.getenv(
        "MILVUS_URI",
        "http://localhost:19530"
    )

    client = MilvusClient(
        uri=uri,
        token=os.getenv("MILVUS_TOKEN", ""),
        db_name=os.getenv(
            "MILVUS_DATABASE",
            "default"
        ),
    )

    print("✅ Milvus 连接成功")
    print("服务地址：", uri)

    # 4. 查看 Collection
    collection_name = os.getenv(
        "MILVUS_COLLECTION",
        "after_sales_policies"
    )

    print("\n[4] Collection")
    print("名称：", collection_name)
    print(
        "是否存在：",
        client.has_collection(collection_name)
    )

    print("\n" + "=" * 60)
    print("第五讲前置环境检查完成")
    print("=" * 60)


if __name__ == "__main__":
    main()