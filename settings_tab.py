import json
import os
import subprocess
import paramiko
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QGroupBox
)

class SettingsTab(QWidget):
    def __init__(self, output_display):
        super().__init__()
        self.output = output_display
        self.ssh = None
        self.sftp = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        load_button = QPushButton("匯入 JSON 設定檔")
        load_button.clicked.connect(self.load_json_file)
        layout.addWidget(load_button)

        # SFTP/SSH 設定區塊
        sftp_group = QGroupBox("SSH 設定")
        sftp_layout = QVBoxLayout()
        self.sftp_host_input = QLineEdit()
        self.sftp_port_input = QLineEdit()
        self.sftp_user_input = QLineEdit()
        self.sftp_pass_input = QLineEdit()

        for widget in (self.sftp_host_input, self.sftp_port_input, self.sftp_user_input, self.sftp_pass_input):
            widget.setReadOnly(True)

        sftp_layout.addWidget(QLabel("SSH 主機名稱："))
        sftp_layout.addWidget(self.sftp_host_input)
        sftp_layout.addWidget(QLabel("SSH 連接埠："))
        sftp_layout.addWidget(self.sftp_port_input)
        sftp_layout.addWidget(QLabel("使用者名稱："))
        sftp_layout.addWidget(self.sftp_user_input)
        sftp_layout.addWidget(QLabel("密碼："))
        sftp_layout.addWidget(self.sftp_pass_input)
        sftp_group.setLayout(sftp_layout)
        layout.addWidget(sftp_group)

        # CMD 控制區塊
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
        cmd_layout.addWidget(QLabel("遠端目標路徑："))
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
                self.output.append(f"❌ 讀取 JSON 錯誤: {e}\n")

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
        # 從介面取得 SSH/SFTP 主機名稱
        self.sftp_host = self.sftp_host_input.text()
        
        # 取得連接埠，若欄位為空則預設為 22（SSH 預設 port）
        self.sftp_port = int(self.sftp_port_input.text().strip() or "22")
        
        # 取得使用者帳號
        self.sftp_user = self.sftp_user_input.text()
        
        # 取得密碼
        self.sftp_pass = self.sftp_pass_input.text()
        
        # 取得本機要執行命令的工作目錄
        self.cmd_working_dir = self.cmd_working_dir_input.text()
        
        # 取得要執行的本機命令（例如 build、打包指令）
        self.cmd_command = self.cmd_command_input.text()
        
        # 取得要上傳的資料來源資料夾（通常是 build 完的資料夾）
        self.cmd_copy_source = self.cmd_copy_source_input.text()
        
        # 設定遠端主機上要儲存的目標路徑
        self.sftp_target_path = self.sftp_target_path_input.text()

        # 建立 SSH 連線，若失敗則中止
        if not self.connect_ssh(): return

        # 切換至本機指定的工作目錄（避免 CMD 指令失效）
        if not self.change_working_directory(): return

        # 執行本機 CMD 指令（例如打包指令）
        if not self.run_cmd_command(): return

        # 清除遠端舊檔並上傳新檔案（透過 SFTP 處理）
        if not self.remote_cleanup_and_upload(): return

        # 若以上步驟皆成功，顯示成功訊息
        self.output.append("✅ 設定已成功套用！\n")

    def connect_ssh(self):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                self.sftp_host,
                port=self.sftp_port,
                username=self.sftp_user,
                password=self.sftp_pass
            )
            self.sftp = self.ssh.open_sftp()
            self.output.append(f"✅ SSH & SFTP 連線成功（port: {self.sftp_port}）\n")
            return True
        except Exception as e:
            self.output.append(f"❌ SSH/SFTP 連線失敗：{e}\n")
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

    def change_working_directory(self):
        try:
            os.chdir(self.cmd_working_dir)
            self.output.append(f"✅ 切換至資料夾：{self.cmd_working_dir}\n")
            return True
        except Exception:
            self.output.append(f"❌ 找不到資料夾：{self.cmd_working_dir}\n")
            return False

    def remote_cleanup_and_upload(self):
        cleanup_cmd = f"rm -rf {self.sftp_target_path}/pspf"
        if not self.run_remote_command(cleanup_cmd, "🗑️ 刪除遠端 pspf 資料夾"):
            return False

        mkdir_cmd = f"mkdir -p {self.sftp_target_path}"
        if not self.run_remote_command(mkdir_cmd, "✅ 建立遠端目標資料夾"):
            return False

        try:
            self.upload_folder_sftp(self.cmd_copy_source, self.sftp_target_path)
            self.output.append(f"✅ 資料夾已透過 SFTP 上傳至遠端：{self.sftp_target_path}\n")
            return True
        except Exception as e:
            self.output.append(f"❌ SFTP 上傳失敗：{e}\n")
            return False

    def run_remote_command(self, command, description="執行指令"):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            out = stdout.read().decode()
            err = stderr.read().decode()
            if out:
                self.output.append(f"{description} 成功：\n{out}")
            if err:
                self.output.append(f"{description} 錯誤：\n{err}")
            return True
        except Exception as e:
            self.output.append(f"❌ 遠端指令失敗：{command} - {e}\n")
            return False

    def upload_folder_sftp(self, local_path, remote_path):
        for root, dirs, files in os.walk(local_path):
            rel_path = os.path.relpath(root, local_path)
            remote_dir = os.path.join(remote_path, rel_path).replace("\\", "/")

            try:
                self.sftp.chdir(remote_dir)
            except IOError:
                self.sftp.mkdir(remote_dir)

            for file in files:
                local_file = os.path.join(root, file)
                remote_file = os.path.join(remote_dir, file).replace("\\", "/")
                self.sftp.put(local_file, remote_file)
