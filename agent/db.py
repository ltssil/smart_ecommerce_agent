# -*- coding: utf-8 -*-

import os

import pymysql
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """
    创建 MySQL 数据库连接。
    """

    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "smart_ecommerce_agent"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )