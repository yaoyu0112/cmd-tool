### 包版指令:
pyinstaller --onefile --noconsole cmd_tool.py

### 環境設置:
pip install PyQt6 paramiko

### 快速安裝 (推薦):
# Windows 用戶
install.bat

# Linux/macOS 用戶
chmod +x install.sh && ./install.sh

### 啟動指令:
python cmd_tool.py

### 虛擬環境啟動指令:
C:/Users/keror/Desktop/cmd_gui_tool/.venv/Scripts/python.exe cmd_tool.py

### 套件安裝方式:
# 從 requirements.txt 安裝
pip install -r requirements.txt

# 使用 setup.py 安裝
pip install .

# 開發模式安裝
pip install -e .[dev]