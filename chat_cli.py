# -*- coding: utf-8 -*-
"""
chat_cli.py —— 电商售后智能客服命令行入口

作用：
    1. 直接在命令行和智能客服对话
    2. 验证 Agent 是否能够正常工作
    3. 验证同一个 session_id 是否能够保持上下文
"""

import argparse  # 导入argparse，用于处理命令行参数
import asyncio  # 导入asyncio，用于运行异步函数

from agent.agent_builder import ask  # 导入Agent的ask函数


async def chat_demo():
    """自动运行一组测试问题。"""

    session_id = "cli_demo"  # 设置本次演示使用的会话ID

    questions = [  # 定义测试问题
        "你好，我想咨询一下退货问题。",  # 测试售后咨询
        "我的订单号是10001。",  # 测试订单号上下文
        "那我还能退吗？",  # 测试连续对话
    ]

    for question in questions:  # 依次处理每一个问题
        print("=" * 60)  # 输出分隔线
        print(f"用户：{question}")  # 输出用户问题

        answer = await ask(  # 调用Agent
            question,  # 传入用户问题
            session_id=session_id,  # 使用同一个会话ID
        )

        print(f"助手：{answer}")  # 输出Agent回答
        print()  # 输出空行


async def chat_interactive():
    """进入交互式命令行聊天模式。"""

    session_id = "cli_user"  # 设置当前命令行会话ID

    print("=" * 60)  # 输出标题分隔线
    print("电商售后智能客服")  # 输出系统名称
    print("输入 exit 或 quit 退出。")  # 输出退出说明
    print("=" * 60)  # 输出标题分隔线

    while True:  # 持续等待用户输入
        question = input("你：").strip()  # 读取用户输入并去除首尾空格

        if not question:  # 如果用户没有输入内容
            continue  # 跳过本轮

        if question.lower() in {"exit", "quit"}:  # 判断是否退出
            print("对话结束。")  # 输出结束提示
            break  # 结束循环

        try:  # 捕获调用Agent过程中可能出现的异常
            answer = await ask(  # 调用Agent
                question,  # 传入用户问题
                session_id=session_id,  # 使用当前会话ID
            )

            print(f"助手：{answer}")  # 输出Agent回答
            print()  # 输出空行

        except Exception as error:  # 捕获异常
            print(f"发生错误：{type(error).__name__}: {error}")  # 输出错误信息


async def main():
    """程序主入口。"""

    parser = argparse.ArgumentParser(  # 创建命令行参数解析器
        description="电商售后智能客服命令行程序"  # 设置程序说明
    )

    parser.add_argument(  # 添加demo参数
        "--demo",  # 参数名称
        action="store_true",  # 使用后将其设置为True
        help="运行预设测试问题",  # 参数帮助信息
    )

    args = parser.parse_args()  # 解析命令行参数

    if args.demo:  # 如果用户指定了--demo
        await chat_demo()  # 执行自动演示
    else:  # 否则
        await chat_interactive()  # 进入交互模式


if __name__ == "__main__":  # 判断是否直接运行该文件
    asyncio.run(main())  # 启动异步主函数