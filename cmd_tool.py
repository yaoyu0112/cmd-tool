from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QTextEdit, QLabel
from cmd_tab import CmdTab
from ftp_tab import FtpTab


class CMDTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CMD 控制工具 - 模組化版")
        self.resize(800, 700)

        layout = QVBoxLayout()
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        tabs = QTabWidget()

        # 初始化 FTP Tab，並將 output 傳入
        self.ftp_tab = FtpTab(self.output)

        # 初始化 CMD Tab，傳入 output 及 ftp_tab 實例（用來使用 FTP 功能）
        self.cmd_tab = CmdTab(self.output, self.ftp_tab)

        tabs.addTab(self.cmd_tab, "CMD 控制")
        tabs.addTab(self.ftp_tab, "FTP 設定")

        layout.addWidget(tabs)
        layout.addWidget(QLabel("輸出結果："))
        layout.addWidget(self.output)

        self.setLayout(layout)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = CMDTool()
    window.show()
    sys.exit(app.exec())
