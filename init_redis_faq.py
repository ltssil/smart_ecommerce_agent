from agent.redis_service import save_faqs


FAQS = [
    "退货几天内可以申请？",
    "退货运费谁承担？",
    "质量问题退货运费谁承担？",
    "普通商品退货需要满足什么条件？",
    "商品拆封后还能退吗？",
    "超过7天还能退货吗？",
    "可以换货吗？",
    "换货需要什么条件？",
    "商品还没发货怎么办？",
    "订单还没有物流信息怎么办？",
]


if __name__ == "__main__":
    save_faqs(FAQS)

    print("Redis 售后高频问题初始化完成。")

    for faq in FAQS:
        print(f"- {faq}")