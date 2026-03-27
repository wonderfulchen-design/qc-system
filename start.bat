@echo off
chcp 65001 >nul
echo ========================================
echo   QC System - 一键启动脚本
echo ========================================
echo.
echo 正在启动后端服务...
echo.
echo 访问地址：http://localhost:8000
echo API 文档：http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

cd /d "%~dp0backend"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
