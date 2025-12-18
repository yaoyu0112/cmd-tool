@echo off
echo ================================
echo   CMD GUI Tool 套件安裝程式
echo ================================
echo.

echo [1/4] 檢查 Python 環境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：找不到 Python！請先安裝 Python 3.8 或以上版本
    echo 下載連結：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python 環境已就緒
echo.

echo [2/4] 升級 pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ pip 升級失敗
    pause
    exit /b 1
)
echo ✅ pip 已升級
echo.

echo [3/4] 安裝必要套件...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 套件安裝失敗
    pause
    exit /b 1
)
echo ✅ 套件安裝完成
echo.

echo [4/4] 測試程式啟動...
echo 正在測試 PyQt6...
python -c "import PyQt6; print('PyQt6 OK')"
if errorlevel 1 (
    echo ❌ PyQt6 測試失敗
    pause
    exit /b 1
)

echo 正在測試 paramiko...
python -c "import paramiko; print('paramiko OK')"
if errorlevel 1 (
    echo ❌ paramiko 測試失敗
    pause
    exit /b 1
)

echo.
echo ================================
echo   🎉 安裝完成！
echo ================================
echo.
echo 啟動方式：
echo   python cmd_tool.py
echo.
echo 打包方式：
echo   pyinstaller --onefile --noconsole cmd_tool.py
echo.
pause