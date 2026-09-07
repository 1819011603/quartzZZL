@echo off
setlocal enableextensions enabledelayedexpansion
title YunShu / GoTuLink Monitor Toggle (keep VPN)

REM ==== auto elevate to administrator ====
net session >nul 2>&1
if %errorlevel% neq 0 (
  echo Requesting administrator rights...
  powershell -Command "Start-Process -Verb RunAs -FilePath '%~f0'"
  exit /b
)

set "A=C:\Program Files\YunShu"
set "B=C:\Program Files\YunShu Plugin"

:MENU
cls
echo ==================================================================
echo   YunShu / GoTuLink  Monitor Toggle
echo ------------------------------------------------------------------
echo   KEEP:   VPN tunnel (wintun/libtunnel), YunShu main app, NAC
echo           Sunlogin remote control (left untouched by request)
echo   TARGET: DLP monitoring (screen-record/watermark/process/
echo           browser/mail/OCR-scan/remote-script ...)
echo ==================================================================
echo.
echo   [1] Disable monitoring plugins  (keep VPN, reversible)
echo   [2] Restore monitoring plugins  (rename back)
echo   [3] Stop all YunShu incl. VPN   (this session only)
echo   [0] Exit
echo.
set /p CH=Enter choice and press Enter:
if "%CH%"=="1" goto DISABLE
if "%CH%"=="2" goto RESTORE
if "%CH%"=="3" goto STOPALL
if "%CH%"=="0" exit /b
goto MENU

:DISABLE
echo.
echo === Killing monitoring / holder processes (not VPN, not Sunlogin) ===
for %%P in ("YunShu Plugin.exe" "YunShu dpengine.exe" "YunShu ScreenLock.exe" "CcOwl.exe" "CcFfmpeg.exe" "CcFileWatermark.exe" "TBRunner.exe" "aitools.exe") do (
  taskkill /f /im %%~P >nul 2>&1 && echo   killed %%~P
)
ping -n 2 127.0.0.1 >nul
echo.
echo === Renaming monitoring components to .disabled ===
set OKN=0
set FAILN=0
set ACTION=ren
call :RUNLIST
echo.
echo Done:  OK !OKN!   Failed(locked/protected) !FAILN!
if !FAILN! gtr 0 (
  echo.
  echo Some renames failed - usually YunShu self-protection.
  echo Reboot into SAFE MODE and run this script option 1 again.
)
echo.
pause
goto MENU

:RESTORE
echo.
echo === Restoring monitoring components ===
set OKN=0
set FAILN=0
set ACTION=unren
call :RUNLIST
echo.
echo Restore done. If VPN worked before, it stays the same.
echo.
pause
goto MENU

:STOPALL
echo.
echo === Stopping all YunShu services/processes (incl. VPN, this session) ===
net stop YunShuService >nul 2>&1 && echo   stopped YunShuService || echo   stop YunShuService failed (protected)
for %%P in ("YunShu.exe" "YunShuLauncher.exe" "YunShu Plugin.exe" "YunShu dpengine.exe" "YunShu ScreenLock.exe" "YunShu Message.exe" "YunShu Diagnosis.exe" "TBRunner.exe" "CcOwl.exe" "aitools.exe") do (
  taskkill /f /im %%~P >nul 2>&1 && echo   killed %%~P
)
echo.
echo Note: services auto-restart after reboot. To stop VPN for good, uninstall.
echo.
pause
goto MENU

REM ================= component list (shared by disable/restore) =================
:RUNLIST
REM --- Sunlogin remote control (slsdk / SLDesktopAgent / plugins) kept, not touched ---
call :%ACTION% "%B%\CcMoniter.dll"
call :%ACTION% "%B%\CcFfmpeg.exe"
call :%ACTION% "%B%\CcWaterMark.dll"
call :%ACTION% "%B%\CcWaterMark-x64.dll"
call :%ACTION% "%B%\CcFileWatermark.exe"
call :%ACTION% "%B%\CcFileWaterShell.dll"
call :%ACTION% "%B%\CcFileWaterShell-x64.dll"
call :%ACTION% "%B%\FileWaterMark.dll"
call :%ACTION% "%B%\FileWaterMark-client-x64.dll"
call :%ACTION% "%B%\CcProcess.dll"
call :%ACTION% "%B%\CcBrowser.dll"
call :%ACTION% "%B%\CcBrowserPluginManager.dll"
call :%ACTION% "%B%\CcDetect.dll"
call :%ACTION% "%B%\CcSoftManage.dll"
call :%ACTION% "%B%\CcInject.dll"
call :%ACTION% "%B%\CcInject-x64.dll"
call :%ACTION% "%B%\CcOwl.exe"
call :%ACTION% "%B%\CcEtw.dll"
call :%ACTION% "%B%\ImLocate.dll"
call :%ACTION% "%B%\libChannelSense.dll"
call :%ACTION% "%B%\Packet.dll"
call :%ACTION% "%B%\wpcap.dll"
call :%ACTION% "%B%\OutlookAddin32.dll"
call :%ACTION% "%B%\OutlookAddin64.dll"
call :%ACTION% "%B%\OutlookPlugin32.dll"
call :%ACTION% "%B%\OutlookPlugin64.dll"
call :%ACTION% "%B%\YunShu dpengine.exe"
call :%ACTION% "%B%\YunShu ScreenLock.exe"
call :%ACTION% "%B%\scanlib"
call :%ACTION% "%B%\channel_model"
call :%ACTION% "%B%\ScriptEngine"
call :%ACTION% "%B%\ScriptEngineNew"
goto :eof

:ren
set "full=%~1"
if exist "%full%" (
  ren "%full%" "%~nx1.disabled" 2>nul && ( echo   [OK]   %~nx1 & set /a OKN+=1 ) || ( echo   [FAIL] %~nx1 & set /a FAILN+=1 )
) else (
  if exist "%full%.disabled" ( echo   [off]  %~nx1 ) else ( echo   [none] %~nx1 )
)
goto :eof

:unren
set "full=%~1"
if exist "%full%.disabled" (
  ren "%full%.disabled" "%~nx1" 2>nul && ( echo   [restored] %~nx1 & set /a OKN+=1 ) || ( echo   [FAIL] %~nx1 & set /a FAILN+=1 )
) else (
  if exist "%full%" ( echo   [on]   %~nx1 ) else ( echo   [none] %~nx1 )
)
goto :eof
