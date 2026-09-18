# -*- coding: utf-8 -*-
"""提示词模板：意图判断、SQL 生成、SQL 纠错、结果解释。

数据库结构直接读取 db/schema.sql 作为提示词的一部分，
保证"喂给大模型的表结构"和"真实表结构"永远一致（单一数据源）。
"""
from pathlib import Path

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "db" / "schema.sql"


def get_schema_text() -> str:
    """读取建表脚本全文，作为大模型可用的数据库结构说明。"""
    return _SCHEMA_PATH.read_text(encoding="utf-8")


def render(template: str, **kwargs) -> str:
    """安全的模板填充。

    用 str.replace 而不是 str.format：查询结果 JSON 里含有花括号，
    format 会把它们误当成占位符而报错，replace 则不受影响。
    """
    for key, value in kwargs.items():
        template = template.replace("{" + key + "}", str(value))
    return template


# ---------- Step 1：意图判断 ----------
INTENT_PROMPT = """你是一个音乐数据库助手的守门员。请判断用户的问题是否属于音乐数据库能回答的范围，
包括：歌手、专辑、歌曲、流派、时长、播放记录、播放设备、用户及播放行为等。

相关请只输出 YES，无关请只输出 NO，不要输出任何其他内容。

用户问题：{question}"""

# ---------- Step 2：SQL 生成 ----------
SQL_GENERATE_PROMPT = """你是专业的 MySQL 查询生成器。请根据用户问题，基于下面的数据库结构生成一条可以直接在 MySQL 8.0 上执行的查询语句。

【数据库建表语句】
{schema}

【业务说明】
- artists：歌手表，country 为国家/地区，debut_year 为出道年份；
- albums：专辑表，album_type 取值 studio(录音室专辑)、live(现场专辑)、compilation(合辑)；
- songs：歌曲表，duration_sec 为时长（秒），genre 为流派，release_year 为发行年份；
- users：用户表，city 为所在城市，register_date 为注册日期；
- play_records：播放记录表，一条记录代表一次播放，play_time 为播放时间，device 为播放设备；
- 一首歌的"播放量" = play_records 中该歌曲的记录条数。

【严格规则】
1. 只允许生成 SELECT 语句，禁止任何修改数据或表结构的语句；
2. 只能使用上面给出的表和字段，表名、字段名必须完全一致，不要虚构字段；
3. 中文条件（如城市"北京"、流派"流行"）直接写在 WHERE 子句中；
4. 涉及"最高/最多/最长/最近"等排名时使用 ORDER BY，列表类结果必须加 LIMIT（不超过 100）；
5. 只输出一条 SQL 语句本身，不要任何解释、注释和 markdown 代码块。

用户问题：{question}"""

# ---------- Step 3：SQL 纠错（执行失败后回传报错自动修正） ----------
SQL_REPAIR_PROMPT = """你是 MySQL 查询修复专家。下面这条 SQL 在 MySQL 8.0 中执行出错了，
请结合数据库结构、用户问题和报错信息，修正这条 SQL。

【数据库建表语句】
{schema}

【用户问题】
{question}

【出错的 SQL】
{sql}

【报错信息】
{error}

【要求】
1. 只允许 SELECT 语句；
2. 只输出修正后的一条 SQL 语句本身，不要任何解释和 markdown 代码块。"""

# ---------- Step 4：结果解释 ----------
EXPLAIN_PROMPT = """你是音乐数据助手。请根据用户问题、执行的 SQL 和查询结果，用不超过 50 字的中文自然语言直接回答用户的问题。

要求：
1. 直接给结论，简洁口语化；
2. 不要提到 SQL、数据库、"查询结果"这类字眼；
3. 数字必须来自查询结果本身，不要编造。

用户问题：{question}

执行的 SQL：{sql}

查询结果（JSON，可能只展示了前几条）：{result}"""
