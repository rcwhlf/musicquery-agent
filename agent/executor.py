# -*- coding: utf-8 -*-
"""Step 3 执行校验：安全拦截 → 执行 SQL → 失败回传大模型自动修正（最多 2 次）→ 写入日志。"""
import re
import time
from datetime import date, datetime, timedelta
from decimal import Decimal

from db.connection import get_connection
from agent.sql_generator import repair_sql
from logs.query_logs import write_log

# 安全拦截：课程要求拦截 DROP/DELETE/UPDATE/INSERT/ALTER，
# 这里额外补充 TRUNCATE 等高危词做双保险。
# 注意：这也会拦截 SELECT 中恰好包含这些单词的极端情况（如 LIKE '%update%'），
# 课程项目中可接受，宁可误拦不可漏拦。
FORBIDDEN_PATTERN = re.compile(
    r"\b(drop|delete|update|insert|alter|truncate|grant|revoke|create|replace)\b",
    re.IGNORECASE,
)

# 首次执行失败后，最多让大模型自动修正重试的次数
MAX_RETRIES = 2


def check_sql_safety(sql: str) -> tuple[bool, str]:
    """安全拦截。返回 (是否拦截, 拦截原因)。"""
    stripped = sql.strip()
    if not stripped:
        return True, "SQL 为空"
    # 只允许查询语句（WITH 开头的 CTE 查询也放行）
    if not re.match(r"^(SELECT|WITH)\b", stripped, re.IGNORECASE):
        return True, "只允许执行 SELECT 查询语句"
    match = FORBIDDEN_PATTERN.search(stripped)
    if match:
        return True, f"检测到禁止的关键词：{match.group(1).upper()}"
    return False, ""


def _normalize_value(value):
    """把查询结果中的特殊类型转为普通值，方便展示和转 JSON 传给大模型。"""
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, timedelta):
        return str(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _run_select(sql: str) -> tuple[list[dict], int]:
    """执行一条 SELECT，返回 (结果行列表, 执行耗时毫秒)。"""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            start = time.perf_counter()
            cursor.execute(sql)
            rows = cursor.fetchall()
            cost_ms = int((time.perf_counter() - start) * 1000)
            return [dict(row) for row in rows], cost_ms
    finally:
        conn.close()


def execute_sql_with_retry(question: str, sql: str) -> dict:
    """执行大模型生成的 SQL，失败时自动让大模型修正后重试，每次结果都写入 query_logs。

    返回 dict：
        success      是否查询成功
        sql          最终实际执行的 SQL
        data         查询结果（list[dict]，已做类型规范化）
        exec_time_ms 最后一次 SQL 执行耗时（毫秒）
        attempts     实际执行次数（>1 说明发生过自动修正）
        error        失败原因（成功时为 None）
    """
    current_sql = sql
    attempts = 0

    while True:
        # 1. 安全拦截（被拦截的 SQL 同样记入日志，便于排查）
        blocked, reason = check_sql_safety(current_sql)
        if blocked:
            write_log(question, current_sql, is_success=0, exec_time_ms=0)
            return {
                "success": False,
                "sql": current_sql,
                "data": [],
                "exec_time_ms": 0,
                "attempts": attempts,
                "error": f"安全拦截：{reason}",
            }

        # 2. 执行 SQL
        attempts += 1
        try:
            rows, cost_ms = _run_select(current_sql)
        except Exception as exc:  # PyMySQL 报错或连接异常，统一进入修正流程
            if attempts > MAX_RETRIES:
                # 首次 + 2 次重试全部失败：写日志并返回失败
                write_log(question, current_sql, is_success=0, exec_time_ms=0)
                return {
                    "success": False,
                    "sql": current_sql,
                    "data": [],
                    "exec_time_ms": 0,
                    "attempts": attempts,
                    "error": f"SQL 执行失败（已自动重试 {MAX_RETRIES} 次）：{exc}",
                }
            # 3. 把报错信息回传给大模型修正，再回到循环顶部重新做安全校验并执行
            current_sql = repair_sql(question, current_sql, str(exc))
            continue

        # 4. 执行成功：写日志并返回结果
        write_log(question, current_sql, is_success=1, exec_time_ms=cost_ms)
        data = [
            {key: _normalize_value(value) for key, value in row.items()}
            for row in rows
        ]
        return {
            "success": True,
            "sql": current_sql,
            "data": data,
            "exec_time_ms": cost_ms,
            "attempts": attempts,
            "error": None,
        }
