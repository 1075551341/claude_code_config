@echo off
chcp 65001 >nul 2>&1
title Claude Code 工具同步

:: 检查是否已有管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在请求管理员权限...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\" %*' -Verb RunAs"
    exit /b
)

echo.
echo ========================================
echo   Claude Code 工具同步
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0sync-tools.ps1" %*

echo.
echo 按任意键关闭...
pause >nul
