# 🎵 MusicQuery Agent

基于自然语言交互的音乐作品库智能查询系统（数据库课程项目）。

用户用中文提问，系统自动把问题转成 SQL、查 MySQL 数据库、再用自然语言回答。
**数据库设计是核心，Agent 是交互层。**

## 功能流程（四步）

```
用户中文提问
    │
    ▼
Step 1 意图判断  ──► 与音乐无关？──► 返回"该问题与音乐数据库无关"
    │ 相关
    ▼
Step 2 SQL 生成  ──► 把建表 DDL + 字段说明塞进 Prompt，大模型生成 SELECT
    │
    ▼
Step 3 执行校验  ──► 正则安全拦截（DROP/DELETE/UPDATE/INSERT/ALTER 等）
    │               ──► 执行失败则把报错回传 LLM 自动修正，最多重试 2 次
    │               ──► 每次结果写入 query_logs 表
    ▼
Step 4 结果解释  ──► 把查询结果翻译成 50 字以内的自然语言回答
```

## 技术栈

- Python 3.10+（本项目在 3.13 下开发验证）
- MySQL 8.0
- PyMySQL（数据库连接）
- Streamlit（网页界面）
- 智谱 GLM 大模型（`glm-5.3-flash`，OpenAI 兼容接口，可在 `.env` 中切换 DeepSeek / OpenAI / Ollama 等）

## 项目结构

```
musicquery-agent/
├── app.py                 # Streamlit 主程序（四步流程编排 + 界面）
├── config.py              # 统一配置：加载 .env（数据库 + 大模型）
├── agent/
│   ├── __init__.py
│   ├── sql_generator.py   # 意图判断 + 调 LLM 生成 SQL + 失败修正
│   ├── executor.py        # 执行 SQL + 安全拦截 + 自动重试
│   ├── explainer.py       # 结果解释（50 字以内自然语言）
│   └── prompts.py         # 提示词模板（意图/生成/纠错/解释）
├── db/
│   ├── connection.py      # PyMySQL 连接
│   └── schema.sql         # 建表语句 + 索引
├── data/
│   └── import_data.py     # Faker 生成测试数据并批量导入
├── logs/
│   └── query_logs.py      # query_logs 表读写
├── requirements.txt
└── .env.example           # 配置模板（复制为 .env 后填写）
```

## 数据库设计（6 张表）

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| artists | 歌手表（维度表） | name, country, debut_year |
| albums | 专辑表 | artist_id FK, release_date, album_type(studio/live/compilation) |
| songs | 歌手表 | album_id FK, artist_id FK, duration_sec, genre, release_year |
| users | 用户表（维度表） | nickname, city, register_date |
| play_records | 播放记录表（事实表） | song_id FK, user_id FK, play_time, device |
| query_logs | Agent 查询日志表 | user_question, generated_sql, is_success, exec_time_ms |

**索引**（已写入 `db/schema.sql`）：

- `songs(artist_id)` — idx_songs_artist
- `songs(genre, release_year)` — 复合索引 idx_songs_genre_year
- `play_records(play_time)` — idx_play_time
- `play_records(song_id, play_time)` — 复合索引 idx_play_song_time

## 快速开始

> 以下所有命令都在**项目目录**下执行，先进入目录：`cd E:\musicquery-agent`

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

CMD / Git Bash：

```bash
mysql -u root -p < db/schema.sql
```

PowerShell 不支持 `<` 重定向，请改用：

```powershell
mysql -u root -p -e "source E:/musicquery-agent/db/schema.sql"
```

会创建数据库 `music_query`、6 张表和要求的索引。

### 3. 配置 .env

复制 `.env.example` 为 `.env`，填入 MySQL 密码和智谱 API Key：

```bash
copy .env.example .env    # Windows
# cp .env.example .env    # macOS/Linux
```

```ini
DB_PASSWORD=你的MySQL密码
LLM_API_KEY=你的智谱APIKey
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-5.3-flash
```

> 智谱 API Key 在 <https://open.bigmodel.cn> 注册后获取。
> 想换其他大模型？改 `LLM_BASE_URL` / `LLM_MODEL` 即可，见 `.env.example` 内注释。

### 4. 导入测试数据

```bash
python data/import_data.py
```

按外键顺序批量插入：50 歌手 → 100 专辑 → 500 歌曲 → 200 用户 → 5000 播放记录。
随机种子固定，每次运行结果一致；重复运行会先清空业务表，不会产生重复数据。

### 5. 启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 <http://localhost:8501>。

## 使用示例

在输入框直接提问，例如：

- 播放量最高的前 5 首歌是哪些？
- 一共有多少首流行歌曲？
- 来自北京的用户有多少个？
- 最长的歌曲是哪一首？
- 2020 年以后发行的专辑有哪些？
- 哪种播放设备用得最多？

界面上方还有一键填入的示例问题按钮。

问"今天天气怎么样"这类无关问题，会得到提示：**该问题与音乐数据库无关**。

## 界面说明

- **主区域**：生成的 SQL（代码块）→ 查询结果表格（含条数和执行耗时）→ 自然语言回答
- **主区域上方**：歌曲分类筛选（流派）下拉框——不输问题也可直接按分类查询
- **侧边栏**：本次耗时、是否成功、最近 10 条历史查询记录（含当时的 SQL），支持**单条删除**与**一键清空**（需勾选确认）

## 常见问题

| 现象 | 原因与解决 |
|------|------------|
| 电脑重启后页面提示正在启动数据库 | 正常现象：数据库按需启动（不常驻占内存），打开页面时应用会自动拉起它，约 5~15 秒 |
| `Access denied for user 'root'` | `.env` 中 `DB_PASSWORD` 不对 |
| `Unknown database 'music_query'` | 先执行第 2 步建库脚本 |
| `cryptography` 相关报错 | MySQL 8 默认认证插件需要它，`pip install cryptography` |
| 提示"未配置大模型 API Key" | 复制 `.env.example` 为 `.env` 并填写 `LLM_API_KEY`，重启应用 |
| 大模型报 401/模型不存在 | 检查 `LLM_API_KEY` 是否有效、`LLM_MODEL` 名称与平台一致 |

## 课程要点对应

- **DDL + 索引**：`db/schema.sql`
- **意图判断**：`agent/sql_generator.py` 的 `check_intent()` + `agent/prompts.py` 的 `INTENT_PROMPT`
- **SQL 生成**：`generate_sql()`，DDL 由 `agent/prompts.py` 的 `get_schema_text()` 直接读取 `db/schema.sql`
- **安全拦截**：`agent/executor.py` 的 `check_sql_safety()`（正则）
- **失败自动修正（最多 2 次）**：`execute_sql_with_retry()` 循环
- **查询日志**：`logs/query_logs.py` 写入 `query_logs` 表
- **结果解释（50 字以内）**：`agent/explainer.py` 的 `explain_result()`
