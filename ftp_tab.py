# ftp_tab.py
from ftplib import FTP, all_errors
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton,
    QFormLayout, QTextEdit
)

class FtpTab(QWidget):
    def __init__(self, output_display=None):
        """
        初始化 FtpTab

        :param output_display: 主視窗的 QTextEdit，用於顯示訊息
        """
        super().__init__()
        self.ftp = None
        self.output = output_display
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.ftp_host_input = QLineEdit()
        self.ftp_user_input = QLineEdit()
        self.ftp_pass_input = QLineEdit()
        self.ftp_pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        test_button = QPushButton("測試 FTP 連線")
        test_button.clicked.connect(self.test_ftp_connection)

        layout.addRow("FTP 主機名稱:", self.ftp_host_input)
        layout.addRow("使用者名稱:", self.ftp_user_input)
        layout.addRow("密碼:", self.ftp_pass_input)
        layout.addRow(test_button)

        self.setLayout(layout)

    def log(self, message):
        """
        輸出訊息到主畫面
        """
        if self.output:
            self.output.append(message)

    def test_ftp_connection(self):
        """
        測試 FTP 是否能連線成功
        """
        try:
            ftp = self.get_ftp_connection()
            ftp.quit()
            self.log("✅ FTP 連線成功！\n")
        except Exception as e:
            self.log(f"❌ FTP 連線失敗：{e}\n")

    def get_ftp_connection(self):
        """
        建立並回傳 FTP 連線物件

        :return: FTP 連線實例
        :raises: 所有連線錯誤
        """
        host = self.ftp_host_input.text().strip()
        user = self.ftp_user_input.text().strip()
        password = self.ftp_pass_input.text().strip()

        if not host or not user or not password:
            raise ValueError("⚠️ 請完整填寫 FTP 資訊！")

        ftp = FTP()
        ftp.connect(host)
        ftp.login(user, password)
        return ftp

    def upload_file(self, local_path: str, remote_dir: str = "/"):
        """
        將本地檔案上傳到 FTP 指定目錄

        :param local_path: 本地檔案完整路徑
        :param remote_dir: FTP 目的資料夾（預設為根目錄）
        """
        from os.path import basename

        try:
            ftp = self.get_ftp_connection()
            ftp.cwd(remote_dir)

            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {basename(local_path)}", f)

            self.log(f"✅ 上傳成功：{local_path} ➡️ FTP:{remote_dir}/{basename(local_path)}\n")
            ftp.quit()

        except Exception as e:
            self.log(f"❌ 上傳失敗：{e}\n")
