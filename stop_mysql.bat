@echo off
rem ===== 停止 MySQL 释放内存（Windows 本机便捷脚本） =====
rem 账号密码统一从 .env 读取，不写死在脚本里（避免随仓库公开泄露）
rem MySQL 路径自动探测：优先 .env 里的 MYSQL_BIN，其次搜索系统 PATH
setlocal

if not exist "%~dp0.env" (
    echo [错误] 未找到 .env 文件，请先复制 .env.example 为 .env 并填写数据库配置。
    pause
    exit /b 1
)

for /f "usebackq tokens=1,* delims==" %%a in ("%~dp0.env") do (
    if /i "%%a"=="DB_USER" set "DB_USER=%%b"
    if /i "%%a"=="DB_PASSWORD" set "DB_PASSWORD=%%b"
    if /i "%%a"=="MYSQL_BIN" set "MYSQL_BIN=%%b"
)

if not defined DB_PASSWORD (
    echo [错误] 未在 .env 中找到 DB_PASSWORD，请检查配置文件。
    pause
    exit /b 1
)

set "MYSQLADMIN_EXE="
if defined MYSQL_BIN if exist "%MYSQL_BIN%\mysqladmin.exe" set "MYSQLADMIN_EXE=%MYSQL_BIN%\mysqladmin.exe"
if not defined MYSQLADMIN_EXE for %%i in (mysqladmin.exe) do if not "%%~$PATH:i"=="" set "MYSQLADMIN_EXE=%%~$PATH:i"
if not defined MYSQLADMIN_EXE (
    echo [错误] 找不到 mysqladmin.exe。
    echo         请在 .env 中设置 MYSQL_BIN 指向 MySQL 的 bin 目录，例如：
    echo         MYSQL_BIN=E:\mysql-8.4.9-winx64\bin
    echo         或把该目录加入系统 PATH。
    pause
    exit /b 1
)

rem 通过 MYSQL_PWD 传递密码，避免密码出现在命令行参数中
set "MYSQL_PWD=%DB_PASSWORD%"
"%MYSQLADMIN_EXE%" -u %DB_USER% shutdown
set "MYSQL_PWD="

echo MySQL 已停止。下次使用请双击 start_mysql.bat
pause
