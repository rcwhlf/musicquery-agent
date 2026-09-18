# -*- coding: utf-8 -*-
"""Step 1 意图判断 + Step 2 SQL 生成 + Step 3 失败修正。

统一通过 OpenAI 兼容接口调用大模型，
默认智谱 GLM（glm-5.3-flash），也可在 .env 中切换 DeepSeek / OpenAI / Ollama 等。
"""
import re

from openai import OpenAI

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from agent.prompts import (
    INTENT_PROMPT,
    SQL_GENERATE_PROMPT,
    SQL_REPAIR_PROMPT,
    get_schema_text,
    render,
)


def _get_client() -> OpenAI:
    """创建大模型客户端；未配置 API Key 时给出明确的中文提示。"""
    if not LLM_API_KEY:
        raise RuntimeError(
            "未配置大模型 API Key：请复制 .env.example 为 .env，填写 LLM_API_KEY 后重试"
        )
    return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)


def chat_with_llm(prompt: str, temperature: float = 0.0) -> str:
    """调用大模型，返回文本回复。本模块与 explainer 共用这一个底层入口。"""
    client = _get_client()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        # glm-5.3-flash 是推理模型，回答前会先输出思考内容，
        # 给足余量防止思考占满额度导致正式回答被截断为空
        max_tokens=4096,
    )
    message = response.choices[0].message
    text = (message.content or "").strip()
    if not text:
        # 兜底：极端情况下正式回答为空，从思考内容里提取
        text = (getattr(message, "reasoning_content", "") or "").strip()
    return text


def check_intent(question: str) -> bool:
    """Step 1：判断用户问题是否与音乐数据库相关。"""
    try:
        answer = chat_with_llm(render(INTENT_PROMPT, question=question))
        return "YES" in answer.upper()
    except Exception:
        # 意图判断环节调用失败时不拦截用户，放行到后续步骤统一报错
        return True


def _extract_sql(text: str) -> str:
    """从大模型输出中提取纯 SQL：去掉 markdown 代码块、多余解释和结尾分号。"""
    text = text.strip()
    fenced = re.search(r"```(?:sql)?\s*(.*?)```", text, re.S | re.I)
    if fenced:  # 输出被 ```sql ... ``` 包裹时，取代码块内容
        text = fenced.group(1).strip()
    found = re.search(r"\b(SELECT|WITH)\b.*", text, re.S | re.I)
    if found:  # 模型附带了解释文字时，从 SQL 开头处截取
        text = found.group(0).strip()
    if ";" in text:  # 只保留第一条语句，防止拼出多条语句
        text = text.split(";")[0]
    return text.strip()


def generate_sql(question: str) -> str:
    """Step 2：根据用户问题生成一条 SELECT 语句。"""
    prompt = render(SQL_GENERATE_PROMPT, question=question, schema=get_schema_text())
    return _extract_sql(chat_with_llm(prompt))


def repair_sql(question: str, failed_sql: str, error: str) -> str:
    """Step 3：SQL 执行报错后，把报错信息回传给大模型进行修正。"""
    prompt = render(
        SQL_REPAIR_PROMPT,
        question=question,
        sql=failed_sql,
        error=error,
        schema=get_schema_text(),
    )
    return _extract_sql(chat_with_llm(prompt))
