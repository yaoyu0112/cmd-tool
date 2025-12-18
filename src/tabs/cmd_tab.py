import os
import shutil
import subprocess
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QFileDialog
)
from PyQt6.QtCore import Qt


class CmdTab(QWidget):
    def __init__(self, output, sftp_tab=None):
        """
        :param output: QTextEdit，用來顯示主輸出
        :param sftp_tab: FtpTab 實例，可使用其 FTP 上傳功能
        """
        super().__init__()
        self.output = output
        self.sftp_tab = sftp_tab
        self.working_dir = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # ── 執行路徑設定區 ──
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        browse_button = QPushButton("瀏覽")
        browse_button.clicked.connect(self.select_folder)

        confirm_button = QPushButton("✅ 確定路徑")
        confirm_button.clicked.connect(self.confirm_folder)

        folder_layout.addWidget(QLabel("CMD 執行資料夾："))
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse_button)
        folder_layout.addWidget(confirm_button)
        layout.addLayout(folder_layout)

        # ── CMD 指令區 ──
        layout.addWidget(QLabel("💬 輸入 CMD 指令："))
        self.cmd_input = QLineEdit()
        self.cmd_input.returnPressed.connect(self.run_command)
        layout.addWidget(self.cmd_input)

        run_button = QPushButton("執行")
        run_button.clicked.connect(self.run_command)
        layout.addWidget(run_button)

        # ── 複製功能區 ──
        layout.addWidget(QLabel("📦 複製檔案或資料夾："))

        # 來源選擇
        from_layout = QHBoxLayout()
        self.from_input = QLineEdit()
        from_button = QPushButton("選來源")
        from_button.clicked.connect(self.select_copy_source)
        from_layout.addWidget(QLabel("來源："))
        from_layout.addWidget(self.from_input)
        from_layout.addWidget(from_button)
        layout.addLayout(from_layout)

        # 本地目標
        to_layout = QHBoxLayout()
        self.to_input = QLineEdit()
        to_button = QPushButton("選目標")
        to_button.clicked.connect(self.select_copy_target)
        to_layout.addWidget(QLabel("本地目標："))
        to_layout.addWidget(self.to_input)
        to_layout.addWidget(to_button)
        layout.addLayout(to_layout)

        # SFTP 目標
        ftp_layout = QHBoxLayout()
        self.ftp_target_input = QLineEdit()
        ftp_layout.addWidget(QLabel("SFTP 目標路徑："))
        ftp_layout.addWidget(self.ftp_target_input)
        layout.addLayout(ftp_layout)

        # 匯入設定檔按鈕
        import_button = QPushButton("📂 匯入設定檔")
        import_button.clicked.connect(self.import_json_config)
        layout.addWidget(import_button)

        # 按鈕：本地複製、SFTP 上傳
        btn_layout = QHBoxLayout()
        copy_button = QPushButton("📋 本地複製")
        copy_button.clicked.connect(self.copy_item)

        upload_button = QPushButton("🌐 上傳到 SFTP")
        upload_button.clicked.connect(self.upload_to_sftp)

        btn_layout.addWidget(copy_button)
        btn_layout.addWidget(upload_button)
        layout.addLayout(btn_layout)

        # 自己區塊內部 log 輸出（可選）
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        layout.addWidget(self.output_display)

        self.setLayout(layout)

    # ──────── 功能區 ────────

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if folder:
            self.folder_input.setText(folder)

    def confirm_folder(self):
        folder = self.folder_input.text().strip()
        if folder:
            self.working_dir = folder
            self.log(f"✅ 已設定執行路徑為：{folder}\n")
        else:
            self.log("⚠️ 請選擇一個有效的資料夾！\n")

    def run_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=self.working_dir or None
            )
            output = f"> {cmd}\n{result.stdout}{result.stderr}\n"
        except Exception as e:
            output = f"執行錯誤：{e}\n"

        self.log(output)
        self.cmd_input.clear()

    def select_copy_source(self):
        """
        只選擇來源資料夾
        """
        path = QFileDialog.getExistingDirectory(self, "選擇來源資料夾")
        if path:
            self.from_input.setText(path)

    def select_copy_target(self):
        path = QFileDialog.getExistingDirectory(self, "選擇目標資料夾")
        if path:
            self.to_input.setText(path)

    def copy_item(self):
        source = self.from_input.text().strip()
        target = self.to_input.text().strip()

        if not source or not target:
            self.log("⚠️ 請選擇來源與目標！\n")
            return

        try:
            dest_path = os.path.join(target, os.path.basename(source))
            if os.path.isdir(source):
                if os.path.exists(dest_path):
                    self.log(f"⚠️ 目標已存在：{dest_path}。\n")
                    return
                shutil.copytree(source, dest_path)
            elif os.path.isfile(source):
                shutil.copy2(source, dest_path)
            else:
                self.log("⚠️ 來源不是檔案也不是資料夾。\n")
                return
            self.log(f"✅ 複製成功：\n{source} ➡️ {dest_path}\n")
        except Exception as e:
            self.log(f"❌ 複製失敗：{e}\n")

    def upload_to_sftp(self):
        if not self.sftp_tab:
            self.log("❌ 未設定 SFTP 模組，無法上傳！\n")
            return

        source = self.from_input.text().strip()
        remote_target = self.ftp_target_input.text().strip() or "/"

        if not os.path.exists(source):
            self.log("⚠️ 請提供有效的來源路徑！\n")
            return

        if os.path.isdir(source):
            self.upload_directory(source, remote_target)
        elif os.path.isfile(source):
            self.sftp_tab.upload_file(source, remote_target, ensure_dir=True)
        else:
            self.log("⚠️ 來源不是有效的檔案或資料夾！\n")

    def upload_directory(self, local_dir, remote_dir):
        for root, dirs, files in os.walk(local_dir):
            relative_path = os.path.relpath(root, local_dir)
            remote_subdir = os.path.join(remote_dir, relative_path).replace("\\", "/")
            for file in files:
                full_local_path = os.path.join(root, file)
                self.sftp_tab.upload_file(full_local_path, remote_subdir, ensure_dir=True)

    def import_json_config(self):
        """
        匯入 JSON 設定檔並填入來源、本地目標與 SFTP 目標路徑
        格式：
        {
            "source": "來源路徑",
            "local_target": "本地目標路徑",
            "sftp_target": "SFTP目標路徑"
        }
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "選擇設定檔", "", "JSON Files (*.json)")
        if not file_name:
            return

        try:
            with open(file_name, "r", encoding="utf-8") as f:
                config = json.load(f)

            self.from_input.setText(config.get("source", ""))
            self.to_input.setText(config.get("local_target", ""))
            self.ftp_target_input.setText(config.get("sftp_target", ""))

            self.log(f"✅ 已匯入設定檔：{file_name}\n")
        except Exception as e:
            self.log(f"❌ 匯入設定檔失敗：{e}\n")

    def log(self, message: str):
        if self.output_display:
            self.output_display.append(message)
        if self.output:
            self.output.append(message)