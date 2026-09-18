# -*- coding: utf-8 -*-
"""query_logs 表读写：Agent 每次查询都记录一条日志，并供侧边栏展示历史记录。"""
from db.connection import get_connection

_INSERT_SQL = """
    INSERT INTO query_logs (user_question, generated_sql, is_success, exec_time_ms)
    VALUES (%s, %s, %s, %s)
"""


def write_log(user_question: str, generated_sql: str, is_success: int, exec_time_ms: int) -> None:
    """写入一条查询日志。is_success：1=成功，0=失败。"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                _INSERT_SQL,
                (user_question, generated_sql, int(is_success), exec_time_ms),
            )
        conn.commit()
    finally:
        conn.close()


def get_recent_logs(limit: int = 10) -> list[dict]:
    """按时间倒序取最近 n 条日志，供侧边栏展示。"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT log_id, user_question, generated_sql, is_success, "
                "exec_time_ms, created_at FROM query_logs ORDER BY log_id DESC LIMIT %s",
                (limit,),
            )
            return list(cursor.fetchall())
    finally:
        conn.close()
