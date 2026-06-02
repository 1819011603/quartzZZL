@echo off
chcp 65001 >nul
title C 盘一键清理
color 0A

echo ========================================
echo        C 盘一键清理脚本
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 请右键 "以管理员身份运行" 本脚本！
    pause
    exit /b
)

echo [1/8] 清理系统临时文件 %TEMP% ...
del /f /s /q "%TEMP%\*.*" >nul 2>&1
for /d %%i in ("%TEMP%\*") do rd /s /q "%%i" >nul 2>&1

echo [2/8] 清理 Windows 临时文件 C:\Windows\Temp ...
del /f /s /q "C:\Windows\Temp\*.*" >nul 2>&1
for /d %%i in ("C:\Windows\Temp\*") do rd /s /q "%%i" >nul 2>&1

echo [3/8] 清理预读取文件 Prefetch ...
del /f /s /q "C:\Windows\Prefetch\*.*" >nul 2>&1

echo [4/8] 清理用户临时文件 ...
del /f /s /q "%USERPROFILE%\AppData\Local\Temp\*.*" >nul 2>&1
for /d %%i in ("%USERPROFILE%\AppData\Local\Temp\*") do rd /s /q "%%i" >nul 2>&1

echo [5/8] 清理回收站 ...
rd /s /q "C:\$Recycle.Bin" >nul 2>&1

echo [6/8] 清理 Windows 更新缓存 ...
net stop wuauserv >nul 2>&1
net stop bits >nul 2>&1
del /f /s /q "C:\Windows\SoftwareDistribution\Download\*.*" >nul 2>&1
for /d %%i in ("C:\Windows\SoftwareDistribution\Download\*") do rd /s /q "%%i" >nul 2>&1
net start wuauserv >nul 2>&1
net start bits >nul 2>&1

echo [7/8] 清理日志与 Dump 文件 ...
del /f /s /q "C:\Windows\Logs\CBS\*.log" >nul 2>&1
del /f /s /q "C:\Windows\*.dmp" >nul 2>&1
del /f /s /q "C:\Windows\Minidump\*.*" >nul 2>&1
del /f /s /q "%LOCALAPPDATA%\CrashDumps\*.*" >nul 2>&1

echo [8/8] 调用系统磁盘清理工具 ...
cleanmgr /sagerun:1 >nul 2>&1

echo.
echo ========================================
echo            清理完成！
echo ========================================
echo.
pause
