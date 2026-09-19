# -*- coding: utf-8 -*-

from agent.db import get_connection


def main():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    policy_id,
                    scenario,
                    rule,
                    basis
                FROM policies
                ORDER BY policy_id
            """

            cursor.execute(sql)
            rows = cursor.fetchall()

        print("=" * 60)
        print("售后政策数据库测试")
        print("=" * 60)

        print(f"共查询到 {len(rows)} 条政策")

        for row in rows:
            print()
            print(f"ID：{row['policy_id']}")
            print(f"场景：{row['scenario']}")
            print(f"规则：{row['rule']}")
            print(f"依据：{row['basis']}")

        print()
        print("=" * 60)
        print("政策数据库测试完成")
        print("=" * 60)

    finally:
        connection.close()


if __name__ == "__main__":
    main()