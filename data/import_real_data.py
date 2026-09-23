# -*- coding: utf-8 -*-
"""真实曲库数据导入脚本。

用法（项目根目录）：
    python data/import_real_data.py

数据构成：
    50 位真实歌手 / 100 张真实专辑 / 约 500 首真实歌曲（整理自公开资料）
    + 200 位仿真用户 + 5000 条播放记录（听歌行为属于隐私数据，无法获取，
    此部分为按真实长尾规律生成的仿真数据）
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from faker import Faker                    # noqa: E402

from db.connection import get_connection   # noqa: E402
from data.real_seed import ARTISTS, ALBUMS, TRACKS, SINGLES  # noqa: E402

random.seed(2026)
Faker.seed(2026)
fake = Faker("zh_CN")

CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "西安", "重庆", "长沙", "苏州"]
DEVICES = ["iOS", "Android", "PC客户端", "网页版", "车载", "智能音箱"]
DEVICE_WEIGHTS = [30, 35, 12, 10, 8, 5]
SINGLE_DATE = "{year}-06-15"  # 单曲发行月份未知时按 6 月 15 日填充


def gen_users(count):
    """仿真用户（昵称/城市/注册日期为模拟数据）。"""
    return [
        (
            fake.name(),
            random.choice(CITIES),
            fake.date_between(start_date=__import__("datetime").date(2019, 1, 1), end_date=__import__("datetime").date(2025, 12, 31)),
        )
        for _ in range(count)
    ]


def gen_play_records(count, song_ids, user_ids):
    """仿真播放记录：对数正态长尾分布模拟真实热度。"""
    song_weights = [random.lognormvariate(0, 1.2) for _ in song_ids]
    user_weights = [random.lognormvariate(0, 1.0) for _ in user_ids]
    songs = random.choices(song_ids, weights=song_weights, k=count)
    users = random.choices(user_ids, weights=user_weights, k=count)
    return [
        (
            songs[i],
            users[i],
            fake.date_time_between(start_date="-365d", end_date="now"),
            random.choices(DEVICES, weights=DEVICE_WEIGHTS)[0],
        )
        for i in range(count)
    ]


def main():
    # ---------- 组装数据 ----------
    albums_real = [(a, t, y, ty) for (a, t, y, ty) in ALBUMS if (a, t) in TRACKS]
    songs = []  # (专辑key 或 None, 歌手, 歌名)
    for key, tracks in TRACKS.items():
        artist = key[0]
        for title in tracks:
            songs.append((key, artist, title))
    print(f"真实专辑 {len(albums_real)} 张，曲目 {len(songs)} 首")

    # 用知名单曲补足到 500 首
    singles = []
    pool = list(SINGLES)
    while len(songs) < 500 and pool:
        artist, title, year = pool.pop(0)
        if artist not in {a[0] for a in ARTISTS}:
            continue
        if any(s[2] == title for s in songs):
            continue
        singles.append((artist, title, year))
        songs.append((None, artist, title))
    if len(songs) != 500:
        print(f"提示：曲目总数 {len(songs)}，与 500 的目标相差 {500 - len(songs)} 首")

    # ---------- 写入数据库 ----------
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("正在清空旧数据...")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")
            for table in ("play_records", "songs", "albums", "artists", "users"):
                cur.execute(f"TRUNCATE TABLE {table}")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1")

            cur.executemany(
                "INSERT INTO artists (name, country, debut_year) VALUES (%s, %s, %s)",
                [(a, c, d) for (a, c, d, _) in ARTISTS],
            )
            cur.execute("SELECT artist_id, name, debut_year FROM artists")
            artist_rows = {r["name"]: (r["artist_id"], r["debut_year"]) for r in cur.fetchall()}
            print(f"artists      插入 {len(artist_rows)} 条")

            cur.executemany(
                "INSERT INTO albums (title, artist_id, release_date, album_type) VALUES (%s, %s, %s, %s)",
                [(t, artist_rows[a][0], f"{y}-06-15", ty) for (a, t, y, ty) in albums_real],
            )
            cur.execute("SELECT album_id, title FROM albums")
            album_rows = {r["title"]: r["album_id"] for r in cur.fetchall()}
            print(f"albums       插入 {len(album_rows)} 条")

            song_rows = []
            for key, artist, title in songs:
                genre = next(a[3] for a in ARTISTS if a[0] == artist)
                duration = random.randint(150, 330)
                if key:  # 专辑曲目：年份取专辑年份
                    album_id = album_rows[key[1]]
                    year = next(y for (a, t, y, ty) in albums_real if (a, t) == key)
                    song_rows.append((title, album_id, artist_rows[artist][0], duration, genre, year))
                else:  # 单曲：album_id 为空
                    year = next(y for (a, t, y) in SINGLES if (a, t) == (artist, title))
                    song_rows.append((title, None, artist_rows[artist][0], duration, genre, year))
            cur.executemany(
                "INSERT INTO songs (title, album_id, artist_id, duration_sec, genre, release_year) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                song_rows,
            )
            print(f"songs        插入 {len(song_rows)} 条（含单曲 {len(singles)} 首）")

            users = gen_users(200)
            cur.executemany(
                "INSERT INTO users (nickname, city, register_date) VALUES (%s, %s, %s)",
                users,
            )
            print(f"users        插入 {len(users)} 条")

            cur.execute("SELECT song_id FROM songs")
            song_ids = [r["song_id"] for r in cur.fetchall()]
            cur.execute("SELECT user_id FROM users")
            user_ids = [r["user_id"] for r in cur.fetchall()]
            plays = gen_play_records(5000, song_ids, user_ids)
            cur.executemany(
                "INSERT INTO play_records (song_id, user_id, play_time, device) VALUES (%s, %s, %s, %s)",
                plays,
            )
            print(f"play_records 插入 {len(plays)} 条")

        conn.commit()
        print("\n✅ 真实曲库数据导入完成！运行 streamlit run app.py 开始体验。")
        print("说明：歌手/专辑/歌曲为真实公开数据；用户与播放行为为仿真数据。")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
