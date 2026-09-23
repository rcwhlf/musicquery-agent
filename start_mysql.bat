@echo off
rem ===== 按需启动 MySQL（不会开机自启，用完可运行 stop_mysql.bat 释放内存） =====
schtasks /run /tn MusicQueryMySQL
timeout /t 5 /nobreak >nul
E:\mysql-8.4.9-winx64\bin\mysql.exe -u root -p123456 -e "SELECT 'MySQL OK' AS status;"
