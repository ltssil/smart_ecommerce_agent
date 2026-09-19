# -*- coding: utf-8 -*-
"""
run.py —— 电商售后智能客服后端启动入口

运行：
    python run.py

启动后：
    http://localhost:8000
    http://localhost:8000/docs
"""

import uvicorn  # 导入Uvicorn


if __name__ == "__main__":
    print("=" * 60)  # 输出分隔线
    print("      🛍️ 电商售后智能客服 · 后端启动中")  # 输出系统名称
    print("=" * 60)  # 输出分隔线
    print("📍 接口地址：http://localhost:8000")  # 输出接口地址
    print("📖 接口文档：http://localhost:8000/docs")  # 输出接口文档地址
    print("=" * 60)  # 输出分隔线

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
    )