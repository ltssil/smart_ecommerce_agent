from agent.tools import get_milvus_client


collection_name = "after_sales_policies"

client = get_milvus_client()

# 查看 Collection 是否存在
if not client.has_collection(collection_name):
    print(f"Collection 不存在：{collection_name}")
    exit()

# 查询 Collection 中的数据
rows = client.query(
    collection_name=collection_name,
    filter="",
    output_fields=["id", "text"],
    limit=20,
)

print("=" * 60)
print(f"Collection：{collection_name}")
print(f"查询到 {len(rows)} 条数据")
print("=" * 60)

for row in rows:
    print(f"ID：{row['id']}")
    print(f"政策内容：{row['text']}")
    print("-" * 60)