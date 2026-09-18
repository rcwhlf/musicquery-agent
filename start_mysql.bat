@echo off
rem ===== 启动 MusicQuery Agent 使用的 MySQL 8.4 =====
rem 双击运行后会弹出控制台窗口，窗口开着数据库就可用；关闭窗口即停止数据库
E:\mysql-8.4.9-winx64\bin\mysqld.exe --defaults-file=E:\mysql-8.4.9-winx64\my.ini --console
