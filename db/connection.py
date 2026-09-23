# -*- coding: utf-8 -*-
"""PyMySQL 连接管理：统一从 config 读取配置，返回带字典游标的数据库连接。"""
import pymysql

from config import DB_CONFIG


def get_connection():
    """获取一个数据库连接。

    使用 DictCursor，查询结果每行是 {列名: 值} 的字典，
    方便直接转 DataFrame 展示或转 JSON 传给大模型。
    """
    return pymysql.connect(
        **DB_CONFIG,
        cursorclass=pymysql.cursors.DictCursor,
    )


def test_connection() -> bool:
    """测试数据库能否正常连接，供界面在查询前做检查。"""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False


def get_genres() -> list[str]:
    """获取歌曲表中的全部流派取值（供界面筛选下拉框与提示词使用）。"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT genre FROM songs WHERE genre IS NOT NULL ORDER BY genre")
            return [row["genre"] for row in cursor.fetchall()]
    finally:
        conn.close()
