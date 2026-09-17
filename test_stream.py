# -*- coding: utf-8 -*-

import asyncio  # 导入asyncio，用于运行异步代码

from agent.stream_agent import assistant_query  # 导入流式Agent函数


async def main():
    """测试Agent流式输出。"""

    print("=" * 60)  # 输出分隔线
    print("开始测试流式输出")  # 输出测试标题
    print("=" * 60)  # 输出分隔线

    async for data in assistant_query(  # 调用流式Agent并遍历输出
        "你好，请简单介绍一下你自己。",
        session_id="stream_test",
    ):
        print(data, end="")  # 原样输出SSE数据

    print()  # 输出换行
    print("=" * 60)  # 输出结束分隔线
    print("流式输出测试结束")  # 输出结束信息


if __name__ == "__main__":  # 判断是否直接运行该文件
    asyncio.run(main())  # 启动异步主函数