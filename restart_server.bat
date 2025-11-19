@echo off
echo ========================================
echo 动态币种管理系统 - 服务器重启
echo ========================================
echo.

echo [1/3] 终止所有 Python 进程...
taskkill /F /IM python.exe 2>nul
if %errorlevel% == 0 (
    echo   [OK] Python 进程已终止
) else (
    echo   [INFO] 无运行中的 Python 进程
)

echo.
echo [2/3] 等待 2 秒...
timeout /t 2 /nobreak >nul
echo   [OK] 等待完成

echo.
echo [3/3] 启动 Flask 服务器...
cd E:\code\nof1_enhanced
python app.py
