from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QTextEdit, QLabel
from cmd_tab import CmdTab
from sftp_tab import SftpTab
from settings_tab import SettingsTab


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
        self.sftp_tab = SftpTab(self.output)

        # 初始化 CMD Tab，傳入 output 及 sftp_tab 實例（用來使用 FTP 功能）
        self.cmd_tab = CmdTab(self.output, self.sftp_tab)

        # 初始化 Settings Tab
        self.settings_tab = SettingsTab(self.output)

        tabs.addTab(self.cmd_tab, "CMD 控制")
        tabs.addTab(self.sftp_tab, "SFTP 設定")
        tabs.addTab(self.settings_tab, "json自動化 設定")

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
