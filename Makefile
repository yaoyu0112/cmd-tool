# CMD GUI Tool - 開發者 Makefile

# 變數定義
PYTHON := python
PIP := $(PYTHON) -m pip
VENV := .venv
DIST_DIR := dist
BUILD_DIR := build

# 預設目標
.PHONY: help
help:
	@echo "CMD GUI Tool 開發指令："
	@echo ""
	@echo "安裝與設定："
	@echo "  install        安裝專案依賴套件"
	@echo "  install-dev    安裝開發依賴套件"
	@echo "  venv          建立虛擬環境"
	@echo ""
	@echo "開發工具："
	@echo "  run           啟動程式"
	@echo "  test          執行測試"
	@echo "  clean         清理建置檔案"
	@echo ""
	@echo "打包與發布："
	@echo "  build         建置套件"
	@echo "  build-exe     打包成執行檔"
	@echo "  dist          建立發布版本"

# 安裝依賴
.PHONY: install
install:
	$(PIP) install -r requirements.txt

.PHONY: install-dev
install-dev:
	$(PIP) install -e .[dev]

# 虛擬環境
.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV)
	@echo "虛擬環境已建立在 $(VENV)"
	@echo "啟動方式："
	@echo "  Windows: $(VENV)\\Scripts\\activate.bat"
	@echo "  Linux/macOS: source $(VENV)/bin/activate"

# 執行程式
.PHONY: run
run:
	$(PYTHON) cmd_tool.py

# 測試
.PHONY: test
test:
	@echo "測試 PyQt6 套件..."
	$(PYTHON) -c "import PyQt6; print('✅ PyQt6 OK')"
	@echo "測試 paramiko 套件..."
	$(PYTHON) -c "import paramiko; print('✅ paramiko OK')"
	@echo "測試主程式..."
	$(PYTHON) -c "import cmd_tool; print('✅ cmd_tool OK')"

# 清理
.PHONY: clean
clean:
	@echo "清理建置檔案..."
	-rm -rf $(BUILD_DIR)
	-rm -rf $(DIST_DIR)
	-rm -rf *.egg-info
	-rm -rf __pycache__
	-rm -rf .pytest_cache
	-find . -name "*.pyc" -delete
	-find . -name "*.pyo" -delete
	-find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "清理完成"

# 建置套件
.PHONY: build
build: clean
	$(PYTHON) -m build

# 建置執行檔
.PHONY: build-exe
build-exe: clean
	pyinstaller --onefile --noconsole cmd_tool.py
	@echo "執行檔已建立在 $(DIST_DIR)/cmd_tool.exe"

# 發布準備
.PHONY: dist
dist: clean build build-exe
	@echo "發布檔案已準備完成"