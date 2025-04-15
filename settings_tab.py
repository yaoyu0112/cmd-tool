import json
import os
import subprocess
from ftplib import FTP
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QGroupBox
)


class SettingsTab(QWidget):
    def __init__(self, output_display):
        super().__init__()
        self.output = output_display  # 輸出顯示區（來自主視窗）
        self.init_ui()  # 初始化 UI

    def init_ui(self):
        layout = QVBoxLayout()

        # 匯入 JSON 設定檔按鈕
        load_button = QPushButton("匯入 JSON 設定檔")
        load_button.clicked.connect(self.load_json_file)
        layout.addWidget(load_button)

        # ---------------- FTP 設定區塊 ----------------
        ftp_group = QGroupBox("FTP 設定")
        ftp_layout = QVBoxLayout()
        self.ftp_host_input = QLineEdit()
        self.ftp_user_input = QLineEdit()
        self.ftp_pass_input = QLineEdit()

        # 設定欄位為唯讀
        for widget in (self.ftp_host_input, self.ftp_user_input, self.ftp_pass_input):
            widget.setReadOnly(True)

        ftp_layout.addWidget(QLabel("FTP 主機名稱："))
        ftp_layout.addWidget(self.ftp_host_input)
        ftp_layout.addWidget(QLabel("使用者名稱："))
        ftp_layout.addWidget(self.ftp_user_input)
        ftp_layout.addWidget(QLabel("密碼："))
        ftp_layout.addWidget(self.ftp_pass_input)
        ftp_group.setLayout(ftp_layout)
        layout.addWidget(ftp_group)

        # ---------------- CMD 控制區塊 ----------------
        cmd_group = QGroupBox("CMD 控制")
        cmd_layout = QVBoxLayout()
        self.cmd_working_dir_input = QLineEdit()
        self.cmd_command_input = QLineEdit()
        self.cmd_copy_source_input = QLineEdit()
        self.ftp_target_path_input = QLineEdit()

        # 設定欄位為唯讀
        for widget in (
            self.cmd_working_dir_input,
            self.cmd_command_input,
            self.cmd_copy_source_input,
            self.ftp_target_path_input
        ):
            widget.setReadOnly(True)

        cmd_layout.addWidget(QLabel("CMD 執行資料夾："))
        cmd_layout.addWidget(self.cmd_working_dir_input)
        cmd_layout.addWidget(QLabel("輸入 CMD 指令："))
        cmd_layout.addWidget(self.cmd_command_input)
        cmd_layout.addWidget(QLabel("複製資料夾來源："))
        cmd_layout.addWidget(self.cmd_copy_source_input)
        cmd_layout.addWidget(QLabel("FTP 目標路徑："))
        cmd_layout.addWidget(self.ftp_target_path_input)
        cmd_group.setLayout(cmd_layout)
        layout.addWidget(cmd_group)

        # 套用設定按鈕
        self.apply_button = QPushButton("✅ 套用設定")
        layout.addWidget(self.apply_button)
        self.apply_button.clicked.connect(self.apply_settings)

        self.setLayout(layout)

    # 讀取 JSON 設定檔
    def load_json_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "選擇 JSON 檔案", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.fill_fields(data)  # 將資料填入欄位
            except Exception as e:
                print(f"❌ 讀取 JSON 錯誤: {e}")

    # 將 JSON 內容填入表單欄位
    def fill_fields(self, data):
        self.ftp_host_input.setText(data.get("ftp_host", ""))
        self.ftp_user_input.setText(data.get("ftp_user", ""))
        self.ftp_pass_input.setText(data.get("ftp_pass", ""))
        self.cmd_working_dir_input.setText(data.get("cmd_working_dir", ""))
        self.cmd_command_input.setText(data.get("cmd_command", ""))
        self.cmd_copy_source_input.setText(data.get("cmd_copy_source", ""))
        self.ftp_target_path_input.setText(data.get("ftp_target_path", ""))

    # 按下「套用設定」時執行的主邏輯流程
    def apply_settings(self):
        # 取得所有欄位資料
        self.ftp_host = self.ftp_host_input.text()
        self.ftp_user = self.ftp_user_input.text()
        self.ftp_pass = self.ftp_pass_input.text()
        self.cmd_working_dir = self.cmd_working_dir_input.text()
        self.cmd_command = self.cmd_command_input.text()
        self.cmd_copy_source = self.cmd_copy_source_input.text()
        self.ftp_target_path = self.ftp_target_path_input.text()

        # 執行流程：FTP → 切資料夾 → CMD → 上傳
        if not self.connect_ftp(): return
        if not self.change_working_directory(): return
        if not self.run_cmd_command(): return
        if not self.upload_folder_to_ftp(): return

        self.output.append("✅ 設定已成功套用！\n")

    # 連接 FTP 伺服器
    def connect_ftp(self):
        try:
            self.ftp = FTP(self.ftp_host)
            self.ftp.login(self.ftp_user, self.ftp_pass)
            self.output.append("✅ FTP 連線成功！\n")
            return True
        except Exception as e:
            self.output.append(f"❌ FTP 連線失敗：{e}\n")
            return False

    # 切換當前工作資料夾
    def change_working_directory(self):
        try:
            os.chdir(self.cmd_working_dir)
            self.output.append(f"✅ 切換至資料夾：{self.cmd_working_dir}\n")
            return True
        except Exception:
            self.output.append(f"❌ 找不到資料夾：{self.cmd_working_dir}\n")
            return False

    # 執行 CMD 指令
    def run_cmd_command(self):
        try:
            result = subprocess.run(
                self.cmd_command, shell=True, capture_output=True, text=True, cwd=self.cmd_working_dir
            )
            self.output.append(f"> {self.cmd_command}\n{result.stdout}{result.stderr}\n")
            return True
        except Exception as e:
            self.output.append(f"❌ 執行 CMD 指令時發生錯誤：{e}\n")
            return False

    # 處理檔案上傳前的檢查與清理
    def upload_folder_to_ftp(self):
        # 檢查來源資料夾是否存在
        if not os.path.isdir(self.cmd_copy_source):
            self.output.append(f"❌ 來源資料夾不存在：{self.cmd_copy_source}\n")
            return False

        # 清空 FTP 上同名目錄（若有）
        if not self.clean_target_folder():
            return False

        return self.upload_directory()  # 上傳資料夾內容

    # 清理 FTP 上的同名目錄，重新建立
    def clean_target_folder(self):
        try:
            self.ftp.cwd(self.ftp_target_path)
            self.ftp.cwd("/")  # 回到根目錄
            self.delete_ftp_folder_recursively(self.ftp_target_path)
            self.output.append(f"🗑️ 已刪除 FTP 上同名資料夾：{self.ftp_target_path}\n")
        except Exception:
            pass  # 忽略錯誤（可能資料夾本來就不存在）

        try:
            self.ftp.mkd(self.ftp_target_path)
            self.output.append(f"✅ 已建立新資料夾：{self.ftp_target_path}\n")
            return True
        except Exception as e:
            self.output.append(f"❌ 建立資料夾失敗：{e}\n")
            return False

    # 遞迴刪除 FTP 上的資料夾（含檔案與子目錄）
    def delete_ftp_folder_recursively(self, path):
        try:
            items = self.ftp.nlst(path)
            for item in items:
                try:
                    self.ftp.delete(item)  # 嘗試刪除檔案
                except Exception:
                    self.delete_ftp_folder_recursively(item)  # 若是資料夾則遞迴
            self.ftp.rmd(path)
        except Exception as e:
            self.output.append(f"⚠️ 刪除舊資料夾失敗或不存在：{e}\n")

    # 上傳本地資料夾至 FTP
    def upload_directory(self):
        for root, dirs, files in os.walk(self.cmd_copy_source):
            for filename in files:
                fullpath = os.path.join(root, filename)
                ftp_path = os.path.join(
                    self.ftp_target_path,
                    os.path.relpath(fullpath, self.cmd_copy_source)
                ).replace("\\", "/")  # Windows 分隔符轉換

                try:
                    dir_path = os.path.dirname(ftp_path)
                    self.ensure_ftp_directory_exists(dir_path)  # 確保目標資料夾存在
                    with open(fullpath, "rb") as f:
                        self.ftp.storbinary(f"STOR {ftp_path}", f)
                    self.output.append(f"✅ 上傳檔案：{ftp_path}\n")
                except Exception as e:
                    self.output.append(f"❌ 上傳檔案失敗：{ftp_path} - {e}\n")
                    return False
        return True

    # 確保 FTP 上的多層資料夾存在（逐層建立）
    def ensure_ftp_directory_exists(self, dir_path):
        parts = dir_path.strip("/").split("/")
        current = ""
        for part in parts:
            current += f"/{part}"
            try:
                self.ftp.mkd(current)
            except Exception:
                pass  # 若已存在則跳過
