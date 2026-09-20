from agent.redis_service import get_faqs, suggest_faq


print("=" * 60)
print("全部 FAQ")
print("=" * 60)

for faq in get_faqs():
    print(faq)


print()
print("=" * 60)
print("输入：退")
print("=" * 60)

for faq in suggest_faq("退"):
    print(f"- {faq}")


print()
print("=" * 60)
print("输入：运")
print("=" * 60)

for faq in suggest_faq("运"):
    print(f"- {faq}")


print()
print("=" * 60)
print("输入：换")
print("=" * 60)

for faq in suggest_faq("换"):
    print(f"- {faq}")