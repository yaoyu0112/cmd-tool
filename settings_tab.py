# settings_tab.py
import json
import os
import subprocess
import paramiko  # 使用 paramiko 來支援 SFTP
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QGroupBox
)

class SettingsTab(QWidget):
    def __init__(self, output_display):
        super().__init__()
        self.output = output_display
        self.sftp = None
        self.ssh = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        load_button = QPushButton("匯入 JSON 設定檔")
        load_button.clicked.connect(self.load_json_file)
        layout.addWidget(load_button)

        ftp_group = QGroupBox("SFTP 設定")
        ftp_layout = QVBoxLayout()
        self.ftp_host_input = QLineEdit()
        self.ftp_user_input = QLineEdit()
        self.ftp_pass_input = QLineEdit()

        for widget in (self.ftp_host_input, self.ftp_user_input, self.ftp_pass_input):
            widget.setReadOnly(True)

        ftp_layout.addWidget(QLabel("SFTP 主機名稱："))
        ftp_layout.addWidget(self.ftp_host_input)
        ftp_layout.addWidget(QLabel("使用者名稱："))
        ftp_layout.addWidget(self.ftp_user_input)
        ftp_layout.addWidget(QLabel("密碼："))
        ftp_layout.addWidget(self.ftp_pass_input)
        ftp_group.setLayout(ftp_layout)
        layout.addWidget(ftp_group)

        cmd_group = QGroupBox("CMD 控制")
        cmd_layout = QVBoxLayout()
        self.cmd_working_dir_input = QLineEdit()
        self.cmd_command_input = QLineEdit()
        self.cmd_copy_source_input = QLineEdit()
        self.ftp_target_path_input = QLineEdit()

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
        cmd_layout.addWidget(QLabel("SFTP 目標路徑："))
        cmd_layout.addWidget(self.ftp_target_path_input)
        cmd_group.setLayout(cmd_layout)
        layout.addWidget(cmd_group)

        self.apply_button = QPushButton("✅ 套用設定")
        layout.addWidget(self.apply_button)
        self.apply_button.clicked.connect(self.apply_settings)

        self.setLayout(layout)

    def load_json_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "選擇 JSON 檔案", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.fill_fields(data)
            except Exception as e:
                print(f"❌ 讀取 JSON 錯誤: {e}")

    def fill_fields(self, data):
        self.ftp_host_input.setText(data.get("ftp_host", ""))
        self.ftp_user_input.setText(data.get("ftp_user", ""))
        self.ftp_pass_input.setText(data.get("ftp_pass", ""))
        self.cmd_working_dir_input.setText(data.get("cmd_working_dir", ""))
        self.cmd_command_input.setText(data.get("cmd_command", ""))
        self.cmd_copy_source_input.setText(data.get("cmd_copy_source", ""))
        self.ftp_target_path_input.setText(data.get("ftp_target_path", ""))

    def apply_settings(self):
        self.ftp_host = self.ftp_host_input.text()
        self.ftp_user = self.ftp_user_input.text()
        self.ftp_pass = self.ftp_pass_input.text()
        self.cmd_working_dir = self.cmd_working_dir_input.text()
        self.cmd_command = self.cmd_command_input.text()
        self.cmd_copy_source = self.cmd_copy_source_input.text()
        self.ftp_target_path = self.ftp_target_path_input.text()

        if not self.connect_sftp(): return
        if not self.change_working_directory(): return
        if not self.run_cmd_command(): return
        if not self.upload_folder_to_sftp(): return

        self.output.append("✅ 設定已成功套用！\n")

    def connect_sftp(self):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.ftp_host, username=self.ftp_user, password=self.ftp_pass)
            self.sftp = self.ssh.open_sftp()
            self.output.append("✅ SFTP 連線成功！\n")
            return True
        except Exception as e:
            self.output.append(f"❌ SFTP 連線失敗：{e}\n")
            return False

    def change_working_directory(self):
        try:
            os.chdir(self.cmd_working_dir)
            self.output.append(f"✅ 切換至資料夾：{self.cmd_working_dir}\n")
            return True
        except Exception:
            self.output.append(f"❌ 找不到資料夾：{self.cmd_working_dir}\n")
            return False

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

    def upload_folder_to_sftp(self):
        if not os.path.isdir(self.cmd_copy_source):
            self.output.append(f"❌ 來源資料夾不存在：{self.cmd_copy_source}\n")
            return False

        if not self.clean_target_folder():
            return False

        return self.upload_directory()

    def clean_target_folder(self):
        try:
            self.delete_sftp_folder_recursively(self.ftp_target_path)
            self.output.append(f"🗑️ 已刪除 SFTP 上同名資料夾：{self.ftp_target_path}\n")
        except Exception:
            pass  # 如果本來就不存在可忽略

        try:
            self.ensure_sftp_directory_exists(self.ftp_target_path)
            self.output.append(f"✅ 已建立新資料夾：{self.ftp_target_path}\n")
            return True
        except Exception as e:
            self.output.append(f"❌ 建立資料夾失敗：{e}\n")
            return False

    def delete_sftp_folder_recursively(self, path):
        try:
            for item in self.sftp.listdir_attr(path):
                full_path = os.path.join(path, item.filename).replace("\\", "/")
                if paramiko.S_ISDIR(item.st_mode):
                    self.delete_sftp_folder_recursively(full_path)
                else:
                    self.sftp.remove(full_path)
            self.sftp.rmdir(path)
        except Exception as e:
            self.output.append(f"⚠️ 刪除舊資料夾失敗或不存在：{e}\n")

    def upload_directory(self):
        for root, dirs, files in os.walk(self.cmd_copy_source):
            for filename in files:
                fullpath = os.path.join(root, filename)
                relative_path = os.path.relpath(fullpath, self.cmd_copy_source).replace("\\", "/")
                sftp_path = os.path.join(self.ftp_target_path, relative_path).replace("\\", "/")

                try:
                    dir_path = os.path.dirname(sftp_path)
                    self.ensure_sftp_directory_exists(dir_path)
                    self.sftp.put(fullpath, sftp_path)
                    self.output.append(f"✅ 上傳檔案：{sftp_path}\n")
                except Exception as e:
                    self.output.append(f"❌ 上傳檔案失敗：{sftp_path} - {e}\n")
                    return False
        return True

    def ensure_sftp_directory_exists(self, dir_path):
        parts = dir_path.strip("/").split("/")
        current = ""
        for part in parts:
            current = f"{current}/{part}" if current else f"/{part}"
            try:
                self.sftp.mkdir(current)
            except IOError:
                pass  # 資料夾已存在
