# -*- coding: utf-8 -*-
"""
stream_agent.py —— 把智能体的回复改造成流式输出

作用：
    调用第02讲已经完成的智能体，
    将模型生成的内容逐段转换成SSE格式的数据。

当前第03讲：
    还没有业务工具，所以主要验证：
    Agent → astream() → SSE
"""

import json  # 导入json，用于将Python字典转换成JSON字符串

from langchain_core.messages import ToolMessage  # 导入工具消息类型，后续挂工具时需要过滤

from agent.agent_builder import construct_agent  # 导入第02讲已经完成的Agent构建函数


def _content_to_text(content) -> str:
    """把模型消息内容统一转换成纯文本。"""

    if isinstance(content, str):  # 如果模型直接返回字符串
        return content  # 直接返回字符串

    if isinstance(content, list):  # 如果模型返回的是内容块列表
        parts = []  # 创建列表，用于保存每个内容块

        for block in content:  # 遍历所有内容块
            if isinstance(block, dict):  # 如果当前内容块是字典
                parts.append(block.get("text") or "")  # 获取text字段并加入列表

            elif isinstance(block, str):  # 如果当前内容块本身就是字符串
                parts.append(block)  # 直接加入列表

        return "".join(parts)  # 将所有内容块拼接成完整文本

    return ""  # 其他类型的内容暂时返回空字符串


def _sse(payload: dict) -> str:
    """将字典转换成一条SSE消息。"""

    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"  # 按SSE格式返回数据


async def assistant_query(
    user_query: str,
    session_id: str = "sid_123",
):
    """接收用户问题，并逐段产生SSE数据。"""

    try:  # 捕获Agent执行过程中的异常

        assistant = await construct_agent()  # 获取第02讲已经组装好的Agent

        config = {  # 创建本次会话的运行配置
            "configurable": {  # LangGraph的可配置参数
                "thread_id": session_id,  # 使用session_id区分不同会话
            }
        }

        stream_iter = assistant.astream(  # 启动Agent流式调用
            input={  # 设置Agent输入
                "messages": [  # 设置消息列表
                    {
                        "role": "user",  # 指定消息角色为用户
                        "content": user_query,  # 设置用户输入内容
                    }
                ]
            },
            config=config,  # 传入会话配置
            stream_mode="messages",  # 按消息片段进行流式输出
        )

        async for chunk in stream_iter:  # 异步遍历模型产生的每一个消息片段

            message = chunk[0]  # 获取消息对象

            if isinstance(message, ToolMessage):  # 如果是工具执行结果
                continue  # 跳过工具消息，不直接展示给用户

            text = _content_to_text(message.content)  # 将消息内容转换成字符串

            if not text:  # 如果当前片段没有文本内容
                continue  # 跳过当前片段

            yield _sse({  # 产生一条SSE消息
                "content": text,  # 当前输出文本
                "type": "token",  # 标记当前数据类型为token
            })

    except Exception as error:  # 如果Agent执行过程中发生异常

        yield _sse({  # 产生一条错误SSE消息
            "type": "error",  # 标记数据类型为error
            "error": f"{type(error).__name__}: {error}",  # 返回异常类型和异常信息
        })