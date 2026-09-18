# -*- coding: utf-8 -*-
"""MusicQuery Agent —— Streamlit 主程序。

四步流程：Step1 意图判断 → Step2 生成 SQL → Step3 执行校验 → Step4 结果解释。
运行方式（在项目根目录）：streamlit run app.py
"""
import time

import pandas as pd
import streamlit as st

from agent.executor import execute_sql_with_retry
from agent.explainer import explain_result
from agent.sql_generator import check_intent, generate_sql
from config import LLM_API_KEY
from db.connection import test_connection
from logs.query_logs import get_recent_logs

st.set_page_config(page_title="MusicQuery Agent", page_icon="🎵", layout="wide")

st.title("🎵 MusicQuery Agent")
st.caption("用中文提问 → 自动生成 SQL → 查询 MySQL → 自然语言回答")

EXAMPLES = [
    "播放量最高的前 5 首歌是哪些？",
    "一共有多少首流行歌曲？",
    "来自北京的用户有多少个？",
    "最长的歌曲是哪一首？",
]

# ---- 示例问题：点击后自动填入下方输入框 ----
st.write("试试这些例子：")
example_cols = st.columns(len(EXAMPLES))
for col, example in zip(example_cols, EXAMPLES):
    if col.button(example):
        st.session_state["question_input"] = example

# ---- 输入区 ----
question = st.text_input(
    "请输入你的问题",
    key="question_input",
    placeholder="例如：播放量最高的前 5 首歌是哪些？",
)
run_query = st.button("🔍 查询", type="primary")

# ---- 主流程 ----
if run_query:
    if not question.strip():
        st.warning("请先输入问题再点击查询。")
    elif not LLM_API_KEY:
        st.error("未配置大模型 API Key：请复制 .env.example 为 .env，填写 LLM_API_KEY 后重启应用。")
    elif not LLM_API_KEY.isascii():
        st.error("API Key 格式不对：LLM_API_KEY 里包含中文或全角字符（可能还没替换成真实 Key）。"
                 "请到智谱开放平台复制 API Key，粘贴到 .env 的 LLM_API_KEY= 后面，保存后重启应用。")
    elif not test_connection():
        st.error("无法连接 MySQL 数据库，请确认数据库已启动，且 .env 中的数据库配置正确。")
    else:
        start = time.perf_counter()
        st.session_state["last_status"] = "失败"
        try:
            # Step 1 意图判断
            with st.spinner("第 1 步：判断问题是否与音乐数据库相关..."):
                if not check_intent(question):
                    st.session_state["last_cost_ms"] = int((time.perf_counter() - start) * 1000)
                    st.session_state["last_status"] = "无关"
                    st.warning("该问题与音乐数据库无关")
                    st.stop()

            # Step 2 生成 SQL
            with st.spinner("第 2 步：生成 SQL..."):
                sql = generate_sql(question)

            # Step 3 执行校验（含安全拦截与失败自动重试）
            with st.spinner("第 3 步：执行 SQL（失败会自动修正重试）..."):
                result = execute_sql_with_retry(question, sql)

            # Step 4 结果解释
            answer = None
            if result["success"]:
                with st.spinner("第 4 步：生成自然语言回答..."):
                    answer = explain_result(question, result["sql"], result["data"])

            st.session_state["last_cost_ms"] = int((time.perf_counter() - start) * 1000)
            st.session_state["last_status"] = "成功" if result["success"] else "失败"

            # ---- 下方三块：生成的 SQL / 查询结果表格 / 自然语言回答 ----
            st.subheader("1️⃣ 生成的 SQL")
            st.code(result["sql"], language="sql")
            if result["attempts"] > 1:
                st.caption(f"首次执行失败，已自动修正，共执行 {result['attempts']} 次")

            st.subheader("2️⃣ 查询结果")
            if result["success"]:
                st.dataframe(pd.DataFrame(result["data"]))
                st.caption(f"共 {len(result['data'])} 条记录 · SQL 执行耗时 {result['exec_time_ms']} ms")
            else:
                st.error(f"查询失败：{result['error']}")

            st.subheader("3️⃣ 自然语言回答")
            if result["success"]:
                st.success(answer)
            else:
                st.info("查询未成功，无法生成回答。")
        except Exception as exc:
            st.session_state["last_cost_ms"] = int((time.perf_counter() - start) * 1000)
            st.session_state["last_status"] = "失败"
            st.error(f"查询过程出错：{exc}")

# ---- 侧边栏 ----
# 注意：Streamlit 自上而下渲染，把侧边栏放在文件末尾，
# 本次查询刚写入的状态（耗时/是否成功）和日志才能立即刷新显示。
with st.sidebar:
    st.header("📊 运行状态")
    cost_ms = st.session_state.get("last_cost_ms")
    st.metric("本次耗时", f"{cost_ms} ms" if cost_ms is not None else "—")

    status = st.session_state.get("last_status")
    if status == "成功":
        st.success("查询成功")
    elif status == "失败":
        st.error("查询失败")
    elif status == "无关":
        st.warning("问题与音乐无关")
    else:
        st.info("尚未执行查询")

    st.divider()
    st.subheader("🕘 历史查询记录")
    try:
        history = get_recent_logs(10)
    except Exception as exc:
        history = []
        st.error(f"读取历史记录失败：{exc}")
    if not history:
        st.caption("暂无记录，去查询一条试试吧。")
    for row in history:
        icon = "✅" if row["is_success"] else "❌"
        title = row["user_question"]
        title = title if len(title) <= 18 else title[:18] + "…"
        with st.expander(f"{icon} {title}"):
            created = row["created_at"]
            st.caption(f"{created} · 耗时 {row['exec_time_ms']} ms")
            st.code(row["generated_sql"] or "（无 SQL）", language="sql")
