@echo off
rem ===== 停止网页应用（数据库如也暂不用，可再运行 stop_mysql.bat） =====
taskkill /F /IM streamlit.exe >nul 2>&1
echo 网页应用已停止。
pause
