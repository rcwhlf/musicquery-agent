# -*- coding: utf-8 -*-
"""统一配置：加载项目根目录的 .env 文件，集中管理数据库和大模型配置。"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
# 显式指定 .env 路径，保证无论从哪个目录启动程序都能读到配置
load_dotenv(BASE_DIR / ".env")

# ---------- MySQL 数据库配置 ----------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "music_query"),
    "charset": "utf8mb4",
}

# ---------- 大模型配置（OpenAI 兼容接口，默认智谱 GLM） ----------
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
LLM_MODEL = os.getenv("LLM_MODEL", "glm-5.3-flash")
