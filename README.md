# CMD GUI Tool

一個功能完整的 CMD 控制工具，具備 GUI 界面和 SFTP 功能。

## 功能特色

- 🖥️ **GUI 界面**：使用 PyQt6 開發的友善圖形界面
- 📁 **檔案管理**：支援本地檔案複製和目錄操作
- 🌐 **SFTP 功能**：完整的遠端檔案傳輸功能
- ⚙️ **自動化設定**：支援 JSON 設定檔匯入
- 💻 **CMD 整合**：內建命令列執行功能
- 📦 **可執行檔**：支援打包成獨立執行檔

## 系統需求

- Python 3.8 或以上版本
- Windows、macOS 或 Linux 系統

## 快速安裝

### 方式一：自動安裝 (推薦)

**Windows 用戶：**
```bash
# 雙擊執行
install.bat
```

**Linux/macOS 用戶：**
```bash
chmod +x install.sh
./install.sh
```

### 方式二：手動安裝

1. 克隆專案：
```bash
git clone https://github.com/yaoyu0112/cmd-tool.git
cd cmd-tool
```

2. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

3. 啟動程式：
```bash
python cmd_tool.py
```

### 方式三：使用 setuptools

```bash
# 從原始碼安裝
pip install .

# 開發模式安裝
pip install -e .

# 包含開發工具
pip install -e .[dev]
```

## 使用方式

### 基本啟動
```bash
python cmd_tool.py
```

### 虛擬環境啟動
```bash
# 如果使用虛擬環境
.venv/Scripts/python.exe cmd_tool.py  # Windows
.venv/bin/python cmd_tool.py          # Linux/macOS
```

## 打包為執行檔

使用 PyInstaller 將程式打包成獨立執行檔：

```bash
pyinstaller --onefile --noconsole cmd_tool.py
```

打包完成後，執行檔位於 `dist/` 目錄中。

## 設定檔格式

程式支援 JSON 格式的設定檔，範例如下：

```json
{
  "sftp_host": "your-server.com",
  "sftp_port": 22,
  "sftp_user": "username",
  "sftp_pass": "password",
  "cmd_working_dir": "C:/your/project/path",
  "cmd_command": "npm run build",
  "cmd_copy_source": "C:/your/project/dist",
  "sftp_target_path": "/remote/target/path"
}
```

## 專案結構

```
cmd_gui_tool/
├── cmd_tool.py          # 主程式
├── cmd_tab.py           # CMD 控制模組
├── sftp_tab.py          # SFTP 功能模組
├── settings_tab.py      # 設定管理模組
├── requirements.txt     # 依賴套件清單
├── setup.py            # 安裝設定檔
├── pyproject.toml      # 現代 Python 專案設定
├── install.bat         # Windows 自動安裝腳本
├── install.sh          # Linux/macOS 自動安裝腳本
├── input_config.json   # 設定檔範例
└── read.md            # 原始說明文件
```

## 依賴套件

- **PyQt6** (>=6.0.0) - GUI 框架
- **paramiko** (>=2.7.0) - SSH/SFTP 功能
- **pyinstaller** (>=4.0.0) - 執行檔打包工具 (可選)

## 授權條款

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 聯繫方式

- GitHub: [yaoyu0112/cmd-tool](https://github.com/yaoyu0112/cmd-tool)
- Issues: [回報問題](https://github.com/yaoyu0112/cmd-tool/issues)