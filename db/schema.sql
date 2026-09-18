-- =====================================================
-- MusicQuery Agent 数据库建表脚本（MySQL 8.0）
-- 执行方式（在项目根目录）：
--   mysql -u root -p < db/schema.sql
-- =====================================================

CREATE DATABASE IF NOT EXISTS music_query
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE music_query;

-- -----------------------------------------------------
-- 1. artists 歌手表
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS artists (
    artist_id  INT          PRIMARY KEY AUTO_INCREMENT COMMENT '歌手ID',
    name       VARCHAR(100) NOT NULL                   COMMENT '歌手姓名',
    country    VARCHAR(50)                              COMMENT '国家/地区',
    debut_year INT                                      COMMENT '出道年份'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='歌手表';

-- -----------------------------------------------------
-- 2. albums 专辑表
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS albums (
    album_id     INT          PRIMARY KEY AUTO_INCREMENT COMMENT '专辑ID',
    title        VARCHAR(200) NOT NULL                   COMMENT '专辑名称',
    artist_id    INT          NOT NULL                   COMMENT '所属歌手ID',
    release_date DATE                                        COMMENT '发行日期',
    album_type   ENUM('studio','live','compilation') DEFAULT 'studio' COMMENT '专辑类型：录音室/现场/合辑',
    -- 支持外键的索引：按歌手查专辑
    KEY idx_albums_artist (artist_id),
    CONSTRAINT fk_albums_artist FOREIGN KEY (artist_id) REFERENCES artists (artist_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专辑表';

-- -----------------------------------------------------
-- 3. songs 歌手表
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS songs (
    song_id      INT          PRIMARY KEY AUTO_INCREMENT COMMENT '歌曲ID',
    title        VARCHAR(200) NOT NULL                   COMMENT '歌曲名称',
    album_id     INT                                     COMMENT '所属专辑ID',
    artist_id    INT          NOT NULL                   COMMENT '演唱歌手ID',
    duration_sec INT                                         COMMENT '时长（秒）',
    genre        VARCHAR(50)                             COMMENT '流派',
    release_year INT                                     COMMENT '发行年份',
    KEY idx_songs_album (album_id),
    -- 课程要求的索引：songs(artist_id)
    KEY idx_songs_artist (artist_id),
    -- 课程要求的复合索引：songs(genre, release_year)
    KEY idx_songs_genre_year (genre, release_year),
    CONSTRAINT fk_songs_album FOREIGN KEY (album_id) REFERENCES albums (album_id),
    CONSTRAINT fk_songs_artist FOREIGN KEY (artist_id) REFERENCES artists (artist_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='歌曲表';

-- -----------------------------------------------------
-- 4. users 用户表
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id       INT         PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    nickname      VARCHAR(50)                            COMMENT '昵称',
    city          VARCHAR(50)                            COMMENT '所在城市',
    register_date DATE                                   COMMENT '注册日期'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- -----------------------------------------------------
-- 5. play_records 播放记录表（事实表）
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS play_records (
    record_id BIGINT      PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    song_id   INT         NOT NULL                   COMMENT '歌曲ID',
    user_id   INT         NOT NULL                   COMMENT '用户ID',
    play_time DATETIME                               COMMENT '播放时间',
    device    VARCHAR(30)                            COMMENT '播放设备',
    KEY idx_play_user (user_id),
    -- 课程要求的索引：play_records(play_time)
    KEY idx_play_time (play_time),
    -- 课程要求的复合索引：play_records(song_id, play_time)
    KEY idx_play_song_time (song_id, play_time),
    CONSTRAINT fk_play_song FOREIGN KEY (song_id) REFERENCES songs (song_id),
    CONSTRAINT fk_play_user FOREIGN KEY (user_id) REFERENCES users (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='播放记录表（事实表）';

-- -----------------------------------------------------
-- 6. query_logs Agent 查询日志表
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS query_logs (
    log_id         BIGINT  PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    user_question  TEXT                               COMMENT '用户问题',
    generated_sql  TEXT                               COMMENT '生成的 SQL',
    is_success     TINYINT DEFAULT 0                  COMMENT '是否成功：1=成功 0=失败',
    exec_time_ms   INT                                COMMENT 'SQL 执行耗时（毫秒）',
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent 查询日志表';
