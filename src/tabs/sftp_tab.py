from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton,
    QFormLayout, QFileDialog
)
import paramiko
import os
import json
from os.path import basename


class SftpTab(QWidget):
    def __init__(self, output_display=None):
        """
        初始化 SftpTab

        :param output_display: 主視窗的 QTextEdit，用於顯示訊息
        """
        super().__init__()
        self.output = output_display
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.sftp_host_input = QLineEdit()
        self.sftp_user_input = QLineEdit()
        self.sftp_pass_input = QLineEdit()
        self.sftp_port_input = QLineEdit()
        self.sftp_port_input.setText("22")  # 預設 SFTP 使用 port 22
        self.sftp_pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        test_button = QPushButton("測試 SFTP 連線")
        test_button.clicked.connect(self.test_sftp_connection)

        import_button = QPushButton("📂 匯入 JSON 設定")
        import_button.clicked.connect(self.import_json_config)

        layout.addRow("SFTP 主機名稱:", self.sftp_host_input)
        layout.addRow("連接埠:", self.sftp_port_input)
        layout.addRow("使用者名稱:", self.sftp_user_input)
        layout.addRow("密碼:", self.sftp_pass_input)
        layout.addRow(test_button)
        layout.addRow(import_button)

        self.setLayout(layout)

    def log(self, message):
        """
        輸出訊息到主畫面
        """
        if self.output:
            self.output.append(message)

    def get_sftp_connection(self):
        """
        建立並回傳 SFTP 連線物件
        """
        host = self.sftp_host_input.text().strip()
        port = int(self.sftp_port_input.text().strip())
        user = self.sftp_user_input.text().strip()
        password = self.sftp_pass_input.text().strip()

        if not host or not user or not password:
            raise ValueError("⚠️ 請完整填寫 SFTP 資訊！")

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=user, password=password)
        sftp = ssh.open_sftp()
        return ssh, sftp

    def test_sftp_connection(self):
        """
        測試 SFTP 是否能連線成功
        """
        try:
            ssh, sftp = self.get_sftp_connection()
            self.log("✅ SFTP 連線成功！\n")
            sftp.close()
            ssh.close()
        except Exception as e:
            self.log(f"❌ SFTP 連線失敗：{e}\n")

    def ensure_remote_dir(self, sftp, remote_dir):
        """
        遞迴建立遠端資料夾
        """
        dirs = remote_dir.strip('/').split('/')
        path = ""
        for d in dirs:
            path += f"/{d}"
            try:
                sftp.chdir(path)
            except IOError:
                sftp.mkdir(path)

    def upload_file(self, local_path: str, remote_dir: str = "."):
        """
        將本地檔案上傳到 SFTP 指定目錄，若遠端路徑不存在則自動建立

        :param local_path: 本地檔案完整路徑
        :param remote_dir: SFTP 目的資料夾（預設為目前目錄）
        """
        try:
            ssh, sftp = self.get_sftp_connection()

            # 確保遠端目錄存在
            self.ensure_remote_dir(sftp, remote_dir)

            remote_path = f"{remote_dir}/{basename(local_path)}"
            sftp.put(local_path, remote_path)

            self.log(f"✅ 上傳成功：{local_path} ➡️ SFTP:{remote_path}\n")

            sftp.close()
            ssh.close()

        except Exception as e:
            self.log(f"❌ 上傳失敗：{e}\n")

    def import_json_config(self):
        """
        匯入 JSON 設定檔，並自動填入欄位
        JSON 格式範例:
        {
            "host": "example.com",
            "port": 22,
            "user": "username",
            "password": "yourpassword"
        }
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "選擇 JSON 設定檔", "", "JSON Files (*.json)")
        if not file_name:
            return

        try:
            with open(file_name, "r", encoding="utf-8") as f:
                config = json.load(f)

            self.sftp_host_input.setText(config.get("host", ""))
            self.sftp_port_input.setText(str(config.get("port", "22")))
            self.sftp_user_input.setText(config.get("user", ""))
            self.sftp_pass_input.setText(config.get("password", ""))

            self.log(f"✅ 已匯入設定檔：{file_name}\n")

        except Exception as e:
            self.log(f"❌ 匯入 JSON 設定失敗：{e}\n")