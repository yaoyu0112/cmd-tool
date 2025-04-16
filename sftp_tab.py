#sftp_tab.py
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton,
    QFormLayout, QTextEdit
)
import paramiko
from os.path import basename


class SftpTab(QWidget):
    def __init__(self, output_display=None):
        """
        初始化 SftpTab

        :param output_display: 主視窗的 QTextEdit，用於顯示訊息
        """
        super().__init__()
        self.sftp = None
        self.ssh_client = None
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

        layout.addRow("SFTP 主機名稱:", self.sftp_host_input)
        layout.addRow("連接埠:", self.sftp_port_input)
        layout.addRow("使用者名稱:", self.sftp_user_input)
        layout.addRow("密碼:", self.sftp_pass_input)
        layout.addRow(test_button)

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

    def upload_file(self, local_path: str, remote_dir: str = "."):
        """
        將本地檔案上傳到 SFTP 指定目錄

        :param local_path: 本地檔案完整路徑
        :param remote_dir: SFTP 目的資料夾（預設為目前目錄）
        """
        try:
            ssh, sftp = self.get_sftp_connection()

            remote_path = f"{remote_dir}/{basename(local_path)}"

            sftp.chdir(remote_dir)
            sftp.put(local_path, remote_path)

            self.log(f"✅ 上傳成功：{local_path} ➡️ SFTP:{remote_path}\n")

            sftp.close()
            ssh.close()

        except Exception as e:
            self.log(f"❌ 上傳失敗：{e}\n")
