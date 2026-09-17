# -*- coding: utf-8 -*-
"""
test_memory.py —— 验证电商售后智能客服的对话记忆

测试两个场景：

1. 同一个session_id：
   第二次提问应该能够记住第一次提供的信息。

2. 换一个session_id：
   新会话不应该看到之前会话的内容。
"""

import asyncio  # 导入asyncio，用于运行异步函数

from agent.agent_builder import ask  # 导入Agent的ask函数


async def main():
    """执行记忆测试。"""

    print("=" * 60)  # 输出分隔线
    print("① 同一个会话（session_id = customer_A）")  # 输出测试场景
    print("=" * 60)  # 输出分隔线

    first = "你好，我叫小王，我的订单号是10001。"  # 第一轮消息

    print(f"用户：{first}")  # 输出第一轮用户消息

    print(  # 输出第一轮Agent回复
        f"助手：{await ask(first, session_id='customer_A')}"
    )

    print()  # 输出空行

    second = "我刚才说的订单号是多少？"  # 第二轮消息

    print(f"用户：{second}")  # 输出第二轮用户消息

    print(  # 输出第二轮Agent回复
        f"助手：{await ask(second, session_id='customer_A')}"
    )

    print()  # 输出空行
    print("=" * 60)  # 输出分隔线
    print("② 换一个会话（session_id = customer_B）")  # 输出测试场景
    print("=" * 60)  # 输出分隔线

    print(f"用户：{second}")  # 在新会话中重新询问同一个问题

    print(  # 输出新会话Agent回复
        f"助手：{await ask(second, session_id='customer_B')}"
    )


if __name__ == "__main__":  # 判断是否直接运行该文件
    asyncio.run(main())  # 启动异步主函数