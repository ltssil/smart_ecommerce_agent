from agent.tools import create_ticket


print("=" * 60)
print("测试 1：创建正常售后工单")
print("=" * 60)

result = create_ticket.invoke({
    "order_no": "ORD202609180001",
    "issue": "退货运费承担问题存在争议，需要人工处理",
})

print(result)


print()
print("=" * 60)
print("测试 2：使用不存在的订单号")
print("=" * 60)

result = create_ticket.invoke({
    "order_no": "ORD999999999999",
    "issue": "我要申请售后",
})

print(result)


print()
print("=" * 60)
print("测试 3：空问题")
print("=" * 60)

result = create_ticket.invoke({
    "order_no": "ORD202609180001",
    "issue": "   ",
})

print(result)