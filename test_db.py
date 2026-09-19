# -*- coding: utf-8 -*-

from agent.db import get_connection


def main():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 AS result")
            result = cursor.fetchone()

        print("MySQL 连接成功！")
        print("测试结果：", result)

    finally:
        connection.close()


if __name__ == "__main__":
    main()