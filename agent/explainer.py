# -*- coding: utf-8 -*-
"""Step 4 结果解释：把查询结果翻译成 50 字以内的自然语言回答。"""
import json

from agent.prompts import EXPLAIN_PROMPT, render
from agent.sql_generator import chat_with_llm

# 传给大模型的结果最多条数，避免结果太长撑爆上下文
MAX_PREVIEW_ROWS = 15


def explain_result(question: str, sql: str, rows: list[dict]) -> str:
    """把查询结果解释成一句不超过 50 字的中文回答。"""
    if not rows:
        return "查询结果为空：数据库里没有符合条件的数据。"

    preview = {"总条数": len(rows), "数据": rows[:MAX_PREVIEW_ROWS]}
    if len(rows) > MAX_PREVIEW_ROWS:
        preview["说明"] = f"仅展示前 {MAX_PREVIEW_ROWS} 条"

    prompt = render(
        EXPLAIN_PROMPT,
        question=question,
        sql=sql,
        result=json.dumps(preview, ensure_ascii=False, default=str),
    )
    try:
        return chat_with_llm(prompt)
    except Exception as exc:
        # 解释环节失败不影响查询本身，退化为固定话术
        return f"共查询到 {len(rows)} 条记录。（自动解释失败：{exc}）"
