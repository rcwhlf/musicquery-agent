# -*- coding: utf-8 -*-
"""测试数据导入脚本。

用法（在项目根目录执行）：
    python data/import_data.py

会先清空业务表旧数据（query_logs 保留），再按外键顺序批量插入：
    50 歌手 → 100 专辑 → 500 歌曲 → 200 用户 → 5000 播放记录
"""
import random
import sys
from datetime import date
from pathlib import Path

# 把项目根目录加入模块搜索路径，保证脚本能直接以 `python data/import_data.py` 运行
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from faker import Faker                    # noqa: E402
from db.connection import get_connection   # noqa: E402

# 固定随机种子：每次运行生成完全相同的数据，便于课程演示与排错复现
random.seed(2026)
Faker.seed(2026)

fake_cn = Faker("zh_CN")   # 中文数据：用户昵称
fake_en = Faker("en_US")   # 英文数据：部分欧美歌手名

GENRES = ["流行", "摇滚", "民谣", "电子", "嘻哈", "爵士", "古典", "R&B", "乡村", "金属"]
COUNTRIES_CN = ["中国", "日本", "韩国"]
COUNTRIES_EN = ["美国", "英国", "加拿大", "澳大利亚"]
CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "西安", "重庆", "长沙", "苏州"]
DEVICES = ["iOS", "Android", "PC客户端", "网页版", "车载", "智能音箱"]
DEVICE_WEIGHTS = [30, 35, 12, 10, 8, 5]

# 用于拼接专辑名/歌曲名的词库，让数据看起来像真实的音乐作品
ALBUM_HEADS = ["夜的", "光之", "时间", "夏日", "流浪", "午夜", "南风", "城市", "青春", "无声", "银河", "半岛"]
ALBUM_TAILS = ["诗篇", "告白", "旅行", "纪年", "回声", "小夜曲", "手记", "放映室", "练习曲", "边界", "信笺", "温度"]
SONG_HEADS = ["凌晨", "夏天的", "一个人的", "再见", "拥抱", "追光", "雨后", "月光下的", "风中的", "最后的", "亲爱的", "遥远的"]
SONG_TAILS = ["车站", "情书", "路灯", "海风", "吉他", "小孩", "日记", "旅行", "烟火", "晚风", "蝴蝶", "答案"]


def gen_artists(count: int) -> list[tuple]:
    """生成歌手 (姓名, 国家, 出道年份)。约 1/4 使用英文名，国家随之匹配。"""
    rows = []
    for _ in range(count):
        if random.random() < 0.25:
            rows.append((fake_en.name(), random.choice(COUNTRIES_EN), random.randint(1975, 2020)))
        else:
            rows.append((fake_cn.name(), random.choice(COUNTRIES_CN), random.randint(1975, 2020)))
    return rows


def gen_albums(count: int, artist_rows: list[dict]) -> list[tuple]:
    """生成专辑 (专辑名, 歌手ID, 发行日期, 类型)。发行年份不早于歌手出道年份。"""
    rows = []
    for _ in range(count):
        artist = random.choice(artist_rows)
        year = random.randint(min(artist["debut_year"], 2025), 2025)
        release = date(year, random.randint(1, 12), random.randint(1, 28))
        album_type = random.choices(["studio", "live", "compilation"], weights=[7, 2, 1])[0]
        title = random.choice(ALBUM_HEADS) + random.choice(ALBUM_TAILS)
        rows.append((title, artist["artist_id"], release, album_type))
    return rows


def gen_songs(count: int, album_rows: list[dict]) -> list[tuple]:
    """生成歌曲 (歌名, 专辑ID, 歌手ID, 时长秒, 流派, 发行年份)。歌曲归属专辑对应的歌手，保持数据一致。"""
    rows = []
    for _ in range(count):
        album = random.choice(album_rows)
        title = random.choice(SONG_HEADS) + random.choice(SONG_TAILS)
        rows.append((
            title,
            album["album_id"],
            album["artist_id"],
            random.randint(120, 420),
            random.choice(GENRES),
            album["release_year"],
        ))
    return rows


