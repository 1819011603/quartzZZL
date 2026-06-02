@echo off
chcp 65001 >nul
title C 盘深度清理脚本 v3
color 0A

echo ========================================
echo        C 盘深度清理脚本 v3
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 请右键 "以管理员身份运行" 本脚本！
    pause
    exit /b
)

echo [提示] 清理前请关闭 WPS / Office / 微信 / QQ / 钉钉 / 飞书！
echo.
pause

echo.
echo ===== 一、系统级清理 =====

echo [1] 清理系统临时文件 %TEMP% ...
del /f /s /q "%TEMP%\*.*" >nul 2>&1
for /d %%i in ("%TEMP%\*") do rd /s /q "%%i" >nul 2>&1

echo [2] 清理 Windows\Temp ...
del /f /s /q "C:\Windows\Temp\*.*" >nul 2>&1
for /d %%i in ("C:\Windows\Temp\*") do rd /s /q "%%i" >nul 2>&1

echo [3] 清理预读取文件 Prefetch ...
del /f /s /q "C:\Windows\Prefetch\*.*" >nul 2>&1

echo [4] 清理用户临时文件 ...
del /f /s /q "%USERPROFILE%\AppData\Local\Temp\*.*" >nul 2>&1
for /d %%i in ("%USERPROFILE%\AppData\Local\Temp\*") do rd /s /q "%%i" >nul 2>&1

echo [5] 清理回收站 ...
rd /s /q "C:\$Recycle.Bin" >nul 2>&1

echo [6] 清理 Windows 更新缓存 ...
net stop wuauserv >nul 2>&1
net stop bits >nul 2>&1
del /f /s /q "C:\Windows\SoftwareDistribution\Download\*.*" >nul 2>&1
for /d %%i in ("C:\Windows\SoftwareDistribution\Download\*") do rd /s /q "%%i" >nul 2>&1
net start wuauserv >nul 2>&1
net start bits >nul 2>&1

echo [7] 清理日志与 Dump ...
del /f /s /q "C:\Windows\Logs\CBS\*.log" >nul 2>&1
del /f /s /q "C:\Windows\*.dmp" >nul 2>&1
del /f /s /q "C:\Windows\Minidump\*.*" >nul 2>&1
del /f /s /q "%LOCALAPPDATA%\CrashDumps\*.*" >nul 2>&1

echo [8] 清理字体缓存 ...
del /f /s /q "%LOCALAPPDATA%\FontCache\*.*" >nul 2>&1

echo [9] 清理缩略图缓存 ...
del /f /s /q "%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*.db" >nul 2>&1
del /f /s /q "%LOCALAPPDATA%\Microsoft\Windows\Explorer\iconcache_*.db" >nul 2>&1

echo.
echo ===== 二、WPS / Office 残留清理 =====

echo [10] WPS 备份文件（30 天以上）...
forfiles /p "%APPDATA%\Kingsoft\office6\backup" /s /m *.* /d -30 /c "cmd /c del /f /q @path" >nul 2>&1
forfiles /p "%LOCALAPPDATA%\Kingsoft\WPS Office\backup" /s /m *.* /d -30 /c "cmd /c del /f /q @path" >nul 2>&1
forfiles /p "%APPDATA%\Kingsoft\WPS Cloud Files\userdata" /s /m *.tmp /d -7 /c "cmd /c del /f /q @path" >nul 2>&1

:: WPS 临时文件
del /f /s /q "%APPDATA%\Kingsoft\office6\*.tmp" >nul 2>&1
del /f /s /q "%LOCALAPPDATA%\Kingsoft\WPS Office\*.tmp" >nul 2>&1
del /f /s /q "%APPDATA%\Kingsoft\office6\*.bak" >nul 2>&1

:: WPS 日志
rd /s /q "%LOCALAPPDATA%\Kingsoft\WPS Office\log" >nul 2>&1
rd /s /q "%LOCALAPPDATA%\Kingsoft\wpscloudsvr\log" >nul 2>&1

echo [11] Office 缓存与残留 ...
rd /s /q "%LOCALAPPDATA%\Microsoft\Office\16.0\OfficeFileCache" >nul 2>&1
rd /s /q "%LOCALAPPDATA%\Microsoft\Office\UnsavedFiles" >nul 2>&1
del /f /s /q "%APPDATA%\Microsoft\Templates\~*.*" >nul 2>&1

echo [12] 全盘 .wbk / .asd / ~$ 临时文件（用户目录,30 天以上）...
forfiles /p "%USERPROFILE%" /s /m ~$*.* /d -30 /c "cmd /c del /f /q @path" >nul 2>&1
forfiles /p "%USERPROFILE%" /s /m *.wbk /d -30 /c "cmd /c del /f /q @path" >nul 2>&1
forfiles /p "%USERPROFILE%" /s /m *.asd /d -30 /c "cmd /c del /f /q @path" >nul 2>&1
forfiles /p "%USERPROFILE%" /s /m *.tmp /d -30 /c "cmd /c del /f /q @path" >nul 2>&1

echo.
echo ===== 三、常用软件缓存 =====

echo [13] 微信文件缓存（仅 Cache,不动聊天记录）...
for /d %%i in ("%USERPROFILE%\Documents\WeChat Files\*") do (
    rd /s /q "%%i\FileStorage\Cache" >nul 2>&1
    rd /s /q "%%i\FileStorage\CDN" >nul 2>&1
)

echo [14] QQ 缓存 ...
for /d %%i in ("%USERPROFILE%\Documents\Tencent Files\*") do (
    rd /s /q "%%i\FileRecv\MobileFile" >nul 2>&1
    rd /s /q "%%i\Image\C2C" >nul 2>&1
    rd /s /q "%%i\Image\Group" >nul 2>&1
)

echo [15] 钉钉缓存 ...
rd /s /q "%USERPROFILE%\AppData\Roaming\DingTalk\cache" >nul 2>&1
for /d %%i in ("%USERPROFILE%\AppData\Roaming\DingTalk\*") do (
    rd /s /q "%%i\ImageCache" >nul 2>&1
    rd /s /q "%%i\VideoCache" >nul 2>&1
)

echo [16] 飞书缓存 ...
rd /s /q "%LOCALAPPDATA%\Lark\Cache" >nul 2>&1
rd /s /q "%LOCALAPPDATA%\Feishu\Cache" >nul 2>&1

echo [17] NVIDIA / 显卡缓存 ...
rd /s /q "%LOCALAPPDATA%\NVIDIA\DXCache" >nul 2>&1
rd /s /q "%LOCALAPPDATA%\NVIDIA\GLCache" >nul 2>&1

echo [18] DirectX Shader 缓存 ...
rd /s /q "%LOCALAPPDATA%\D3DSCache" >nul 2>&1

echo.
echo ===== 四、最终系统清理 =====

echo [19] 调用系统磁盘清理工具 ...
cleanmgr /sagerun:1 >nul 2>&1

echo.
echo ========================================
echo            全部清理完成！
echo ========================================
echo.

:: 显示 C 盘剩余空间
for /f "tokens=3" %%a in ('dir c:\ ^| findstr /c:"可用字节"') do set free=%%a
echo C 盘剩余空间: %free% 字节
echo.

pause
