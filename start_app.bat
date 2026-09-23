@echo off
rem ===== 一键启动 MusicQuery Agent =====
rem 启动 MySQL 与网页应用（均为计划任务方式，不占开机自启），并打开浏览器
schtasks /run /tn MusicQueryMySQL
schtasks /run /tn MusicQueryApp
timeout /t 8 /nobreak >nul
start http://localhost:8501
echo 已启动：数据库 + 网页应用，浏览器即将打开 http://localhost:8501
