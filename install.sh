#!/bin/bash

echo "================================"
echo "  CMD GUI Tool 套件安裝程式"
echo "================================"
echo

# 檢查 Python 環境
echo "[1/4] 檢查 Python 環境..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ 錯誤：找不到 Python！請先安裝 Python 3.8 或以上版本"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Python 環境已就緒"
echo

# 升級 pip
echo "[2/4] 升級 pip..."
$PYTHON_CMD -m pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "❌ pip 升級失敗"
    exit 1
fi
echo "✅ pip 已升級"
echo

# 安裝套件
echo "[3/4] 安裝必要套件..."
$PYTHON_CMD -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 套件安裝失敗"
    exit 1
fi
echo "✅ 套件安裝完成"
echo

# 測試套件
echo "[4/4] 測試程式啟動..."
echo "正在測試 PyQt6..."
$PYTHON_CMD -c "import PyQt6; print('PyQt6 OK')"
if [ $? -ne 0 ]; then
    echo "❌ PyQt6 測試失敗"
    exit 1
fi

echo "正在測試 paramiko..."
$PYTHON_CMD -c "import paramiko; print('paramiko OK')"
if [ $? -ne 0 ]; then
    echo "❌ paramiko 測試失敗"
    exit 1
fi

echo
echo "================================"
echo "  🎉 安裝完成！"
echo "================================"
echo
echo "啟動方式："
echo "  $PYTHON_CMD cmd_tool.py"
echo
echo "打包方式："
echo "  pyinstaller --onefile --noconsole cmd_tool.py"
echo