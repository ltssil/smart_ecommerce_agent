# -*- coding: utf-8 -*-
"""
agent_builder.py —— 把"零件"组装成一个智能体

Agent = 模型(LLM) + 工具(Tools) + 记忆(Checkpointer) + 系统提示词(System Prompt)

这一讲先组装一个"会说话、能记住上下文"的智能体，工具位先空着。
从第 04 讲开始，每做完一个功能，就往 tools 里挂一个工具。
"""

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from agent.tools import ALL_TOOLS

load_dotenv()

# 项目根目录（本文件在 agent/ 下，所以往上一级）
ROOT_PATH = Path(__file__).resolve().parent.parent

# 全局单例：智能体只构建一次，之后每次对话复用
_agent = None

async def construct_agent():
    """构建智能体（全局单例）"""
    global _agent
    if _agent is not None:
        return _agent

    # s1-选一个模型作为"大脑"
    #    模型名从 .env 读，方便在云端模型和本机模型之间切换
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL") or "gpt-4o-mini",
        temperature=0,
    )

    # s2-读取系统提示词
    #    提示词写在单独的文件里，不塞进代码——改措辞不用动代码
    prompt_file = ROOT_PATH / "agent" / "prompts" / "system_prompt.txt"
    system_prompt = prompt_file.read_text(encoding="utf-8")

    # s3-把"今天几号"补进提示词末尾
    #    模型的训练数据有截止日期，它并不知道"今天"是哪天，所以要告诉它。
    #    注意：这句必须并进系统提示词，不能作为一条消息塞进对话里——
    #    那样会被模型当成"用户说的话"，回复里可能莫名其妙冒出日期。
    today = datetime.now()
    weekday_cn = "一二三四五六日"[today.weekday()]
    system_prompt += (
        f"\n\n# 当前时间：\n"
        f"    今天是 {today:%Y-%m-%d}，星期{weekday_cn}，需要判断日期时以此为准。\n"
    )

    # s3-准备记忆：InMemorySaver 把对话历史存在内存里
    #    有了它，同一会话里客人说"那订晚上七点吧"，模型才知道"那"指的是什么
    checkpointer = InMemorySaver()

    # s4-组装
    _agent = create_agent(
        model=llm,
        tools=ALL_TOOLS,
        system_prompt=system_prompt,
        checkpointer=checkpointer
    )
    return _agent


async def ask(query: str, session_id: str = "sid_123") -> str:
    """问一句、答一句：非流式版本，返回完整回复文本

    session_id 就是 thread_id：不同会话用不同 id，对话历史互不干扰。
    """
    assistant = await construct_agent()

    # 只发用户这一句。"今天几号"已经在构建智能体时并进系统提示词了，
    # 不再作为一条消息混进对话里。
    config = {"configurable": {"thread_id": session_id}}
    response = await assistant.ainvoke(
        input={"messages": [{"role": "user", "content": query}]},
        config=config,
    )
    return response["messages"][-1].content