def gen_users(count: int) -> list[tuple]:
    """生成用户 (昵称, 城市, 注册日期)。"""
    return [
        (
            fake_cn.name(),
            random.choice(CITIES),
            fake_cn.date_between(start_date=date(2019, 1, 1), end_date=date(2025, 12, 31)),
        )
        for _ in range(count)
    ]


def gen_play_records(count: int, song_ids: list[int], user_ids: list[int]) -> list[tuple]:
    """生成播放记录 (歌曲ID, 用户ID, 播放时间, 设备)。

    用对数正态分布模拟真实的长尾热度：少数"爆款"歌曲和活跃用户占大头，
    大多数歌曲/用户播放很少。这样"播放量前几名"等查询结果有明显区分度，
    更接近真实产品数据；若用完全均匀随机，排名会全是并列，看不出差异。
    """
    song_weights = [random.lognormvariate(0, 1.2) for _ in song_ids]
    user_weights = [random.lognormvariate(0, 1.0) for _ in user_ids]
    songs = random.choices(song_ids, weights=song_weights, k=count)
    users = random.choices(user_ids, weights=user_weights, k=count)
    return [
        (
            songs[i],
            users[i],
            fake_cn.date_time_between(start_date="-365d", end_date="now"),
            random.choices(DEVICES, weights=DEVICE_WEIGHTS)[0],
        )
        for i in range(count)
    ]


def main() -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 0. 清空旧数据（临时关闭外键检查以便 TRUNCATE），保证脚本可重复执行
            print("正在清空旧数据...")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")
            for table in ("play_records", "songs", "albums", "artists", "users"):
                cur.execute(f"TRUNCATE TABLE {table}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1")

            # 1. 歌手（最顶层，先插入）
            artists = gen_artists(50)
            cur.executemany(
                "INSERT INTO artists (name, country, debut_year) VALUES (%s, %s, %s)",
                artists,
            )
            cur.execute("SELECT artist_id, debut_year FROM artists")
            artist_rows = cur.fetchall()
            print(f"artists      插入 {len(artists)} 条")

            # 2. 专辑（依赖歌手ID）
            albums = gen_albums(100, artist_rows)
            cur.executemany(
                "INSERT INTO albums (title, artist_id, release_date, album_type) VALUES (%s, %s, %s, %s)",
                albums,
            )
            cur.execute("SELECT album_id, artist_id, YEAR(release_date) AS release_year FROM albums")
            album_rows = cur.fetchall()
            print(f"albums       插入 {len(albums)} 条")

            # 3. 歌曲（依赖专辑ID、歌手ID）
            songs = gen_songs(500, album_rows)
            cur.executemany(
                "INSERT INTO songs (title, album_id, artist_id, duration_sec, genre, release_year) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                songs,
            )
            print(f"songs        插入 {len(songs)} 条")

            # 4. 用户
            users = gen_users(200)
            cur.executemany(
                "INSERT INTO users (nickname, city, register_date) VALUES (%s, %s, %s)",
                users,
            )
            print(f"users        插入 {len(users)} 条")

            # 5. 播放记录（依赖歌曲ID、用户ID）
            cur.execute("SELECT song_id FROM songs")
            song_ids = [row["song_id"] for row in cur.fetchall()]
            cur.execute("SELECT user_id FROM users")
            user_ids = [row["user_id"] for row in cur.fetchall()]
            plays = gen_play_records(5000, song_ids, user_ids)
            cur.executemany(
                "INSERT INTO play_records (song_id, user_id, play_time, device) VALUES (%s, %s, %s, %s)",
                plays,
            )
            print(f"play_records 插入 {len(plays)} 条")

        # 全部插入成功后统一提交；任何一步失败则整体回滚，不留脏数据
        conn.commit()
        print("\n✅ 测试数据导入完成！运行 streamlit run app.py 开始体验。")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
