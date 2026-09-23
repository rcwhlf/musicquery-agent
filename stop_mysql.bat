@echo off
rem ===== 停止 MySQL 释放内存 =====
E:\mysql-8.4.9-winx64\bin\mysqladmin.exe -u root -p123456 shutdown
echo MySQL 已停止。下次使用请双击 start_mysql.bat
pause
