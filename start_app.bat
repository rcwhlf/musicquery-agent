@echo off
rem ===== 一键启动 MusicQuery Agent（Windows 本机便捷脚本） =====
rem 本脚本依赖本机手动建好的计划任务 MusicQueryMySQL / MusicQueryApp。
rem 换一台机器（例如交给同伴）时请勿使用本脚本 —— 请按 README「快速开始」：
rem 先启动 MySQL，再在项目目录执行 streamlit run app.py
setlocal

schtasks /query /tn MusicQueryMySQL >nul 2>&1
if errorlevel 1 (
    echo.
    echo [提示] 未找到计划任务 MusicQueryMySQL —— 本脚本是本机专用的快捷启动方式，
    echo        它依赖手动创建的计划任务，新环境里不存在。
    echo.
    echo        请改用 README「快速开始」：
    echo          1^) 启动 MySQL（或确认已运行）
    echo          2^) 在项目目录执行： streamlit run app.py
    echo.
    pause
    exit /b 1
)

schtasks /run /tn MusicQueryMySQL >nul 2>&1
schtasks /run /tn MusicQueryApp >nul 2>&1
timeout /t 8 /nobreak >nul
start http://localhost:8501
echo 已启动：数据库 + 网页应用，浏览器即将打开 http://localhost:8501
