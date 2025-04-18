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

        sftp_group = QGroupBox("SFTP 設定")
        sftp_layout = QVBoxLayout()
        self.sftp_host_input = QLineEdit()
        self.sftp_port_input = QLineEdit()
        self.sftp_user_input = QLineEdit()
        self.sftp_pass_input = QLineEdit()

        for widget in (self.sftp_host_input, self.sftp_port_input, self.sftp_user_input, self.sftp_pass_input):
            widget.setReadOnly(True)

        sftp_layout.addWidget(QLabel("SFTP 主機名稱："))
        sftp_layout.addWidget(self.sftp_host_input)
        sftp_layout.addWidget(QLabel("SFTP 連接埠："))
        sftp_layout.addWidget(self.sftp_port_input)
        sftp_layout.addWidget(QLabel("使用者名稱："))
        sftp_layout.addWidget(self.sftp_user_input)
        sftp_layout.addWidget(QLabel("密碼："))
        sftp_layout.addWidget(self.sftp_pass_input)
        sftp_group.setLayout(sftp_layout)
        layout.addWidget(sftp_group)

        cmd_group = QGroupBox("CMD 控制")
        cmd_layout = QVBoxLayout()
        self.cmd_working_dir_input = QLineEdit()
        self.cmd_command_input = QLineEdit()
        self.cmd_copy_source_input = QLineEdit()
        self.sftp_target_path_input = QLineEdit()

        for widget in (
            self.cmd_working_dir_input,
            self.cmd_command_input,
            self.cmd_copy_source_input,
            self.sftp_target_path_input
        ):
            widget.setReadOnly(True)

        cmd_layout.addWidget(QLabel("CMD 執行資料夾："))
        cmd_layout.addWidget(self.cmd_working_dir_input)
        cmd_layout.addWidget(QLabel("輸入 CMD 指令："))
        cmd_layout.addWidget(self.cmd_command_input)
        cmd_layout.addWidget(QLabel("複製資料夾來源："))
        cmd_layout.addWidget(self.cmd_copy_source_input)
        cmd_layout.addWidget(QLabel("SFTP 目標路徑："))
        cmd_layout.addWidget(self.sftp_target_path_input)
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
        self.sftp_host_input.setText(data.get("sftp_host", ""))
        self.sftp_port_input.setText(str(data.get("sftp_port", "")))
        self.sftp_user_input.setText(data.get("sftp_user", ""))
        self.sftp_pass_input.setText(data.get("sftp_pass", ""))
        self.cmd_working_dir_input.setText(data.get("cmd_working_dir", ""))
        self.cmd_command_input.setText(data.get("cmd_command", ""))
        self.cmd_copy_source_input.setText(data.get("cmd_copy_source", ""))
        self.sftp_target_path_input.setText(data.get("sftp_target_path", ""))

    def apply_settings(self):
        self.sftp_host = self.sftp_host_input.text()
        self.sftp_port = self.sftp_port_input.text()
        self.sftp_user = self.sftp_user_input.text()
        self.sftp_pass = self.sftp_pass_input.text()
        self.cmd_working_dir = self.cmd_working_dir_input.text()
        self.cmd_command = self.cmd_command_input.text()
        self.cmd_copy_source = self.cmd_copy_source_input.text()
        self.sftp_target_path = self.sftp_target_path_input.text()

        if not self.connect_sftp(): return
        if not self.change_working_directory(): return
        if not self.run_cmd_command(): return
        if not self.upload_folder_to_sftp(): return

        self.output.append("✅ 設定已成功套用！\n")

    def connect_sftp(self):
        try:
            port = int(self.sftp_port) if self.sftp_port.strip() else 22
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                self.sftp_host,
                port=port,
                username=self.sftp_user,
                password=self.sftp_pass
            )
            self.sftp = self.ssh.open_sftp()
            self.output.append(f"✅ SFTP 連線成功（port: {port}）！\n")
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
            self.delete_pspf_folder(self.sftp_target_path)
            self.output.append(f"🗑️ 已刪除 SFTP 上同名資料夾：{self.sftp_target_path}\n")
        except Exception:
            return False

        try:
            self.ensure_sftp_directory_exists(self.sftp_target_path)
            self.output.append(f"✅ 已建立新資料夾：{self.sftp_target_path}\n")
            return True
        except Exception as e:
            self.output.append(f"❌ 建立資料夾失敗：{e}\n")
            return False

    def delete_pspf_folder(self, path):
        try:
            items = self.sftp.listdir_attr(path)
            for item in items:
                if item.filename == "pspf" and paramiko.S_ISDIR(item.st_mode):
                    target_path = os.path.join(path, "pspf").replace("\\", "/")
                    self._delete_folder_contents(target_path)
                    self.sftp.rmdir(target_path)
                    self.output.append("✅ 資料夾 'pspf' 已成功刪除\n")
                    return
            self.output.append("ℹ️ 未找到 'pspf' 資料夾\n")
        except Exception as e:
            self.output.append(f"⚠️ 無法刪除 'pspf' 資料夾：{e}\n")

    def _delete_folder_contents(self, folder_path):
        # 遞迴刪除內容（但只針對 pspf 裡面的內容）
        for item in self.sftp.listdir_attr(folder_path):
            full_path = os.path.join(folder_path, item.filename).replace("\\", "/")
            if paramiko.S_ISDIR(item.st_mode):
                self._delete_folder_contents(full_path)
                self.sftp.rmdir(full_path)
            else:
                self.sftp.remove(full_path)

    def upload_directory(self):
        for root, dirs, files in os.walk(self.cmd_copy_source):
            for filename in files:
                fullpath = os.path.join(root, filename)
                relative_path = os.path.relpath(fullpath, self.cmd_copy_source).replace("\\", "/")
                sftp_path = os.path.join(self.sftp_target_path, relative_path).replace("\\", "/")

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
                pass
