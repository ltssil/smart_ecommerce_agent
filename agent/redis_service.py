import json
import os

import redis
from dotenv import load_dotenv


load_dotenv()


REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

FAQ_KEY = "after_sales_faq"


_redis_client = None


def get_redis_client():
    """获取 Redis 客户端，只初始化一次。"""

    global _redis_client

    if _redis_client is None:
        _redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
        )

    return _redis_client


def save_faqs(faqs: list[str]) -> bool:
    """保存售后高频问题。"""

    client = get_redis_client()

    client.set(
        FAQ_KEY,
        json.dumps(
            faqs,
            ensure_ascii=False,
        ),
    )

    return True


def get_faqs() -> list[str]:
    """读取全部售后高频问题。"""

    client = get_redis_client()

    value = client.get(FAQ_KEY)

    if not value:
        return []

    return json.loads(value)


def suggest_faq(keyword: str, limit: int = 5) -> list[str]:
    """根据用户输入匹配售后高频问题。"""

    keyword = keyword.strip()

    if not keyword:
        return []

    faqs = get_faqs()

    results = []

    for faq in faqs:
        if keyword in faq:
            results.append(faq)

        if len(results) >= limit:
            break

    return results